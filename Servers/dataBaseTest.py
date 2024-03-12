from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint
import json
from bson import ObjectId


class dataBaseTools:
    def __init__(self):
        # Get URI form dbURI.txt
        with open("dbURI.txt", "r") as file:
            uriArray = file.readlines()
            uri = uriArray[0].strip()

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    # Print all the databases in the server
    def printDatabase(self):
        for db_info in self.client.list_database_names():
            print(db_info)

    # List all the collections in a specific database
    def printCollection(self, dbName):
        db = self.client[dbName]

        for collection_info in db.list_collection_names():
            print(collection_info)

    # Create a database and the first collection
    def createDatabase(self, dbName, collectionName):
        # Create a collection and insert a document to actually create the database
        db = self.client[dbName]
        collection = db[collectionName]

        collection.insert_one(
            {
                'dbIndex': 'This collection is for storing ' + collectionName,
            }
        )

        print("Database " + dbName + " & collection " + collectionName + " created.")

    # Delete a database
    def delteDatabase(self, dbName):
        self.client.drop_database(dbName)
        print(f"Database '{dbName}' deleted.")

    # Create a collection given a database name and a collection name
    def createCollection(self, dbName, collectionName):
        db = self.client[dbName]
        collection = db[collectionName]
        collection.insert_one(
            {
                'dbIndex': 'This collection is for storing ' + collectionName,
                'pin': 'collectionIndex',
            }
        )
        print(f"Collection '{collectionName}' created.")

    # Format a collection
    def cleanCollection(self, dbName, collectionName):
        db = self.client[dbName]
        collection = db[collectionName]

        collection.delete_many({})

        print(f"Collection '{collectionName}' cleaned.")

    # Delete a collection given a database name and a collection name
    def deleteCollection(self, dbName, collectionName):
        db = self.client[dbName]
        db.drop_collection(collectionName)

        print(f"Collection '{collectionName}' deleted.")

    # Insert a file into a specific collection in a specific database
    # Use for stroing jsonl file
    def insertFile(self, dbName, collectionName, filePath):
        db = self.client[dbName]
        collection = db[collectionName]

        with open(filePath, "r") as file:
            data = file.readlines()
            for line in data:
                collection.insert_one(json.loads(line))

        print(f"File '{filePath}' inserted into '{collectionName}'.")

    # Find a specific document in a collection and return the document id
    def findSpecificDocument(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        result = collection.find(query)

        for item in result:
            test = item.pop('_id')
            pprint(item)

        return test

    # Delete one document in a collection that meet the query
    def deleteOneDocument(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        # delete only one even their is multiple documents meet the query
        collection.delete_one(query)

        print(f"Document deleted.")

    # Delete all the documents in a collection that meet the query
    def deleteManyDocument(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        # delete all documents meet the query
        collection.delete_many(query)

        print(f"Documents deleted.")

    ######################################################################################################above is tested and working successfully######################################################################################################

    # Get random  number of document from a collection
    def getRandomDocument(self, dbName, collectionName, sampleSize=1):
        db = self.client[dbName]
        collection = db[collectionName]

        result = collection.aggregate([{"$sample": {"size": sampleSize}}])

        for item in result:
            pprint(item)

    # Get random  number of document from a collection with condition
    def getRandomeDocumentWithCondition(self, dbName, collectionName, condition, sampleSize=1):
        db = self.client[dbName]
        collection = db[collectionName]

        result = collection.aggregate([{"$match": condition}, {"$sample": {"size": sampleSize}}])

        for item in result:
            # item.pop('_id')
            pprint(item)

    # Insert a document into a collection
    def insertDocument(self, dbName, collectionName, document):
        db = self.client[dbName]
        collection = db[collectionName]

        collection.insert_one(document)

        print(f"Document inserted.")

    # Update a document in a collection
    # Parametres: dbName, collectionName, id(filter), field, newValue
    def updateDocument(self, dbName, collectionName, id, field, newValue):
        db = self.client[dbName]
        collection = db[collectionName]

        collection.update_one(id, {"$set": {field: newValue}})

        print(f"Document updated.")

    # parametres: dbName, collectionName, inputCode, outputCode, rate, comment
    # Insert a document into a collection and retrun the id of the document
    def insertModifyDocument(
        self, dbName, collectionName, inputCode, outputCode, rate="No rate", comment="No comment"
    ):
        db = self.client[dbName]
        collection = db[collectionName]
        data = {
            "pin": "data",
            "type": "modify code",
            "sourceCode": inputCode,
            "modifiedCode": outputCode,
            "rate": rate,
            "comment": comment,
        }

        collection.insert_one(data)
        id = data.get("_id")

        print(f"Document inserted.")

        return id

    # parametres: dbName, collectionName, requirement, gptList, generatedCode, rate, comment
    # Insert a document into a collection and retrun the id of the document
    def insertGenerateDocument(
        self,
        dbName,
        collectionName,
        requirement,
        gptList,
        generatedCode,
        rate="No rate",
        comment="No comment",
    ):
        db = self.client[dbName]
        collection = db[collectionName]
        data = {
            "pin": "data",
            "type": "generate code",
            "requirement": requirement,
            "gptList": gptList,
            "generatedCode": generatedCode,
            "rate": rate,
            "comment": comment,
        }

        collection.insert_one(data)
        id = data.get("_id")

        print(f"Document inserted.")

        return id

    # parametres: dbName, collectionName, input, output
    def insertGeneralCaseDocument(self, dbName, collectionName, input, output):
        db = self.client[dbName]
        collection = db[collectionName]
        data = {
            "pin": "data",
            "type": "general case",
            "input": input,
            "output": output,
        }

        collection.insert_one(data)

        print(f"Document inserted.")

    # Find similar documents in a collection
    def searchSimilarDocument(self, dbName, collectionName, index, query):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {index: {'$regex': query}}

        result = collection.find(filter)

        for item in result:
            pprint(item)


# Document example:
""" 
_id (atuo)

Modify:
1. Type : modify code 
2. source code
3. modified code 
4. good or bad
5. comment

Generate:
1. Type : generate code 
2. requirement
3. gpt given list
4. generated code 
5. good or bad
6. comment

common case like coding style
1. Type : general case
2. input
3. output 
"""
