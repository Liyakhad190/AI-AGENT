"""Concrete tool implementations registered with the tool registry."""
from __future__ import annotations

from typing import Any

from app.tools.registry import RiskLevel, ToolSpec, tool_registry


async def _email_search(arguments: dict[str, Any]) -> dict[str, Any]:
    # Requires an active Gmail connection; without it returns a clear limitation.
    return {
        "emails": [],
        "note": "Gmail integration not connected; no real emails retrieved.",
        "count": 0,
    }


async def _email_draft(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "draft_id": "draft-mock-001",
        "status": "saved",
        "note": "Draft saved (mock). Real draft requires connected Gmail account.",
    }


async def _email_send(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "sent": False,
        "note": "Send requires explicit user confirmation and connected Gmail.",
    }


async def _reminder_create(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "reminder_id": "reminder-mock-001",
        "status": "scheduled",
        "note": "Reminder scheduled (mock durable job).",
    }


async def _calendar_read(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "events": [],
        "note": "Calendar integration not connected.",
    }


async def _knowledge_answer(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "answer": f"[mock] I don't have a real knowledge source for: {arguments.get('query', '')}",
        "source": "mock",
    }


def register_default_tools() -> None:
    tool_registry.register(
        ToolSpec(
            name="email_search",
            description="Search authorized emails",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}},
                "required": ["query"],
            },
            required_permissions=["email.read"],
            risk=RiskLevel.LOW,
            timeout_seconds=15,
            idempotent=True,
            implementation=_email_search,
            verification_strategy="provider_confirmation",
            audit_required=True,
        )
    )
    tool_registry.register(
        ToolSpec(
            name="email_draft",
            description="Save an email draft",
            input_schema={
                "type": "object",
                "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"],
            },
            required_permissions=["email.read", "email.compose"],
            risk=RiskLevel.MEDIUM,
            timeout_seconds=15,
            idempotent=False,
            implementation=_email_draft,
            verification_strategy="provider_confirmation",
            audit_required=True,
        )
    )
    tool_registry.register(
        ToolSpec(
            name="email_send",
            description="Send an email (high risk - requires confirmation)",
            input_schema={
                "type": "object",
                "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"],
            },
            required_permissions=["email.send"],
            risk=RiskLevel.HIGH,
            timeout_seconds=20,
            idempotent=False,
            implementation=_email_send,
            verification_strategy="explicit_confirmation",
            audit_required=True,
        )
    )
    tool_registry.register(
        ToolSpec(
            name="reminder_create",
            description="Create a reminder",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}, "run_at": {"type": "string"}},
                "required": ["text"],
            },
            required_permissions=["reminder.write"],
            risk=RiskLevel.MEDIUM,
            timeout_seconds=10,
            idempotent=True,
            implementation=_reminder_create,
            verification_strategy="job_recorded",
            audit_required=True,
        )
    )
    tool_registry.register(
        ToolSpec(
            name="calendar_read",
            description="Read upcoming calendar events",
            input_schema={
                "type": "object",
                "properties": {"max_results": {"type": "integer"}},
                "required": [],
            },
            required_permissions=["calendar.read"],
            risk=RiskLevel.LOW,
            timeout_seconds=15,
            idempotent=True,
            implementation=_calendar_read,
            verification_strategy="provider_confirmation",
            audit_required=True,
        )
    )
    tool_registry.register(
        ToolSpec(
            name="knowledge_answer",
            description="Answer a general question",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            required_permissions=[],
            risk=RiskLevel.LOW,
            timeout_seconds=10,
            idempotent=True,
            implementation=_knowledge_answer,
            verification_strategy="none",
            audit_required=False,
        )
    )


register_default_tools()
