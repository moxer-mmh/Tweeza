import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    API_STR: str = "/api"
    PROJECT_NAME: str = "Tweeza"

    # SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ENVIRONMENT
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # SMS/WhatsApp Integration (optional)
    SMS_API_KEY: Optional[str] = os.getenv("SMS_API_KEY")
    SMS_API_SECRET: Optional[str] = os.getenv("SMS_API_SECRET")
    WHATSAPP_API_KEY: Optional[str] = os.getenv("WHATSAPP_API_KEY")

    # DATABASE
    # We get this dynamically from the session.py in our implementation
    DATABASE_URL: Optional[str] = None

    # Database initialization
    INITIALIZE_DB: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
