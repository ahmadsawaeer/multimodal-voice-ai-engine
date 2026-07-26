from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    result: Dict[str, Any]
    formatted_speech_output: str


class BaseAIPlugin(ABC):
    """Abstract Base Class for AI Plugins & Executable Tools."""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        pass

    @abstractmethod
    async def execute(self, kwargs: Dict[str, Any]) -> ToolExecutionResult:
        pass
