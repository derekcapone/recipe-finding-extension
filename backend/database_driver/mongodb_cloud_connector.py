from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import logging_config, logging

# Get logger instance
logger = logging.getLogger(__name__)

def get_cloud_connection_client() -> MongoClient:
    username = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    cluster_name = os.getenv("MONGO_CLUSTER")
    appname = os.getenv("MONGO_APP")

    uri = f"mongodb+srv://{username}:{password}@{cluster_name}.blbbn.mongodb.net/?retryWrites=true&w=majority&appName={appname}"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        logger.debug("Successfully connected to MongoDB Cluster")
    except Exception as e:
        logger.error("Error connecting to MongoDB Cluster")
        logger.error(e)

    return client


if __name__ == "__main__":
    client_instance = get_cloud_connection_client()