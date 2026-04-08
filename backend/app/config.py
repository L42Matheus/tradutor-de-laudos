"""
Configurações da aplicação usando pydantic-settings
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # API
    app_name: str = "Traduz Saúde API"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM Providers API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    
    # Model Defaults (atualizados abril/2026)
    claude_model: str = "claude-sonnet-4-6"           # Claude Sonnet 4.6
    openai_model: str = "gpt-5-preview"               # GPT-5 Preview
    gemini_model: str = "gemini-3-flash"              # Gemini 3 Flash
    
    # Enabled Providers
    enabled_providers: list[str] = ["claude", "openai", "gemini"]

    # LLM General Settings
    max_tokens: int = 4000
    temperature: float = 0.3

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://traduz-saude-app.up.railway.app",
        "*"
    ]

    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 100

    # Limits
    max_text_length: int = 10000
    max_requests_per_session: int = 20
    free_translations_limit: int = 5

    # File upload
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = ["pdf", "txt", "png", "jpg", "jpeg", "gif", "webp"]

    # Database
    database_url: str = "sqlite:///./traduz_saude.db"
    database_auto_migrate: bool = True
    postgres_enable_pgvector: bool = True

    # Storage & Encryption
    storage_backend: str = "filesystem"
    storage_root: str = str((Path(__file__).resolve().parents[1] / "storage").resolve())
    storage_public_base_url: str = "/api/v1/storage"
    storage_keep_legacy_base64_history: bool = False
    encryption_key: str = "3p6v9y$B&E)H@McQfTjWmZq4t7w!z%C*F-JaNdRgUkXp2s5u8x/A?D(G+KbPeShV"

    # Pipeline / RAG
    default_pipeline_name: str = "traduz_saude"
    default_pipeline_version: str = "v1"
    rag_embedding_dimensions: int = 1536

    # K-anonimidade LGPD
    k_anonimidade_minimo: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações"""
    return Settings()
