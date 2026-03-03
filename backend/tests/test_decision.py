"""Tests for decision endpoint: Authority-only; Mode A blocks GRANTED without UGC."""

from __future__ import annotations

import asyncio
import os
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.db.models import (
    Application,
    Decision,
    DecisionType,
    Document,
    DocumentType,
    Institution,
    User,
    UserRole,
)
from app.workflow import ApplicationStatus
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
    if "UPLOAD_DIR" not in os.environ:
        os.environ["UPLOAD_DIR"] = tempfile.mkdtemp()


client = TestClient(app)


def _setup_mom_finalized(ugc_policy_mode: str = "A", ugc_approval_recorded: bool = False):
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(
                name="TC Dec", code="TCDEC", address="A", district="D",
                contact_email="dec@t.com", contact_phone="1",
            )
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            auth = User(email="authdec@t.com", name="Auth", hashed_password=pw, role=UserRole.AUTHORITY)
            reg = User(email="regdec@t.com", name="Reg", hashed_password=pw, role=UserRole.REGISTRAR)
            session.add_all([auth, reg])
            await session.flush()
            app_obj = Application(
                institution_id=inst.id,
                status=ApplicationStatus.MOM_FINALIZED.value,
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode=ugc_policy_mode,
                ugc_approval_recorded=ugc_approval_recorded,
            )
            session.add(app_obj)
            await session.commit()
            return app_obj.id, auth.email, reg.email
    return asyncio.run(_setup())


def test_authority_only_can_issue_decision() -> None:
    """Only AUTHORITY can call POST /decision; REGISTRAR gets 403."""
    app_id, auth_email, reg_email = _setup_mom_finalized(ugc_policy_mode="A", ugc_approval_recorded=True)
    tok_reg = client.post("/api/auth/login", json={"email": reg_email, "password": "secret"}).json()["access_token"]
    payload = {
        "decision_type": "GRANTED",
        "tenure_years": 5,
        "reasons": "Approved.",
        "conditions": "",
    }
    r = client.post(
        f"/api/applications/{app_id}/decision",
        json=payload,
        headers={"Authorization": f"Bearer {tok_reg}"},
    )
    assert r.status_code == 403


def test_mode_a_blocks_granted_without_ugc_approval() -> None:
    """Mode A: GRANTED returns 400 when ugc_approval_recorded is False."""
    app_id, auth_email, _ = _setup_mom_finalized(ugc_policy_mode="A", ugc_approval_recorded=False)
    tok = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]
    payload = {
        "decision_type": "GRANTED",
        "tenure_years": 5,
        "reasons": "Approved.",
        "conditions": "",
    }
    r = client.post(
        f"/api/applications/{app_id}/decision",
        json=payload,
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 400
    assert "UGC" in r.json().get("detail", "")


def test_mode_a_allows_granted_when_ugc_recorded() -> None:
    """Mode A: GRANTED succeeds when ugc_approval_recorded is True."""
    app_id, auth_email, _ = _setup_mom_finalized(ugc_policy_mode="A", ugc_approval_recorded=True)
    tok = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]
    payload = {
        "decision_type": "GRANTED",
        "tenure_years": 5,
        "reasons": "Approved.",
        "conditions": "",
    }
    r = client.post(
        f"/api/applications/{app_id}/decision",
        json=payload,
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 201
    assert r.json()["decision_type"] == "GRANTED"
    assert r.json()["ugc_subject_to_flag"] is False


def test_mode_b_sets_ugc_subject_to_flag_when_not_approved() -> None:
    """Mode B: ugc_subject_to_flag is True when UGC not recorded."""
    app_id, auth_email, _ = _setup_mom_finalized(ugc_policy_mode="B", ugc_approval_recorded=False)
    tok = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]
    payload = {
        "decision_type": "GRANTED",
        "tenure_years": 3,
        "reasons": "Subject to UGC.",
        "conditions": "",
    }
    r = client.post(
        f"/api/applications/{app_id}/decision",
        json=payload,
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 201
    assert r.json()["ugc_subject_to_flag"] is True


def test_decision_creates_document_and_status_closed_for_rejected() -> None:
    """REJECTED leads to CLOSED status and Decision Letter document stored."""
    app_id, auth_email, _ = _setup_mom_finalized(ugc_policy_mode="A", ugc_approval_recorded=False)
    tok = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]
    payload = {
        "decision_type": "REJECTED",
        "reasons": "Does not meet criteria.",
        "conditions": "",
    }
    r = client.post(
        f"/api/applications/{app_id}/decision",
        json=payload,
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 201
    assert r.json()["decision_type"] == "REJECTED"

    async def _check():
        async with TestingSessionLocal() as session:
            app_result = await session.execute(select(Application).where(Application.id == app_id))
            app = app_result.scalar_one_or_none()
            assert app is not None
            assert app.status == ApplicationStatus.CLOSED.value
            doc_result = await session.execute(
                select(Document).where(
                    Document.application_id == app_id,
                    Document.doc_type == DocumentType.DECISION_LETTER,
                )
            )
            doc = doc_result.scalar_one_or_none()
            assert doc is not None
    asyncio.run(_check())
