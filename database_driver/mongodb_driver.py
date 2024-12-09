import json
from calendar import error

import database_driver.mongodb_cloud_connector as mongodb_cloud_connector
import os
import logging_config, logging

# Get logger instance
logger = logging.getLogger(__name__)

# Load Config file
config_path = os.path.join(os.path.dirname(__file__), 'config', 'mongo_config.json')
with open(config_path, 'r') as file:
    config_data = json.load(file)

try:
    # Connect to MongoDB (use the default host and port)
    client = mongodb_cloud_connector.get_cloud_connection_client()
    db = client[config_data["database-name"]]

    # Get all collections
    config_collection_name = config_data["config-collection-name"]
    recipe_list_collection_name = config_data["recipe-list-collection-name"]
    normalized_ingredients_name = config_data["normalized_ingredients_name"]

    if recipe_list_collection_name not in db.list_collection_names():
        logger.info(f"Collection {recipe_list_collection_name} does not exist, creating with unique index")
        db[recipe_list_collection_name].create_index("source_url", unique=True)
        db[recipe_list_collection_name].create_index("ingredients")

    # Set up all collection objects
    config_collection = db[config_collection_name]
    recipe_collection = db[recipe_list_collection_name]
    normalized_ingredients_collection = db[normalized_ingredients_name]
except Exception as e:
    error_msg = f"MongoDB Error: {str(e)}"
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def insert_recipe_list(recipe_list):
    try:
        # Insert entire provided recipe list, not inserting any duplicate entries (ordered=False)
        result = recipe_collection.insert_many(recipe_list, ordered=False)
        logger.info(f"Inserted {len(recipe_list)} new recipes")
    except Exception as e:
        # Print the type of the exception and the exception message
        logger.error(f"Exception type: {type(e)}")


def insert_pantry_essentials(ingredient_list: dict):
    """
    Inserts an ingredient list to be stored as pantry essentials
    :param ingredient_list: dict containing list of ingredients
    """
    insert_config_item("pantryEssentials", ingredient_list)


def get_pantry_essentials() -> dict:
    """
    Retrieves pantry essentials from database
    :return: dict holding list of ingredients
    """
    try:
        return config_collection.find_one({"config_item": "pantryEssentials"})
    except Exception as e:
        # Print the type of the exception and the exception message
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception message: {str(e)}")


def get_normalized_ingredients():
    """
        Retrieves normalized ingredients from database
        :return: dict holding list of ingredients
        """
    try:
        return normalized_ingredients_collection.find()
    except Exception as e:
        # Print the type of the exception and the exception message
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception message: {str(e)}")


def insert_normalized_ingredient(new_normalized_ingredient: dict):
    # Verify structure matches normalized ingredient schema
    expected_structure = {
        "normalized_name": str,
        "alias": list
    }
    for key, expected_type in expected_structure.items():
        if key not in new_normalized_ingredient:
            raise KeyError(f"Missing key for normalized ingredient: {key}")
        elif isinstance(type(new_normalized_ingredient[key]), expected_type):
            raise TypeError(f"Expected type {expected_type} for {key} but got {type(new_normalized_ingredient[key]).__name__}")

    # Insert if structure matches
    normalized_ingredients_collection.insert_one(new_normalized_ingredient)


def insert_config_item(item_name: str, dict_to_insert: dict):
    if type(dict_to_insert) is not dict:
        raise TypeError(f"Expected parameter to be of type 'dict' but got {type(dict_to_insert).__name__}")

    try:
        # Delete existing item and add new item
        config_collection.delete_one({"config_item": item_name})
        result = config_collection.insert_one(dict_to_insert)
        logger.info(f"Inserted item with ID: {result.inserted_id}")
    except Exception as e:
        # Print the type of the exception and the exception message
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception message: {str(e)}")


if __name__ == "__main__":
    normalized_ingredients = normalized_ingredients_collection.find()
    for ing in normalized_ingredients:
        print(ing)
