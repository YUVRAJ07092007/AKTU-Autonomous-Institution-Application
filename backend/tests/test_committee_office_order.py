"""Tests for committee formation and office order generation."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.db.models import (
    Application,
    Committee,
    CommitteeMember,
    CommitteeMemberRole,
    Document,
    DocumentType,
    Institution,
    User,
    UserRole,
)
from app.main import app


engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


async def _init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def setup_module(module) -> None:  # type: ignore[override]
    asyncio.run(_init_db())


client = TestClient(app)


def test_authority_required_for_approval() -> None:
    """Only AUTHORITY can call committee/approve; REGISTRAR gets 403."""
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC", code="TCCO", address="A", district="D", contact_email="e@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            reg = User(email="reg@t.com", name="Reg", hashed_password=pw, role=UserRole.REGISTRAR)
            auth = User(email="auth@t.com", name="Auth", hashed_password=pw, role=UserRole.AUTHORITY)
            mem = User(email="mem@t.com", name="Mem", hashed_password=pw, role=UserRole.COMMITTEE)
            session.add_all([reg, auth, mem])
            await session.flush()
            app_obj = Application(
                institution_id=inst.id,
                status="SCRUTINY_CLEARED",
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode="A",
            )
            session.add(app_obj)
            await session.flush()
            comm = Committee(application_id=app_obj.id, created_by_user_id=reg.id)
            session.add(comm)
            await session.flush()
            session.add(CommitteeMember(committee_id=comm.id, user_id=mem.id, role=CommitteeMemberRole.MEMBER))
            await session.commit()
            return app_obj.id, reg.email, auth.email
    app_id, reg_email, auth_email = asyncio.run(_setup())
    tok_reg = client.post("/api/auth/login", json={"email": reg_email, "password": "secret"}).json()["access_token"]
    tok_auth = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]

    r = client.post(
        f"/api/applications/{app_id}/committee/approve",
        headers={"Authorization": f"Bearer {tok_reg}"},
    )
    assert r.status_code == 403

    r2 = client.post(
        f"/api/applications/{app_id}/committee/approve",
        headers={"Authorization": f"Bearer {tok_auth}"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "COMMITTEE_CONSTITUTED"


def test_document_created_and_saved() -> None:
    """Approve creates Office Order document and saves file."""
    from app.core.security import hash_password
    upload_dir = Path(os.environ.get("UPLOAD_DIR", "./data/uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    os.environ["UPLOAD_DIR"] = str(upload_dir)
    from app.core.config import get_settings
    get_settings.cache_clear()

    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC2", code="TCCO2", address="A", district="D", contact_email="e2@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            auth = User(email="auth2@t.com", name="Auth", hashed_password=pw, role=UserRole.AUTHORITY)
            mem = User(email="mem2@t.com", name="Mem", hashed_password=pw, role=UserRole.COMMITTEE)
            session.add_all([auth, mem])
            await session.flush()
            app_obj = Application(
                institution_id=inst.id,
                status="SCRUTINY_CLEARED",
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode="A",
            )
            session.add(app_obj)
            await session.flush()
            comm = Committee(application_id=app_obj.id, created_by_user_id=auth.id)
            session.add(comm)
            await session.flush()
            session.add(CommitteeMember(committee_id=comm.id, user_id=mem.id, role=CommitteeMemberRole.MEMBER))
            await session.commit()
            return app_obj.id, auth.email
    app_id, auth_email = asyncio.run(_setup())
    tok_auth = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]

    r = client.post(
        f"/api/applications/{app_id}/committee/approve",
        headers={"Authorization": f"Bearer {tok_auth}"},
    )
    assert r.status_code == 200

    async def _check_doc():
        async with TestingSessionLocal() as session:
            result = await session.execute(
                select(Document).where(
                    Document.application_id == app_id,
                    Document.doc_type == DocumentType.OFFICE_ORDER,
                )
            )
            doc = result.scalar_one_or_none()
            return doc
    doc = asyncio.run(_check_doc())
    assert doc is not None
    assert doc.filename.endswith(".docx")
    assert Path(doc.storage_path).exists()
