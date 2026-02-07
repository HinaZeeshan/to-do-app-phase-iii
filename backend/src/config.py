"""
Application configuration using pydantic-settings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # Security
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    # CORS
    cors_origins: str = "http://localhost:3000,https://todo-app-phase-ii-ashen.vercel.app"

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
