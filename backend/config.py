import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "test")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "test")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "test")
SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "mistralai/mistral-7b-instruct")
BACKUP_MODEL = os.getenv("PRIMARY_MODEL", "meta-llama/llama-3-8b-instruct")

GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.heart_rate.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.body.read",
    "openid",
    "email",
    "profile"
]
