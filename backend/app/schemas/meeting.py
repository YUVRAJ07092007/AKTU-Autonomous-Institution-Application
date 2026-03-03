"""Meeting notice schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models import MeetingMode


class MeetingCreate(BaseModel):
    mode: MeetingMode
    date_time: datetime
    venue: str | None = None
    online_link: str | None = Field(None, max_length=512)
    agenda: str = Field(..., min_length=1)


class MeetingOut(BaseModel):
    id: int
    application_id: int
    mode: MeetingMode
    date_time: datetime
    venue: str | None
    online_link: str | None
    agenda: str
    created_by: int | None

    class Config:
        from_attributes = True
