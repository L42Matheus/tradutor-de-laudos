"""
Remove Gov.br-specific fields from users table.
"""
from alembic import op
import sqlalchemy as sa


revision = "20260409_0005"
down_revision = "20260409_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if "ix_users_cpf" in indexes:
        op.drop_index("ix_users_cpf", table_name="users")

    if "govbr_reliability_level" in columns:
        op.drop_column("users", "govbr_reliability_level")

    if "cpf_verified" in columns:
        op.drop_column("users", "cpf_verified")

    if "cpf" in columns:
        op.drop_column("users", "cpf")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if "cpf" not in columns:
        op.add_column("users", sa.Column("cpf", sa.String(length=11), nullable=True))

    if "cpf_verified" not in columns:
        op.add_column(
            "users",
            sa.Column("cpf_verified", sa.Boolean(), nullable=False, server_default="0"),
        )

    if "govbr_reliability_level" not in columns:
        op.add_column(
            "users",
            sa.Column("govbr_reliability_level", sa.String(length=10), nullable=True),
        )

    if "ix_users_cpf" not in indexes:
        op.create_index("ix_users_cpf", "users", ["cpf"], unique=True)
