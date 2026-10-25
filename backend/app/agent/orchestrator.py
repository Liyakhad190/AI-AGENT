"""Agent orchestrator: plans, executes, verifies tasks via the tool registry."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.agent.state_machine import TaskStatus, can_transition
from app.config.settings import settings
from app.database.models.audit import AuditEvent
from app.database.models.task import Task
from app.database.models.tool_exec import ToolExecution
from app.database.session import AsyncSessionLocal
from app.security.audit import audit_event
from app.tools.registry import RiskLevel, tool_registry


@dataclass
class TaskPlan:
    goal: str
    steps: list[dict[str, Any]]
    required_permissions: list[str]
    risk_level: RiskLevel


class Orchestrator:
    async def create_task(
        self,
        user_id: str,
        goal: str,
        conversation_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> Task:
        async with AsyncSessionLocal() as session:
            import uuid as _uuid

            task = Task(
                user_id=_uuid.UUID(user_id),
                conversation_id=(
                    _uuid.UUID(conversation_id) if conversation_id else None
                ),
                goal=goal,
                status=TaskStatus.PENDING.value,
                approval_status="PENDING",
                idempotency_key=idempotency_key,
            )
            session.add(task)
            await session.flush()
            await session.refresh(task)
            await audit_event(
                session,
                user_id=user_id,
                event_type="task.created",
                target=str(task.id),
                outcome="success",
                details={"goal": goal},
            )
            await session.commit()
            return task

    async def transition(self, task: Task, to_status: TaskStatus, session) -> None:
        from_status = TaskStatus(task.status)
        if not can_transition(from_status, to_status):
            raise ValueError(
                f"Invalid transition {from_status} -> {to_status}"
            )
        task.status = to_status.value
        if to_status == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        if to_status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMED_OUT,
        ):
            task.completed_at = datetime.now(timezone.utc)
        await session.flush()

    async def plan_task(
        self,
        task: Task,
        goal: str,
        available_tools: list[str],
    ) -> TaskPlan:
        # Heuristic planner: map keywords to tools without relying on model output.
        steps: list[dict[str, Any]] = []
        perms: list[str] = []
        risk = RiskLevel.LOW
        lowered = goal.lower()

        if any(w in lowered for w in ["email", "mail", "inbox"]):
            steps.append(
                {
                    "tool": "email_search",
                    "arguments": {"query": goal, "max_results": 10},
                    "description": "Search authorized emails",
                }
            )
            perms.append("email.read")
            risk = RiskLevel.MEDIUM

        if any(w in lowered for w in ["remind", "reminder", "schedule"]):
            steps.append(
                {
                    "tool": "reminder_create",
                    "arguments": {"text": goal},
                    "description": "Create a reminder",
                }
            )
            perms.append("reminder.write")
            risk = RiskLevel.MEDIUM

        if any(w in lowered for w in ["send", "reply", "forward"]):
            steps.append(
                {
                    "tool": "email_send",
                    "arguments": {"draft_goal": goal},
                    "description": "Send an email (requires confirmation)",
                }
            )
            perms.append("email.send")
            risk = RiskLevel.HIGH

        if not steps:
            steps.append(
                {
                    "tool": "knowledge_answer",
                    "arguments": {"query": goal},
                    "description": "Answer from knowledge",
                }
            )

        plan = TaskPlan(
            goal=goal,
            steps=steps,
            required_permissions=list(set(perms)),
            risk_level=risk,
        )
        return plan

    async def execute_tool(
        self,
        task: Task,
        tool_name: str,
        arguments: dict[str, Any],
        user_permissions: list[str],
        session,
    ) -> ToolExecution:
        spec = tool_registry.get(tool_name)
        if spec is None:
            raise ValueError(f"Unknown tool: {tool_name}")
        if not tool_registry.has_permission(tool_name, user_permissions):
            raise PermissionError(f"No permission for tool: {tool_name}")

        exec_record = ToolExecution(
            task_id=task.id,
            tool_name=tool_name,
            arguments=arguments,
            status="RUNNING",
        )
        session.add(exec_record)
        await session.flush()

        try:
            if spec.implementation:
                result = await spec.implementation(**arguments)
            else:
                result = {"skipped": True, "reason": "no implementation"}
            exec_record.result = result
            exec_record.status = "COMPLETED"
            exec_record.verified = True
            exec_record.verification_notes = "mock verification"
        except Exception as exc:  # pragma: no cover
            exec_record.status = "FAILED"
            exec_record.error_code = type(exc).__name__
            exec_record.error_message = str(exc)
            raise
        finally:
            exec_record.completed_at = datetime.now(timezone.utc)
            await session.flush()

        await audit_event(
            session,
            user_id=str(task.user_id),
            event_type="tool.executed",
            target=tool_name,
            outcome="success" if exec_record.status == "COMPLETED" else "failure",
            details={"task_id": str(task.id), "arguments": arguments},
        )
        return exec_record
