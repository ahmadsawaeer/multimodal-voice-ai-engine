from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class RAGQueryResult(BaseModel):
    query: str
    matched_doc: str
    citation: str
    relevance_score: float
    is_conversational_fallback: bool = False


class VoiceRAGEngine:
    """Retrieval-Augmented Generation Knowledge Base for Voice Agents."""

    def __init__(self):
        self.documents = [
            {"id": "DOC-001", "citation": "Dubai Tourism Manual Sec 3.1", "content": "Burj Khalifa observatory tickets are available for At The Top (Levels 124 & 125) and SKY (Level 148). Prime hours are 4:00 PM to 6:30 PM."},
            {"id": "DOC-002", "citation": "Emirates Airline Policy Sec 5.4", "content": "Flight EK202 operates daily from DXB Terminal 3 to JFK. Baggage allowance includes 2 checked bags for Business Class."},
            {"id": "DOC-003", "citation": "Atlantis The Royal Concierge Policy", "content": "Check-in time is 3:00 PM. All luxury suite reservations include complimentary access to Aquaventure Waterpark."}
        ]

    def query(self, text: str) -> RAGQueryResult:
        t = text.lower().strip()

        # Conversational greetings & hearing checks
        if any(w in t for w in ["hear me", "can you hear", "hello", "hi", "hey", "testing", "who are you"]):
            return RAGQueryResult(
                query=text,
                matched_doc="Yes, I can hear you clearly! I am your real-time multimodal voice AI assistant. How can I assist you today?",
                citation="System Conversational Agent",
                relevance_score=0.99,
                is_conversational_fallback=True
            )

        if any(w in t for w in ["burj", "khalifa", "attraction", "ticket", "safari"]):
            return RAGQueryResult(
                query=text,
                matched_doc=self.documents[0]["content"],
                citation=self.documents[0]["citation"],
                relevance_score=0.95
            )
        elif any(w in t for w in ["flight", "emirates", "baggage", "plane"]):
            return RAGQueryResult(
                query=text,
                matched_doc=self.documents[1]["content"],
                citation=self.documents[1]["citation"],
                relevance_score=0.93
            )
        elif any(w in t for w in ["hotel", "atlantis", "check-in", "suite", "room"]):
            return RAGQueryResult(
                query=text,
                matched_doc=self.documents[2]["content"],
                citation=self.documents[2]["citation"],
                relevance_score=0.91
            )

        # Default conversational fallback
        return RAGQueryResult(
            query=text,
            matched_doc="I heard you clearly! How can I assist with your journey, hotel reservations, or flight queries today?",
            citation="System Conversational Agent",
            relevance_score=0.88,
            is_conversational_fallback=True
        )
