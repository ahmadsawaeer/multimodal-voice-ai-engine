import math
import struct
from typing import Tuple, List
from pydantic import BaseModel, Field


class VADResult(BaseModel):
    is_speech: bool
    rms_energy: float
    decibels: float
    duration_ms: float


class AudioProcessor:
    """Voice Activity Detection (VAD) & Audio PCM Processing Engine."""

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 30, silence_threshold_db: float = -40.0):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.silence_threshold_db = silence_threshold_db

    def calculate_rms_and_db(self, pcm_bytes: bytes) -> Tuple[float, float]:
        """Calculates Root Mean Square (RMS) energy and Decibels (dB) from 16-bit PCM bytes."""
        if not pcm_bytes:
            return 0.0, -100.0

        # 16-bit signed integer samples
        sample_count = len(pcm_bytes) // 2
        if sample_count == 0:
            return 0.0, -100.0

        try:
            samples = struct.unpack(f"<{sample_count}h", pcm_bytes)
        except Exception:
            return 0.0, -100.0

        sum_squares = sum(s * s for s in samples)
        mean_square = sum_squares / sample_count
        rms = math.sqrt(mean_square)

        # Normalize RMS (0.0 to 1.0 relative to max 32768)
        norm_rms = rms / 32768.0

        if norm_rms > 0:
            db = 20 * math.log10(norm_rms)
        else:
            db = -100.0

        return norm_rms, db

    def process_frame(self, pcm_bytes: bytes) -> VADResult:
        """Evaluates a raw audio frame for speech activity."""
        rms, db = self.calculate_rms_and_db(pcm_bytes)
        is_speech = db > self.silence_threshold_db

        sample_count = len(pcm_bytes) // 2
        duration_ms = (sample_count / self.sample_rate) * 1000.0 if self.sample_rate > 0 else 0.0

        return VADResult(
            is_speech=is_speech,
            rms_energy=round(rms, 4),
            decibels=round(db, 2),
            duration_ms=round(duration_ms, 2)
        )
