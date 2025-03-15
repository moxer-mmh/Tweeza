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

    # OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    FACEBOOK_CLIENT_ID: str = os.getenv("FACEBOOK_CLIENT_ID", "")
    FACEBOOK_CLIENT_SECRET: str = os.getenv("FACEBOOK_CLIENT_SECRET", "")
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    TWITTER_CLIENT_ID: str = os.getenv("TWITTER_CLIENT_ID", "")
    TWITTER_CLIENT_SECRET: str = os.getenv("TWITTER_CLIENT_SECRET", "")

    # Email settings
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "no-reply@tweeza.com")
    EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "True").lower() in (
        "true",
        "1",
        "t",
    )

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
