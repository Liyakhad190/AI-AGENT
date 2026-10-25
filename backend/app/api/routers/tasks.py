"""Task management routes (create, list, get, cancel, approve)."""
from __future__ import annotations

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import Orchestrator
from app.agent.state_machine import TaskStatus, can_transition
from app.api.deps import RateLimitDep
from app.auth.dependencies import require_user
from app.config.settings import settings
from app.database.models.audit import AuditEvent
from app.database.models.task import Task, TaskApproval
from app.database.models.tool_exec import ToolExecution
from app.database.session import get_session
from app.security.audit import audit_event

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/")
async def create_task(
    payload: dict[str, Any],
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
    _rate: None = Depends(RateLimitDep(limit=50, window_seconds=60)),
):
    goal = payload.get("goal")
    if not goal:
        raise HTTPException(status_code=400, detail="goal required")
    orchestrator = Orchestrator()
    task = await orchestrator.create_task(
        user_id=str(user.id),
        goal=goal,
        conversation_id=payload.get("conversation_id"),
        idempotency_key=payload.get("idempotency_key"),
    )
    return {"id": str(task.id), "status": task.status, "goal": task.goal}


@router.get("/")
async def list_tasks(
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
    status: str | None = Query(None),
):
    stmt = select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())
    if status:
        stmt = stmt.where(Task.status == status)
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "goal": t.goal,
            "status": t.status,
            "approval_status": t.approval_status,
            "created_at": t.created_at.isoformat(),
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "result_summary": t.result_summary,
            "error_code": t.error_code,
        }
        for t in tasks
    ]


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(Task, uuid.UUID(task_id))
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    steps = [
        {
            "id": str(s.id),
            "tool_name": s.tool_name,
            "status": s.status,
            "result": s.result,
            "error_code": s.error_code,
        }
        for s in task.steps
    ]
    return {
        "id": str(task.id),
        "goal": task.goal,
        "status": task.status,
        "plan": task.plan,
        "approval_status": task.approval_status,
        "execution_attempts": task.execution_attempts,
        "result_summary": task.result_summary,
        "error_code": task.error_code,
        "steps": steps,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(Task, uuid.UUID(task_id))
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    orchestrator = Orchestrator()
    await orchestrator.transition(task, TaskStatus.CANCELLED, session)
    task.cancelled = True
    await session.commit()
    await audit_event(
        session,
        user_id=str(user.id),
        event_type="task.cancelled",
        target=str(task.id),
        outcome="success",
    )
    return {"id": str(task.id), "status": task.status}


@router.post("/{task_id}/approve")
async def approve_task(
    task_id: str,
    payload: dict[str, Any],
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(Task, uuid.UUID(task_id))
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.approval_status != "PENDING":
        raise HTTPException(status_code=400, detail="Task not awaiting approval")
    task.approval_status = "APPROVED"
    decision = payload.get("decision", "approved")
    if decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be approved or rejected")
    task.approval_status = "APPROVED" if decision == "approved" else "REJECTED"
    approval = TaskApproval(
        task_id=task.id,
        action=payload.get("action", "execute"),
        target=payload.get("target", task.goal),
        reason=payload.get("reason"),
        status=task.approval_status,
        decided_at=datetime.datetime.now(datetime.timezone.utc),
        decided_by=str(user.id),
    )
    session.add(approval)
    await session.commit()
    return {
        "id": str(task.id),
        "approval_status": task.approval_status,
    }


@router.get("/{task_id}/executions")
async def task_executions(
    task_id: str,
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(Task, uuid.UUID(task_id))
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return [
        {
            "id": str(e.id),
            "tool_name": e.tool_name,
            "status": e.status,
            "result": e.result,
            "error_code": e.error_code,
            "verified": e.verified,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in task.tool_executions
    ]


@router.get("/audit")
async def audit_logs(
    user=Depends(require_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, le=200),
):
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.user_id == user.id)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "actor": e.actor,
            "target": e.target,
            "outcome": e.outcome,
            "details": e.details,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
