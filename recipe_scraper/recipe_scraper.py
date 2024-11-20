import requests
import json
import os
import database_driver

# Your API key
API_KEY = os.getenv("SPOONACULAR_APP_ID")

# Base URL for the Spoonacular API
BASE_URL = 'https://api.spoonacular.com'


def scrape_and_insert_recipes(num_recipes: int):
    # Get random recipes
    random_recipe_list = get_random_recipes(num_recipes)

    transformed_random_recipes = transform_recipe_structure(random_recipe_list)

    # Ensure each recipe link still works before inserting
    final_recipe_list = check_recipe_links(transformed_random_recipes)
    database_driver.insert_recipe_list(final_recipe_list)


def check_recipe_links(recipe_list):
    """
    Filters list based on whether the source URL is still active
    :param recipe_list:
    :return:
    """
    filtered_recipes = []
    for recipe_dict in recipe_list:
        try:
            response = requests.head(recipe_dict["source_url"], allow_redirects=True, stream=True)
            if response.status_code == 200:
                filtered_recipes.append(recipe_dict)
                print("Successful link")
            else:
                print("Link doesnt work")
        except requests.RequestException as e:
            continue
    return filtered_recipes



def transform_recipe_structure(recipe_list_obj: dict):
    """
    Transform API recipes version of returned recipes to schema used by DB
    :param recipe_list_obj: list of recipes with API schema
    :return: List of recipes ready to be inserted into DB
    """
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
        'includeNutrition': False
    }

    # Make the GET request to Spoonacular API
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()
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
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == "__main__":
    numRecipes = 100
    scrape_and_insert_recipes(numRecipes)