from pymongo import MongoClient, errors
from bson.json_util import dumps
import json

# Load Config file
with open('config/mongo_config.json', 'r') as file:
    config_data = json.load(file)

try:
    # Connect to MongoDB (use the default host and port)
    client = MongoClient(config_data["mongo-client-host"])
    db = client[config_data["database-name"]]

    # Set up all collection objects
    pantry_essentials_collection = db[config_data["pantry-essentials-collection-name"]]
    saved_recipe_collection = db[config_data["saved-recipes-collection-name"]]
    print("Successfully connected to MongoDB database")
except Exception as e:
    print(f"MongoDB Error: {str(e)}")


def insert_pantry_essentials(ingredient_list: dict):
    """
    Inserts an ingredient list to be stored as pantry essentials
    :param ingredient_list: dict containing list of ingredients
    """
    if type(ingredient_list) is not dict:
        raise TypeError(f"Expected parameter to be of type 'dict' but got {type(ingredient_list).__name__}")

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
