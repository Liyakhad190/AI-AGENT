"""Google Calendar OAuth integration client."""
from __future__ import annotations

from typing import Any

from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.config.settings import settings


GOOGLE_CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


class CalendarClient:
    def __init__(self, access_token: str) -> None:
        self._client = AsyncOAuth2Client(
            client_id=settings.google_oauth_client_id,
            client_secret=settings.google_oauth_client_secret,
            token={"access_token": access_token},
        )
        self._base = "https://www.googleapis.com/calendar/v3"

    async def list_events(
        self, calendar_id: str = "primary", max_results: int = 10, time_min: str | None = None
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"maxResults": max_results, "singleEvents": True, "orderBy": "startTime"}
        if time_min:
            params["timeMin"] = time_min
        resp = await self._client.get(
            f"{self._base}/calendars/{calendar_id}/events", params=params
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    async def create_event(self, event_body: dict[str, Any]) -> dict[str, Any]:
        resp = await self._client.post(
            f"{self._base}/calendars/primary/events", json=event_body
        )
        resp.raise_for_status()
        return resp.json()
