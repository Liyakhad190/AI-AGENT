"""Task execution engine models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    JSON,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("call_sessions.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="PENDING")
    plan: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    required_permissions: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    execution_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    timeout_seconds: Mapped[int] = mapped_column(default=300, nullable=False)
    cancelled: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tasks")
    call_session: Mapped[Optional["CallSession"]] = relationship(
        "CallSession", back_populates="tasks"
    )
    steps: Mapped[list["TaskStep"]] = relationship(
        "TaskStep", back_populates="task", cascade="all, delete-orphan"
    )
    approvals: Mapped[list["TaskApproval"]] = relationship(
        "TaskApproval", back_populates="task", cascade="all, delete-orphan"
    )
    tool_executions: Mapped[list["ToolExecution"]] = relationship(
        "ToolExecution", back_populates="task", cascade="all, delete-orphan"
    )


class TaskStep(Base, TimestampMixin):
    __tablename__ = "task_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    arguments: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    task: Mapped["Task"] = relationship("Task", back_populates="steps")


class TaskApproval(Base, TimestampMixin):
    __tablename__ = "task_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(256), nullable=False)
    target: Mapped[str] = mapped_column(String(512), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    decided_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="approvals")



