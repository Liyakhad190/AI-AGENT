"""Telephony provider abstraction interface."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CallDirection(str, Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class CallStatus(str, Enum):
    INITIATED = "initiated"
    CALLING = "calling"
    RINGING = "ringing"
    CONNECTED = "connected"
    AGENT_LISTENING = "agent_listening"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class CallResult:
    provider_call_id: str
    status: CallStatus
    to_number: str
    from_number: str
    direction: CallDirection
    cost_usd: Optional[float] = None
    error_message: Optional[str] = None
    raw: Optional[dict] = None


@dataclass
class CallStatusUpdate:
    provider_call_id: str
    status: CallStatus
    duration_seconds: Optional[int] = None
    answered_at: Optional[str] = None
    ended_at: Optional[str] = None
    cost_usd: Optional[float] = None
    error_message: Optional[str] = None
    raw: Optional[dict] = None


class TelephonyProvider:
    """Abstract telephony provider interface."""

    async def initiate_call(
        self,
        to_number: str,
        from_number: str,
        webhook_url: str,
        status_callback_url: str,
        max_duration_seconds: int,
    ) -> CallResult:
        raise NotImplementedError

    async def terminate_call(self, provider_call_id: str) -> bool:
        raise NotImplementedError

    async def get_call_status(self, provider_call_id: str) -> CallStatusUpdate:
        raise NotImplementedError

    def verify_webhook_signature(self, body: bytes, headers: dict) -> bool:
        raise NotImplementedError

    def parse_webhook(self, body: bytes, headers: dict) -> Optional[CallStatusUpdate]:
        raise NotImplementedError
