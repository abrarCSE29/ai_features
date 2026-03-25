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
    redis_uri = os.getenv("REDIS_URI") or "redis://localhost:6379/"
    redis_draft_order_ttl = int(os.getenv("REDIS_DRAFT_ORDER_TTL") or 900)
    smtp_host = os.getenv("SMTP_HOST") or "smtp.gmail.com"
    smtp_port = int(os.getenv("SMTP_PORT") or 587)
    smtp_user = os.getenv("SMTP_USER") or ""
    smtp_password = os.getenv("SMTP_PASSWORD") or ""
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL") or ""


class ChatbotConfig:
    model_name = os.getenv("GEMINI_MODEL_NAME") or "gemini-2.5-flash"
