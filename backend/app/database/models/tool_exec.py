"""Tool execution audit models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    Boolean,
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


class ToolExecution(Base, TimestampMixin):
    __tablename__ = "tool_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    arguments: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="tool_executions")



