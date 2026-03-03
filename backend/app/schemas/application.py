"""Request/response schemas for applications."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    """Payload for POST /api/applications (draft)."""

    institution_id: int
    requested_from_year: int = Field(..., ge=2020, le=2030)
    programmes_json: dict[str, Any] = Field(default_factory=dict)
    ugc_policy_mode: str = Field("A", pattern="^[AB]$")


class ApplicationUpdate(BaseModel):
    """Payload for PATCH /api/applications/{id} (draft fields only)."""

    requested_from_year: int | None = Field(None, ge=2020, le=2030)
    programmes_json: dict[str, Any] | None = None
    ugc_policy_mode: str | None = Field(None, pattern="^[AB]$")


class ApplicationOut(BaseModel):
    id: int
    public_id: str
    institution_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    requested_from_year: int
    programmes_json: dict[str, Any]
    ugc_policy_mode: str
    ugc_approval_recorded: bool = False

    class Config:
        from_attributes = True


class DispatchIn(BaseModel):
    speedpost_no: str = Field(..., min_length=1, max_length=100)
    dispatch_date: str | None = None  # ISO date YYYY-MM-DD


class ReceiveIn(BaseModel):
    akt_diary_no: str = Field(..., min_length=1, max_length=100)
    remarks: str | None = None


class DeficiencyIn(BaseModel):
    remarks: str = Field(..., min_length=1)
    due_date: str | None = None
