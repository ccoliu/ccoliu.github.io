from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint

with open("dbURI.txt", "r") as file:
    uriArray = file.readlines()

uri = uriArray[0].strip()

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

for db_info in client.list_database_names():
    print(db_info)

# Get a reference to the 'sample_mflix' database:
db = client['sample_mflix']

# List all the collections in 'sample_mflix':
collections = db.list_collection_names()

for collection in collections:
    print(collection)
