from pymongo import MongoClient, errors
from bson.json_util import dumps
import json

try:
    # Connect to MongoDB (use the default host and port)
    client = MongoClient('mongodb://localhost:27017/')
    db = client['RecipeDatabase']

    # Set up all collection objects
    pantry_essentials_collection = db['pantryEssentials']
    recipe_link_collection = db['recipeLinks']
    saved_recipe_collection = db['savedRecipes']
    print("Successfully connected to MongoDB database")
except Exception as e:
    print(f"MongoDB Error: {str(e)}")


def insert_pantry_essentials(ingredient_list: dict):
    """
    Inserts an ingredient list to be stored as pantry essentials
    :param ingredient_list: dict containing list of ingredients
    """
    try:
        # Delete existing item and add new item
        pantry_essentials_collection.delete_many({})
        result = pantry_essentials_collection.insert_one(ingredient_list)
        print(f"Inserted item with ID: {result.inserted_id}")
    except Exception as e:
        # Print the type of the exception and the exception message
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")


def get_pantry_essentials() -> dict:
    """
    Retrieves pantry essentials from database
    :return: dict holding list of ingredients
    """
    try:
        return pantry_essentials_collection.find_one()
    except Exception as e:
        # Print the type of the exception and the exception message
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")


if __name__ == "__main__":
    ingredients_list = {
        "ingredients": ["eggs", "milk", "flour", "salt", "pepper"]
    }

    insert_pantry_essentials(ingredients_list)

    pantry_essentials = get_pantry_essentials()
    print(type(pantry_essentials))
