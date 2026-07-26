import pytest
import asyncio
from app.audio_processor import AudioProcessor
from app.intent_classifier import MultimodalIntentClassifier
from app.voice_engine import MultimodalVoiceEngine
from app.barge_in import BargeInEngine


def test_audio_processor_vad():
    processor = AudioProcessor(sample_rate=16000, silence_threshold_db=-40.0)
    silent_pcm = b"\x00\x00" * 480
    res_silent = processor.process_frame(silent_pcm)
    assert res_silent.is_speech is False
    assert res_silent.decibels == -100.0


def test_intent_classifier():
    classifier = MultimodalIntentClassifier()
    res1 = classifier.classify_transcript("I want to book a hotel in Dubai for tomorrow")
    assert res1.intent == "RESERVATION_BOOKING"
    assert res1.emotion == "CALM"


def test_barge_in_engine():
    engine = BargeInEngine()
    status = engine.evaluate_interruption(ai_is_speaking=True, user_is_speaking=True, active_turn_id="turn_001")
    assert status.barge_in_detected is True
    assert status.cancelled_turn_id == "turn_001"


@pytest.mark.asyncio
async def test_voice_engine_turn_and_benchmark():
    engine = MultimodalVoiceEngine()
    dummy_pcm = b"\x00\x20" * 512

    turn = await engine.process_audio_chunk(
        session_id="test_sess",
        pcm_bytes=dummy_pcm,
        user_text_override="Tell me about Burj Khalifa tours"
    )

    assert turn.turn_id.startswith("turn_")
    assert turn.latency_ms < 200.0

    benchmark = engine.calculate_latency_benchmark()
    assert benchmark.total_turns > 0
    assert benchmark.sla_target_passed is True
