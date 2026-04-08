"""
Initial schema for legacy tables plus platform tables in Postgres.
"""
from alembic import op

from app.database import Base
import app.models.db_models  # noqa: F401
import app.models.platform_models  # noqa: F401


revision = "20260408_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
