"""Tests for MoM draft, content, and finalize (COMMITTEE only; status rules)."""

from __future__ import annotations

import asyncio
import os
import tempfile
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
    MomContent,
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
    # Ensure DOCX generation has a writable dir (get_settings() may use env)
    if "UPLOAD_DIR" not in os.environ:
        d = tempfile.mkdtemp()
        os.environ["UPLOAD_DIR"] = d


client = TestClient(app)


def _setup_meeting_scheduled_app():
    from app.core.security import hash_password
    import tempfile
    import os
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(
                name="TC MoM", code="TCMOM", address="A", district="D",
                contact_email="mom@t.com", contact_phone="1",
            )
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            reg = User(email="regmom@t.com", name="Reg", hashed_password=pw, role=UserRole.REGISTRAR)
            comm_user = User(email="commom@t.com", name="Committee", hashed_password=pw, role=UserRole.COMMITTEE)
            dealing = User(email="deal@t.com", name="Dealing", hashed_password=pw, role=UserRole.DEALING_HAND)
            session.add_all([reg, comm_user, dealing])
            await session.flush()
            app_obj = Application(
                institution_id=inst.id,
                status=ApplicationStatus.MEETING_SCHEDULED.value,
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode="A",
            )
            session.add(app_obj)
            await session.flush()
            committee = Committee(
                application_id=app_obj.id,
                office_order_no="OO/2026/1",
                created_by_user_id=reg.id,
            )
            session.add(committee)
            await session.flush()
            session.add(CommitteeMember(committee_id=committee.id, user_id=comm_user.id, role=CommitteeMemberRole.MEMBER))
            await session.commit()
            return app_obj.id, reg.email, comm_user.email, dealing.email
    return asyncio.run(_setup())


def test_mom_draft_creates_document_and_status() -> None:
    """POST mom/draft as COMMITTEE: status -> MOM_DRAFT_GENERATED, MoM document and MomContent created."""
    app_id, _reg, comm_email, _deal = _setup_meeting_scheduled_app()
    tok = client.post("/api/auth/login", json={"email": comm_email, "password": "secret"}).json()["access_token"]

    r = client.post(
        f"/api/applications/{app_id}/mom/draft",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == ApplicationStatus.MOM_DRAFT_GENERATED.value

    async def _check():
        async with TestingSessionLocal() as session:
            doc_result = await session.execute(
                select(Document).where(
                    Document.application_id == app_id,
                    Document.doc_type == DocumentType.MOM,
                )
            )
            doc = doc_result.scalar_one_or_none()
            assert doc is not None
            assert "mom_draft" in doc.filename or "mom_draft_v1" in doc.filename
            mom_result = await session.execute(
                select(MomContent).where(MomContent.application_id == app_id)
            )
            mom = mom_result.scalar_one_or_none()
            assert mom is not None
            assert mom.version == 1
            assert "section_6_29_a_i" in mom.content_json
    asyncio.run(_check())


def test_only_committee_can_edit_and_finalize() -> None:
    """Registrar/Dealing cannot call mom/draft, mom/content, mom/finalize (403)."""
    app_id, reg_email, comm_email, deal_email = _setup_meeting_scheduled_app()
    tok_reg = client.post("/api/auth/login", json={"email": reg_email, "password": "secret"}).json()["access_token"]
    tok_deal = client.post("/api/auth/login", json={"email": deal_email, "password": "secret"}).json()["access_token"]

    r_draft_reg = client.post(
        f"/api/applications/{app_id}/mom/draft",
        headers={"Authorization": f"Bearer {tok_reg}"},
    )
    assert r_draft_reg.status_code == 403
    r_draft_deal = client.post(
        f"/api/applications/{app_id}/mom/draft",
        headers={"Authorization": f"Bearer {tok_deal}"},
    )
    assert r_draft_deal.status_code == 403

    # Committee generates draft
    tok_comm = client.post("/api/auth/login", json={"email": comm_email, "password": "secret"}).json()["access_token"]
    client.post(f"/api/applications/{app_id}/mom/draft", headers={"Authorization": f"Bearer {tok_comm}"})
    payload = {
        "section_6_29_a_i": "Summary text",
        "section_6_29_a_ii": "Points and response",
        "section_6_29_a_iii": "Recommendations",
        "comments": "",
    }
    r_put_reg = client.put(
        f"/api/applications/{app_id}/mom/content",
        json=payload,
        headers={"Authorization": f"Bearer {tok_reg}"},
    )
    assert r_put_reg.status_code == 403
    r_fin_reg = client.post(
        f"/api/applications/{app_id}/mom/finalize",
        headers={"Authorization": f"Bearer {tok_reg}"},
    )
    assert r_fin_reg.status_code == 403


def test_mom_status_rules_enforced() -> None:
    """Cannot call mom/draft from non-MEETING_SCHEDULED; cannot finalize without draft/content."""
    app_id, _reg, comm_email, _deal = _setup_meeting_scheduled_app()
    tok = client.post("/api/auth/login", json={"email": comm_email, "password": "secret"}).json()["access_token"]

    # Finalize without draft -> 400 (no content)
    r_fin = client.post(
        f"/api/applications/{app_id}/mom/finalize",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r_fin.status_code == 400

    # Draft -> MOM_DRAFT_GENERATED
    client.post(f"/api/applications/{app_id}/mom/draft", headers={"Authorization": f"Bearer {tok}"})
    # Second draft from same status not allowed (transition MEETING_SCHEDULED -> MOM_DRAFT_GENERATED only once)
    r_draft2 = client.post(
        f"/api/applications/{app_id}/mom/draft",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r_draft2.status_code == 400

    # PUT content then finalize -> MOM_FINALIZED
    payload = {
        "section_6_29_a_i": "Done",
        "section_6_29_a_ii": "Done",
        "section_6_29_a_iii": "Done",
        "comments": "",
    }
    r_put = client.put(
        f"/api/applications/{app_id}/mom/content",
        json=payload,
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r_put.status_code == 200
    assert r_put.json()["version"] >= 2

    r_fin2 = client.post(
        f"/api/applications/{app_id}/mom/finalize",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r_fin2.status_code == 200
    assert r_fin2.json()["status"] == ApplicationStatus.MOM_FINALIZED.value


def test_ugc_can_issue_granted() -> None:
    """can_issue_granted: Mode A blocks until ugc_approval_recorded; Mode B allows."""
    from app.workflow import can_issue_granted
    allowed, msg = can_issue_granted("A", False)
    assert allowed is False
    assert "UGC" in msg
    allowed, _ = can_issue_granted("A", True)
    assert allowed is True
    allowed, _ = can_issue_granted("B", False)
    assert allowed is True
