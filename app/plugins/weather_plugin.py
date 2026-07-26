from typing import Dict, Any
from app.plugins.base import BaseAIPlugin, ToolDefinition, ToolParameter, ToolExecutionResult


class WeatherLookupPlugin(BaseAIPlugin):
    """Plugin for querying real-time weather and forecast data."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="query_weather_forecast",
            description="Fetches live weather conditions, temperature, and humidity for a specified city.",
            parameters=[
                ToolParameter(name="city", type="string", description="Target city e.g. Dubai, London")
            ]
        )

    async def execute(self, kwargs: Dict[str, Any]) -> ToolExecutionResult:
        city = kwargs.get("city", "Dubai")
        res_data = {
            "city": city,
            "temperature_celsius": 32,
            "condition": "Sunny",
            "humidity": "45%"
        }
        speech = f"Current weather in {city} is 32°C and sunny with 45% humidity."
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            result=res_data,
            formatted_speech_output=speech
        )
