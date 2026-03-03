"""add user institution_id

Revision ID: 0002_user_institution
Revises: 0001_initial_schema
Create Date: 2026-03-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_user_institution"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_users_institution_id", "users", ["institution_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_institution_id", table_name="users")
    op.drop_column("users", "institution_id")
