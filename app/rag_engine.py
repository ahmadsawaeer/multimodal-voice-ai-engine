from typing import List, Dict, Any
from pydantic import BaseModel


class RAGQueryResult(BaseModel):
    query: str
    matched_doc: str
    citation: str
    relevance_score: float


class VoiceRAGEngine:
    """Retrieval-Augmented Generation Knowledge Base for Voice Agents."""

    def __init__(self):
        self.documents = [
            {"id": "DOC-001", "citation": "Dubai Tourism Manual Sec 3.1", "content": "Burj Khalifa observatory tickets are available for At The Top (Levels 124 & 125) and SKY (Level 148). Prime hours are 4:00 PM to 6:30 PM."},
            {"id": "DOC-002", "citation": "Emirates Airline Policy Sec 5.4", "content": "Flight EK202 operates daily from DXB Terminal 3 to JFK. Baggage allowance includes 2 checked bags for Business Class."},
            {"id": "DOC-003", "citation": "Atlantis The Royal Concierge Policy", "content": "Check-in time is 3:00 PM. All luxury suite reservations include complimentary access to Aquaventure Waterpark."}
        ]

    def query(self, text: str) -> RAGQueryResult:
        t = text.lower()
        matched = self.documents[0]
        score = 0.82

        if "burj" in t or "khalifa" in t or "attraction" in t:
            matched = self.documents[0]
            score = 0.95
        elif "flight" in t or "emirates" in t or "baggage" in t:
            matched = self.documents[1]
            score = 0.93
        elif "hotel" in t or "atlantis" in t or "check-in" in t:
            matched = self.documents[2]
            score = 0.91

        return RAGQueryResult(
            query=text,
            matched_doc=matched["content"],
            citation=matched["citation"],
            relevance_score=score
        )
