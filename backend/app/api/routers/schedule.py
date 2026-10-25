"""Scheduled call and reminder management routes."""
from __future__ import annotations

import datetime
import uuid
from typing import Any

from dateutil import parser as date_parser
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import Orchestrator
from app.auth.dependencies import require_user
from app.database.models.call import CallSession
from app.database.models.scheduler import ScheduledJob
from app.database.models.user import User
from app.database.session import get_session
from app.telephony.adapter import get_telephony_provider
from app.telephony.base import CallDirection

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.post("/")
async def create_scheduled_reminder(
    payload: dict[str, Any],
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    """Schedule a voice call for a reminder or task at a specific day/time."""
    to_number = payload.get("to_number") or payload.get("phone_number")
    reminder_text = payload.get("reminder_text") or payload.get("prompt") or payload.get("goal")
    scheduled_time_str = payload.get("scheduled_time") or payload.get("run_at")

    if not to_number:
        raise HTTPException(status_code=400, detail="Phone number is required")
    if not reminder_text:
        raise HTTPException(status_code=400, detail="Reminder / task text is required")
    if not scheduled_time_str:
        raise HTTPException(status_code=400, detail="Scheduled date/time is required")

    try:
        run_at = date_parser.parse(str(scheduled_time_str))
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=datetime.timezone.utc)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {exc}")

    job = ScheduledJob(
        user_id=user.id,
        job_type="reminder_call",
        run_at=run_at,
        next_run_at=run_at,
        timezone="UTC",
        is_active=True,
        payload={
            "to_number": to_number,
            "reminder_text": reminder_text,
            "instructions": payload.get("instructions", ""),
        },
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    return {
        "id": str(job.id),
        "to_number": to_number,
        "reminder_text": reminder_text,
        "run_at": job.run_at.isoformat() if job.run_at else None,
        "is_active": job.is_active,
    }


@router.get("/")
async def list_scheduled_jobs(
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    """List all scheduled calls and reminders for the current user."""
    stmt = (
        select(ScheduledJob)
        .where(ScheduledJob.user_id == user.id)
        .order_by(ScheduledJob.run_at.asc())
    )
    res = await session.execute(stmt)
    jobs = res.scalars().all()

    return [
        {
            "id": str(j.id),
            "job_type": j.job_type,
            "run_at": j.run_at.isoformat() if j.run_at else None,
            "is_active": j.is_active,
            "run_count": j.run_count,
            "last_run_at": j.last_run_at.isoformat() if j.last_run_at else None,
            "payload": j.payload or {},
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


@router.delete("/{job_id}")
async def cancel_scheduled_job(
    job_id: str,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    """Cancel a scheduled reminder call."""
    job = await session.get(ScheduledJob, uuid.UUID(job_id))
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    job.is_active = False
    await session.commit()
    return {"status": "cancelled", "id": job_id}


@router.post("/{job_id}/trigger")
async def trigger_scheduled_job_now(
    job_id: str,
    user: User = Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    """Immediately trigger a scheduled reminder call and execute its task."""
    job = await session.get(ScheduledJob, uuid.UUID(job_id))
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    payload = job.payload or {}
    to_number = payload.get("to_number", "+1234567890")
    reminder_text = payload.get("reminder_text", "Reminder from AI Voice Agent")

    # 1. Execute task in orchestrator
    orchestrator = Orchestrator()
    task = await orchestrator.create_task(
        user_id=str(user.id),
        goal=f"[Voice Reminder] {reminder_text}",
    )

    # 2. Initiate outbound call
    provider = get_telephony_provider()
    call_result = await provider.initiate_call(
        to_number=to_number,
        from_number="+15550192834",
        webhook_url="http://localhost:8000/api/v1/calls/webhook",
        status_callback_url="http://localhost:8000/api/v1/calls/webhook",
        max_duration_seconds=300,
    )

    # Record Call Session
    call = CallSession(
        user_id=user.id,
        provider_call_id=call_result.provider_call_id,
        direction=CallDirection.OUTBOUND.value,
        from_number=call_result.from_number,
        to_number=to_number,
        status=call_result.status.value,
        provider_status=call_result.status.value,
        max_duration_seconds=300,
    )
    session.add(call)

    # Mark job executed
    job.is_active = False
    job.run_count += 1
    job.last_run_at = datetime.datetime.now(datetime.timezone.utc)
    job.task_id = task.id
    await session.commit()

    return {
        "status": "triggered",
        "call_id": str(call.id),
        "task_id": str(task.id),
        "provider_call_id": call_result.provider_call_id,
        "to_number": to_number,
    }
