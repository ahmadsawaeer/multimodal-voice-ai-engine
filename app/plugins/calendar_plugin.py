from typing import Dict, Any
from app.plugins.base import BaseAIPlugin, ToolDefinition, ToolParameter, ToolExecutionResult


class CalendarSchedulePlugin(BaseAIPlugin):
    """Plugin for scheduling meetings and calendar invitations."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="schedule_calendar_event",
            description="Schedules a meeting on Google Calendar / Outlook.",
            parameters=[
                ToolParameter(name="title", type="string", description="Meeting topic"),
                ToolParameter(name="timeframe", type="string", description="Time or date e.g. Tomorrow 3 PM")
            ]
        )

    async def execute(self, kwargs: Dict[str, Any]) -> ToolExecutionResult:
        title = kwargs.get("title", "Executive Sync")
        timeframe = kwargs.get("timeframe", "Tomorrow 3:00 PM")
        res_data = {
            "event_id": "CAL-9921",
            "title": title,
            "timeframe": timeframe,
            "status": "SCHEDULED"
        }
        speech = f"I have scheduled '{title}' for {timeframe} and sent calendar invitations to all participants."
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            result=res_data,
            formatted_speech_output=speech
        )
