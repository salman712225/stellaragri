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

    UPLOAD_FOLDER = "uploads"
    STORAGE_FOLDER = "storage"

    TOP_K = 5
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100


settings = Settings()