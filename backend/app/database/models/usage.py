"""Usage / cost tracking models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    JSON,
    ForeignKey,
    Float,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class UsageRecord(Base, TimestampMixin):
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    record_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)



