"""Gmail OAuth integration client (least-privilege scopes)."""
from __future__ import annotations

from typing import Any

from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.config.settings import settings


GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]


class GmailClient:
    def __init__(self, access_token: str) -> None:
        self._client = AsyncOAuth2Client(
            client_id=settings.google_oauth_client_id,
            client_secret=settings.google_oauth_client_secret,
            token={"access_token": access_token},
        )
        self._base = "https://gmail.googleapis.com/gmail/v1/users/me"

    async def list_messages(self, max_results: int = 10, query: str = "") -> list[dict[str, Any]]:
        params: dict[str, Any] = {"maxResults": max_results}
        if query:
            params["q"] = query
        resp = await self._client.get(f"{self._base}/messages", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("messages", [])

    async def get_message(self, message_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"{self._base}/messages/{message_id}")
        resp.raise_for_status()
        return resp.json()

    async def create_draft(self, raw_message: dict[str, Any]) -> dict[str, Any]:
        resp = await self._client.post(
            f"{self._base}/drafts", json={"message": raw_message}
        )
        resp.raise_for_status()
        return resp.json()

    async def send_message(self, raw_message: dict[str, Any]) -> dict[str, Any]:
        resp = await self._client.post(
            f"{self._base}/messages/send", json={"raw": raw_message.get("raw", "")}
        )
        resp.raise_for_status()
        return resp.json()
