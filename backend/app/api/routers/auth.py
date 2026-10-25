"""Authentication routes (register, login, me, Google OAuth)."""
from __future__ import annotations

import datetime
from typing import Any

from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_user
from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.config.settings import settings
from app.database.models.integration import IntegrationConnection
from app.database.models.user import User, UserSettings
from app.database.session import AsyncSessionLocal, get_session
from app.security.audit import audit_event

router = APIRouter(tags=["auth"])


@router.post("/register")
async def register(payload: dict[str, Any], session: AsyncSession = Depends(get_session)):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")
    existing = await session.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="email already registered")
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=payload.get("full_name"),
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    session.add(UserSettings(user_id=user.id))
    await session.commit()
    await audit_event(
        session,
        user_id=str(user.id),
        event_type="user.registered",
        target=str(user.id),
        outcome="success",
    )
    return {"id": str(user.id), "email": user.email}


@router.post("/login")
async def login(payload: dict[str, Any], session: AsyncSession = Depends(get_session)):
    email = payload.get("email")
    password = payload.get("password")
    user = await session.scalar(select(User).where(User.email == email)) if email else None
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(user.id, expires_delta=datetime.timedelta(minutes=settings.access_token_expire_minutes))
    user.last_login_at = datetime.datetime.now(datetime.timezone.utc)
    await session.commit()
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def me(user: User = Depends(require_user), session: AsyncSession = Depends(get_session)):
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "time_zone": user.time_zone,
        "locale": user.locale,
    }


def _google_scopes() -> str:
    return " ".join(
        [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
        ]
    )


@router.get("/google/oauth/authorize")
async def google_authorize(user: User = Depends(require_user)):
    if not settings.google_oauth_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    client = AsyncOAuth2Client(
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
        redirect_uri=settings.google_oauth_redirect_uri
        or f"{settings.public_base_url}/auth/google/oauth/callback",
        scope=_google_scopes(),
    )
    uri, state = client.create_authorization_url(
        "https://accounts.google.com/o/oauth2/v2/auth"
    )
    return {"authorize_url": uri, "state": state}


@router.get("/google/oauth/callback")
async def google_callback(
    code: str = Query(...),
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    if not settings.google_oauth_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    client = AsyncOAuth2Client(
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
        redirect_uri=settings.google_oauth_redirect_uri
        or f"{settings.public_base_url}/auth/google/oauth/callback",
    )
    token = await client.fetch_token(
        "https://oauth2.googleapis.com/token",
        code=code,
    )
    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")
    expires_at = token.get("expires_at")
    conn = IntegrationConnection(
        user_id=user.id,
        provider="google",
        provider_account_id="google",
        access_token_encrypted=access_token,
        refresh_token_encrypted=refresh_token,
        token_expires_at=(
            datetime.datetime.fromtimestamp(expires_at, tz=datetime.timezone.utc)
            if expires_at
            else None
        ),
        is_active=True,
    )
    session.add(conn)
    await session.commit()
    return {"status": "connected", "provider": "google"}
