"""Tests for meeting notice creation and visibility."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

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
    Institution,
    Meeting,
    MeetingMode,
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


def test_only_registrar_can_schedule_meeting() -> None:
    """Authority or other role POST /meetings returns 403."""
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC", code="TCM", address="A", district="D", contact_email="e@t.com", contact_phone="1")
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
                status="COMMITTEE_CONSTITUTED",
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode="A",
            )
            session.add(app_obj)
            await session.flush()
            comm = Committee(application_id=app_obj.id, office_order_no="OO/2026/1", created_by_user_id=reg.id)
            session.add(comm)
            await session.flush()
            session.add(CommitteeMember(committee_id=comm.id, user_id=mem.id, role=CommitteeMemberRole.MEMBER))
            await session.commit()
            return app_obj.id, auth.email, mem.email
    app_id, auth_email, mem_email = asyncio.run(_setup())
    tok_auth = client.post("/api/auth/login", json={"email": auth_email, "password": "secret"}).json()["access_token"]
    tok_mem = client.post("/api/auth/login", json={"email": mem_email, "password": "secret"}).json()["access_token"]

    payload = {
        "mode": "ONLINE",
        "date_time": "2026-06-01T10:00:00+00:00",
        "online_link": "https://meet.example.com/x",
        "agenda": "Clause 6.29 review",
    }
    r_auth = client.post(f"/api/applications/{app_id}/meetings", json=payload, headers={"Authorization": f"Bearer {tok_auth}"})
    assert r_auth.status_code == 403
    r_mem = client.post(f"/api/applications/{app_id}/meetings", json=payload, headers={"Authorization": f"Bearer {tok_mem}"})
    assert r_mem.status_code == 403


def test_meeting_visible_to_committee_not_to_institution_by_default() -> None:
    """Registrar schedules meeting; committee member sees it; institution gets empty list (default OFF)."""
    from app.core.security import hash_password
    async def _setup():
        async with TestingSessionLocal() as session:
            inst = Institution(name="TC2", code="TCM2", address="A", district="D", contact_email="e2@t.com", contact_phone="1")
            session.add(inst)
            await session.flush()
            pw = hash_password("secret")
            reg = User(email="reg2@t.com", name="Reg", hashed_password=pw, role=UserRole.REGISTRAR)
            mem = User(email="mem2@t.com", name="Mem", hashed_password=pw, role=UserRole.COMMITTEE)
            inst_user = User(email="inst2@t.com", name="Inst", hashed_password=pw, role=UserRole.INSTITUTION, institution_id=inst.id)
            session.add_all([reg, mem, inst_user])
            await session.flush()
            app_obj = Application(
                institution_id=inst.id,
                status="COMMITTEE_CONSTITUTED",
                requested_from_year=2026,
                programmes_json={},
                ugc_policy_mode="A",
            )
            session.add(app_obj)
            await session.flush()
            comm = Committee(application_id=app_obj.id, office_order_no="OO/2026/2", created_by_user_id=reg.id)
            session.add(comm)
            await session.flush()
            session.add(CommitteeMember(committee_id=comm.id, user_id=mem.id, role=CommitteeMemberRole.MEMBER))
            await session.commit()
            return app_obj.id, reg.email, mem.email, inst_user.email
    app_id, reg_email, mem_email, inst_email = asyncio.run(_setup())
    tok_reg = client.post("/api/auth/login", json={"email": reg_email, "password": "secret"}).json()["access_token"]
    tok_mem = client.post("/api/auth/login", json={"email": mem_email, "password": "secret"}).json()["access_token"]
    tok_inst = client.post("/api/auth/login", json={"email": inst_email, "password": "secret"}).json()["access_token"]

    payload = {
        "mode": "HYBRID",
        "date_time": "2026-06-15T14:00:00+00:00",
        "venue": "Room 101",
        "online_link": "https://meet.example.com/y",
        "agenda": "Review annexures.",
    }
    r = client.post(f"/api/applications/{app_id}/meetings", json=payload, headers={"Authorization": f"Bearer {tok_reg}"})
    assert r.status_code == 201
    assert r.json()["mode"] == "HYBRID"
    assert r.json()["agenda"] == "Review annexures."

    r_list = client.get(f"/api/applications/{app_id}/meetings", headers={"Authorization": f"Bearer {tok_mem}"})
    assert r_list.status_code == 200
    assert len(r_list.json()) == 1
    assert r_list.json()[0]["mode"] == "HYBRID"

    r_inst = client.get(f"/api/applications/{app_id}/meetings", headers={"Authorization": f"Bearer {tok_inst}"})
    assert r_inst.status_code == 200
    assert r_inst.json() == []
