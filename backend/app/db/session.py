from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.debug_log import write_debug_log


settings = get_settings()
engine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        # region agent log
        write_debug_log(
            hypothesis_id="H2",
            location="backend/app/db/session.py:get_db",
            message="Created DB session",
            data={"database_url_prefix": str(settings.database_url)[:32]},
        )
        # endregion agent log
        yield session

