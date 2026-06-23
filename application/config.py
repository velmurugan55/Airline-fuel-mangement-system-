"""
Application configuration using Pydantic Settings.
Reads from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",   # silently ignore undeclared .env vars (e.g. POSTGRES_*)
    )

    # Project
    PROJECT_NAME: str = "Airline Fuel Management System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/fuel_system"

    # JWT
    SECRET_KEY: str = "changethis-to-a-very-long-and-secure-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
