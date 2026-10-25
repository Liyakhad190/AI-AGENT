"""FastAPI dependency for current authenticated user."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token
from app.config.settings import settings
from app.database.models.user import User
from app.database.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    session: AsyncSession = Depends(get_session),
) -> User | None:
    if not token:
        if settings.application_env == "development":
            from sqlalchemy import select
            user = await session.scalar(select(User).where(User.is_active == True))
            if user:
                return user
        return None
    user_id_str = decode_access_token(token)
    if not user_id_str:
        return None
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        return None
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user


async def require_user(
    user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
