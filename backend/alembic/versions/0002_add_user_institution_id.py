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
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "institution_id",
                sa.Integer(),
                sa.ForeignKey("institutions.id", ondelete="SET NULL", name="fk_users_institution_id"),
                nullable=True,
            ),
        )
        batch_op.create_index("ix_users_institution_id", ["institution_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index("ix_users_institution_id", if_exists=True)
        batch_op.drop_column("institution_id")
