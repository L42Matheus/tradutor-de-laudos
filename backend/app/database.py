"""
ConfiguraÃ§Ã£o do banco de dados SQLAlchemy e migraÃ§Ãµes.
"""
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def is_sqlite_url(database_url: str | None = None) -> bool:
    return "sqlite" in (database_url or settings.database_url)


def is_postgres_url(database_url: str | None = None) -> bool:
    target = (database_url or settings.database_url).lower()
    return target.startswith("postgresql") or target.startswith("postgres")


def get_db():
    """Dependency para injeÃ§Ã£o de sessÃ£o do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager para uso fora de rotas FastAPI."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Inicializa o banco.

    - Em Postgres: habilita extensÃµes e executa Alembic.
    - Em SQLite: mantÃ©m create_all + migraÃ§Ãµes leves para compatibilidade local.
    """
    import app.models.db_models  # noqa: F401
    import app.models.platform_models  # noqa: F401

    if is_postgres_url():
        _ensure_postgres_extensions()
        if settings.database_auto_migrate:
            _run_alembic_migrations()
        else:
            Base.metadata.create_all(bind=engine)
        return

    Base.metadata.create_all(bind=engine)
    _run_lightweight_migrations()


def _ensure_postgres_extensions() -> None:
    if not is_postgres_url() or not settings.postgres_enable_pgvector:
        return

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def _run_alembic_migrations() -> None:
    alembic_ini_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")


def _run_lightweight_migrations():
    """
    Aplica alteracoes leves de schema para SQLite sem depender de Alembic.
    Restrito a colunas novas e nullable/default-safe.
    """
    migrations = {
        "users": {
            "age": "ALTER TABLE users ADD COLUMN age INTEGER",
            "city": "ALTER TABLE users ADD COLUMN city VARCHAR(100)",
            "state": "ALTER TABLE users ADD COLUMN state VARCHAR(2)",
            "specialty": "ALTER TABLE users ADD COLUMN specialty VARCHAR(120)",
            "professional_registry_type": "ALTER TABLE users ADD COLUMN professional_registry_type VARCHAR(20)",
            "professional_registry_number": "ALTER TABLE users ADD COLUMN professional_registry_number VARCHAR(30)",
            "professional_registry_state": "ALTER TABLE users ADD COLUMN professional_registry_state VARCHAR(2)",
            "specialist_verification_status": (
                "ALTER TABLE users ADD COLUMN specialist_verification_status "
                "VARCHAR(20) NOT NULL DEFAULT 'not_applicable'"
            ),
            "preferred_llm_provider": "ALTER TABLE users ADD COLUMN preferred_llm_provider VARCHAR(20) NOT NULL DEFAULT 'claude'",
            "preferred_llm_model": "ALTER TABLE users ADD COLUMN preferred_llm_model VARCHAR(50)",
        },
        "traducoes": {
            "user_id": "ALTER TABLE traducoes ADD COLUMN user_id VARCHAR(36)",
            "solicitar_revisao": "ALTER TABLE traducoes ADD COLUMN solicitar_revisao BOOLEAN NOT NULL DEFAULT 0",
            "status_revisao": "ALTER TABLE traducoes ADD COLUMN status_revisao VARCHAR(20) NOT NULL DEFAULT 'nao_solicitada'",
            "resultado_json": "ALTER TABLE traducoes ADD COLUMN resultado_json TEXT",
            "glossario_json": "ALTER TABLE traducoes ADD COLUMN glossario_json TEXT",
            "documento_hash": "ALTER TABLE traducoes ADD COLUMN documento_hash VARCHAR(64)",
            "ultimo_acesso_em": "ALTER TABLE traducoes ADD COLUMN ultimo_acesso_em DATETIME",
            "total_acessos": "ALTER TABLE traducoes ADD COLUMN total_acessos INTEGER NOT NULL DEFAULT 1",
            "cache_hits": "ALTER TABLE traducoes ADD COLUMN cache_hits INTEGER NOT NULL DEFAULT 0",
        },
        "translation_history": {
            "original_text": "ALTER TABLE translation_history ADD COLUMN original_text TEXT",
            "original_image_base64": "ALTER TABLE translation_history ADD COLUMN original_image_base64 TEXT",
            "original_image_media_type": "ALTER TABLE translation_history ADD COLUMN original_image_media_type VARCHAR(50)",
            "document_hash": "ALTER TABLE translation_history ADD COLUMN document_hash VARCHAR(64)",
            "file_hash": "ALTER TABLE translation_history ADD COLUMN file_hash VARCHAR(64)",
            "total_accesses": "ALTER TABLE translation_history ADD COLUMN total_accesses INTEGER NOT NULL DEFAULT 1",
            "last_accessed_at": "ALTER TABLE translation_history ADD COLUMN last_accessed_at DATETIME",
        },
    }

    with engine.begin() as connection:
        for table_name, columns in migrations.items():
            try:
                existing_columns = {
                    row[1]
                    for row in connection.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                }
            except Exception:
                continue

            for column_name, statement in columns.items():
                if column_name not in existing_columns:
                    try:
                        connection.execute(text(statement))
                    except Exception:
                        pass
