from pymongo import MongoClient, errors
from bson.json_util import dumps
import json

try:
    # Connect to MongoDB (use the default host and port)
    client = MongoClient('mongodb://localhost:27017/')
    db = client['RecipeDatabase']

    # Set up all collections objects
    pantry_essentials_collection = db['pantryEssentials']
    print("Successfully connected to MongoDB database")
except Exception as e:
    print(f"MongoDB Error: {str(e)}")


def insert_pantry_essentials(ingredient_item):
    try:
        # Delete existing item and add new item
        pantry_essentials_collection.delete_many({})
        result = pantry_essentials_collection.insert_one(ingredient_item)
        print(f"Inserted item with ID: {result.inserted_id}")
    except Exception as e:
        # Print the type of the exception and the exception message
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")


def get_pantry_essentials():
    try:
        result = pantry_essentials_collection.find_one()
        return dumps(result)
    except Exception as e:
        # Print the type of the exception and the exception message
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")

if __name__ == "__main__":


    pantry_essentials = get_pantry_essentials()
    print(pantry_essentials)
