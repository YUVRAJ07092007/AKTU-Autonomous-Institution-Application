import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.db.models import UserRole
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


def _register_user(email: str, password: str, role: UserRole) -> None:
    payload = {
        "email": email,
        "name": "Test User",
        "password": password,
        "role": role.value,
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201


def _login(email: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    return data["access_token"]


def test_auth_flow_register_login_me() -> None:
    _register_user("inst@example.com", "secret123", UserRole.INSTITUTION)
    token = _login("inst@example.com", "secret123")

    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "inst@example.com"
    assert body["role"] == UserRole.INSTITUTION.value


def test_login_invalid_credentials_forbidden() -> None:
    resp = client.post(
        "/api/auth/login",
        json={"email": "unknown@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401

