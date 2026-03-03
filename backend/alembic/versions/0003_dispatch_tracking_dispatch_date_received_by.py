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
    with op.batch_alter_table("dispatch_tracking", schema=None) as batch_op:
        batch_op.add_column(sa.Column("dispatch_date", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(
            sa.Column(
                "received_by_user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL", name="fk_dispatch_tracking_received_by_user_id"),
                nullable=True,
            ),
        )
        batch_op.create_index("ix_dispatch_tracking_received_by_user_id", ["received_by_user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("dispatch_tracking", schema=None) as batch_op:
        batch_op.drop_index("ix_dispatch_tracking_received_by_user_id", if_exists=True)
        batch_op.drop_column("received_by_user_id")
        batch_op.drop_column("dispatch_date")
