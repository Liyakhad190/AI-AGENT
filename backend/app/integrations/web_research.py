"""Web research integration (treated as untrusted data)."""
from __future__ import annotations

from typing import Any

import httpx

from app.config.settings import settings


class WebResearchClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=15.0, headers={"User-Agent": "ai-voice-agent/0.1"})

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        # Placeholder: real implementation plugs into an approved search API.
        return [
            {
                "title": f"Result for: {query}",
                "url": "https://example.com",
                "snippet": "[mock] search results require a configured search provider",
                "source": "mock",
            }
        ]

    async def fetch(self, url: str) -> dict[str, Any]:
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            return {"url": url, "status": resp.status_code, "content": resp.text[:4000]}
        except Exception as exc:  # pragma: no cover - network
            return {"url": url, "error": str(exc)}
