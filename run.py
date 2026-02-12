# ---------------------------------------------------
# Codoctopus — Application Entry Point
# Usage: python run.py        (local dev server)
#        gunicorn run:app      (production on Render)
# ---------------------------------------------------

from backend import create_app
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
