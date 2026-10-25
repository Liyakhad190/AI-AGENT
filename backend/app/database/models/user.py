"""User and authentication models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_zone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(16), default="en-US", nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    settings: Mapped["UserSettings"] = relationship(
        "UserSettings", back_populates="user", cascade="all, delete-orphan"
    )
    phone_numbers: Mapped[list["VerifiedPhoneNumber"]] = relationship(
        "VerifiedPhoneNumber", back_populates="user", cascade="all, delete-orphan"
    )
    integrations: Mapped[list["IntegrationConnection"]] = relationship(
        "IntegrationConnection", back_populates="user", cascade="all, delete-orphan"
    )
    call_sessions: Mapped[list["CallSession"]] = relationship(
        "CallSession", back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="user", cascade="all, delete-orphan"
    )
    scheduled_jobs: Mapped[list["ScheduledJob"]] = relationship(
        "ScheduledJob", back_populates="user", cascade="all, delete-orphan"
    )
    memory_records: Mapped[list["MemoryRecord"]] = relationship(
        "MemoryRecord", back_populates="user", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    assistant_name: Mapped[str] = mapped_column(String(100), default="Assistant", nullable=False)
    assistant_voice: Mapped[str] = mapped_column(String(100), default="alloy", nullable=False)
    greeting: Mapped[str] = mapped_column(
        String(500),
        default="Hello! I'm your personal AI assistant. I'm ready to help. What would you like me to do?",
        nullable=False,
    )
    max_call_duration_seconds: Mapped[int] = mapped_column(default=600, nullable=False)
    allow_inbound_calls: Mapped[bool] = mapped_column(default=False, nullable=False)
    long_term_memory_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    confirmation_required_high_risk: Mapped[bool] = mapped_column(default=True, nullable=False)
    confirmation_required_medium_risk: Mapped[bool] = mapped_column(default=True, nullable=False)
    retain_transcripts: Mapped[bool] = mapped_column(default=True, nullable=False)
    retain_recordings: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="settings")


class VerifiedPhoneNumber(Base, TimestampMixin):
    __tablename__ = "verified_phone_numbers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    e164: Mapped[str] = mapped_column(String(32), nullable=False)
    country_code: Mapped[str] = mapped_column(String(8), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_code: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    verification_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    authorized_for_outbound: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    authorized_for_inbound: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="phone_numbers")
