"""Unit tests for password hashing and JWT."""
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token


def test_password_roundtrip():
    h = hash_password("s3cret")
    assert h != "s3cret"
    assert verify_password("s3cret", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token("user-123")
    sub = decode_access_token(token)
    assert sub == "user-123"
    assert decode_access_token("invalid.token.value") is None
