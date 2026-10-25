"""JWT access token creation and verification."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Union

import uuid
from jose import JWTError, jwt

from app.config.settings import settings


def create_access_token(
    subject: Union[str, uuid.UUID],
    expires_delta: timedelta | None = None,
) -> str:
    to_encode: dict[str, Any] = {"sub": str(subject)}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.app_secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, settings.app_secret_key, algorithms=[settings.algorithm]
        )
        sub: str | None = payload.get("sub")
        return sub
    except JWTError:
        return None
