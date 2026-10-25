"""API dependencies (rate limiting, etc.)."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.security.rate_limit import call_limit_key, rate_limiter
from app.config.settings import settings


class RateLimitDep:
    def __init__(self, limit: int | None = None, window_seconds: int = 60):
        self.limit = limit or settings.max_daily_calls
        self.window_seconds = window_seconds

    async def __call__(self, user_id: str = "anon") -> None:
        key = call_limit_key(user_id, "calls")
        if not rate_limiter.is_allowed(key, self.limit, self.window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
