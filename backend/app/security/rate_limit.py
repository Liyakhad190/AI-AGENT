"""In-memory rate limiter (Redis-backed in production)."""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict

from app.config.settings import settings


class RateLimiter:
    def __init__(self) -> None:
        self._calls: Dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        window = self._calls[key]
        # prune old entries
        self._calls[key] = [t for t in window if now - t < window_seconds]
        if len(self._calls[key]) >= limit:
            return False
        self._calls[key].append(now)
        return True


rate_limiter = RateLimiter()


def call_limit_key(user_id: str, resource: str) -> str:
    return f"{resource}:{user_id}"
