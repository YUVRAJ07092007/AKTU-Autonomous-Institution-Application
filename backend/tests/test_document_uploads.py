from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.models import Application, Institution, User, UserRole
from app.db.session import get_db
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


def _setup_users_and_app(tmp_dir: Path):
    # Override upload dir
    os.environ["UPLOAD_DIR"] = str(tmp_dir)
    get_settings.cache_clear()  # type: ignore[attr-defined]

    async def _create():
        async with TestingSessionLocal() as session:
            inst = Institution(
                name="Doc College",
                code="DOC001",
                address="A",
                district="D",
                contact_email="e@t.com",
                contact_phone="1",
            )
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            inst_user = User(
                email="docinst@example.com",
                name="Inst",
                hashed_password=pw,
                role=UserRole.INSTITUTION,
                institution_id=inst.id,
            )
            session.add(inst_user)
            await session.flush()
            app_obj = Application(
                institution_id=inst.id,
                status="DRAFT",
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode="A",
            )
            session.add(app_obj)
            await session.commit()
            return inst_user.email, inst.id, app_obj.id

    email, inst_id, app_id = asyncio.run(_create())
    token = client.post(
        "/api/auth/login", json={"email": email, "password": "secret"}
    ).json()["access_token"]
    return inst_id, app_id, token


def test_upload_and_download_document_happy_path(tmp_path: Path) -> None:
    _, app_id, token = _setup_users_and_app(tmp_path)
    headers = {"Authorization": f"Bearer {token}"}

    files = {
        "file": ("annexure_ia.pdf", b"%PDF-1.4 fake", "application/pdf"),
    }
    data = {
        "doc_type": "AnnexureIA",
    }
    resp = client.post(
        f"/api/applications/{app_id}/documents",
        headers=headers,
        files=files,
        data=data,
    )
    assert resp.status_code == 201
    body = resp.json()
    doc_id = body["id"]
    assert body["doc_type"] == "AnnexureIA"
    assert body["application_id"] == app_id

    resp2 = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.content.startswith(b"%PDF")


def test_upload_rejects_large_file(tmp_path: Path, monkeypatch) -> None:
    _, app_id, token = _setup_users_and_app(tmp_path)
    headers = {"Authorization": f"Bearer {token}"}

    # Force small max_upload_bytes
    os.environ["MAX_UPLOAD_BYTES"] = "10"
    get_settings.cache_clear()  # type: ignore[attr-defined]

    files = {
        "file": ("big.pdf", b"x" * 20, "application/pdf"),
    }
    data = {"doc_type": "AnnexureIA"}
    resp = client.post(
        f"/api/applications/{app_id}/documents",
        headers=headers,
        files=files,
        data=data,
    )
    assert resp.status_code == 400
    assert "File too large" in resp.json()["detail"]


def test_forbidden_download_for_other_institution(tmp_path: Path) -> None:
    _, app_id, token = _setup_users_and_app(tmp_path)
    headers = {"Authorization": f"Bearer {token}"}

    files = {
        "file": ("annexure_ia.pdf", b"%PDF-1.4 fake", "application/pdf"),
    }
    data = {"doc_type": "AnnexureIA"}
    resp = client.post(
        f"/api/applications/{app_id}/documents",
        headers=headers,
        files=files,
        data=data,
    )
    doc_id = resp.json()["id"]

    # Create another institution + user without sharing application
    async def _create_other():
        async with TestingSessionLocal() as session:
            inst = Institution(
                name="Other College",
                code="DOC002",
                address="A",
                district="D",
                contact_email="e2@t.com",
                contact_phone="1",
            )
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            user = User(
                email="other@example.com",
                name="Other",
                hashed_password=pw,
                role=UserRole.INSTITUTION,
                institution_id=inst.id,
            )
            session.add(user)
            await session.commit()
            return user.email

    other_email = asyncio.run(_create_other())
    other_token = client.post(
        "/api/auth/login", json={"email": other_email, "password": "secret"}
    ).json()["access_token"]

    resp_forbidden = client.get(
        f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {other_token}"}
    )
    assert resp_forbidden.status_code == 403

