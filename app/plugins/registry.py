from typing import Dict, Any, List, Optional
from app.plugins.base import BaseAIPlugin, ToolExecutionResult
from app.plugins.hotel_plugin import HotelBookingPlugin
from app.plugins.weather_plugin import WeatherLookupPlugin
from app.plugins.calendar_plugin import CalendarSchedulePlugin


class PluginRegistry:
    """Registry & Execution Engine for AI Tool Plugins."""

    def __init__(self):
        self.plugins: Dict[str, BaseAIPlugin] = {}
        self.register_plugin(HotelBookingPlugin())
        self.register_plugin(WeatherLookupPlugin())
        self.register_plugin(CalendarSchedulePlugin())

    def register_plugin(self, plugin: BaseAIPlugin):
        self.plugins[plugin.definition.name] = plugin

    def list_definitions(self) -> List[Dict[str, Any]]:
        return [p.definition.model_dump() for p in self.plugins.values()]

    async def execute_matched_tool(self, text: str) -> Optional[ToolExecutionResult]:
        t = text.lower()
        if "hotel" in t or "book" in t or "reserve" in t:
            return await self.plugins["book_hotel_suite"].execute({"location": "Dubai", "nights": 2, "guests": 2})
        elif "weather" in t or "forecast" in t or "temperature" in t:
            return await self.plugins["query_weather_forecast"].execute({"city": "Dubai"})
        elif "calendar" in t or "meeting" in t or "schedule" in t:
            return await self.plugins["schedule_calendar_event"].execute({"title": "Executive Sync", "timeframe": "Tomorrow 3 PM"})
        return None
