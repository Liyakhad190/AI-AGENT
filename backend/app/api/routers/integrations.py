"""Integration connection routes."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_user
from app.database.models.integration import IntegrationConnection
from app.database.session import get_session

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("")
async def list_integrations(user=Depends(require_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(IntegrationConnection).where(IntegrationConnection.user_id == user.id)
    )
    conns = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "provider": c.provider,
            "provider_account_id": c.provider_account_id,
            "is_active": c.is_active,
            "authorized_at": c.authorized_at.isoformat() if c.authorized_at else None,
            "scopes": c.scopes,
        }
        for c in conns
    ]


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    import uuid

    conn = await session.get(IntegrationConnection, uuid.UUID(integration_id))
    if not conn or conn.user_id != user.id:
        raise HTTPException(status_code=404, detail="Integration not found")
    await session.delete(conn)
    await session.commit()
    return {"status": "disconnected"}
