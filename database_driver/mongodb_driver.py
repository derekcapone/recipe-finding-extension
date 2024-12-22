import json
import database_driver.mongodb_cloud_connector as mongodb_cloud_connector
import os
import logging_config, logging
import pymongo
from pymongo.errors import BulkWriteError

# Number of recipes to return from the recipe retrieval
NUMBER_RECIPES_TO_RETURN = 1

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
    except BulkWriteError as bwe:
        logger.info(f"{type(bwe)} occurred, likely due to duplicate source URLs. Rest of recipes still written")
    except Exception as e:
        # Print the type of the exception and the exception message
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception message: {e}")


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
    :return: list of dicts of ingredients and aliases
    """
    try:
        return list(normalized_ingredients_collection.find())
    except Exception as e:
        # Print the type of the exception and the exception message
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception message: {str(e)}")


def insert_normalized_ingredient(new_normalized_ingredient_name):
    """
    Inserts a new normalized ingredient with the name provided as parameter
    :param new_normalized_ingredient_name: New ingredient name to be inserted
    """
    new_normalized_ingredient = {
        "normalized_name": new_normalized_ingredient_name,
        "alias": []
    }

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


def get_ingredient_set_difference(ingredient_list: list[str]):
    # Define pipeline for aggregation
    pipeline = [
        {
            "$addFields": {
                "difference_ingredients": {
                    "$setDifference": ["$ingredients", ingredient_list]
                }
            }
        },
        # Compute size of difference
        {
            "$addFields": {
                "difference_count": {"$size": "$difference_ingredients"}
            }
        },
        # Sort by ascending so that smallest difference is at the top
        {
            "$sort": {"difference_count": 1}
        },
        # Get top item (smallest difference)
        {
            "$limit": NUMBER_RECIPES_TO_RETURN
        }
    ]
    return list(recipe_collection.aggregate(pipeline))


if __name__ == "__main__":
    new_ingredients = ["almond extract", "blueberry jam", "raspberry jam", "strawberry jam", "fig jam"]


    for ingredient in new_ingredients:
        insert_normalized_ingredient(ingredient)
