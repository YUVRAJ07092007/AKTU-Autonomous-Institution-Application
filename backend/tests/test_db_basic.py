import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.db.base import Base
from app.db.models import (
    Application,
    Document,
    DocumentType,
    Institution,
    User,
    UserRole,
)


async def _run() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        user = User(
            email="inst@example.com",
            name="Inst Admin",
            hashed_password="hashed",
            role=UserRole.INSTITUTION,
        )
        inst = Institution(
            name="Test College",
            code="TC001",
            address="Somewhere",
            district="Lucknow",
            contact_email="contact@test.example",
            contact_phone="1234567890",
        )
        session.add_all([user, inst])
        await session.flush()

        app = Application(
            institution_id=inst.id,
            status="DRAFT",
            requested_from_year=2026,
            programmes_json={"programmes": []},
            ugc_policy_mode="A",
        )
        session.add(app)
        await session.flush()

        doc = Document(
            application_id=app.id,
            doc_type=DocumentType.APPLICATION_FORM,
            filename="form.pdf",
            storage_path="/tmp/form.pdf",
            uploaded_by=user.id,
            uploaded_at=datetime.utcnow(),
            version=1,
            sha256="0" * 64,
        )
        session.add(doc)
        await session.commit()

        result = await session.execute(select(Application).where(Application.id == app.id))
        fetched = result.scalar_one()
        assert fetched.institution_id == inst.id


def test_basic_crud() -> None:
    asyncio.run(_run())

