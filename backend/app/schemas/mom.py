"""MoM content schemas — Clause 6.29(a) sections."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MomContentIn(BaseModel):
    """Structured MoM sections for PUT /mom/content."""

    section_6_29_a_i: str = Field("", description="6.29(a)(i) — Summary of presentation by institution")
    section_6_29_a_ii: str = Field("", description="6.29(a)(ii) — Points raised by committee and response")
    section_6_29_a_iii: str = Field("", description="6.29(a)(iii) — Recommendations / observations")
    comments: str = Field("", description="Comments or change log (optional)")

    def to_content_json(self) -> dict:
        return {
            "section_6_29_a_i": self.section_6_29_a_i,
            "section_6_29_a_ii": self.section_6_29_a_ii,
            "section_6_29_a_iii": self.section_6_29_a_iii,
            "comments": self.comments,
        }


class MomContentOut(BaseModel):
    """Latest MoM content for editor."""

    application_id: int
    version: int
    content_json: dict
    updated_by: int
    updated_at: datetime

    class Config:
        from_attributes = True
