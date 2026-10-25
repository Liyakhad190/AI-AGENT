"""Memory / personalization models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class MemoryRecord(Base, TimestampMixin):
    __tablename__ = "memory_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(256), nullable=False)
    value: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_explicit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="memory_records")



