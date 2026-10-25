"""Unit tests for the agent orchestrator planning logic."""
import uuid

import pytest

from app.agent.orchestrator import Orchestrator
from app.agent.state_machine import TaskStatus


@pytest.mark.asyncio
async def test_create_task_defaults_to_pending():
    orch = Orchestrator()
    task = await orch.create_task(
        user_id=str(uuid.uuid4()), goal="Check my email"
    )
    assert task.status == TaskStatus.PENDING.value
    assert task.approval_status == "PENDING"
    assert task.execution_attempts == 0


@pytest.mark.asyncio
async def test_planner_maps_email_to_email_search():
    orch = Orchestrator()
    plan = await orch.plan_task(
        None, goal="Check my email for important messages", available_tools=[]
    )
    tool_names = [s["tool"] for s in plan.steps]
    assert "email_search" in tool_names
    assert "email.read" in plan.required_permissions


@pytest.mark.asyncio
async def test_planner_maps_reminder():
    orch = Orchestrator()
    plan = await orch.plan_task(None, goal="Remind me tomorrow at 9 AM", available_tools=[])
    assert any(s["tool"] == "reminder_create" for s in plan.steps)
    assert "reminder.write" in plan.required_permissions


@pytest.mark.asyncio
async def test_planner_maps_send_to_high_risk():
    orch = Orchestrator()
    plan = await orch.plan_task(None, goal="Send an email to alice@example.com", available_tools=[])
    assert plan.risk_level.value == "high"
    assert "email.send" in plan.required_permissions
