"""Application configuration using Pydantic Settings."""

import logging
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongodb_url: str
    database_name: str

    # Application Configuration
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # API Configuration
    api_title: str = "FastAPI MongoDB CRUD"
    api_version: str = "1.0.0"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **data):
        """Initialize settings and validate required fields."""
        super().__init__(**data)
        self._validate_required_fields()

    def _validate_required_fields(self) -> None:
        """Validate that all required fields are set."""
        required_fields = {"mongodb_url", "database_name"}
        missing_fields = [field for field in required_fields if not getattr(self, field)]

        if missing_fields:
            msg = f"Missing required environment variables: {', '.join(missing_fields)}"
            raise ValueError(msg)

        logger = logging.getLogger(__name__)
        logger.info(
            "Configuration loaded",
            extra={
                "environment": self.environment,
                "log_level": self.log_level,
                "database_name": self.database_name,
            },
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
