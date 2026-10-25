"""Unit tests for the mock telephony provider."""
import pytest
from app.telephony.mock import MockTelephonyProvider
from app.telephony.base import CallStatus, CallDirection


@pytest.mark.asyncio
async def test_mock_initiate_call_returns_ringing():
    provider = MockTelephonyProvider()
    result = await provider.initiate_call(
        to_number="+919876543210",
        from_number="+1234567890",
        webhook_url="http://example.com/webhook",
        status_callback_url="http://example.com/webhook",
        max_duration_seconds=600,
    )
    assert result.status == CallStatus.RINGING
    assert result.direction == CallDirection.OUTBOUND
    assert result.provider_call_id.startswith("mock-call-")
    assert result.to_number == "+919876543210"


@pytest.mark.asyncio
async def test_mock_terminate_and_status():
    provider = MockTelephonyProvider()
    result = await provider.initiate_call(
        to_number="+919876543210",
        from_number="+1234567890",
        webhook_url="http://example.com/webhook",
        status_callback_url="http://example.com/webhook",
        max_duration_seconds=600,
    )
    ok = await provider.terminate_call(result.provider_call_id)
    assert ok is True
    status = await provider.get_call_status(result.provider_call_id)
    assert status.status == CallStatus.COMPLETED
