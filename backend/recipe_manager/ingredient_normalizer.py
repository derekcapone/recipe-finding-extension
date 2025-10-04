from pathlib import Path

from ingredient_parser import parse_ingredient
from typing import Tuple, List
from recipe_manager.ingredient_readers import IngredientReaderInterface
from tests.ingredient_testing.raw_json_ingredient_reader import RawJsonIngredientReader
import logging_config, logging
from sentence_transformers import SentenceTransformer
import faiss

# Get logger instance
logger = logging.getLogger(__name__)

IGNORED_INGREDIENTS = [
    "water",
]

class IngredientNormalizer:
    MATCHED_INGREDIENT_LOG_FILE = Path("contextual_matched_ingredients.log")
    OVERWRITE_LOG_FILE = True  # Removes existing log file when instantiated if True. Easier for debugging.

    """
    Class to handle normalizing ingredient strings
    This class uses the nlp-ingredient-parser library, for more information on this, see https://ingredient-parser.readthedocs.io/en/latest/
    """
    def __init__(self, ingredient_reader: IngredientReaderInterface):
        self.ingredient_reader = ingredient_reader

        # Generate set of existing ingredient strings for efficient exact string matching
        unrolled_ingredient_strings_list = self.ingredient_reader.get_and_unroll_ingredients()
        self.unrolled_ingredient_strings = set(unrolled_ingredient_strings_list)

        self.all_ingredients = self.ingredient_reader.get_all_ingredients()  # List[dict] of all ingredients and their aliases

        self.sentence_transformer = SentenceTransformerHandler(unrolled_ingredient_strings_list)

        if IngredientNormalizer.OVERWRITE_LOG_FILE:
            IngredientNormalizer.MATCHED_INGREDIENT_LOG_FILE.unlink(missing_ok=True)

    def generate_normalized_ingredients(self, ingredient_strings: List[str] | str) -> Tuple[List[str], List[str]]:
        """
        Takes ingredient_string_list and generates a final normalized ingredients list.
        Iterates through ingredient_string_list and calls generate_normalized_ingredient_string on each tuple.
        Prioritize the "non-foundational" ingredient name first, only use match for "foundational" ingredient if the non-foundational match doesn't exist
        If any values are None, this means that the ingredient could not be normalized confidently.
        """
        # First generate the ingredient string tuples by trimming/parsing provided ingredient list
        list_to_parse = [ingredient_strings] if not isinstance(ingredient_strings, List) else ingredient_strings
        ingredient_string_tuples = self.trim_ingredient_string_list(list_to_parse)

        normalized_list = []
        unmatched_ingredient_list = []
        for ingredient_tuple, ingredient_str in zip(ingredient_string_tuples, list_to_parse):
            if ingredient_tuple[0] in IGNORED_INGREDIENTS or ingredient_tuple[1] in IGNORED_INGREDIENTS:
                # Ignore anything in IGNORED_INGREDIENTS list
                logger.info(f"Ignored ingredient found: {ingredient_tuple}, skipping.")
                continue

            # Attempt to generate normalized name
            new_normalized_name = self.check_exact_ingredient_string_match(ingredient_tuple)

            if not new_normalized_name:
                # No exact match, try other methods of matching
                new_normalized_name = self.contextual_ingredient_match(ingredient_str, ingredient_tuple[0], ingredient_tuple[1])

            if not new_normalized_name:
                # Ingredient match not confidently found. Log warning and continue
                logger.warning(f"Couldn't find ingredient match for tuple: {ingredient_str}")
                unmatched_ingredient_list.append(ingredient_str)
                continue

            # If match was found, append to our list and continue
            normalized_list.append(new_normalized_name)
            logger.debug(f"For tuple: {ingredient_tuple}, matched string was '{new_normalized_name}'")

        return normalized_list, unmatched_ingredient_list

    def check_exact_ingredient_string_match(self, ingredient_tuple_to_normalize: Tuple[str,str]) -> str | None:
        """
        Generates a normalized ingredient string based on the passed in ingredient string.
        Prioritizes regular ingredient name over foundational ingredient name
        """
        # First check the regular ingredient string for an exact match in the unrolled_ingredient_strings set
        if ingredient_tuple_to_normalize[0] and self.exact_ingredient_match(ingredient_tuple_to_normalize[0]):
            # If match found, we then need to find the top level ingredient string to ensure this isn't an alias match
            return self.find_top_level_ingredient_name(ingredient_tuple_to_normalize[0])

        # Next check foundational ingredient string for exact match
        if ingredient_tuple_to_normalize[1] and self.exact_ingredient_match(ingredient_tuple_to_normalize[1]):
            # If match found, we then need to find the top level ingredient string to ensure this isn't an alias match
            return self.find_top_level_ingredient_name(ingredient_tuple_to_normalize[1])

        return None  # Nothing found, return None

    def find_top_level_ingredient_name(self, ingredient_to_find: str) -> str:
        """
        Finds the top level name of the ingredient_to_find string.
        Changes this string from alias to top-level name if necessary.
        """
        for ingredient_dict in self.all_ingredients:
            # First check if the string is the top level name
            if ingredient_dict["name"] == ingredient_to_find:
                return ingredient_to_find

            # Then iterate through each alias for this entry and check string matching
            for alias in ingredient_dict["alias"]:
                if alias == ingredient_to_find:
                    return ingredient_dict["name"]

        # This method should only be called if we know the string exists in our ingredient list, so raise error if we reach this point
        raise RuntimeError(f"find_top_level_ingredient_name method called for string '{ingredient_to_find}', but string doesn't exist in ingredients")

    def trim_ingredient_string_list(self, ingredient_string_list: List[str]) -> List[Tuple[str, str]]:
        """
        Iterates through ingredient_string_list and calls "trim_ingredient_string" method on each string value
        Returns list of Tuples containing <trimmed ingredient, trimmed foundation ingredient>
        """
        trimmed_ingredient_string_list = []
        for ingredient_string in ingredient_string_list:
            next_ingredient_tuple = self.trim_ingredient_string(ingredient_string)
            trimmed_ingredient_string_list.append(next_ingredient_tuple)

        return trimmed_ingredient_string_list

    @staticmethod
    def trim_ingredient_string(ingredient_string: str) -> Tuple[str, str]:
        # Use foundation foods for extra trimming
        lower_ingredient_string = ingredient_string.lower()
        parsed_ingredient = parse_ingredient(lower_ingredient_string, foundation_foods=True)

        foundation_text = None
        ingredient_text = None

        # Grab the foundation food if it exists, this is the most simplified version of the ingredient string
        if parsed_ingredient.foundation_foods:
            foundation_text = parsed_ingredient.foundation_foods[0].text

        # Grab the regular trimmed name
        if parsed_ingredient.name:
            ingredient_text = parsed_ingredient.name[0].text

        return ingredient_text, foundation_text

    def exact_ingredient_match(self, string_to_check: str) -> bool:
        """
        Checks the "unrolled_ingredient_strings" set for exact match.
        Returns True if match exists, False if no match
        """
        return string_to_check in self.unrolled_ingredient_strings

    def contextual_ingredient_match(self, *args) -> str | None:
        highest_score = 0
        best_matched_string = None
        for ingredient in args:
            if ingredient is None or type(ingredient) is not str:
                # Ignore if type is incorrect or if value is None.
                continue

            matched_string, score = self.sentence_transformer.search_ingredient(ingredient)

            if matched_string is None:
                # Score wasn't high enough, next iteration.
                continue

            if score > highest_score:
                highest_score = score
                best_matched_string = matched_string

        if not best_matched_string:
            # Nothing found, return None
            return None

        with open(IngredientNormalizer.MATCHED_INGREDIENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"Contextal match: best score is for '{args}' is {best_matched_string} with cosine score: {highest_score}\n")

        # Find and return top-level ingredient name
        normalized_string = self.find_top_level_ingredient_name(best_matched_string)
        return normalized_string


class SentenceTransformerHandler:
    COSINE_SIMILARITY_THRESHOLD = 0.75
    UNKNOWN_INGREDIENT_LOG_FILE = Path("unknown_ingredients_scores.log")
    OVERWRITE_LOG_FILE = True  # Removes existing log file when instantiated if True. Easier for debugging.

    def __init__(self, known_ingredients: List[str]):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.known_ingredients = known_ingredients  # Keep reference to ingredient list

        # Pre-encode ingredient embeddings
        self.ingredient_embeddings = self.model.encode(
            known_ingredients,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        ).astype("float32")

        # Build FAISS index for cosine similarity search for all known ingredients.
        self.index = faiss.IndexFlatIP(self.ingredient_embeddings.shape[1])
        self.index.add(self.ingredient_embeddings)

        if SentenceTransformerHandler.OVERWRITE_LOG_FILE:
            SentenceTransformerHandler.UNKNOWN_INGREDIENT_LOG_FILE.unlink(missing_ok=True)

    def search_ingredient(self, query, k=5, debug_print=False) -> Tuple[str, float] | Tuple[None, None]:
        # Encode query embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        ).astype("float32")

        # FAISS similarity search
        scores, indices = self.index.search(query_embedding, k)

        if debug_print:
            print(f"\nQuery: '{query}'")
            for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
                print(f"{rank}. {self.known_ingredients[idx]} (score: {score:.4f})")

        # Filter out anything below score threshold.
        highest_score = scores[0][0]
        if highest_score < self.COSINE_SIMILARITY_THRESHOLD:
            log_string = f"QUERY FOR INGREDIENT: '{query}'\n"
            for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
                log_string += f"{rank}. {self.known_ingredients[idx]} (score: {score:.4f})\n"
            log_string += "\n\n"
            self.log_ingredient_miss(log_string, write_to_console=True)
            return None, None

        # Return string with the highest score and the score value
        highest_score_idx = indices[0][0]
        return self.known_ingredients[highest_score_idx], highest_score

    @staticmethod
    def log_ingredient_miss(log_message: str, write_to_console: bool = False):
        if write_to_console:
            print(log_message)

        with open(SentenceTransformerHandler.UNKNOWN_INGREDIENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message)


if __name__ == "__main__":
    ingredient_strings = [
        "1 teaspoon Mexican oregano",
        "2 tablespoons packed light brown sugar",
        "cooking spray",
        "2 pounds ground chuck",
        "1 cup flour",
        "butter or olive oil, 1 tbsp",
        "chicken thigh",
        "1 (16 ounce) package pasta",
        "2 tablespoons olive oil",
        "½ cup chopped onion",
        "2 ½ tablespoons pesto",
        "salt to taste",
        "ground black pepper to taste",
        "2 tablespoons grated Parmesan cheese",
        "1 large organic cucumber",
        "2 pounds 85% lean ground beef",
        "1 (12-ounce) package frozen mixed vegetables",
        "1 1/2 cups lower-sodium beef broth",
        "6 green olives",
        "parmigiano reggiano",
        "somerandomingredient sasdf"
    ]

    # Instance of ingredient Normalizer
    raw_ingredient_reader = RawJsonIngredientReader()
    ingredient_normalizer = IngredientNormalizer(raw_ingredient_reader)

    generated_ingredient_string_list, unmatched_ingredient_list = ingredient_normalizer.generate_normalized_ingredients(ingredient_strings)
    print(generated_ingredient_string_list)
