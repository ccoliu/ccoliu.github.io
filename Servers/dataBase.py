'''This is the database class has tools to manupulate the database.'''

import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Import the mongodb library
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint  # To print out all the item in single data.
import json
from bson import ObjectId  # To convert the id to a string.
from fileFormatt import StringToJsonl  # Self defined class to write the data to a jsonl file.


class dataBaseTools:
    def __init__(self):
        # Get URI form dbURI.txt
        uri_file_path = resource_path("dbURI.txt")
        with open(uri_file_path, "r") as file:
            uriArray = file.readlines()
            uri = uriArray[0].strip()

        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        # Create a new fileFormat object
        self.fileFormat = StringToJsonl()

        try:
            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    '''Note: The following functions are used by backend to manupulate the database.'''

    # List all the data bases in the server.
    def printDataBaseList(self):
        for db_info in self.client.list_database_names():
            print(db_info)

    # List all the collections in a specific database
    def printCollections(self, dbName):
        db = self.client[dbName]

        for collection_info in db.list_collection_names():
            print(collection_info)

    # Create a database and the first collection.
    def createDatabase(self, dbName, collectionName):
        # Create a collection and insert a document to actually create the database
        db = self.client[dbName]
        collection = db[collectionName]

        collection.insert_one(
            {
                'pin': 'collectionIndex',
                'dbIndex': 'This collection is for storing ' + collectionName,
            }
        )

        print(f"Database '{dbName}' & collection '{collectionName}' created.")

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
                'pin': 'collectionIndex',
                'dbIndex': 'This collection is for storing ' + collectionName,
            }
        )

        print(f"Collection '{collectionName}' created.")

    # Wipe out all the data in a collection.
    def cleanCollection(self, dbName, collectionName):
        db = self.client[dbName]
        collection = db[collectionName]

        collection.delete_many({})

        print(f"Collection '{collectionName}' cleaned.")

    # Delete a collection in a database.
    def deleteCollection(self, dbName, collectionName):
        db = self.client[dbName]
        db.drop_collection(collectionName)

        print(f"Collection '{collectionName}' deleted.")

    # Insert a JOSNL file into a collection ex
    def insertFile(self, dbName, collectionName, filePath):
        db = self.client[dbName]
        collection = db[collectionName]

        with open(filePath, "r") as file:
            data = file.readlines()

            for line in data:
                collection.insert_one(json.loads(line))

        print(f"File '{filePath}' inserted into '{collectionName}'.")

    # Find a document in a collection that meet the query, and the query need to match perfectly.
    def findSpecificDocument(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        found = collection.find(query)

        for item in found:
            objId = item.pop('_id')
            pprint(item)

        return objId

    # Delete one document in a collection that meet the query.
    def deleteOneDocument(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        # delete only one even if their are multiple documents meet the query.
        collection.delete_one(query)

        print(f"Document deleted.")

    # Delete all the documents in a collection that meet the query
    def deleteAllDocumentMeetQuery(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        # delete all documents meet the query
        collection.delete_many(query)

        print(f"Documents deleted.")

    '''Note: The following functions may used by frontend to manupulate the database.'''

    # Get random  number of document from a collection.
    def getRandomDocument(self, dbName, collectionName, sampleSize=1):
        db = self.client[dbName]
        collection = db[collectionName]

        found = collection.aggregate([{"$sample": {"size": sampleSize}}])

        for item in found:
            pprint(item)

    # Get random  number of document with condition.
    def getRandomeDocumentWithCondition(self, dbName, collectionName, condition, sampleSize=1):
        db = self.client[dbName]
        collection = db[collectionName]

        found = collection.aggregate([{"$match": condition}, {"$sample": {"size": sampleSize}}])

        for item in found:
            pprint(item)

    # Insert a document into a collection
    def insertDocument(self, dbName, collectionName, document):
        db = self.client[dbName]
        collection = db[collectionName]

        collection.insert_one(document)

        print(f"Document inserted.")

    # Update a document in a collection
    # Parametres: dbName, collectionName, id, field, newValue
    def updateDocument(self, dbName, collectionName, id, field, newValue):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        collection.update_one(filter, {"$set": {field: newValue}})

        print(f"Document updated.")

    # Insert a document into a collection and retrun the id of the document
    # Parametres: dbName, collectionName, inputCode, outputCode, summary
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
        objId = data.get("_id")

        print(f"Modify document inserted.")

        return objId

    # Insert a document into a collection and retrun the id of the document
    # parametres: dbName, collectionName, requirement, language, gptList, generatedCode, summary, rate, comment
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
        objId = data.get("_id")

        print(f"Generate document inserted.")

        return objId

    # Insert a document into a collection and retrun the id of the document
    # Parametres: dbName, collectionName, inputCode, outputCode, summary
    def insertAiEmployeesMode(
        self,
        dbName,
        collectionName,
        userInputRequest,
        dividedTasks,
        finalOutput,
        rate="No rate",
        comment="No comment",
    ):
        db = self.client[dbName]
        collection = db[collectionName]

        data = {
            "pin": "data",
            "type": "generate code",
            "request": userInputRequest,
            "tasks": dividedTasks,
            "output": finalOutput,
            "rate": rate,
            "comment": comment,
        }

        collection.insert_one(data)
        objId = data.get("_id")

        print(f"AI emloyee document inserted.")

        return objId

    def insertGenerateData(
        self,
        dbName,
        collectionName,
        userInputRequest,
        dividedTasks,
        finalTasks,
        finalOutput,
        summary,
        rate="No rate",
        comment="No comment",
    ):
        db = self.client[dbName]
        collection = db[collectionName]

        data = {
            "pin": "data",
            "type": "generate code",
            "request": userInputRequest,
            "tasks": dividedTasks,
            "finalTasks": finalTasks,
            "output": finalOutput,
            "summary": summary,
            "rate": rate,
            "comment": comment,
        }

        collection.insert_one(data)
        objId = data.get("_id")

        print(f"Generate data document inserted.")

        return objId

    # Insert a document into a collection and retrun the id of the document
    # Use to store the general case and futher use to fine tune the model
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
        objId = data.get("_id")

        print(f"General case document inserted.")

        return objId

    def insertsimilarityCheck(self, dbName, collectionName, LHS, RHS, gptOutput):
        db = self.client[dbName]
        collection = db[collectionName]

        data = {
            "pin": "data",
            "type": "similarity check",
            "LHS": LHS,
            "RHS": RHS,
            "gptOutput": gptOutput,
            "comment": "No comment yet",
        }

        collection.insert_one(data)
        objId = data.get("_id")

        print(f"Similarity check event inserted.")

        return objId

    def insertAutoFineTune(self, dbName, collectionName, problem, code):
        db = self.client[dbName]
        collection = db[collectionName]

        data = {
            "pin": "data",
            "type": "auto fine tune",
            "problem": problem,
            "code": code,
        }

        collection.insert_one(data)
        objId = data.get("_id")

        print(f"Similarity check event inserted.")

        return objId

    def insertGptCode(self, dbName, collectionName, problem, language, code):
        db = self.client[dbName]
        collection = db[collectionName]

        data = {
            "pin": "data",
            "type": "gpt code",
            "problem": problem,
            "code": code,
            "language": language,
        }

        collection.insert_one(data)
        objId = data.get("_id")

        print(f"Gpt code event inserted.")

        return objId

    # Find a document in a collection that meet the query, and the sort the result by how similar the query is.
    def communitySearch(self, dbName, collectionName, query):
        db = self.client[dbName]
        collection = db[collectionName]

        idSummayPair = []
        resultArray = []

        # Divide the query sentence into seperate words and join them with '|'.
        regex_pattern = '|'.join(query.split())
        # Use regex to match the index, and use 'i' to make it case insensitive.
        filter = {"summary": {'$regex': regex_pattern, '$options': 'i'}}

        found = collection.find(filter)
        for item in found:
            # Store the related array in a list
            idSummayPair = {str(item.get("_id")): item.get("summary")}
            resultArray.append(idSummayPair)

        identifier = query.split()
        match_max = len(query.split())

        # If the qurey is a single word than no need to sort.
        if match_max == 1:
            return resultArray

        complete_match = []
        match = [[] for i in range(match_max + 1)]
        sortedOutput = []

        for dicts in resultArray:
            match_num = 0
            first_value = next(iter(dicts.values()))  # Get the first value of the dict
            if query in first_value:
                complete_match.append(dicts)
                continue
            for word in identifier:
                if word in first_value:
                    match_num += 1
            match[match_num] += [dicts]

        sortedOutput += complete_match

        for i in range(match_max, 0, -1):
            sortedOutput += match[i]

        return sortedOutput

    # This function will copy a certain data to community collection and update the rate and comment from the viewer.
    def updateCommentToCommnity(self, id, rate, comment):
        db = self.client["fineTune"]
        collection = db["codoctopus"]

        filter = {'_id': ObjectId(id)}
        cpyData = collection.find_one(filter)

        # Delte the _id field to make sure the data is not duplicated.
        if '_id' in cpyData:
            del cpyData['_id']

        # Switch to the communityRate collection.
        collection = db["communityRate"]
        communityData = collection.insert_one(cpyData)

        filter = {'_id': ObjectId(communityData.inserted_id)}

        self.updateDocument("fineTune", "communityRate", communityData.inserted_id, "rate", rate)
        self.updateDocument(
            "fineTune", "communityRate", communityData.inserted_id, "comment", comment
        )

        print(f"Document inserted.")

    # Will print out the input and gpt output given the obeject id
    def searchById(self, dbName, collectionName, id):
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

    def searchThroughCollections(self, dbName, index, query):
        db = self.client[dbName]

        for collectionName in db.list_collection_names():
            collection = db[collectionName]

            filter = {index: {'$regex': query}}
            found = collection.find(filter)

            for item in found:
                if item.get("type") == "modify code":
                    print(item.get("sourceCode"))
                    print(item.get("modifiedCode"))
                else:
                    print(item.get("requirement"))
                    print(item.get("generatedCode"))

    # Write all data in collection to a file
    def writeDatabaseToFile(self, dbName, collectionName, filePath):
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

    '''Note: The following functions are used by the frontend to get the data from the database.'''

    # All things are get through id #
    def getSummary(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            return item.get("summary")

    def getOriginMessage(self, dbName, collectionName, id):
        db = self.client[dbName]
        collection = db[collectionName]

        filter = {'_id': ObjectId(id)}
        result = collection.find(filter)

        for item in result:
            if item.get("type") == "generate code":
                return item.get("requirement")
            else:
                return item.get("sourceCode")

    def getGptOutput(self, dbName, collectionName, id):
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


# TODO:
# 1. Generate server data base structure modify the data base structure to fit the server.
# 2. Rest server data base structure modify the data base structure to fit the rest server.
