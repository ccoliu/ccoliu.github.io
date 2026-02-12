# ---------------------------------------------------
# Codoctopus — Configuration
# Loads environment variables and YAML config files.
# ---------------------------------------------------

import os
import yaml


def _get_config_dir():
    """Return the absolute path to the config_data directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_data")


def load_yaml_config(file_path):
    """Load configuration from a YAML file."""
    with open(file_path, "r", encoding="utf-8") as yaml_file:
        return yaml.safe_load(yaml_file)


def load_config(app):
    """Load all configuration into the Flask app."""

    # --- Environment variables (secrets) ---
    app.config["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI", "")
    app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "change-me-in-production")
    app.config["JWT_EXPIRY_HOURS"] = float(os.environ.get("JWT_EXPIRY_HOURS", "0.5"))

    # RSA keys for login encryption (PEM strings stored in env vars)
    app.config["RSA_PRIVATE_KEY"] = os.environ.get("RSA_PRIVATE_KEY", "")
    app.config["RSA_PUBLIC_KEY"] = os.environ.get("RSA_PUBLIC_KEY", "")

    # --- YAML config files ---
    config_dir = _get_config_dir()

    config_file_path = os.path.join(config_dir, "Config.yaml")
    app.config["YAML_CONFIG"] = load_yaml_config(config_file_path)

    database_file_path = os.path.join(config_dir, "DatabaseConfig.yaml")
    app.config["DATABASE_CONFIG"] = load_yaml_config(database_file_path)

    # --- Extracted settings ---
    yaml_cfg = app.config["YAML_CONFIG"]
    app.config["AI_MODEL"] = yaml_cfg["ServerSettings"]["AiModel"]
