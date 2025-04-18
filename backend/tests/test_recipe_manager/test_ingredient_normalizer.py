import recipe_manager
from recipe_manager.ingredient_normalizer import IngredientNormalizer


def test_ingredient_trimmer():
    ingredient_trimmer = IngredientNormalizer()

    ingredient_strings = ["1 cup flour", "butter, 1 tbsp", "chicken breasts"]

    for ingredient in ingredient_strings:
        ingredient_trimmer.trim_ingredient_string(ingredient)