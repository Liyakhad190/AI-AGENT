"""In-memory voice session manager (Redis-backed in production)."""
from __future__ import annotations

import uuid
from typing import Optional

from app.voice.base import VoiceSession


class VoiceSessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, VoiceSession] = {}

    def create(self, call_session_id: str, user_id: str, language: str = "en-US") -> VoiceSession:
        session = VoiceSession(
            session_id=str(uuid.uuid4()),
            call_session_id=call_session_id,
            user_id=user_id,
            language=language,
        )
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Optional[VoiceSession]:
        return self._sessions.get(session_id)

    def get_by_call(self, call_session_id: str) -> Optional[VoiceSession]:
        for s in self._sessions.values():
            if s.call_session_id == call_session_id:
                return s
        return None

    def end(self, session_id: str) -> None:
        s = self._sessions.get(session_id)
        if s:
            s.is_active = False


voice_sessions = VoiceSessionManager()
