from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.db.models import DocumentType


class DocumentOut(BaseModel):
  id: int
  application_id: int
  doc_type: DocumentType
  filename: str
  version: int
  sha256: str
  uploaded_at: datetime

  class Config:
    from_attributes = True

