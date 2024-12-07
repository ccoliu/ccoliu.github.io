# ---------------------------------------------------
# Import the necessary libraries
# ---------------------------------------------------
import os
import sys
import ssl
import yaml
import base64
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from LogHelper import initialize_logging  # For logging
from DataBase import MongoDBTools, DocumentBuilder, AuthSystem  # Custom database tools

# ---------------------------------------------------
# System initialization and configuration
# ---------------------------------------------------


def resource_path(relative_path):
    """
    Get the absolute path to the resource, whether in development or when packaged with PyInstaller.
    """
    try:
        # If using PyInstaller, the base path is in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Initialize logging
log_handler = initialize_logging("Log_in")

# Initialize custom tools and systems
database_tools = MongoDBTools()
document_builder = DocumentBuilder()
auth_system = AuthSystem(jwt_secret="my_testing_secret", jwt_expiry_hours=24)


# Load YAML configuration
def load_yaml_config(file_path):
    """
    Load configuration from a YAML file.
    """
    with open(file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


# Load server settings from configuration
config_file_path = resource_path("Servers\\Config.yaml")
config = load_yaml_config(config_file_path)
server_type = config["ServerSettings"]["ConnectionType"]

# SSL certificate paths
cert_path = resource_path('certificate.crt')
key_path = resource_path('private_key.key')

# RSA key paths
public_key_path = resource_path('public_key.pem')
private_key_path = resource_path('private_key.pem')

# ---------------------------------------------------
# RSA encryption and decryption functions
# ---------------------------------------------------


def load_private_key():
    """
    Load the RSA private key from a PEM file.
    """
    with open(private_key_path, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)


def decrypt_password(encrypted_password):
    """
    Decrypt an RSA-encrypted password.
    The encrypted password is expected to be Base64-encoded and PKCS1v15 padded.
    """
    private_key = load_private_key()

    try:
        # Decode the Base64 string to get the encrypted bytes
        encrypted_password_bytes = base64.b64decode(encrypted_password)
        print("Decoded Encrypted Password Bytes:", encrypted_password_bytes)
    except Exception as e:
        print("Base64 decoding failed:", e)
        raise ValueError("Invalid encrypted password format.")

    try:
        # Decrypt using the private key and PKCS1v15 padding
        decrypted_password = private_key.decrypt(encrypted_password_bytes, padding.PKCS1v15())
        print("Decrypted Password (raw bytes):", decrypted_password)
        return decrypted_password.decode("utf-8")
    except Exception as e:
        print("RSA Decryption failed:", e)
        raise ValueError("RSA decryption failed.")


# ---------------------------------------------------
# Flask application setup
# ---------------------------------------------------

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing


@app.route("/", methods=["GET"])
def index():
    """
    Default route to handle redirections or responses.
    """
    referrer = request.referrer
    return redirect(referrer) if referrer else "Welcome to the Log-in server!"


@app.route("/public_key", methods=["GET"])
def get_public_key():
    """
    Provide the public key to the front-end for encryption.
    """
    try:
        with open(public_key_path, "r") as file:
            public_key = file.read()
        return jsonify({"success": True, "public_key": public_key})
    except Exception as e:
        print("Failed to load public key:", e)
        return jsonify({"success": False, "error": "Public key not available."}), 500


@app.route("/register", methods=["POST"])
def register_user():
    """
    Handle user registration.
    Expects a JSON payload with 'username' and 'password' (Base64-encoded RSA-encrypted).
    """
    try:
        user_data = request.get_json(force=True)
        print("Received data:", user_data)

        if not user_data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        try:
            # Decrypt the password
            decrypted_password = decrypt_password(user_data["password"])
            print("Decrypted password:", decrypted_password)
        except ValueError as ve:
            print("Decryption failed:", ve)
            return jsonify({"success": False, "error": str(ve)}), 400

        # Register the user with the decrypted password
        registration_result = auth_system.register_user(user_data["username"], decrypted_password)

        if registration_result:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"success": False, "error": "Username already exists."}), 400

    except Exception as e:
        print("Error during registration:", e)
        return jsonify({"success": False, "error": "Server error occurred."}), 500


@app.route("/login", methods=["POST"])
def login_user():
    """
    Handle user login.
    Expects a JSON payload with 'username' and 'password' (Base64-encoded RSA-encrypted).
    """
    try:
        user_data = request.get_json(force=True)
        print("Received login data:", user_data)

        if not user_data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        # Decrypt the password
        try:
            decrypted_password = decrypt_password(user_data["password"])
            print("Decrypted password:", decrypted_password)
        except ValueError as ve:
            print("Decryption failed:", ve)
            return jsonify({"success": False, "error": str(ve)}), 400

        # Authenticate user
        token = auth_system.login_user(user_data["username"], decrypted_password)
        if token:
            return jsonify({"success": True, "token": token}), 200
        else:
            return jsonify({"success": False, "error": "Invalid username or password."}), 401

    except Exception as e:
        print("Error during login:", e)
        return jsonify({"success": False, "error": "Server error occurred."}), 500


@app.route("/verify", methods=["GET"])
def verify_token():
    """
    Verify if the user is still logged in by validating the JWT token.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "error": "Authorization header missing or invalid."}), 401

    token = auth_header.split(" ")[1]

    try:
        # Verify the token
        user = auth_system.verify_token(token)
        if user:
            return (
                jsonify(
                    {"success": True, "message": "Token is valid.", "username": user["user_name"]}
                ),
                200,
            )
        else:
            return jsonify({"success": False, "error": "Token is invalid or expired."}), 401
    except Exception as e:
        print("Error verifying token:", e)
        return (
            jsonify(
                {"success": False, "error": "Server error occurred during token verification."}
            ),
            500,
        )


# ---------------------------------------------------
# Server launch logic
# ---------------------------------------------------

if __name__ == "__main__":
    if server_type == "http":
        app.run(host="0.0.0.0", port=56123)  # HTTP mode
    elif server_type == "https":
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=56123, ssl_context=context)  # HTTPS mode
