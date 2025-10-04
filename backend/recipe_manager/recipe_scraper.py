import requests
import os
import logging_config, logging
from recipe_manager.ingredient_normalizer import IngredientNormalizer
from tests.ingredient_testing.raw_json_ingredient_reader import RawJsonIngredientReader
from mongodb_driver import DatabaseDriver

# Get logger instance
logger = logging.getLogger(__name__)

# Your API key
API_KEY = os.getenv("SPOONACULAR_APP_ID")

# Base URL for the Spoonacular API
BASE_URL = 'https://api.spoonacular.com'


class RecipeScraper:
    MAXIMUM_NUMBER_UNKNOWN_INGREDIENTS = 3  # Number of unknown ingredients to tolerate before scrapping recipe.

    def __init__(self, ingredient_normalizer: IngredientNormalizer):
        self.ingredient_normalizer = ingredient_normalizer

        self.database_driver = DatabaseDriver()

    def scrape_and_insert_recipes(self, num_recipes: int):
        # Get random recipes and transform to remove unused data
        random_recipe_list = self.get_random_recipes(num_recipes)
        transformed_random_recipes = self.transform_recipe_structure(random_recipe_list)

        # Ensure each recipe link still works before inserting
        valid_recipe_list = self.check_and_normalize_recipes(transformed_random_recipes)

        self.database_driver.insert_recipe_list(valid_recipe_list)

    def get_random_recipes(self, num_recipes: int) -> dict | None:
        """
        Scrapes provided number of random recipes from API
        :param num_recipes: Number of recipes to retrieve
        :return: dict of "num_recipes" number of random recipes
        """
        endpoint = '/recipes/random'
        url = f'{BASE_URL}{endpoint}'

        # Parameters for the request
        params = {
            'number': num_recipes,  # Number of recipes to return
            'apiKey': API_KEY,  # Your Spoonacular API key
            'includeNutrition': False,
            'exclude-tags': "foodista.com"
        }

        # Make the GET request to Spoonacular API
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error, could not get random recipes: {response.status_code}")
            return None

    def transform_recipe_structure(self, recipe_list_obj: dict):
        """
        Transform API recipes version of returned recipes to schema used by DB
        :param recipe_list_obj: list of recipes with API schema
        :return: List of recipes ready to be inserted into DB
        """
        recipes_list = [
            {
                "recipe_name": recipe["title"],
                "source_url": recipe["sourceUrl"],
                "ingredients": sorted([ingredient["name"] for ingredient in recipe["extendedIngredients"]])
            }
            for recipe in recipe_list_obj["recipes"]
        ]
        return recipes_list

    def check_and_normalize_recipes(self, recipe_list):
        """
        Filters list based on whether the source URL is still active
        If link is active, ingredients are normalized based on valid ingredient names
        :param recipe_list: List of recipes to check for validity and transform
        :return: List of recipes that are valid and normalized
        """
        filtered_recipes = []
        for recipe_dict in recipe_list:
            try:
                response = requests.head(recipe_dict["source_url"], allow_redirects=True, stream=True)
                if response.status_code == 200:
                    # Normalize ingredients then append
                    normalized_recipe = self.normalize_ingredients_from_dict(recipe_dict)
                    filtered_recipes.append(normalized_recipe)
            except requests.RequestException as e:
                continue
            except RuntimeError as e:
                error_msg = f"Could not add recipe at URL '{recipe_dict["source_url"]}' due to exception: {e}"
                logger.error(error_msg)
                continue
        return filtered_recipes

    def normalize_ingredients_from_dict(self, recipe_dict):
        """
        Iterates through the ingredients in the recipe and normalizes each of the ingredients
        :param recipe_dict: recipe dict to normalize
        :return: recipe dict with ingredients normalized
        """
        number_unknown_ingredients = 0
        new_ingredients = []
        for ingredient in recipe_dict["ingredients"]:
            # Normalize and append ingredient names
            ingredient_names, _ = self.ingredient_normalizer.generate_normalized_ingredients(ingredient)

            if len(ingredient_names):
                ingredient_name = ingredient_names[0]
                new_ingredients.append(ingredient_name)
            else:
                number_unknown_ingredients += 1  # Ingredient unknown, add to running count

        if number_unknown_ingredients >= RecipeScraper.MAXIMUM_NUMBER_UNKNOWN_INGREDIENTS:
            error_msg = f"Exceeded maximum number of unknown ingredients ({RecipeScraper.MAXIMUM_NUMBER_UNKNOWN_INGREDIENTS}) for this recipe"
            raise RuntimeError(error_msg)

        normalized_dict = {
            "recipe_name": recipe_dict["recipe_name"],
            "source_url": recipe_dict["source_url"],
            "ingredients": sorted(new_ingredients)
        }
        return normalized_dict

    def search_recipes_by_ingredient(self, ingredients: str) -> dict | None:
        # Method to search for recipes based on ingredients
        endpoint = '/recipes/findByIngredients'
        url = f'{BASE_URL}{endpoint}'

        # Parameters for the request
        params = {
            'ingredients': ingredients,  # A comma-separated list of ingredients
            'number': 5,  # Number of recipes to return
            'apiKey': API_KEY  # Your Spoonacular API key
        }

        # Make the GET request to Spoonacular API
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None


if __name__ == "__main__":
    raw_ingredient_reader = RawJsonIngredientReader()
    ingredient_normalizer = IngredientNormalizer(raw_ingredient_reader)

    # Init recipe scraper
    recipe_scraper = RecipeScraper(ingredient_normalizer)

    recipe_scraper.scrape_and_insert_recipes(10)  # Scrape 10 recipes
