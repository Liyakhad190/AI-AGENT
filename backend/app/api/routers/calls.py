"""Call control routes (outbound initiation, termination, status, webhooks)."""
from __future__ import annotations

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RateLimitDep
from app.auth.dependencies import require_user
from app.config.settings import settings
from app.database.models.call import CallSession
from app.database.models.user import User
from app.database.session import get_session
from app.security.audit import audit_event
from app.telephony.adapter import get_telephony_provider
from app.telephony.base import CallDirection, CallStatus

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/initiate")
async def initiate_call(
    payload: dict[str, Any],
    request: Request,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
    _rate: None = Depends(RateLimitDep(limit=settings.max_daily_calls)),
):
    to_number = payload.get("to_number") or settings.verified_destination_number
    from_number = payload.get("from_number") or settings.telephony_phone_number
    if not to_number:
        raise HTTPException(status_code=400, detail="No destination number configured")

    provider = get_telephony_provider()
    webhook_url = f"{settings.public_base_url}/api/v1/calls/webhook"
    status_callback_url = f"{settings.public_base_url}/api/v1/calls/webhook"

    try:
        result = await provider.initiate_call(
            to_number=to_number,
            from_number=from_number or "+1234567890",
            webhook_url=webhook_url,
            status_callback_url=status_callback_url,
            max_duration_seconds=settings.max_call_duration_seconds,
        )
    except Exception as exc:
        await audit_event(
            session,
            user_id=str(user.id),
            event_type="call.initiate.failed",
            target=to_number,
            outcome="failure",
            details={"error": str(exc)},
        )
        await session.commit()
        raise HTTPException(status_code=502, detail=f"Call initiation failed: {exc}")

    call = CallSession(
        user_id=user.id,
        provider_call_id=result.provider_call_id,
        direction=CallDirection.OUTBOUND.value,
        from_number=result.from_number,
        to_number=result.to_number,
        status=result.status.value,
        provider_status=result.status.value,
        max_duration_seconds=settings.max_call_duration_seconds,
        error_message=result.error_message,
    )
    session.add(call)
    await session.flush()
    await session.refresh(call)
    await audit_event(
        session,
        user_id=str(user.id),
        event_type="call.initiated",
        target=str(call.id),
        outcome="success",
        details={"provider_call_id": result.provider_call_id, "to": to_number},
    )
    await session.commit()
    return {
        "call_id": str(call.id),
        "provider_call_id": result.provider_call_id,
        "status": result.status.value,
        "to_number": result.to_number,
        "from_number": result.from_number,
    }


@router.post("/{call_id}/terminate")
async def terminate_call(
    call_id: str,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    call = await session.get(CallSession, uuid.UUID(call_id))
    if not call or call.user_id != user.id:
        raise HTTPException(status_code=404, detail="Call not found")
    provider = get_telephony_provider()
    ok = await provider.terminate_call(call.provider_call_id or "")
    call.status = CallStatus.COMPLETED.value if ok else call.status
    call.ended_at = datetime.datetime.now(datetime.timezone.utc)
    await session.commit()
    await audit_event(
        session,
        user_id=str(user.id),
        event_type="call.terminated",
        target=str(call.id),
        outcome="success" if ok else "failure",
    )
    return {"call_id": str(call.id), "terminated": ok, "status": call.status}


@router.get("/{call_id}/status")
async def call_status(
    call_id: str,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    call = await session.get(CallSession, uuid.UUID(call_id))
    if not call or call.user_id != user.id:
        raise HTTPException(status_code=404, detail="Call not found")
    if call.provider_call_id:
        provider = get_telephony_provider()
        update = await provider.get_call_status(call.provider_call_id)
        call.provider_status = update.status.value
        if update.duration_seconds is not None:
            call.duration_seconds = update.duration_seconds
        if update.ended_at:
            ended = update.ended_at
            if isinstance(ended, str):
                try:
                    ended = datetime.datetime.fromisoformat(ended)
                except ValueError:
                    ended = None
            call.ended_at = ended
        if update.status != CallStatus.FAILED:
            call.status = update.status.value
        if update.error_message:
            call.error_message = update.error_message
        await session.commit()
    return {
        "call_id": str(call.id),
        "status": call.status,
        "provider_status": call.provider_status,
        "duration_seconds": call.duration_seconds,
        "error_message": call.error_message,
    }


@router.post("/webhook")
async def telephony_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    provider = get_telephony_provider()
    body = await request.body()
    headers = dict(request.headers)
    if not provider.verify_webhook_signature(body, headers):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    update = provider.parse_webhook(body, headers)
    if not update:
        return {"received": True}
    result = await session.execute(
        select(CallSession).where(CallSession.provider_call_id == update.provider_call_id)
    )
    call = result.scalar_one_or_none()
    if not call:
        return {"received": True, "note": "unknown call id"}
    call.provider_status = update.status.value
    call.status = update.status.value
    if update.duration_seconds is not None:
        call.duration_seconds = update.duration_seconds
    if update.error_message:
        call.error_message = update.error_message
    await session.commit()
    await audit_event(
        session,
        user_id=str(call.user_id),
        event_type="call.webhook",
        target=str(call.id),
        outcome="success",
        details={"status": update.status.value},
    )
    return {"received": True, "call_id": str(call.id), "status": update.status.value}
