"""Provider adapter that selects the concrete implementation."""
from __future__ import annotations

from app.config.settings import settings
from app.telephony.base import TelephonyProvider
from app.telephony.mock import MockTelephonyProvider
from app.telephony.twilio import TwilioTelephonyProvider


def get_telephony_provider() -> TelephonyProvider:
    provider = settings.telephony_provider.lower()
    if provider == "twilio":
        return TwilioTelephonyProvider()
    if provider == "mock":
        return MockTelephonyProvider()
    raise ValueError(f"Unsupported telephony provider: {settings.telephony_provider}")
