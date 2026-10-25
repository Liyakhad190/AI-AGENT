"""Mock voice providers for development (no real audio processing)."""
from __future__ import annotations

from app.voice.base import LLMProvider, STTProvider, TTSProvider, TranscriptionResult, TTSResult


class MockSTTProvider(STTProvider):
    async def transcribe(self, audio_bytes: bytes, language: str = "en-US") -> TranscriptionResult:
        return TranscriptionResult(
            text="",
            confidence=1.0,
            is_final=True,
            language=language,
        )


class MockTTSProvider(TTSProvider):
    async def synthesize(self, text: str, voice: str = "alloy", language: str = "en-US") -> TTSResult:
        return TTSResult(audio_url=None, duration_ms=len(text) * 40)


class MockLLMProvider(LLMProvider):
    async def generate(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.3,
    ) -> dict:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break
        return {
            "text": f"[mock response] I heard: {last_user}",
            "tool_calls": [],
            "finish_reason": "stop",
        }


def get_voice_providers():
    from app.config.settings import settings

    provider = settings.voice_provider.lower()
    if provider == "mock":
        return MockSTTProvider(), MockTTSProvider(), MockLLMProvider()
    raise ValueError(f"Unsupported voice provider: {settings.voice_provider}")
