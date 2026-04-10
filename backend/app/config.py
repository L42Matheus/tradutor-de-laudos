"""
Configuracoes da aplicacao usando pydantic-settings.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuracoes da aplicacao."""

    # API
    app_name: str = "Traduz Saude API"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM Providers API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""

    # Model Defaults (abril/2026)
    claude_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-5-preview"
    gemini_model: str = "gemini-3-flash"

    # Enabled Providers
    enabled_providers: list[str] = ["claude", "openai", "gemini"]

    # LLM General Settings
    max_tokens: int = 4000
    temperature: float = 0.3

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Email / Notifications
    email_from: str = "noreply@traduzsaude.com.br"
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # URLs
    frontend_url: str = "http://localhost:5173"
    session_secret_key: str = "traduz-saude-session-dev-key"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
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

    # LGPD
    k_anonimidade_minimo: int = 5

    # Specialist verification
    specialist_verification_enabled: bool = False
    specialist_auto_verify_crm: bool = True
    specialist_require_documents: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                import json

                parsed = json.loads(raw)
                return [item.strip() for item in parsed if isinstance(item, str) and item.strip()]
            return [item.strip() for item in raw.split(",") if item.strip()]

        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada das configuracoes."""
    return Settings()
