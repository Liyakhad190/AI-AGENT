"""Call session and conversation message models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class CallSession(Base, TimestampMixin):
    __tablename__ = "call_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_call_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # outbound/inbound
    from_number: Mapped[str] = mapped_column(String(32), nullable=False)
    to_number: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    provider_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    max_duration_seconds: Mapped[int] = mapped_column(default=600, nullable=False)
    recording_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="call_sessions")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="call_session", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="call_session", cascade="all, delete-orphan"
    )


class ConversationMessage(Base, TimestampMixin):
    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    call_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("call_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # user/assistant/system/tool
    content: Mapped[str] = mapped_column(Text, nullable=False)
    transcript_confidence: Mapped[Optional[float]] = mapped_column(nullable=True)
    audio_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    call_session: Mapped["CallSession"] = relationship(
        "CallSession", back_populates="messages"
    )
