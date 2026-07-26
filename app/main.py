import os
import json
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.voice_engine import MultimodalVoiceEngine, VoiceTurnEvent, LatencyBenchmark
from app.audio_processor import AudioProcessor
from app.plugins.registry import PluginRegistry

app = FastAPI(
    title="Real-Time Multimodal Voice AI Platform & Infrastructure",
    description="Production-grade full-duplex conversational voice AI framework with multi-agent orchestration, tool calling, session memory, RAG, and sub-15ms barge-in handling.",
    version="4.0.0"
)

voice_engine = MultimodalVoiceEngine()
audio_processor = AudioProcessor()
plugin_registry = PluginRegistry()


class ProcessAudioRequest(BaseModel):
    session_id: str = "session_001"
    user_transcript: Optional[str] = "Book a hotel in Dubai for tomorrow"
    ai_is_speaking: bool = False


@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "multimodal-voice-ai-platform", "latency_target": "<100ms", "version": "4.0.0"}


@app.get("/api/v1/voice/benchmark", response_model=LatencyBenchmark)
async def get_latency_benchmark():
    """Returns P50, P90, P99 turn-taking latency SLA benchmark metrics."""
    return voice_engine.calculate_latency_benchmark()


@app.get("/api/v1/voice/plugins")
async def get_loaded_plugins():
    """Returns definitions of all auto-loaded AI tool plugins."""
    return {"loaded_plugins": plugin_registry.list_definitions()}


@app.get("/api/v1/voice/memory/{session_id}")
async def get_session_memory(session_id: str):
    """Returns multi-turn conversational context & entity memory for a session."""
    summary = voice_engine.memory_store.get_context_summary(session_id)
    session = voice_engine.memory_store.get_or_create_session(session_id)
    return {
        "session_id": session_id,
        "turns_count": len(session.turns),
        "context_summary": summary,
        "active_entities": session.active_entities
    }


@app.post("/api/v1/voice/process-audio", response_model=VoiceTurnEvent)
async def process_audio_turn(payload: ProcessAudioRequest):
    dummy_pcm = b"\x00\x10" * 512
    turn_event = await voice_engine.process_audio_chunk(
        session_id=payload.session_id,
        pcm_bytes=dummy_pcm,
        user_text_override=payload.user_transcript,
        ai_is_currently_speaking=payload.ai_is_speaking
    )
    return turn_event


@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"sess_{id(websocket)}"

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message and message["bytes"]:
                pcm_bytes = message["bytes"]
                turn_event = await voice_engine.process_audio_chunk(session_id=session_id, pcm_bytes=pcm_bytes)
                await websocket.send_text(turn_event.model_dump_json())

            elif "text" in message and message["text"]:
                data = json.loads(message["text"])
                text_input = data.get("text", "Hello AI Voice Assistant")
                ai_speaking = data.get("ai_is_speaking", False)
                dummy_pcm = b"\x00\x20" * 512
                turn_event = await voice_engine.process_audio_chunk(
                    session_id=session_id,
                    pcm_bytes=dummy_pcm,
                    user_text_override=text_input,
                    ai_is_currently_speaking=ai_speaking
                )
                await websocket.send_text(turn_event.model_dump_json())

    except WebSocketDisconnect:
        pass


# Serve Static Studio UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Realtime Voice AI Platform API Running. Access /docs for API schema.</h1>"
