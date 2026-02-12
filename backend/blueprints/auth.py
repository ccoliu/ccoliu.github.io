# ---------------------------------------------------
# Codoctopus — Auth Blueprint
# Migrated from Servers/Log_in.py
# Routes: /public_key, /register, /login, /verify, /logout
# ---------------------------------------------------

import base64
from flask import Blueprint, request, jsonify, current_app
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

from backend.extensions import auth_system

auth_bp = Blueprint("auth", __name__)


# ===================================================
# RSA helpers
# ===================================================

def _load_private_key():
    """Load RSA private key from the RSA_PRIVATE_KEY env var (PEM string)."""
    pem_string = current_app.config.get("RSA_PRIVATE_KEY", "")
    if not pem_string:
        raise ValueError("RSA_PRIVATE_KEY environment variable is not set.")
    return serialization.load_pem_private_key(pem_string.encode("utf-8"), password=None)


def decrypt_password(encrypted_password):
    """Decrypt an RSA-encrypted password (Base64 encoded, PKCS1v15 padded)."""
    private_key = _load_private_key()
    try:
        encrypted_password_bytes = base64.b64decode(encrypted_password)
    except Exception:
        print("Base64 decoding failed.")
        raise ValueError("Invalid encrypted password format.")

    try:
        decrypted_password = private_key.decrypt(encrypted_password_bytes, padding.PKCS1v15())
        return decrypted_password.decode("utf-8")
    except Exception:
        print("RSA decryption failed.")
        raise ValueError("RSA decryption failed.")


# ===================================================
# Routes
# ===================================================

@auth_bp.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Auth API is running."})


@auth_bp.route("/public_key", methods=["GET"])
def get_public_key():
    """Provide the RSA public key to the front-end for encryption."""
    try:
        public_key = current_app.config.get("RSA_PUBLIC_KEY", "")
        if not public_key:
            return jsonify({"success": False, "error": "Public key not configured."}), 500
        return jsonify({"success": True, "public_key": public_key})
    except Exception:
        return jsonify({"success": False, "error": "Public key not available."}), 500


@auth_bp.route("/register", methods=["POST"])
def register_user():
    """Handle user registration."""
    try:
        user_data = request.get_json(force=True)
        if not user_data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        try:
            decrypted_password = decrypt_password(user_data["password"])
        except ValueError as ve:
            return jsonify({"success": False, "error": str(ve)}), 400

        registration_result = auth_system.register_user(user_data["username"], decrypted_password)

        if registration_result:
            return jsonify({"success": True}), 201
        else:
            return jsonify({"success": False, "error": "Username already exists."}), 400
    except Exception:
        return jsonify({"success": False, "error": "Server error occurred."}), 500


@auth_bp.route("/login", methods=["POST"])
def login_user():
    """Handle user login."""
    try:
        user_data = request.get_json(force=True)
        if not user_data:
            return jsonify({"success": False, "error": "No data provided."}), 400

        try:
            decrypted_password = decrypt_password(user_data["password"])
        except ValueError as ve:
            return jsonify({"success": False, "error": str(ve)}), 400

        token = auth_system.login_user(user_data["username"], decrypted_password)
        if token:
            return jsonify({"success": True, "token": token}), 200
        else:
            return jsonify({"success": False, "error": "Invalid username or password."}), 401
    except Exception:
        return jsonify({"success": False, "error": "Server error occurred."}), 500


@auth_bp.route("/verify", methods=["GET"])
def verify_token():
    """Verify if the user is still logged in."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "error": "Authorization header missing or invalid."}), 401

    token = auth_header.split(" ")[1]
    try:
        user = auth_system.verify_token(token)
        if user:
            return jsonify(
                {"success": True, "message": "Token is valid.", "username": user["user_name"]}
            ), 200
        else:
            return jsonify({"success": False, "error": "Token is invalid or expired."}), 401
    except Exception:
        return jsonify(
            {"success": False, "error": "Server error occurred during token verification."}
        ), 500


@auth_bp.route("/logout", methods=["POST"])
def logout_user():
    """Handle user logout."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "error": "Authorization header missing or invalid."}), 401

    token = auth_header.split(" ")[1]
    try:
        user = auth_system.verify_token(token)
        if not user:
            return jsonify({"success": False, "error": "Invalid or expired token."}), 401

        logout_result = auth_system.logout_user(user["_id"])
        if logout_result:
            return jsonify({"success": True, "message": "User logged out successfully."}), 200
        else:
            return jsonify({"success": False, "error": "Logout failed. Please try again."}), 500
    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({"success": False, "error": "Server error occurred during logout."}), 500
