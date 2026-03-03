from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import AnyUrl, BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings

from app.core.debug_log import write_debug_log


class Settings(BaseSettings):
    env: str = Field("dev", alias="ENV")
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            f"sqlite+aiosqlite:///{os.getenv('AKTU_DB_PATH', 'aktu_autonomy.db')}",
        )
    )
    upload_dir: Path = Field(
        default_factory=lambda: Path(
            os.getenv(
                "UPLOAD_DIR",
                "/content/drive/MyDrive/AKTU_Autonomy_Uploads"
                if os.getenv("COLAB_GPU") or "COLAB_RELEASE_TAG" in os.environ
                else "./data/uploads",
            )
        )
    )
    base_url: AnyUrl | None = Field(default=None, alias="BASE_URL")
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    ngrok_public_url: AnyUrl | None = Field(default=None, alias="NGROK_PUBLIC_URL")
    max_upload_bytes: int = Field(20 * 1024 * 1024, alias="MAX_UPLOAD_BYTES")
    meeting_visible_to_institution: bool = Field(False, alias="MEETING_VISIBLE_TO_INSTITUTION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class RuntimeConfig(BaseModel):
    settings: Settings

    @property
    def is_test(self) -> bool:
        return self.settings.env.lower() == "test"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        settings = Settings()
    except ValidationError:
        env = os.getenv("ENV", "dev").lower()
        if env == "test":
            os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production")
            settings = Settings()
        else:
            raise

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    # region agent log
    write_debug_log(
        hypothesis_id="H1",
        location="backend/app/core/config.py:get_settings",
        message="Loaded settings",
        data={
            "env": settings.env,
            "database_url_prefix": str(settings.database_url)[:32],
            "upload_dir": str(settings.upload_dir),
        },
    )
    # endregion agent log
    return settings


def get_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(settings=get_settings())

