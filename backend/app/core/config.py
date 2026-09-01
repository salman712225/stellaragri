from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME = "Stellar Agri"
    APP_VERSION = "1.0.0"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral/mistral-small-latest")

    SNAPSERVE_API_KEY = os.getenv("SNAPSERVE_API_KEY", "")
    SNAPSERVE_BASE_URL = os.getenv("SNAPSERVE_BASE_URL", "https://app.snapserve.ai/api")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "59595d305ea74112b9c105207261907")
    MARKET_API_URL = os.getenv("MARKET_API_URL", "")
    DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "New Delhi")

    # Admin Authentication
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "stellar2026")
    SECRET_KEY = os.getenv("SECRET_KEY", "stellar-agri-secret-key-2026-secure-session")

    # MongoDB Atlas
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "stellar_agri")

    UPLOAD_FOLDER = "uploads"
    STORAGE_FOLDER = "storage"

    TOP_K = 5
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100


settings = Settings()