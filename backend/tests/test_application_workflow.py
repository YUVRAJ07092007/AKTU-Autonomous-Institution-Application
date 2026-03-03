"""Tests for application lifecycle endpoints and status transitions."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.db.models import Application, Document, DocumentType, Institution, User, UserRole
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


def test_application_create_and_submit_rejects_without_mandatory_annexures() -> None:
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC1", code="TC001", address="A", district="D", contact_email="e1@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            session.add(User(email="i1@t.com", name="I", hashed_password=pw, role=UserRole.INSTITUTION, institution_id=inst.id))
            await session.commit()
            return inst.id
    inst_id = asyncio.run(_setup())
    tok = client.post("/api/auth/login", json={"email": "i1@t.com", "password": "secret"}).json()["access_token"]
    auth = {"Authorization": f"Bearer {tok}"}
    create_resp = client.post(
        "/api/applications",
        json={"institution_id": inst_id, "requested_from_year": 2026, "programmes_json": {}, "ugc_policy_mode": "A"},
        headers=auth,
    )
    assert create_resp.status_code == 201
    app_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "DRAFT"
    submit_resp = client.post(f"/api/applications/{app_id}/submit", headers=auth)
    assert submit_resp.status_code == 400
    assert "Mandatory annexures missing" in submit_resp.json()["detail"]


def test_application_allowed_transitions() -> None:
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC", code="TC003", address="A", district="D", contact_email="e@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            u1 = User(email="i@t.com", name="I", hashed_password=pw, role=UserRole.INSTITUTION, institution_id=inst.id)
            u2 = User(email="d@t.com", name="D", hashed_password=pw, role=UserRole.DEALING_HAND)
            session.add_all([u1, u2])
            await session.flush()
            inst_user_id = u1.id
            await session.commit()
            return inst.id, inst_user_id
    inst_id, inst_user_id = asyncio.run(_setup())
    tok_i = client.post("/api/auth/login", json={"email": "i@t.com", "password": "secret"}).json()["access_token"]
    tok_d = client.post("/api/auth/login", json={"email": "d@t.com", "password": "secret"}).json()["access_token"]

    auth_i = {"Authorization": f"Bearer {tok_i}"}
    auth_d = {"Authorization": f"Bearer {tok_d}"}

    r = client.post("/api/applications", json={"institution_id": inst_id, "requested_from_year": 2026, "programmes_json": {}, "ugc_policy_mode": "A"}, headers=auth_i)
    assert r.status_code == 201
    app_id = r.json()["id"]

    async def _add_docs():
        async with TestingSessionLocal() as session:
            for dt in [DocumentType.ANNEXURE_IA, DocumentType.ANNEXURE_II, DocumentType.ANNEXURE_III, DocumentType.ANNEXURE_IV, DocumentType.ANNEXURE_V, DocumentType.ANNEXURE_VII, DocumentType.FEE_PROOF]:
                doc = Document(application_id=app_id, doc_type=dt, filename="x.pdf", storage_path="/x", uploaded_by=inst_user_id, uploaded_at=datetime.now(timezone.utc), version=1, sha256="0" * 64)
                session.add(doc)
            await session.commit()
    asyncio.run(_add_docs())

    r = client.post(f"/api/applications/{app_id}/submit", headers=auth_i)
    assert r.status_code == 200
    assert r.json()["status"] == "SUBMITTED_ONLINE"

    r = client.post(f"/api/applications/{app_id}/dispatch", json={"speedpost_no": "SP123"}, headers=auth_i)
    assert r.status_code == 200
    assert r.json()["status"] == "HARDCOPY_DISPATCHED"

    r = client.post(f"/api/applications/{app_id}/receive", json={"akt_diary_no": "DIARY1"}, headers=auth_d)
    assert r.status_code == 200
    assert r.json()["status"] == "HARDCOPY_RECEIVED"

    r = client.post(f"/api/applications/{app_id}/start-scrutiny", headers=auth_d)
    assert r.status_code == 200
    assert r.json()["status"] == "UNDER_SCRUTINY"

    r = client.post(f"/api/applications/{app_id}/deficiency", json={"remarks": "Missing signature"}, headers=auth_d)
    assert r.status_code == 200
    assert r.json()["status"] == "DEFICIENCY_RAISED"

    r = client.post(f"/api/applications/{app_id}/start-scrutiny", headers=auth_d)  # back to UNDER_SCRUTINY
    assert r.status_code == 200
    assert r.json()["status"] == "UNDER_SCRUTINY"

    r = client.post(f"/api/applications/{app_id}/scrutiny-clear", headers=auth_d)
    assert r.status_code == 200
    assert r.json()["status"] == "SCRUTINY_CLEARED"


def test_forbidden_transition_returns_400() -> None:
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC4", code="TC004", address="A", district="D", contact_email="e4@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            session.add_all([
                User(email="i4@t.com", name="I", hashed_password=pw, role=UserRole.INSTITUTION, institution_id=inst.id),
                User(email="d4@t.com", name="D", hashed_password=pw, role=UserRole.DEALING_HAND),
            ])
            await session.commit()
            return inst.id
    inst_id = asyncio.run(_setup())
    tok_i = client.post("/api/auth/login", json={"email": "i4@t.com", "password": "secret"}).json()["access_token"]
    tok_d = client.post("/api/auth/login", json={"email": "d4@t.com", "password": "secret"}).json()["access_token"]
    r = client.post("/api/applications", json={"institution_id": inst_id, "requested_from_year": 2026, "programmes_json": {}, "ugc_policy_mode": "A"}, headers={"Authorization": f"Bearer {tok_i}"})
    app_id = r.json()["id"]
    # Dealing hand cannot submit (only institution can) -> 403
    r2 = client.post(f"/api/applications/{app_id}/submit", headers={"Authorization": f"Bearer {tok_d}"})
    assert r2.status_code == 403
    # Institution cannot receive (only dealing hand) -> 403
    r3 = client.post(f"/api/applications/{app_id}/receive", json={"akt_diary_no": "X"}, headers={"Authorization": f"Bearer {tok_i}"})
    assert r3.status_code == 403
    # Only dealing hand can ack-received -> 403 for institution
    r4 = client.post(f"/api/applications/{app_id}/ack-received", json={"akt_diary_no": "X"}, headers={"Authorization": f"Bearer {tok_i}"})
    assert r4.status_code == 403


def test_institution_cannot_dispatch_after_hardcopy_received() -> None:
    """Institution can set speedpost only before hardcopy received; after ack, dispatch returns 400."""
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC5", code="TC005", address="A", district="D", contact_email="e5@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            u1 = User(email="i5@t.com", name="I", hashed_password=pw, role=UserRole.INSTITUTION, institution_id=inst.id)
            u2 = User(email="d5@t.com", name="D", hashed_password=pw, role=UserRole.DEALING_HAND)
            session.add_all([u1, u2])
            await session.flush()
            inst_user_id = u1.id
            await session.commit()
            return inst.id, inst_user_id
    inst_id, inst_user_id = asyncio.run(_setup())
    tok_i = client.post("/api/auth/login", json={"email": "i5@t.com", "password": "secret"}).json()["access_token"]
    tok_d = client.post("/api/auth/login", json={"email": "d5@t.com", "password": "secret"}).json()["access_token"]
    auth_i = {"Authorization": f"Bearer {tok_i}"}
    auth_d = {"Authorization": f"Bearer {tok_d}"}

    r = client.post("/api/applications", json={"institution_id": inst_id, "requested_from_year": 2026, "programmes_json": {}, "ugc_policy_mode": "A"}, headers=auth_i)
    assert r.status_code == 201
    app_id = r.json()["id"]
    async def _add_docs():
        async with TestingSessionLocal() as session:
            for dt in [DocumentType.ANNEXURE_IA, DocumentType.ANNEXURE_II, DocumentType.ANNEXURE_III, DocumentType.ANNEXURE_IV, DocumentType.ANNEXURE_V, DocumentType.ANNEXURE_VII, DocumentType.FEE_PROOF]:
                session.add(Document(application_id=app_id, doc_type=dt, filename="x.pdf", storage_path="/x", uploaded_by=inst_user_id, uploaded_at=datetime.now(timezone.utc), version=1, sha256="0" * 64))
            await session.commit()
    asyncio.run(_add_docs())

    client.post(f"/api/applications/{app_id}/submit", headers=auth_i)
    client.post(f"/api/applications/{app_id}/dispatch", json={"speedpost_no": "SP999"}, headers=auth_i)
    client.post(f"/api/applications/{app_id}/ack-received", json={"akt_diary_no": "DIARY99"}, headers=auth_d)
    # Now status is HARDCOPY_RECEIVED; institution must not be able to dispatch again
    r_dispatch = client.post(f"/api/applications/{app_id}/dispatch", json={"speedpost_no": "SP2"}, headers=auth_i)
    assert r_dispatch.status_code == 400
    assert "not allowed" in r_dispatch.json()["detail"].lower()
