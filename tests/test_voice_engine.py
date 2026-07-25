import pytest
import asyncio
from app.audio_processor import AudioProcessor
from app.intent_classifier import MultimodalIntentClassifier
from app.voice_engine import MultimodalVoiceEngine


def test_audio_processor_vad():
    processor = AudioProcessor(sample_rate=16000, silence_threshold_db=-40.0)
    
    # Silent PCM audio
    silent_pcm = b"\x00\x00" * 480
    res_silent = processor.process_frame(silent_pcm)
    assert res_silent.is_speech is False
    assert res_silent.decibels == -100.0

    # Loud PCM audio sample (active speech simulation)
    loud_sample = (3000).to_bytes(2, byteorder='little', signed=True) * 480
    res_loud = processor.process_frame(loud_sample)
    assert res_loud.is_speech is True
    assert res_loud.decibels > -40.0


def test_intent_classifier():
    classifier = MultimodalIntentClassifier()

    res1 = classifier.classify_transcript("I want to book a hotel in Dubai for tomorrow")
    assert res1.intent == "RESERVATION_BOOKING"
    assert res1.emotion == "CALM"

    res2 = classifier.classify_transcript("Urgent help needed ASAP with my flight cancellation")
    assert res2.intent == "CUSTOMER_SUPPORT" or res2.intent == "FLIGHT_STATUS"
    assert res2.emotion in ["URGENT", "FRUSTRATED"]


@pytest.mark.asyncio
async def test_voice_engine_turn():
    engine = MultimodalVoiceEngine()
    dummy_pcm = b"\x00\x20" * 512

    turn = await engine.process_audio_chunk(
        session_id="test_sess",
        pcm_bytes=dummy_pcm,
        user_text_override="Tell me about Burj Khalifa tours"
    )

    assert turn.turn_id.startswith("turn_")
    assert "Burj Khalifa" in turn.ai_response_text or "dubai" in turn.ai_response_text.lower()
    assert turn.latency_ms < 200.0
