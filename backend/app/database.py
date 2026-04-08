"""
Configuração do banco de dados SQLAlchemy
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para injeção de sessão do banco."""
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
    """Inicializa o banco de dados criando todas as tabelas."""
    from app.models.db_models import Base as DBBase
    DBBase.metadata.create_all(bind=engine)
    _run_lightweight_migrations()


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
