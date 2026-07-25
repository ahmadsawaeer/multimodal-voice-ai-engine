from typing import Dict, Any, List
from pydantic import BaseModel, Field


class VoiceIntentAnalysis(BaseModel):
    intent: str  # "RESERVATION_BOOKING", "CUSTOMER_SUPPORT", "TOURISM_GUIDE", "FLIGHT_STATUS", "GENERAL_INQUIRY"
    emotion: str  # "CALM", "EXCITED", "FRUSTRATED", "URGENT"
    confidence: float
    detected_entities: Dict[str, str] = Field(default_factory=dict)
    recommended_action: str = ""


class MultimodalIntentClassifier:
    """Real-Time Voice Intent & Emotion Classification Engine."""

    def classify_transcript(self, text: str) -> VoiceIntentAnalysis:
        t = text.lower().strip()
        entities = {}

        # Default classification
        intent = "GENERAL_INQUIRY"
        emotion = "CALM"
        confidence = 0.88
        action = "Provide standard conversational response"

        # Emotion heuristics
        if any(w in t for w in ["help", "urgent", "immediately", "asap", "emergency"]):
            emotion = "URGENT"
            confidence = 0.95
        elif any(w in t for w in ["angry", "bad", "terrible", "worst", "refund", "frustrated"]):
            emotion = "FRUSTRATED"
            confidence = 0.92
        elif any(w in t for w in ["awesome", "great", "love", "wonderful", "amazing"]):
            emotion = "EXCITED"
            confidence = 0.90

        # Intent heuristics
        if any(w in t for w in ["support", "problem", "issue", "speak to human", "cancellation", "cancel"]):
            intent = "CUSTOMER_SUPPORT"
            action = "Transfer to Senior Customer Support Specialist"

        elif any(w in t for w in ["flight", "status", "where is", "delayed", "gate"]):
            intent = "FLIGHT_STATUS"
            action = "Query Real-Time Flight Data API"

        elif any(w in t for w in ["book", "reserve", "hotel", "ticket", "table"]):
            intent = "RESERVATION_BOOKING"
            action = "Route to Booking Agent Workflow"
            if "dubai" in t: entities["location"] = "Dubai"
            if "today" in t or "tomorrow" in t: entities["timeframe"] = "Immediate"

        elif any(w in t for w in ["tour", "burj khalifa", "safari", "desert", "museum", "attraction"]):
            intent = "TOURISM_GUIDE"
            action = "Route to Tourism & Concierge Agent"
            entities["category"] = "Attraction"

        return VoiceIntentAnalysis(
            intent=intent,
            emotion=emotion,
            confidence=confidence,
            detected_entities=entities,
            recommended_action=action
        )
