"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    # SQLite for quick testing (change to PostgreSQL for production)
    DATABASE_URL: str = "sqlite:///./untangle.db"
    # PostgreSQL (use this for production):
    # DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/untangle"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Dodo Payments
    DODO_API_KEY: str = ""
    DODO_WEBHOOK_SECRET: str = ""
    DODO_BASE_URL: str = "https://api.dodopayments.com/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        # Add your production frontend URL here after deployment
        # Example: "https://untangle-frontend.vercel.app"
    ]

    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
