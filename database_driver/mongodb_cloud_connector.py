from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

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
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)