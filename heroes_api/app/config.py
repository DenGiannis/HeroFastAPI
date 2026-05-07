from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """App settings."""
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    database_url: str = "sqlite:///./heroes_database.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    """Get cached app settings (singleton)."""
    return Settings()