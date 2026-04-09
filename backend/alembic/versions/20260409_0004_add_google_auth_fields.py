"""
Add Google social auth and password reset fields to users table.
"""
from alembic import op
import sqlalchemy as sa


revision = "20260409_0004"
down_revision = "20260408_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if "google_id" not in columns:
        op.add_column("users", sa.Column("google_id", sa.String(length=100), nullable=True))

    if "social_provider" not in columns:
        op.add_column("users", sa.Column("social_provider", sa.String(length=20), nullable=True))

    if "reset_password_token" not in columns:
        op.add_column(
            "users",
            sa.Column("reset_password_token", sa.String(length=100), nullable=True),
        )

    if "reset_password_expires" not in columns:
        op.add_column(
            "users",
            sa.Column("reset_password_expires", sa.DateTime(), nullable=True),
        )

    if "ix_users_google_id" not in indexes:
        op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)

    if "ix_users_reset_password_token" not in indexes:
        op.create_index(
            "ix_users_reset_password_token",
            "users",
            ["reset_password_token"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if "ix_users_reset_password_token" in indexes:
        op.drop_index("ix_users_reset_password_token", table_name="users")

    if "ix_users_google_id" in indexes:
        op.drop_index("ix_users_google_id", table_name="users")

    if "reset_password_expires" in columns:
        op.drop_column("users", "reset_password_expires")

    if "reset_password_token" in columns:
        op.drop_column("users", "reset_password_token")

    if "social_provider" in columns:
        op.drop_column("users", "social_provider")

    if "google_id" in columns:
        op.drop_column("users", "google_id")
