from ingredient_parser import parse_ingredient
from typing import Tuple
from recipe_manager.ingredient_readers import IngredientReaderInterface
from tests.ingredient_testing.ingredient_writer import RawIngredientReader

IGNORED_INGREDIENTS = [
    "water",
]

class IngredientNormalizer:
    def __init__(self, ingredient_reader: IngredientReaderInterface):
        self.ingredient_reader = ingredient_reader
        self.unrolled_ingredient_strings = self.ingredient_reader.get_and_unroll_ingredients()
        self.all_ingredients = self.ingredient_reader.get_all_ingredients()

    @staticmethod
    def trim_ingredient_string(ingredient_string: str) -> Tuple[str, str]:
        # Use foundation foods for extra trimming
        lower_ingredient_string = ingredient_string.lower()
        parsed_ingredient = parse_ingredient(lower_ingredient_string, foundation_foods=True)

        foundation_text = None
        ingredient_text = None

        # Grab the foundation food if it exists
        if parsed_ingredient.foundation_foods:
            foundation_text = parsed_ingredient.foundation_foods[0].text

        if parsed_ingredient.name:
            ingredient_text = parsed_ingredient.name[0].text

        return ingredient_text, foundation_text




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

    raw_ingredient_reader = RawIngredientReader()
    ingredient_normalizer = IngredientNormalizer(raw_ingredient_reader)

    for ingredient in ingredient_strings:
        new_ingredient = IngredientNormalizer.trim_ingredient_string(ingredient)
        print(new_ingredient)