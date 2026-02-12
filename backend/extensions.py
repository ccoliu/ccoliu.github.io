# ---------------------------------------------------
# Codoctopus — Shared Extensions
# Singleton instances initialised once at app startup.
# ---------------------------------------------------

from google import genai
from backend.services.db_utility import MongoDBTools, DocumentBuilder, AuthSystem
from backend.services.format_enforcer import Enforcer
from backend.services.plagiarism_checker import PlagiarismChecker

# These will be populated by init_extensions()
gemini_client = None  # type: ignore

database_tools: MongoDBTools = None  # type: ignore
document_builder: DocumentBuilder = None  # type: ignore
auth_system: AuthSystem = None  # type: ignore

message_enforcer: Enforcer = None  # type: ignore
similarity_helper: PlagiarismChecker = None  # type: ignore


def init_extensions(app):
    """Initialise all shared objects using app config."""
    global gemini_client
    global database_tools, document_builder, auth_system
    global message_enforcer, similarity_helper

    # Google GenAI client (new SDK)
    gemini_client = genai.Client(api_key=app.config["GEMINI_API_KEY"])

    # Database
    database_tools = MongoDBTools(uri=app.config["MONGODB_URI"])
    document_builder = DocumentBuilder()
    auth_system = AuthSystem(
        uri=app.config["MONGODB_URI"],
        jwt_secret=app.config["JWT_SECRET"],
        jwt_expiry_hours=app.config["JWT_EXPIRY_HOURS"],
    )

    # Helpers
    message_enforcer = Enforcer()
    similarity_helper = PlagiarismChecker()
