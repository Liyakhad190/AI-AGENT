"""Scheduled job / reminder models."""
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


class ScheduledJob(Base, TimestampMixin):
    __tablename__ = "scheduled_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)  # reminder/call/check
    cron_expression: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    run_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_runs: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dedupe_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="scheduled_jobs")



