from ingredient_parser import parse_ingredient
from typing import Tuple, List
from recipe_manager.ingredient_readers import IngredientReaderInterface
from recipe_manager.sentence_transformer_handler import SentenceTransformerHandler
from tests.ingredient_testing.ingredient_writer import RawIngredientReader
import logging_config, logging

# Get logger instance
logger = logging.getLogger(__name__)

IGNORED_INGREDIENTS = [
    "water",
]

class IngredientNormalizer:
    """
    Class to handle normalizing ingredient strings
    This class uses the nlp-ingredient-parser library, for more information on this, see https://ingredient-parser.readthedocs.io/en/latest/
    """
    def __init__(self, ingredient_reader: IngredientReaderInterface):
        # Keep reference to ingredient reader
        self.ingredient_reader = ingredient_reader

        # Generate set of existing ingredient strings for efficient exact string matching
        self.unrolled_ingredient_strings = set(self.ingredient_reader.get_and_unroll_ingredients())

        # Generate dict of all ingredients and their aliases
        self.all_ingredients = self.ingredient_reader.get_all_ingredients()

        # Instantiate SentenceTransformerHandler object
        self.sentence_transformer = SentenceTransformerHandler()

    def generate_normalize_ingredient_string_list(self, ingredient_string_list: List[str]) -> List[str]:
        """
        Takes ingredient_string_list and generates a final normalized ingredients list.
        Iterates through ingredient_string_list and calls generate_normalized_ingredient_string on each tuple.
        Prioritize the "non-foundational" ingredient name first, only use match for "foundational" ingredient if the non-foundational match doesn't exist
        If any values are None, this means that the ingredient could not be normalized confidently.
        """
        # First generate the ingredient string tuples by trimming/parsing provided ingredient list
        ingredient_string_tuples = self.trim_ingredient_string_list(ingredient_string_list)

        normalized_list = []
        for ingredient_tuple in ingredient_string_tuples:
            if ingredient_tuple[0] in IGNORED_INGREDIENTS or ingredient_tuple[1] in IGNORED_INGREDIENTS:
                # Ignore anything in IGNORED_INGREDIENTS list
                logger.info(f"Ignored ingredient found: {ingredient_tuple}, skipping.")
                continue

            # Attempt to generate normalized name for next tuple
            new_normalized_name = self.generate_normalized_ingredient_string(ingredient_tuple)

            if not new_normalized_name:
                # Ingredient match not confidently found. Log warning and continue
                logger.warning(f"Couldn't find ingredient match for tuple: {ingredient_tuple}")
                continue

            # If match was found, append to our list and continue
            normalized_list.append(new_normalized_name)
            print(f"For tuple: {ingredient_tuple}, matched string was {new_normalized_name}")

        return normalized_list

    def generate_normalized_ingredient_string(self, ingredient_tuple_to_normalize: Tuple[str,str]) -> str | None:
        """
        Generates a normalized ingredient string based on the passed in ingredient string.
        Prioritizes regular ingredient name over foundational ingredient name
        """
        normalized_string = None

        # First check the regular ingredient string for an exact match in the unrolled_ingredient_strings set
        if ingredient_tuple_to_normalize[0] and self.exact_ingredient_match(ingredient_tuple_to_normalize[0]):
            # If match found, we then need to find the top level ingredient string to ensure this isn't an alias match
            return self.find_top_level_ingredient_name(ingredient_tuple_to_normalize[0])

        # Next check foundational ingredient string for exact match
        if ingredient_tuple_to_normalize[1] and self.exact_ingredient_match(ingredient_tuple_to_normalize[1]):
            # If match found, we then need to find the top level ingredient string to ensure this isn't an alias match
            return self.find_top_level_ingredient_name(ingredient_tuple_to_normalize[1])

        # If an exact match was not found, we need to perform more contextual string processing
        # TODO: Perform sentence transformer cosine similarity matching here. Should probably be a different class.

        return normalized_string

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
        "6 green olives"
    ]

    # Instance of ingredient Normalizer
    raw_ingredient_reader = RawIngredientReader()
    ingredient_normalizer = IngredientNormalizer(raw_ingredient_reader)

    generated_ingredient_string_list = ingredient_normalizer.generate_normalize_ingredient_string_list(ingredient_strings)
    print("Finished processing ingredient list")
