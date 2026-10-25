"""Twilio Programmable Voice provider implementation."""
from __future__ import annotations

import hashlib
import hmac
import urllib.parse
from typing import Optional

from app.config.settings import settings
from app.telephony.base import (
    CallDirection,
    CallResult,
    CallStatus,
    CallStatusUpdate,
    TelephonyProvider,
)


def _map_twilio_status(twilio_status: str) -> CallStatus:
    mapping = {
        "queued": CallStatus.CALLING,
        "initiated": CallStatus.CALLING,
        "ringing": CallStatus.RINGING,
        "in-progress": CallStatus.CONNECTED,
        "completed": CallStatus.COMPLETED,
        "busy": CallStatus.BUSY,
        "no-answer": CallStatus.NO_ANSWER,
        "failed": CallStatus.FAILED,
        "canceled": CallStatus.CANCELLED,
        "rejected": CallStatus.REJECTED,
    }
    return mapping.get(twilio_status, CallStatus.FAILED)


class TwilioTelephonyProvider(TelephonyProvider):
    def __init__(self) -> None:
        try:
            from twilio.rest import Client as TwilioClient
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "twilio package is required for the twilio provider"
            ) from exc

        self._account_id = settings.telephony_account_id
        self._auth_secret = settings.telephony_auth_secret
        self._from_number = settings.telephony_phone_number
        self._client = None
        if self._account_id and self._auth_secret:
            self._client = TwilioClient(self._account_id, self._auth_secret)

    async def initiate_call(
        self,
        to_number: str,
        from_number: str,
        webhook_url: str,
        status_callback_url: str,
        max_duration_seconds: int,
    ) -> CallResult:
        if not self._client:
            raise RuntimeError("Twilio client not configured (missing credentials)")
        if not self._from_number:
            raise RuntimeError("Twilio phone number not configured")
        call = self._client.calls.create(
            to=to_number,
            from_=self._from_number,
            url=webhook_url,
            status_callback=status_callback_url,
            status_callback_event=[
                "initiated",
                "ringing",
                "answered",
                "completed",
            ],
            status_callback_method="POST",
            timeout=max_duration_seconds,
        )
        return CallResult(
            provider_call_id=call.sid,
            status=_map_twilio_status(call.status),
            to_number=to_number,
            from_number=self._from_number,
            direction=CallDirection.OUTBOUND,
            cost_usd=call.price,
            raw={"sid": call.sid, "status": call.status},
        )

    async def terminate_call(self, provider_call_id: str) -> bool:
        if not self._client:
            return False
        try:
            self._client.calls(provider_call_id).update(status="completed")
            return True
        except Exception:
            return False

    async def get_call_status(self, provider_call_id: str) -> CallStatusUpdate:
        if not self._client:
            return CallStatusUpdate(
                provider_call_id=provider_call_id,
                status=CallStatus.FAILED,
                error_message="twilio not configured",
            )
        try:
            call = self._client.calls(provider_call_id).fetch()
            return CallStatusUpdate(
                provider_call_id=provider_call_id,
                status=_map_twilio_status(call.status),
                duration_seconds=call.duration,
                answered_at=str(call.start_time) if call.start_time else None,
                ended_at=str(call.end_time) if call.end_time else None,
                cost_usd=call.price,
                raw={"sid": call.sid, "status": call.status},
            )
        except Exception as exc:  # pragma: no cover - network
            return CallStatusUpdate(
                provider_call_id=provider_call_id,
                status=CallStatus.FAILED,
                error_message=str(exc),
            )

    def verify_webhook_signature(self, body: bytes, headers: dict) -> bool:
        """Validate Twilio request signature (X-Twilio-Signature)."""
        signature = headers.get("X-Twilio-Signature", "")
        url = headers.get("X-Twilio-Url", "")
        if not self._auth_secret or not signature:
            return False
        # Twilio signs the full URL + POST body (sorted params)
        data = urllib.parse.parse_qs(body.decode("utf-8"))
        sorted_params = "&".join(
            f"{k}={v[0]}" for k, v in sorted(data.items())
        )
        message = url + sorted_params
        digest = hmac.new(
            self._auth_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        expected = hmac.compare_digest(
            signature,
            __import__("base64").b64encode(digest).decode("utf-8"),
        )
        return expected

    def parse_webhook(self, body: bytes, headers: dict) -> Optional[CallStatusUpdate]:
        data = urllib.parse.parse_qs(body.decode("utf-8"))
        call_sid = data.get("CallSid", [None])[0]
        status = data.get("CallStatus", [None])[0]
        duration = data.get("CallDuration", [None])[0]
        if not call_sid or not status:
            return None
        return CallStatusUpdate(
            provider_call_id=call_sid,
            status=_map_twilio_status(status),
            duration_seconds=int(duration) if duration else None,
            raw={k: v[0] for k, v in data.items()},
        )
