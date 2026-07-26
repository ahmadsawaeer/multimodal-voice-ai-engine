import pytest
import asyncio
from app.audio_processor import AudioProcessor
from app.intent_classifier import MultimodalIntentClassifier
from app.voice_engine import MultimodalVoiceEngine
from app.barge_in import BargeInEngine
from app.plugins.registry import PluginRegistry
from app.memory_store import SessionMemoryStore, MemoryTurn
from app.rag_engine import VoiceRAGEngine
from app.multi_agent import MultiAgentOrchestrator


def test_audio_processor_vad():
    processor = AudioProcessor(sample_rate=16000, silence_threshold_db=-40.0)
    silent_pcm = b"\x00\x00" * 480
    res_silent = processor.process_frame(silent_pcm)
    assert res_silent.is_speech is False


def test_plugin_tool_calling():
    registry = PluginRegistry()
    defs = registry.list_definitions()
    assert len(defs) >= 3
    tool_names = [d["name"] for d in defs]
    assert "book_hotel_suite" in tool_names
    assert "query_weather_forecast" in tool_names


def test_session_memory_store():
    store = SessionMemoryStore()
    store.add_turn(
        session_id="sess_test",
        turn=MemoryTurn(
            user_text="Book hotel in Dubai",
            ai_text="Confirmed Atlantis hotel",
            detected_intent="RESERVATION_BOOKING",
            emotion="CALM",
            timestamp=100.0
        ),
        entities={"location": "Dubai"}
    )
    summary = store.get_context_summary("sess_test")
    assert "Atlantis" in summary
    assert store.get_or_create_session("sess_test").active_entities["location"] == "Dubai"


def test_voice_rag_engine():
    rag = VoiceRAGEngine()
    res = rag.query("Burj Khalifa ticket prices")
    assert "Burj Khalifa" in res.matched_doc
    assert res.relevance_score > 0.90


@pytest.mark.asyncio
async def test_multi_agent_workflow():
    orchestrator = MultiAgentOrchestrator()
    res = await orchestrator.execute_workflow("What is the weather forecast in Dubai?")
    assert len(res.steps) >= 3
    assert "32°C" in res.final_speech or "weather" in res.final_speech.lower()


@pytest.mark.asyncio
async def test_voice_engine_full_pipeline():
    engine = MultimodalVoiceEngine()
    dummy_pcm = b"\x00\x20" * 512

    turn = await engine.process_audio_chunk(
        session_id="sess_001",
        pcm_bytes=dummy_pcm,
        user_text_override="Reserve a hotel suite for 2 nights"
    )

    assert turn.turn_id.startswith("turn_")
    assert turn.workflow_result is not None
    assert turn.latency_ms < 200.0
