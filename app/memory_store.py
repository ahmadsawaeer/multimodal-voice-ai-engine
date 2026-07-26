from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MemoryTurn(BaseModel):
    user_text: str
    ai_text: str
    detected_intent: str
    emotion: str
    timestamp: float


class SessionMemory(BaseModel):
    session_id: str
    turns: List[MemoryTurn] = Field(default_factory=list)
    active_entities: Dict[str, Any] = Field(default_factory=dict)


class SessionMemoryStore:
    """Multi-Turn Conversational Context & Entity Memory Store."""

    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}

    def get_or_create_session(self, session_id: str) -> SessionMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id=session_id)
        return self.sessions[session_id]

    def add_turn(self, session_id: str, turn: MemoryTurn, entities: Optional[Dict[str, Any]] = None):
        sess = self.get_or_create_session(session_id)
        sess.turns.append(turn)
        if entities:
            sess.active_entities.update(entities)

    def get_context_summary(self, session_id: str) -> str:
        sess = self.get_or_create_session(session_id)
        if not sess.turns:
            return "No previous conversation context."

        recent = sess.turns[-3:]
        context_lines = [f"User: {t.user_text} | AI: {t.ai_text}" for t in recent]
        return "\n".join(context_lines)
