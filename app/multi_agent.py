from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.rag_engine import VoiceRAGEngine, RAGQueryResult
from app.plugins.registry import PluginRegistry, ToolExecutionResult


class AgentPipelineStep(BaseModel):
    agent_name: str  # "PlannerAgent", "ResearchRAGAgent", "ToolExecutionAgent", "VoiceResponseAgent"
    action: str
    output: str


class MultiAgentWorkflowResult(BaseModel):
    user_query: str
    steps: list[AgentPipelineStep]
    final_speech: str
    tool_executed: Optional[ToolExecutionResult] = None
    rag_result: Optional[RAGQueryResult] = None


class MultiAgentOrchestrator:
    """Multi-Agent System Orchestrating RAG, Tool Execution & Voice Synthesis."""

    def __init__(self):
        self.rag_engine = VoiceRAGEngine()
        self.plugin_registry = PluginRegistry()

    async def execute_workflow(self, text: str) -> MultiAgentWorkflowResult:
        steps = []

        # 1. Planner Agent
        steps.append(AgentPipelineStep(
            agent_name="PlannerAgent",
            action="Analyze query intent and orchestrate sub-agents",
            output=f"Task planned for query: '{text}'"
        ))

        # 2. Tool Execution Agent
        tool_res = await self.plugin_registry.execute_matched_tool(text)
        if tool_res:
            steps.append(AgentPipelineStep(
                agent_name="ToolExecutionAgent",
                action=f"Executed AI Tool '{tool_res.tool_name}'",
                output=tool_res.formatted_speech_output
            ))
            final_speech = tool_res.formatted_speech_output
            rag_res = None
        else:
            # 3. Research RAG Agent
            rag_res = self.rag_engine.query(text)
            steps.append(AgentPipelineStep(
                agent_name="ResearchRAGAgent",
                action=f"Retrieved citation '{rag_res.citation}'",
                output=rag_res.matched_doc
            ))
            final_speech = rag_res.matched_doc

        # 4. Voice Response Agent
        steps.append(AgentPipelineStep(
            agent_name="VoiceResponseAgent",
            action="Format speech cadence for natural neural TTS",
            output=final_speech
        ))

        return MultiAgentWorkflowResult(
            user_query=text,
            steps=steps,
            final_speech=final_speech,
            tool_executed=tool_res,
            rag_result=rag_res
        )
