"""decisions table

Revision ID: 0007_decisions
Revises: 0006_mom
Create Date: 2026-03-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.db.models import DecisionType


revision = "0007_decisions"
down_revision = "0006_mom"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "decision_type",
            sa.Enum(DecisionType, values_callable=lambda obj: [e.value for e in obj]),
            nullable=False,
        ),
        sa.Column("tenure_years", sa.Integer(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reasons", sa.Text(), nullable=False, server_default=""),
        sa.Column("conditions", sa.Text(), nullable=False, server_default=""),
        sa.Column("ugc_subject_to_flag", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("(datetime('now'))")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
    )
    op.create_index("ix_decisions_application_id", "decisions", ["application_id"], unique=True)


def downgrade() -> None:
    op.drop_table("decisions")
