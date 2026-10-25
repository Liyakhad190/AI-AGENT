"""Voice engine provider-independent interfaces."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TranscriptionResult:
    text: str
    confidence: float
    is_final: bool
    language: str = "en-US"


@dataclass
class TTSResult:
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class VoiceSession:
    session_id: str
    call_session_id: str
    user_id: str
    language: str = "en-US"
    is_active: bool = True
    turn_count: int = 0
    metadata: dict = field(default_factory=dict)


class STTProvider:
    async def transcribe(self, audio_bytes: bytes, language: str = "en-US") -> TranscriptionResult:
        raise NotImplementedError


class TTSProvider:
    async def synthesize(self, text: str, voice: str = "alloy", language: str = "en-US") -> TTSResult:
        raise NotImplementedError


class LLMProvider:
    async def generate(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        temperature: float = 0.3,
    ) -> dict:
        raise NotImplementedError
