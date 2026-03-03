from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.core.config import get_settings


def test_password_hash_roundtrip() -> None:
    password = "S3cret!"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_encode_decode_roundtrip(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret")
    settings = get_settings()
    token = create_access_token("user-123", extra_claims={"roles": ["TEST"]})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["roles"] == ["TEST"]
