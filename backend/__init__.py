# ---------------------------------------------------
# Codoctopus — Flask App Factory
# Consolidates Rest, Generate, and Auth servers into one app.
# ---------------------------------------------------

import os
from flask import Flask, send_from_directory, redirect
from flask_cors import CORS


def create_app():
    """Create and configure the Flask application."""

    # Resolve paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, "frontend")

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path="",
    )

    # Enable CORS for all routes
    CORS(app)

    # Load configuration
    from backend.config import load_config
    load_config(app)

    # Initialize shared extensions (OpenAI clients, DB, etc.)
    from backend.extensions import init_extensions
    init_extensions(app)

    # Register blueprints
    from backend.blueprints.rest import rest_bp
    from backend.blueprints.generate import generate_bp
    from backend.blueprints.auth import auth_bp

    app.register_blueprint(rest_bp, url_prefix="/api/rest")
    app.register_blueprint(generate_bp, url_prefix="/api/generate")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # -----------------------------------------------
    # Serve frontend static files
    # -----------------------------------------------

    @app.route("/")
    def serve_root():
        """Redirect root to the main index page."""
        return redirect("/pages/index.html")

    @app.route("/<path:path>")
    def serve_frontend(path):
        """Serve any file from the frontend directory."""
        return send_from_directory(frontend_dir, path)

    return app
