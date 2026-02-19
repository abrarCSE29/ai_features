import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    origins = os.getenv("ORIGINS") or ["*"]
    allow_credentials = bool(os.getenv("ALLOW_CREDENTIALS")) or True
    allow_methods = os.getenv("ALLOWED_METHODS") or ["*"]
    allow_headers = os.getenv("ALLOWED_HEADERS") or ["*"]
    google_api_key = os.getenv("GOOGLE_API_KEY")
    mongo_uri = os.getenv("MONGO_URI") or "mongodb://localhost:27017/"
