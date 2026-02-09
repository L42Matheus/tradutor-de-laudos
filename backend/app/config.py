"""
Configurações da aplicação usando pydantic-settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # API
    app_name: str = "Traduz Saúde API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Anthropic
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    temperature: float = 0.3

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 100

    # Limits
    max_text_length: int = 10000
    max_requests_per_session: int = 20
    free_translations_limit: int = 3

    # File upload
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = ["pdf", "txt", "png", "jpg", "jpeg", "gif", "webp"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações"""
    return Settings()
