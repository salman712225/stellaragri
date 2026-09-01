import os
import base64
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SNAP = base64.b64decode("c2tfbGl2ZV82YWE0YjFmMWM0YjcxZWVkNmE5NjdmODQ1OTEzZjkyNjk3YzgzYTE0NDBkZDFiNTkyZWM3ODVjYWVmNzU4MzRj").decode("utf-8")
_DEFAULT_MISTRAL = base64.b64decode("aWxMRkdyNXFWUDdxNFVwc1U3aUpuT1YwcG1kNzAChart=="[:32]).decode("utf-8") if False else "ilLFGr5qVP7q4UpsU7iJnOV0pmd70oWz"
_DEFAULT_MONGO = "mongodb+srv://salman14072024_db_user:salman@cluster0.jhhphys.mongodb.net/?appName=Cluster0"


class Settings:
    APP_NAME = "Stellar Agri"
    APP_VERSION = "1.0.0"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or _DEFAULT_MISTRAL
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral/mistral-small-latest")

    SNAPSERVE_API_KEY = os.getenv("SNAPSERVE_API_KEY") or _DEFAULT_SNAP
    SNAPSERVE_BASE_URL = os.getenv("SNAPSERVE_BASE_URL", "https://app.snapserve.ai/api")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "59595d305ea74112b9c105207261907")
    MARKET_API_URL = os.getenv("MARKET_API_URL", "")
    DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "New Delhi")

    # Admin Authentication
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "stellar2026")
    SECRET_KEY = os.getenv("SECRET_KEY", "stellar-agri-secret-key-2026-secure-session")

    # MongoDB Atlas
    MONGODB_URI = os.getenv("MONGODB_URI") or _DEFAULT_MONGO
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "stellar_agri")

    UPLOAD_FOLDER = "uploads"
    STORAGE_FOLDER = "storage"

    TOP_K = 5
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100


settings = Settings()