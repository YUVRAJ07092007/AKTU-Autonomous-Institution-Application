import os

from app.core.config import get_settings


def test_settings_test_env_allows_missing_jwt_secret(monkeypatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.setenv("ENV", "test")
    settings = get_settings()
    assert settings.env == "test"
    assert settings.jwt_secret


def test_upload_dir_created(tmp_path, monkeypatch) -> None:
    upload_dir = tmp_path / "uploads"
    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("JWT_SECRET", "dummy")
    settings = get_settings()
    assert settings.upload_dir == upload_dir
    assert upload_dir.exists()

