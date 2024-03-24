'''This is the database class that will be used to store the data from the frontend.'''

# Import the mongodb library
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint
import json
from bson import ObjectId
from fileFormatt import StringToJsonl
import numpy as np


class dataBaseTools:
    def __init__(self):
        # Get URI form dbURI.txt
        with open("dbURI.txt", "r") as file:
            uriArray = file.readlines()
            uri = uriArray[0].strip()

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))

        self.fileFormat = StringToJsonl()

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    # Print all the databases in the server
    def printDataBaseList(self):
        for db_info in self.client.list_database_names():
            print(db_info)

    # Print all the collections in a specific database
    def printCollections(self, dbName):
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
        self,
        dbName,
        collectionName,
        inputCode,
        outputCode,
        summay,
        rate="No rate",
        comment="No comment",
    ):
        db = self.client[dbName]
        collection = db[collectionName]
        data = {
            "pin": "data",
            "type": "modify code",
            "sourceCode": inputCode,
            "modifiedCode": outputCode,
            "searchIndex": outputCode,
            "summary": summay,
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
        lang,
        gptList,
        generatedCode,
        summary,
        rate="No rate",
        comment="No comment",
    ):
        db = self.client[dbName]
        collection = db[collectionName]
        data = {
            "pin": "data",
            "type": "generate code",
            "language": lang,
            "requirement": requirement,
            "gptList": gptList,
            "generatedCode": generatedCode,
            "searchIndex": requirement,
            "summary": summary,
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
    def communitySearch(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        resultArray = [[]]
        singleIdSummaryPair = []

        # Divide the query sentence into seperate words and join them with '|'.
        regex_pattern = '|'.join(query.split())
        # Use regex to match the index, and use 'i' to make it case insensitive.
        filter = {"summary": {'$regex': regex_pattern, '$options': 'i'}}

        result = collection.find(filter)

        for item in result:
            # Store the related array in a list
            singleIdSummaryPair.append(item.get("_id"))
            singleIdSummaryPair.append(item.get("summary"))

            resultArray.append(singleIdSummaryPair)
        return resultArray

    # This function will copy a certain data to community collection and update the rate and comment from the viewer.
    def copyToCommunity(self, id, rate, comment):
        db = self.client["fineTune"]
        collection = db["codoctopus"]

        filter = {'_id': ObjectId(id)}
        result = collection.find_one(filter)

        cpyData = result
        # 刪除原來的 _id 字段
        if '_id' in cpyData:
            del cpyData['_id']

        collection = db["communityRate"]

        communityData = collection.insert_one(cpyData)

        filter = {'_id': ObjectId(communityData.inserted_id)}

        self.updateDocument("fineTune", "communityRate", filter, "rate", rate)
        self.updateDocument("fineTune", "communityRate", filter, "comment", comment)

        print(f"Document inserted.")

    # will print out the input and gpt output given the obeject id
    def searchDocumentUsingId(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            if item.get("type") == "modify code":
                print(item.get("sourceCode"))
                print(item.get("modifiedCode"))
            else:
                print(item.get("requirement"))
                print(item.get("generatedCode"))

    def searchInAllCollections(self, dbName, index, query):
        db = self.client[dbName]

        for collectionName in db.list_collection_names():
            collection = db[collectionName]

            filter = {index: {'$regex': query}}

            result = collection.find(filter)
            for item in result:
                if item.get("type") == "modify code":
                    print(item.get("sourceCode"))
                    print(item.get("modifiedCode"))
                else:
                    print(item.get("requirement"))
                    print(item.get("generatedCode"))

    # write all data in collection to a file
    def readDBToFile(self, dbName, collectionName, filePath):
        db = self.client[dbName]
        collection = db[collectionName]

        for item in collection.find():
            if item.get("type") == "modify code":
                self.fileFormat.write_to_file(
                    "modify code",
                    item.get("modifiedCode"),
                    item.get("rate"),
                    item.get("comment"),
                    filePath,
                )
            elif item.get("type") == "generate code":
                self.fileFormat.write_to_file(
                    "generate code",
                    item.get("generatedCode"),
                    item.get("rate"),
                    item.get("comment"),
                    filePath,
                )

    def getSummary(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            return item.get("summary")

    def getOriginalCode(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            if item.get("type") == "generate code":
                return item.get("requirement")
            else:
                return item.get("sourceCode")

    def getOutputCode(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            if item.get("type") == "generate code":
                return item.get("generatedCode")
            else:
                return item.get("modifiedCode")

    def getMode(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            return item.get("type")

    def getLang(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            return item.get("language")
