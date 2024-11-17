import requests
import json
import os
import database_driver

# Your API key
API_KEY = os.getenv("SPOONACULAR_APP_ID")

# Base URL for the Spoonacular API
BASE_URL = 'https://api.spoonacular.com'


def transform_recipe_structure(recipe_list_obj: dict):
    recipes_list = [
        {
            "recipe_name": recipe["title"],
            "source_url": recipe["sourceUrl"],
            "ingredients": [ingredient["name"] for ingredient in recipe["extendedIngredients"]]
        }
        for recipe in recipe_list_obj["recipes"]
    ]
    return recipes_list


def get_random_recipes(num_recipes: int) -> dict:
    endpoint = '/recipes/random'
    url = f'{BASE_URL}{endpoint}'

    # Parameters for the request
    params = {
        'number': num_recipes,  # Number of recipes to return
        'apiKey': API_KEY,  # Your Spoonacular API key
        'includeNutrition': False
    }

    # Make the GET request to Spoonacular API
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        recipes = response.json()
        return recipes
    else:
        print(f"Error, could not get random recipes: {response.status_code}")
        return None


# Function to search for recipes based on ingredients
def search_recipes_by_ingredient(ingredients: str) -> dict:
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
        recipes = response.json()
        return recipes
    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == "__main__":
    # numRecipes = 20
    # recipes = get_random_recipes(numRecipes)

    # Open and load the JSON file
    with open("config/recipe_output.json", "r") as file:
        recipes = json.load(file)

    transformed_recipes = transform_recipe_structure(recipes)
    database_driver.insert_recipe_list(transformed_recipes)

    # if recipes:
    #     # Write the JSON string to a file
    #     with open("config/recipe_output.json", "w") as file:
    #         file.write(json.dumps(recipes, indent=3))
