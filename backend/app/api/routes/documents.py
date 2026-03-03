from __future__ import annotations

import hashlib
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, log_audit, require_roles
from app.core.config import get_settings
from app.db.models import Application, Document, DocumentType, User, UserRole
from app.db.session import get_db
from app.schemas.document import DocumentOut


router = APIRouter(prefix="/api", tags=["documents"])

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
}


def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


async def _ensure_app_access(db: AsyncSession, app_id: int, user: User) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if user.role == UserRole.INSTITUTION and user.institution_id is not None:
        if app.institution_id != user.institution_id:
            raise HTTPException(status_code=403, detail="Forbidden: not your institution's application")
    return app


@router.post(
    "/applications/{application_id}/documents",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    application_id: int,
    doc_type: DocumentType,
    version: int | None = None,
    notes: str | None = None,
    file: UploadFile = File(...),
    request: Request = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentOut:
    settings = get_settings()
    app = await _ensure_app_access(db, application_id, user)

    ext = _get_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {ext or 'unknown'}",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file not allowed")
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400,
            detail="File too large",
        )

    sha = hashlib.sha256(content).hexdigest()

    safe_name = os.path.basename(file.filename) or f"{doc_type.value}{ext or '.bin'}"
    target_dir: Path = settings.upload_dir / str(application_id) / doc_type.value
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / safe_name
    with target_path.open("wb") as f:
        f.write(content)

    doc = Document(
        application_id=app.id,
        doc_type=doc_type,
        filename=safe_name,
        storage_path=str(target_path),
        uploaded_by=user.id,
        uploaded_at=None,
        version=version or 1,
        sha256=sha,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    if request is not None:
        await log_audit(
            db,
            actor=user,
            action="DOCUMENT_UPLOADED",
            entity_type="document",
            entity_id=str(doc.id),
            request=request,
            details={"application_id": app.id, "doc_type": doc_type.value, "notes": notes},
            application_id=app.id,
        )

    return DocumentOut.model_validate(doc)


@router.get("/applications/{application_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    application_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentOut]:
    """List documents for an application (same access rules as application)."""
    await _ensure_app_access(db, application_id, user)
    result = await db.execute(
        select(Document).where(Document.application_id == application_id).order_by(Document.uploaded_at.desc())
    )
    docs = result.scalars().all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/documents/{document_id}")
async def download_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    result = await db.execute(
        select(Document, Application)
        .join(Application, Document.application_id == Application.id)
        .where(Document.id == document_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Document not found")
    doc: Document = row[0]
    app: Application = row[1]

    if user.role == UserRole.INSTITUTION and user.institution_id is not None:
        if app.institution_id != user.institution_id:
            raise HTTPException(status_code=403, detail="Forbidden: not your institution's application")

    if not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=410, detail="Stored file missing")

    media_type = "application/octet-stream"
    ext = _get_extension(doc.filename)
    if ext == ".pdf":
        media_type = "application/pdf"
    elif ext in {".png"}:
        media_type = "image/png"
    elif ext in {".jpg", ".jpeg"}:
        media_type = "image/jpeg"
    elif ext == ".docx":
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ext == ".xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(
        path=doc.storage_path,
        media_type=media_type,
        filename=doc.filename,
    )

