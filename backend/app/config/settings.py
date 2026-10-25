"""Application configuration loaded from environment variables.

All values are optional with safe defaults for development/mock mode.
Never hard-code credentials or personal phone numbers here.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    application_env: str = Field(default="development", alias="APPLICATION_ENV")
    public_base_url: str = Field(default="http://localhost:8000", alias="PUBLIC_BASE_URL")
    app_secret_key: str = Field(default="dev-secret-change-me", alias="APP_SECRET_KEY")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./dev.db", alias="DATABASE_URL"
    )
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")

    # Telephony
    telephony_provider: str = Field(default="mock", alias="TELEPHONY_PROVIDER")
    telephony_account_id: Optional[str] = Field(default=None, alias="TELEPHONY_ACCOUNT_ID")
    telephony_auth_secret: Optional[str] = Field(default=None, alias="TELEPHONY_AUTH_SECRET")
    telephony_phone_number: Optional[str] = Field(default=None, alias="TELEPHONY_PHONE_NUMBER")
    verified_destination_number: Optional[str] = Field(
        default=None, alias="VERIFIED_DESTINATION_NUMBER"
    )
    telephony_webhook_secret: Optional[str] = Field(
        default=None, alias="TELEPHONY_WEBHOOK_SECRET"
    )

    # Voice
    voice_provider: str = Field(default="mock", alias="VOICE_PROVIDER")
    voice_api_key: Optional[str] = Field(default=None, alias="VOICE_API_KEY")
    voice_model: str = Field(default="gpt-4o-realtime-preview", alias="VOICE_MODEL")
    voice_name: str = Field(default="alloy", alias="VOICE_NAME")

    # LLM / STT / TTS
    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    llm_api_key: Optional[str] = Field(default=None, alias="LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    stt_provider: str = Field(default="mock", alias="STT_PROVIDER")
    stt_api_key: Optional[str] = Field(default=None, alias="STT_API_KEY")

    tts_provider: str = Field(default="mock", alias="TTS_PROVIDER")
    tts_api_key: Optional[str] = Field(default=None, alias="TTS_API_KEY")

    # Google OAuth
    google_oauth_client_id: Optional[str] = Field(default=None, alias="GOOGLE_OAUTH_CLIENT_ID")
    google_oauth_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_OAUTH_CLIENT_SECRET")
    google_oauth_redirect_uri: Optional[str] = Field(
        default=None, alias="GOOGLE_OAUTH_REDIRECT_URI"
    )

    # Limits
    max_call_duration_seconds: int = Field(default=600, alias="MAX_CALL_DURATION_SECONDS")
    max_daily_calls: int = Field(default=10, alias="MAX_DAILY_CALLS")
    max_concurrent_calls: int = Field(default=3, alias="MAX_CONCURRENT_CALLS")
    monthly_budget_limit_usd: float = Field(default=50.0, alias="MONTHLY_BUDGET_LIMIT")

    # Security
    access_token_expire_minutes: int = Field(default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    encryption_key: Optional[str] = Field(default=None, alias="ENCRYPTION_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
