"""Decision request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models import DecisionType


class DecisionCreate(BaseModel):
    """Payload for POST /api/applications/{id}/decision."""

    decision_type: DecisionType
    tenure_years: int | None = Field(None, ge=1, le=30)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    reasons: str = Field("", max_length=10000)
    conditions: str = Field("", max_length=10000)


class DecisionOut(BaseModel):
    """Issued decision (read)."""

    id: int
    application_id: int
    decision_type: str
    tenure_years: int | None
    valid_from: datetime | None
    valid_to: datetime | None
    reasons: str
    conditions: str
    ugc_subject_to_flag: bool
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True
