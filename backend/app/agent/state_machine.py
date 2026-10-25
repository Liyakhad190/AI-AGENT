"""Task execution state machine with guarded transitions."""
from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"


TERMINAL_STATES = {
    TaskStatus.COMPLETED,
    TaskStatus.FAILED,
    TaskStatus.CANCELLED,
    TaskStatus.TIMED_OUT,
    TaskStatus.PARTIALLY_COMPLETED,
}

# allowed transitions: from -> set of allowed to
ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {
        TaskStatus.PLANNING,
        TaskStatus.NEEDS_CLARIFICATION,
        TaskStatus.CANCELLED,
        TaskStatus.FAILED,
    },
    TaskStatus.PLANNING: {
        TaskStatus.AWAITING_APPROVAL,
        TaskStatus.RUNNING,
        TaskStatus.NEEDS_CLARIFICATION,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.AWAITING_APPROVAL: {
        TaskStatus.RUNNING,
        TaskStatus.CANCELLED,
        TaskStatus.FAILED,
        TaskStatus.PENDING,
    },
    TaskStatus.RUNNING: {
        TaskStatus.VERIFYING,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.TIMED_OUT,
        TaskStatus.PARTIALLY_COMPLETED,
    },
    TaskStatus.VERIFYING: {
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.PARTIALLY_COMPLETED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.NEEDS_CLARIFICATION: {
        TaskStatus.PENDING,
        TaskStatus.CANCELLED,
        TaskStatus.FAILED,
    },
}


def can_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    if from_status in TERMINAL_STATES:
        return False
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())
