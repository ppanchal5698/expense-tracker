"""Application configuration and settings management."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENV: str = "development"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str
    DATABASE_POOL_MIN: int = 1
    DATABASE_POOL_MAX: int = 20
    DATABASE_TIMEOUT: int = 30

    @property
    def database_url_async(self) -> str:
        """Get database URL with asyncpg driver if not already present."""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL

    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Configuration
    API_TITLE: str = "Expense Management API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Track and analyze personal expenses"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

