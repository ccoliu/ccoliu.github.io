# ---------------------------------------------------
# Import the necessary libraries
# ---------------------------------------------------
import os
import sys
import ssl
import yaml
from flask import Flask, request, jsonify, redirect, Response
from flask_cors import CORS
from LogHelper import initialize_logging  # For logging
from DataBase import MongoDBTools, DocumentBuilder, AuthSystem  # Custom database tools

# ---------------------------------------------------
# System initialization and configuration
# ---------------------------------------------------


# Function to get the file path after packaging
def resource_path(relative_path):
    """
    Get the absolute path to the resource for development and PyInstaller builds.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Initialize the logging system
log_handler = initialize_logging("Log_in")

# Initialize tools and systems
database_tools = MongoDBTools()
document_builder = DocumentBuilder()
auth_system = AuthSystem(jwt_secret="my_testing_secret", jwt_expiry_hours=24)


# Load the YAML configuration
def load_yaml_config(file_path):
    """
    Load configuration from a YAML file.
    """
    with open(file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)


# Load server configuration
config_file_path = resource_path("Servers\\Config.yaml")
config = load_yaml_config(config_file_path)

# Extract server settings from configuration
server_type = config["ServerSettings"]["ConnectionType"]

# Set up SSL keys for HTTPS
cert_path = resource_path('certificate.crt')
key_path = resource_path('private_key.key')

# ---------------------------------------------------
# Flask application setup
# ---------------------------------------------------

# Create a Flask app and enable CORS
app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    """
    Default route to handle redirections or responses.
    """
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return "Welcome to the Log-in server!"


@app.route("/register", methods=["POST"])
def register_user():
    """
    Route to register a new user.
    """
    try:
        # 獲取請求數據
        user_data = request.get_json(force=True)  # 使用 force=True 強制解析 JSON
        print("Received data:", user_data)

        # 驗證數據是否存在
        if not user_data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        # 驗證必填欄位
        required_fields = ["username", "password"]
        if not all(field in user_data for field in required_fields):
            return jsonify({"success": False, "error": "Missing required fields."}), 400

        # 註冊用戶
        registration_result = auth_system.register_user(
            user_data["username"], user_data["password"]
        )

        # 根據註冊結果返回對應的 JSON 響應
        if registration_result:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"success": False, "error": "Username already exists."}), 400

    except Exception as e:
        print("Error during registration:", e)
        return jsonify({"success": False, "error": "Server error occurred."}), 500


# ---------------------------------------------------
# Server launch logic
# ---------------------------------------------------

if __name__ == "__main__":
    if server_type == "http":
        # Run the app with HTTP
        app.run(host="0.0.0.0", port=56123)
    elif server_type == "https":
        # Run the app with HTTPS
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(host='0.0.0.0', port=56123, ssl_context=context)
