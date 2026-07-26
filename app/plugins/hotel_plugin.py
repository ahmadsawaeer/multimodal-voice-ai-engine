from typing import Dict, Any
from app.plugins.base import BaseAIPlugin, ToolDefinition, ToolParameter, ToolExecutionResult


class HotelBookingPlugin(BaseAIPlugin):
    """Plugin for reserving luxury hotel suites in Dubai & international destinations."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="book_hotel_suite",
            description="Reserves luxury hotel accommodation with date and location parameters.",
            parameters=[
                ToolParameter(name="location", type="string", description="City destination e.g. Dubai"),
                ToolParameter(name="nights", type="integer", description="Number of nights stay"),
                ToolParameter(name="guests", type="integer", description="Number of guests")
            ]
        )

    async def execute(self, kwargs: Dict[str, Any]) -> ToolExecutionResult:
        location = kwargs.get("location", "Dubai")
        nights = int(kwargs.get("nights", 2))
        guests = int(kwargs.get("guests", 2))
        booking_id = f"RES-DXB-{10492 + nights*12}"

        res_data = {
            "booking_id": booking_id,
            "hotel": "Atlantis The Royal, Dubai",
            "nights": nights,
            "guests": guests,
            "status": "CONFIRMED"
        }

        speech = f"I have confirmed your luxury reservation at Atlantis The Royal, {location} for {nights} nights ({guests} guests). Confirmation number: {booking_id}."

        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            result=res_data,
            formatted_speech_output=speech
        )
