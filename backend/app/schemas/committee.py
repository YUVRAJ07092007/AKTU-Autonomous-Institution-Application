"""Committee and member schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models import CommitteeMemberRole


class CommitteeMemberIn(BaseModel):
    user_id: int
    role: CommitteeMemberRole


class CommitteeCreate(BaseModel):
    members: list[CommitteeMemberIn] = Field(..., min_length=1)


class CommitteeMemberOut(BaseModel):
    id: int
    user_id: int
    role: CommitteeMemberRole

    class Config:
        from_attributes = True


class CommitteeOut(BaseModel):
    id: int
    application_id: int
    office_order_no: str | None
    created_at: datetime
    created_by_user_id: int | None
    members: list[CommitteeMemberOut] = []

    class Config:
        from_attributes = True
