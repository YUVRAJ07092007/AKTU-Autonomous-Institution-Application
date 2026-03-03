"""meetings table

Revision ID: 0005_meetings
Revises: 0004_committee
Create Date: 2026-03-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.db.models import MeetingMode


revision = "0005_meetings"
down_revision = "0004_committee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode", sa.Enum(MeetingMode), nullable=False),
        sa.Column("date_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("venue", sa.String(length=255), nullable=True),
        sa.Column("online_link", sa.String(length=512), nullable=True),
        sa.Column("agenda", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_meetings_application_id", "meetings", ["application_id"], unique=False)


def downgrade() -> None:
    op.drop_table("meetings")
