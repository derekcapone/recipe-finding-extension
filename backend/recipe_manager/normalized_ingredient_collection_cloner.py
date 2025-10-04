# from pymongo import MongoClient
# import database_driver.mongodb_cloud_connector as mongodb_cloud_connector
# import os
# import json
#
# ### WARNING: This will overwrite the current backup for normalized_ingredients, BE SURE YOU WANT TO RUN THIS
#
# # Load Config file
# config_path = os.path.join(os.path.dirname(__file__), 'config', 'mongo_config.json')
# with open(config_path, 'r') as file:
#     config_data = json.load(file)
#
# # Connect to MongoDB
# client = mongodb_cloud_connector.get_cloud_connection_client()
# db = client[config_data["database-name"]]
#
# normalized_ingredients_name = config_data["normalized_ingredients_name"]
# normalized_ingredients_collection = db[normalized_ingredients_name]
#
# backup_collection_name = f"{normalized_ingredients_name}_backup"
#
# # Clone the collection
# pipeline = [{"$match": {}}, {"$out": backup_collection_name}]
# normalized_ingredients_collection.aggregate(pipeline)
#
# print(f"Collection cloned to '{backup_collection_name}'")