"""
Add missing user preference columns required by the auth flow.
"""
from alembic import op
import sqlalchemy as sa


revision = "20260408_0002"
down_revision = "20260408_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "preferred_llm_provider" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "preferred_llm_provider",
                sa.String(length=20),
                nullable=False,
                server_default="claude",
            ),
        )

    if "preferred_llm_model" not in columns:
        op.add_column(
            "users",
            sa.Column("preferred_llm_model", sa.String(length=50), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "preferred_llm_model" in columns:
        op.drop_column("users", "preferred_llm_model")

    if "preferred_llm_provider" in columns:
        op.drop_column("users", "preferred_llm_provider")
