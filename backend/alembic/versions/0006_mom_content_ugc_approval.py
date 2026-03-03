"""mom_content table and ugc_approval_recorded on applications

Revision ID: 0006_mom
Revises: 0005_meetings
Create Date: 2026-03-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_mom"
down_revision = "0005_meetings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("applications", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("ugc_approval_recorded", sa.Boolean(), nullable=False, server_default="0"),
        )
    op.create_table(
        "mom_content",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("(datetime('now'))")),
    )
    op.create_index("ix_mom_content_application_id", "mom_content", ["application_id"], unique=False)


def downgrade() -> None:
    op.drop_table("mom_content")
    with op.batch_alter_table("applications", schema=None) as batch_op:
        batch_op.drop_column("ugc_approval_recorded")
