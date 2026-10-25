"""Unit tests for the task state machine."""
from app.agent.state_machine import TaskStatus, can_transition, TERMINAL_STATES


def test_pending_to_planning_allowed():
    assert can_transition(TaskStatus.PENDING, TaskStatus.PLANNING)


def test_planning_to_running_allowed():
    assert can_transition(TaskStatus.PLANNING, TaskStatus.RUNNING)


def test_running_to_verifying_allowed():
    assert can_transition(TaskStatus.RUNNING, TaskStatus.VERIFYING)


def test_verifying_to_completed_allowed():
    assert can_transition(TaskStatus.VERIFYING, TaskStatus.COMPLETED)


def test_completed_is_terminal():
    assert TaskStatus.COMPLETED in TERMINAL_STATES
    assert not can_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING)


def test_running_to_planning_not_allowed():
    assert not can_transition(TaskStatus.RUNNING, TaskStatus.PLANNING)


def test_completed_to_anything_not_allowed():
    for s in TaskStatus:
        if s == TaskStatus.COMPLETED:
            continue
        assert not can_transition(TaskStatus.COMPLETED, s)


def test_needs_clarification_back_to_pending():
    assert can_transition(TaskStatus.NEEDS_CLARIFICATION, TaskStatus.PENDING)
