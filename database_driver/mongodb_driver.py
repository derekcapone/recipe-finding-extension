import json
import database_driver.mongodb_cloud_connector as mongodb_cloud_connector
import os
from pymongo import ASCENDING, DESCENDING

# Load Config file
config_path = os.path.join(os.path.dirname(__file__), 'config', 'mongo_config.json')
with open(config_path, 'r') as file:
    config_data = json.load(file)

try:
    # Connect to MongoDB (use the default host and port)
    client = mongodb_cloud_connector.get_cloud_connection_client()
    db = client[config_data["database-name"]]

    pantry_essentials_collection_name = config_data["pantry-essentials-collection-name"]
    recipe_list_collection_name = config_data["recipe-list-collection-name"]

    if recipe_list_collection_name not in db.list_collection_names():
        print(f"Collection {recipe_list_collection_name} does not exist, creating with unique index")
        db[recipe_list_collection_name].create_index("source_url", unique=True)
        db[recipe_list_collection_name].create_index("ingredients")

    # Set up all collection objects
    pantry_essentials_collection = db[pantry_essentials_collection_name]
    recipe_collection = db[recipe_list_collection_name]
except Exception as e:
    print(f"MongoDB Error: {str(e)}")


def insert_recipe_list(recipe_list):
    try:
        # Insert entire provided recipe list, not inserting any duplicate entries (ordered=False)
        result = recipe_collection.insert_many(recipe_list, ordered=False)
        print(f"Inserted {len(recipe_list)} new recipes")
    except Exception as e:
        # Print the type of the exception and the exception message
        print(f"Exception type: {type(e)}")


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
