"""committee and committee_members tables

Revision ID: 0004_committee
Revises: 0003_dispatch_tracking
Create Date: 2026-03-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.db.models import CommitteeMemberRole


revision = "0004_committee"
down_revision = "0003_dispatch_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "committees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("office_order_no", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_committees_application_id", "committees", ["application_id"], unique=False)

    op.create_table(
        "committee_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("committee_id", sa.Integer(), sa.ForeignKey("committees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum(CommitteeMemberRole), nullable=False),
    )
    op.create_index("ix_committee_members_committee_id", "committee_members", ["committee_id"], unique=False)
    op.create_index("ix_committee_members_user_id", "committee_members", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("committee_members")
    op.drop_table("committees")
