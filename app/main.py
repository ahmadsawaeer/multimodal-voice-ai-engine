import os
import json
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.voice_engine import MultimodalVoiceEngine, VoiceTurnEvent
from app.audio_processor import AudioProcessor

app = FastAPI(
    title="Real-Time Multimodal Voice AI Engine",
    description="Sub-100ms full-duplex WebSockets voice intelligence engine with VAD, emotion intent classification & barge-in handling.",
    version="2.0.0"
)

voice_engine = MultimodalVoiceEngine()
audio_processor = AudioProcessor()


class ProcessAudioRequest(BaseModel):
    session_id: str = "session_001"
    user_transcript: Optional[str] = "Book a tour in Dubai for tomorrow"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "multimodal-voice-ai-engine", "latency_target": "<100ms", "version": "2.0.0"}


@app.post("/api/v1/voice/process-audio", response_model=VoiceTurnEvent)
async def process_audio_turn(payload: ProcessAudioRequest):
    # Simulated 16-bit PCM audio frame (1024 bytes)
    dummy_pcm = b"\x00\x10" * 512
    turn_event = await voice_engine.process_audio_chunk(
        session_id=payload.session_id,
        pcm_bytes=dummy_pcm,
        user_text_override=payload.user_transcript
    )
    return turn_event


@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"sess_{id(websocket)}"

    try:
        while True:
            # Receive text or binary frame from client
            message = await websocket.receive()

            if "bytes" in message and message["bytes"]:
                pcm_bytes = message["bytes"]
                turn_event = await voice_engine.process_audio_chunk(session_id=session_id, pcm_bytes=pcm_bytes)
                await websocket.send_text(turn_event.model_dump_json())

            elif "text" in message and message["text"]:
                data = json.loads(message["text"])
                text_input = data.get("text", "Hello AI Voice Assistant")
                dummy_pcm = b"\x00\x20" * 512
                turn_event = await voice_engine.process_audio_chunk(session_id=session_id, pcm_bytes=dummy_pcm, user_text_override=text_input)
                await websocket.send_text(turn_event.model_dump_json())

    except WebSocketDisconnect:
        pass


# Serve Static UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Multimodal Voice AI Engine API Running. Access /docs for API schema.</h1>"
