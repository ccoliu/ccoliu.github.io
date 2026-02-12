# ---------------------------------------------------
# Codoctopus — Database Utility
# Refactored from Servers/DbUtility.py
# MongoDB URI is now loaded from environment variable.
# ---------------------------------------------------

import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt
import pytz


class MongoDBTools:
    def __init__(self, uri=None):
        self.client = self._initialize_client(uri)

    @staticmethod
    def _initialize_client(uri):
        """Initialize MongoDB client from a URI string."""
        if not uri:
            print("Warning: No MongoDB URI provided. Database operations will fail.")
            return None
        try:
            client = MongoClient(uri, server_api=ServerApi('1'))
            client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            print(f"MongoDB version: {client.server_info().get('version', 'Unknown')}")
            return client
        except Exception as e:
            print(f"Warning: Failed to connect to MongoDB: {e}")
            return None

    def _get_collection(self, db_name, collection_name):
        """Retrieve a specific collection."""
        if self.client is None:
            raise ConnectionError("MongoDB client is not connected.")
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
        """Insert data from a JSONL file into a collection and return inserted _id values."""
        collection = self._get_collection(db_name, collection_name)
        inserted_ids = []

        with open(file_path, "r") as file:
            for line in file:
                data = json.loads(line.strip())
                result = collection.insert_one(data)
                inserted_ids.append(result.inserted_id)

        print(f"File '{file_path}' inserted into '{collection_name}'.")
        return inserted_ids

    def find_documents(self, db_name, collection_name, query):
        """Find documents that match a query."""
        collection = self._get_collection(db_name, collection_name)
        return collection.find(query)

    def find_field_by_id(self, db_name, document_id, field_name):
        try:
            db = self.client[db_name]
            filter_query = {"_id": ObjectId(document_id)}

            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                document = collection.find_one(filter_query)

                if document:
                    print(f"Document found in collection '{collection_name}'")
                    if field_name in document:
                        print(f"Field '{field_name}' found in document: {document[field_name]}")
                        return document[field_name]
                    else:
                        print(
                            f"Field '{field_name}' does not exist in the document "
                            f"in collection '{collection_name}'."
                        )
                        return None

            print(
                f"No document with ID '{document_id}' found in any collection "
                f"of database '{db_name}'."
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
        """Insert a single document into a collection."""
        collection = self._get_collection(db_name, collection_name)
        try:
            result = collection.insert_one(document)
            obj_id = result.inserted_id
            print("Document inserted successfully.")
            return obj_id
        except Exception as e:
            print(f"Failed to insert document: {e}")
            return None

    def update_document(self, db_name, collection_name, document_id, field_name, new_value):
        try:
            collection = self._get_collection(db_name, collection_name)
            filter_query = {"_id": ObjectId(document_id)}
            update_query = {"$set": {field_name: new_value}}
            result = collection.update_one(filter_query, update_query)

            if result.modified_count > 0:
                print(
                    f"Document with _id '{document_id}' updated successfully. "
                    f"Field '{field_name}' set to: {new_value}"
                )
                return document_id
            else:
                print(f"No document matched the filter. Update failed for _id: {document_id}")
                return None
        except Exception as e:
            print(f"Failed to update document with _id '{document_id}': {e}")
            return None

    def update_document_in_database(self, db_name, document_id, field_name, new_value):
        db = self.client[db_name]
        filter_query = {"_id": ObjectId(document_id)}
        update_query = {"$set": {field_name: new_value}}

        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            result = collection.update_one(filter_query, update_query)

            if result.modified_count > 0:
                print(
                    f"Document with _id '{document_id}' updated successfully "
                    f"in collection '{collection_name}'. "
                    f"Field '{field_name}' set to: {new_value}"
                )
                return document_id

        print(
            f"No document found with _id '{document_id}' "
            f"in any collection of database '{db_name}'."
        )
        return None

    def update_data_chain(self, db_name, collection_name, id, field_name, new_value):
        db = self.client[db_name]
        collection = db[collection_name]

        filter_query = {"data_id": ObjectId(id)}
        document = collection.find_one(filter_query)

        if not document:
            print(f"No document found with 'data_id' = '{id}' in collection '{collection_name}'.")
            return 0

        current_value = document.get(field_name, None)

        if current_value is None:
            update_query = {"$set": {field_name: new_value}}
        elif isinstance(current_value, list):
            update_query = {"$push": {field_name: new_value}}
        else:
            update_query = {"$set": {field_name: [current_value, new_value]}}

        result = collection.update_one(filter_query, update_query)

        if result.modified_count > 0:
            print(
                f"Document with 'data_id' = '{id}' updated successfully "
                f"in collection '{collection_name}'."
            )
            return result.modified_count
        else:
            print(f"No changes made to the document with 'data_id' = '{id}'.")
            return 0

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
            {"data_id": 1, "data_summary": 1},
        )

        sorted_results = sorted(
            results,
            key=lambda doc: sum(word in doc.get("data_summary", "") for word in query.split()),
            reverse=True,
        )

        return [{str(doc["data_id"]): doc["data_summary"]} for doc in sorted_results]


class DocumentBuilder:
    """Assembles documents for MongoDB operations."""

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


class AuthSystem(MongoDBTools):
    def __init__(self, uri=None, jwt_secret="change-me", jwt_expiry_hours=24):
        super().__init__(uri=uri)
        self.jwt_secret = jwt_secret
        self.jwt_expiry_hours = jwt_expiry_hours
        self.db_name = "user_db"
        self.collection_name = "user_info"

    @staticmethod
    def _get_current_time():
        tz = pytz.timezone('Asia/Taipei')
        return datetime.now(tz)

    def _generate_jwt(self, user_id):
        payload = {
            "user_id": str(user_id),
            "exp": self._get_current_time() + timedelta(hours=self.jwt_expiry_hours),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def register_user(self, user_name, password):
        collection = self._get_collection(self.db_name, self.collection_name)

        if collection.find_one({"user_name": user_name}):
            print("User already exists.")
            return None

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

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
        collection.insert_one(user_document)
        return "User registered successfully."

    def login_user(self, user_name, password):
        collection = self._get_collection(self.db_name, self.collection_name)
        user = collection.find_one({"user_name": user_name})
        if not user:
            return None

        if not bcrypt.checkpw(password.encode('utf-8'), user["user_password"].encode('utf-8')):
            return None

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
