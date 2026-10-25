"""Mock telephony provider for development (no real calls placed)."""
from __future__ import annotations

import asyncio
import random
from typing import Optional

from app.config.settings import settings
from app.telephony.base import (
    CallDirection,
    CallResult,
    CallStatus,
    CallStatusUpdate,
    TelephonyProvider,
)


class MockTelephonyProvider(TelephonyProvider):
    _calls: dict[str, CallStatusUpdate] = {}

    async def initiate_call(
        self,
        to_number: str,
        from_number: str,
        webhook_url: str,
        status_callback_url: str,
        max_duration_seconds: int,
    ) -> CallResult:
        provider_call_id = f"mock-call-{random.randint(100000, 999999)}"
        # simulate ringing then connected after a short delay
        await asyncio.sleep(0.2)
        update = CallStatusUpdate(
            provider_call_id=provider_call_id,
            status=CallStatus.RINGING,
            raw={"mock": True},
        )
        self._calls[provider_call_id] = update
        return CallResult(
            provider_call_id=provider_call_id,
            status=CallStatus.RINGING,
            to_number=to_number,
            from_number=from_number or settings.telephony_phone_number or "+1234567890",
            direction=CallDirection.OUTBOUND,
            raw={"mock": True},
        )

    async def terminate_call(self, provider_call_id: str) -> bool:
        if provider_call_id in self._calls:
            self._calls[provider_call_id].status = CallStatus.COMPLETED
            return True
        return False

    async def get_call_status(self, provider_call_id: str) -> CallStatusUpdate:
        return self._calls.get(
            provider_call_id,
            CallStatusUpdate(
                provider_call_id=provider_call_id,
                status=CallStatus.FAILED,
                error_message="unknown call",
            ),
        )

    def verify_webhook_signature(self, body: bytes, headers: dict) -> bool:
        return True

    def parse_webhook(self, body: bytes, headers: dict) -> Optional[CallStatusUpdate]:
        return None
