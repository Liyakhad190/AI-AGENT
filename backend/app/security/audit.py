"""Audit logging helper."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.audit import AuditEvent


async def audit_event(
    session: AsyncSession,
    *,
    user_id: str | None = None,
    event_type: str,
    actor: str | None = None,
    target: str | None = None,
    outcome: str = "success",
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    import uuid

    uid: uuid.UUID | None = None
    if user_id:
        try:
            uid = uuid.UUID(user_id)
        except (ValueError, AttributeError):
            uid = None

    event = AuditEvent(
        user_id=uid,
        event_type=event_type,
        actor=actor,
        target=target,
        outcome=outcome,
        details=details or {},
        ip_address=ip_address,
    )
    session.add(event)
    await session.flush()
