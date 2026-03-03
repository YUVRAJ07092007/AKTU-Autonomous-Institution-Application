"""dispatch_tracking: dispatch_date, received_by_user_id

Revision ID: 0003_dispatch_tracking
Revises: 0002_user_institution
Create Date: 2026-03-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_dispatch_tracking"
down_revision = "0002_user_institution"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dispatch_tracking",
        sa.Column("dispatch_date", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "dispatch_tracking",
        sa.Column("received_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_dispatch_tracking_received_by_user_id", "dispatch_tracking", ["received_by_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_dispatch_tracking_received_by_user_id", table_name="dispatch_tracking")
    op.drop_column("dispatch_tracking", "received_by_user_id")
    op.drop_column("dispatch_tracking", "dispatch_date")
