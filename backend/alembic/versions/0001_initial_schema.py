"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-03 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.db.models import DocumentType, UserRole


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
            nullable=False,
        ),
    )

    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("public_id", sa.String(length=36), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id")),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("requested_from_year", sa.Integer(), nullable=False),
        sa.Column("programmes_json", sa.JSON(), nullable=False),
        sa.Column("ugc_policy_mode", sa.String(length=1), nullable=False),
    )
    op.create_index(
        "ix_applications_public_id", "applications", ["public_id"], unique=True
    )

    op.create_table(
        "dispatch_tracking",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id")),
        sa.Column("speedpost_no", sa.String(length=100)),
        sa.Column("akt_diary_no", sa.String(length=100)),
        sa.Column("received_date", sa.DateTime(timezone=True)),
        sa.Column("remarks", sa.Text()),
        sa.UniqueConstraint("application_id", "speedpost_no", name="uq_dispatch_speedpost"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id")),
        sa.Column(
            "doc_type",
            sa.Enum(DocumentType, values_callable=lambda obj: [e.value for e in obj]),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(length=50)),
        sa.Column("details_json", sa.JSON()),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id")),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("documents")
    op.drop_table("dispatch_tracking")
    op.drop_index("ix_applications_public_id", table_name="applications")
    op.drop_table("applications")
    op.drop_table("institutions")
    op.drop_table("users")

