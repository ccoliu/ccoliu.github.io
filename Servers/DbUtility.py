# ---------------------------------------------------
# Author: Daniel Hsiao
# Date: 2024/10/01
# Update: 2024/12/05
# Version: <V10.0.0.0>
# File Name: DataBase.py
# File Description: Provides tools for connecting to MongoDB and manipulating the database.
# ---------------------------------------------------

import os
import sys
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from fileFormatt import StringToJsonl
from datetime import datetime, timedelta
import bcrypt
import jwt
import pytz


# To get the absolute path of the resource file, which works for both development and PyInstaller
def resource_path(relative_path):
    """Get absolute path to a resource, works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MongoDBTools:
    def __init__(self):
        self.client = self._initialize_client()
        self.file_formatter = StringToJsonl()

    @staticmethod
    def _initialize_client():
        """Initialize MongoDB client from a URI file."""
        uri_file_path = resource_path("Keys\\database_uri.txt")
        try:
            with open(uri_file_path, "r") as file:
                uri = file.readline().strip()
            client = MongoClient(uri, server_api=ServerApi('1'))
            client.admin.command('ping')  # Test connection
            print("Successfully connected to MongoDB!")
            print(f"MongoDB version: {client.server_info().get('version', 'Unknown')}")
            return client
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def _get_collection(self, db_name, collection_name):
        """Retrieve a specific collection."""
        return self.client[db_name][collection_name]

    def list_databases(self):
        """Print all database names."""
        for db_name in self.client.list_database_names():
            print(db_name)

    def list_collections(self, db_name):
        """Print all collections in a database."""
        db = self.client[db_name]
        for collection_name in db.list_collection_names():
            print(collection_name)

    def create_database(self, db_name, collection_name):
        """Create a new database and a collection with a sample document."""
        self.create_collection(db_name, collection_name)
        print(f"Database '{db_name}' and collection '{collection_name}' created.")

    def create_collection(self, db_name, collection_name):
        """Create a new collection and insert a sample document."""
        collection = self._get_collection(db_name, collection_name)
        collection.insert_one({"pin": "collectionIndex", "dbIndex": f"Storing {collection_name}"})
        print(f"Collection '{collection_name}' created.")

    def delete_database(self, db_name):
        """Delete a database."""
        self.client.drop_database(db_name)
        print(f"Database '{db_name}' deleted.")

    def delete_collection(self, db_name, collection_name):
        """Delete a collection."""
        db = self.client[db_name]
        db.drop_collection(collection_name)
        print(f"Collection '{collection_name}' deleted.")

    def clean_collection(self, db_name, collection_name):
        """Delete all documents in a collection."""
        collection = self._get_collection(db_name, collection_name)
        collection.delete_many({})
        print(f"Collection '{collection_name}' cleaned.")

    def insert_file(self, db_name, collection_name, file_path):
        """
        Insert data from a JSONL file into a collection and return the inserted _id values.
        """
        collection = self._get_collection(db_name, collection_name)
        inserted_ids = []  # List to store the inserted _id values

        with open(file_path, "r") as file:
            for line in file:
                data = json.loads(line.strip())
                result = collection.insert_one(data)  # Insert the document
                inserted_ids.append(result.inserted_id)  # Append the _id to the list

        print(f"File '{file_path}' inserted into '{collection_name}'.")
        return inserted_ids  # Return the list of _id values

    def find_documents(self, db_name, collection_name, query):
        """Find documents that match a query."""
        collection = self._get_collection(db_name, collection_name)
        return collection.find(query)

    def find_field_by_id(self, db_name, document_id, field_name):
        try:
            # Get the database
            db = self.client[db_name]
            filter_query = {"_id": ObjectId(document_id)}

            # Iterate through all collections in the database
            for collection_name in db.list_collection_names():
                collection = db[collection_name]

                # Search for the document in the collection
                document = collection.find_one(filter_query)

                # If the document is found
                if document:
                    print(f"Document found in collection '{collection_name}'")

                    # Check if the field exists in the document
                    if field_name in document:
                        print(f"Field '{field_name}' found in document: {document[field_name]}")
                        return document[field_name]
                    else:
                        print(
                            f"Field '{field_name}' does not exist in the document in collection '{collection_name}'."
                        )
                        return None

            # If no document is found
            print(
                f"No document with ID '{document_id}' found in any collection of database '{db_name}'."
            )
            return None
        except Exception as e:
            print(f"An error occurred while searching for ID '{document_id}': {e}")
            return None

    def delete_documents(self, db_name, collection_name, query, single=False):
        """Delete documents matching a query."""
        collection = self._get_collection(db_name, collection_name)
        if single:
            collection.delete_one(query)
            print("One document deleted.")
        else:
            collection.delete_many(query)
            print("All matching documents deleted.")

    def insert_document(self, db_name, collection_name, document):
        """
        Insert a single document into a collection and handle exceptions.
        """
        collection = self._get_collection(db_name, collection_name)
        try:
            result = collection.insert_one(document)  # Attempt to insert the document
            obj_id = result.inserted_id  # Retrieve the generated _id
            print("Document inserted successfully.")
            return obj_id
        except Exception as e:  # Catch any exception that occurs during insertion
            print(f"Failed to insert document: {e}")
            return None

    def update_document(self, db_name, collection_name, document_id, field_name, new_value):
        try:
            # Get the collection
            collection = self._get_collection(db_name, collection_name)

            # Build filter and update query
            filter_query = {"_id": ObjectId(document_id)}
            update_query = {"$set": {field_name: new_value}}

            # Perform the update
            result = collection.update_one(filter_query, update_query)

            # Check the result
            if result.modified_count > 0:
                print(
                    f"Document with _id '{document_id}' updated successfully. Field '{field_name}' set to: {new_value}"
                )
                return document_id
            else:
                print(f"No document matched the filter. Update failed for _id: {document_id}")
                return None
        except Exception as e:
            print(f"Failed to update document with _id '{document_id}': {e}")
            return None

    # Search through all collections in the database
    def update_document_in_database(self, db_name, document_id, field_name, new_value):
        # Get the database
        db = self.client[db_name]

        # Build filter and update query
        filter_query = {"_id": ObjectId(document_id)}
        update_query = {"$set": {field_name: new_value}}

        # Iterate through all collections in the database
        for collection_name in db.list_collection_names():
            collection = db[collection_name]

            # Perform the update
            result = collection.update_one(filter_query, update_query)

            # Check if any document was updated
            if result.modified_count > 0:
                print(
                    f"Document with _id '{document_id}' updated successfully in collection '{collection_name}'. "
                    f"Field '{field_name}' set to: {new_value}"
                )
                return document_id

        # If no document was found in any collection
        print(
            f"No document found with _id '{document_id}' in any collection of database '{db_name}'."
        )
        return None

    # The search index is not the collections _id is the data_id
    def update_data_chain(self, db_name, collection_name, id, field_name, new_value):
        # Get the collection
        db = self.client[db_name]
        collection = db[collection_name]

        # Filter to find documents where 'data_id' matches
        filter_query = {"data_id": ObjectId(id)}

        # Retrieve the document to check the current state of the field
        document = collection.find_one(filter_query)

        if not document:
            print(f"No document found with 'data_id' = '{id}' in collection '{collection_name}'.")
            return 0

        # Check the current state of the field
        current_value = document.get(field_name, None)

        if current_value is None:
            # If the field does not exist, set it to the new value
            update_query = {"$set": {field_name: new_value}}
        elif isinstance(current_value, list):
            # If the field is already a list, append the new value
            update_query = {"$push": {field_name: new_value}}
        else:
            # If the field is a single value, convert it into a list with the new value
            update_query = {"$set": {field_name: [current_value, new_value]}}

        # Perform the update
        result = collection.update_one(filter_query, update_query)

        if result.modified_count > 0:
            print(
                f"Document with 'data_id' = '{id}' updated successfully in collection '{collection_name}'."
            )
            return result.modified_count
        else:
            print(f"No changes made to the document with 'data_id' = '{id}'.")
            return 0

    def write_collection_to_file(self, db_name, collection_name, file_path):
        """Write all documents from a collection to a JSONL file."""
        collection = self._get_collection(db_name, collection_name)
        for item in collection.find():
            doc_type = item.get("type", "general")
            output = {
                "type": doc_type,
                "content": item,
            }
            self.file_formatter.write_to_file(file_path, output)

    def get_random_documents(self, db_name, collection_name, sample_size=1, condition=None):
        """Retrieve random documents, optionally with a condition."""
        collection = self._get_collection(db_name, collection_name)
        pipeline = [{"$match": condition}] if condition else []
        pipeline.append({"$sample": {"size": sample_size}})
        return list(collection.aggregate(pipeline))

    def community_search(self, db_name, collection_name, query):
        """Search documents based on query similarity and return only _id and data_summary."""
        collection = self._get_collection(db_name, collection_name)

        regex = "|".join(query.split())
        results = collection.find(
            {"data_summary": {"$regex": regex, "$options": "i"}},
            {"data_id": 1, "data_summary": 1},  # Only return _id and summary
        )

        # Sort results by the number of query words found in the summary
        sorted_results = sorted(
            results,
            key=lambda doc: sum(word in doc.get("data_summary", "") for word in query.split()),
            reverse=True,
        )

        return [{str(doc["data_id"]): doc["data_summary"]} for doc in sorted_results]


class DocumentBuilder:
    """
    This class is responsible for assembling documents for MongoDB operations.
    Each method corresponds to a specific document format (e.g., generate, modify).
    """

    @staticmethod
    def _get_current_time():
        tz = pytz.timezone('Asia/Taipei')
        return datetime.now(tz)

    @staticmethod
    def generate_document(
        user_input,
        language,
        ai_tasks,
        final_tasks,
        final_output,
        summary,
        rate="No rate",
        comment="No comment",
        creator="System",
    ):
        """
        Build a document for "generate code" type.
        """
        return {
            "pin": "data",
            "mode": "generate_mode",
            "user_input": user_input,
            "language": language,
            "ai_tasks": ai_tasks,
            "final_tasks": final_tasks,
            "final_output": final_output,
            "summary": summary,
            "rate": rate,
            "comment": comment,
            "created_time": DocumentBuilder._get_current_time(),
            "creator": creator,
        }

    @staticmethod
    def modify_document(
        user_input, final_output, summary, rate="No rate", comment="No comment", creator="System"
    ):
        """
        Build a document for "modify code" type.
        """
        return {
            "pin": "data",
            "mode": "modify_mode",
            "user_input": user_input,
            "final_output": final_output,
            "summary": summary,
            "rate": rate,
            "comment": comment,
            "created_time": DocumentBuilder._get_current_time(),
            "creator": creator,
        }

    @staticmethod
    def similarity_check_document(
        lhs, rhs, final_output, rate="No rate", comment="No comment", creator="System"
    ):
        """
        Build a document for "similarity check" type.
        """
        return {
            "pin": "data",
            "mode": "similarity_mode",
            "lhs": lhs,
            "rhs": rhs,
            "final_output": final_output,
            "rate": rate,
            "comment": comment,
            "created_time": DocumentBuilder._get_current_time(),
            "creator": creator,
        }

    @staticmethod
    def plagiarism_ai_document(
        user_input, final_output, rate="No rate", comment="No comment", creator="System"
    ):
        """
        Build a document for "plagiarism_mode" type.
        """
        return {
            "pin": "data",
            "mode": "plagiarism_mode",
            "user_input": user_input,
            "final_output": final_output,
            "rate": rate,
            "comment": comment,
            "created_time": DocumentBuilder._get_current_time(),
            "creator": creator,
        }

    @staticmethod
    def viewer_document(
        data_id, data_summary, viewer_rate="No rate", viewer_comment="No comment", creator="System"
    ):
        """
        Build a document for "viewer" type.
        """
        return {
            "pin": "data",
            "mode": "viewer_mode",
            "data_id": data_id,
            "data_summary": data_summary,
            "viewer_rate": viewer_rate,
            "viewer_comment": viewer_comment,
            "created_time": DocumentBuilder._get_current_time(),
            "creator": creator,
        }

    @staticmethod
    def auto_fine_tune_data_document(problem, code):
        """
        Build a document for "auto fine tune" type.
        """
        return {
            "pin": "data",
            "type": "auto fine tune",
            "problem": problem,
            "code": code,
        }

    @staticmethod
    def gpt_code_document(problem, language, code):
        """
        Build a document for "gpt code" type.
        """
        return {
            "pin": "data",
            "type": "gpt code",
            "problem": problem,
            "language": language,
            "code": code,
        }

    @staticmethod
    def ai_employees_mode_document(
        user_input_request, divided_tasks, final_output, rate="No rate", comment="No comment"
    ):
        """
        Build a document for "AI employee mode" type.
        """
        return {
            "pin": "data",
            "type": "generate code",
            "request": user_input_request,
            "tasks": divided_tasks,
            "output": final_output,
            "rate": rate,
            "comment": comment,
        }


class AuthSystem(MongoDBTools):
    def __init__(self, jwt_secret, jwt_expiry_hours=24):
        """
        Initialize the AuthSystem with JWT settings and MongoDB client.
        """
        super().__init__()  # Initialize MongoDBTools
        self.jwt_secret = jwt_secret
        self.jwt_expiry_hours = jwt_expiry_hours
        self.db_name = "user_db"
        self.collection_name = "user_info"

    @staticmethod
    def _get_current_time():
        tz = pytz.timezone('Asia/Taipei')
        return datetime.now(tz)

    def _generate_jwt(self, user_id):
        """
        Generate a JWT token for the given user ID.
        """
        payload = {
            "user_id": str(user_id),
            "exp": self._get_current_time() + timedelta(hours=self.jwt_expiry_hours),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def register_user(self, user_name, password):
        """
        Register a new user by hashing their password and storing it in the database.
        """
        collection = self._get_collection(self.db_name, self.collection_name)

        # Check if user already exists
        if collection.find_one({"user_name": user_name}):
            print("User already exists.")
            return None

        # Generate password hash
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Insert user into the database
        user_document = {
            "user_name": user_name,
            "user_password": hashed_password.decode('utf-8'),
            "salt": salt.decode('utf-8'),
            "created_time": self._get_current_time(),
            "last_login_time": None,
            "token": None,
            "token_created_time": None,
            "token_expires_time": None,
        }
        result = collection.insert_one(user_document)

        return "User registered successfully."

    def login_user(self, user_name, password):
        """
        Authenticate a user and return a JWT token if successful.
        """
        collection = self._get_collection(self.db_name, self.collection_name)
        user = collection.find_one({"user_name": user_name})
        if not user:
            return None

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user["user_password"].encode('utf-8')):
            return None

        # Generate token
        token = self._generate_jwt(user["_id"])
        collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "token": token,
                    "token_created_time": self._get_current_time(),
                    "token_expires_time": self._get_current_time()
                    + timedelta(hours=self.jwt_expiry_hours),
                    "last_login_time": self._get_current_time(),
                }
            },
        )
        print("User: " + user_name + " logged in successfully.")
        return token

    def verify_token(self, token):
        """
        Verify a JWT token and return the associated user if valid.
        """
        collection = self._get_collection(self.db_name, self.collection_name)
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload["user_id"]
            user = collection.find_one({"_id": ObjectId(user_id), "token": token})
            if user:
                return user
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
        except jwt.InvalidTokenError:
            print("Invalid token.")
        return None

    def logout_user(self, user_id):
        """
        Invalidate a user's token by clearing it from the database.
        """
        collection = self._get_collection(self.db_name, self.collection_name)
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"token": None, "token_created_time": None, "token_expires_time": None}},
        )
        if result.modified_count > 0:
            print(f"User with _id '{user_id}' logged out successfully.")
            return True
        else:
            print(f"Failed to log out user with _id '{user_id}'.")
            return False
