"""
Local Audio Feature Extraction Module
Extracts measurable audio characteristics (NOT diagnostic).
"""

import numpy as np
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa not available")


@dataclass
class AudioFeatures:
    speech_rate_score: float = 0.5
    pause_score: float = 0.5
    pitch_variation_score: float = 0.5
    energy_variation_score: float = 0.5
    voice_activity_score: float = 0.5
    audio_quality_score: float = 0.5
    speech_rate_wpm: float = 0.0
    pause_duration_mean: float = 0.0
    pitch_mean: float = 0.0
    pitch_std: float = 0.0
    energy_mean: float = 0.0
    energy_std: float = 0.0
    voice_activity_ratio: float = 0.0
    duration_seconds: float = 0.0
    snr_estimate: float = 0.0
    processing_time_ms: int = 0
    model_name: str = "librosa-audio-analysis"
    confidence: float = 0.0

    def to_dict(self):
        return asdict(self)


class AudioFeatureExtractor:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.model_name = "librosa-audio-analysis"

    def _normalize(self, value, min_v, max_v, invert=False):
        if max_v <= min_v:
            return 0.5
        n = (value - min_v) / (max_v - min_v)
        n = max(0.0, min(1.0, n))
        return 1.0 - n if invert else n

    def _fallback(self, start):
        return AudioFeatures(
            speech_rate_score=0.5, pause_score=0.5, pitch_variation_score=0.5,
            energy_variation_score=0.5, voice_activity_score=0.5, audio_quality_score=0.5,
            processing_time_ms=int((time.time() - start) * 1000),
            model_name="fallback-demo", confidence=0.3,
        )

    def extract(self, audio_data: bytes, file_format: str = "wav") -> AudioFeatures:
        start = time.time()
        if not LIBROSA_AVAILABLE or not audio_data or len(audio_data) < 100:
            return self._fallback(start)
        try:
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            y, sr = librosa.load(tmp_path, sr=self.sample_rate)
            os.unlink(tmp_path)
            duration = len(y) / sr

            # Speech rate
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            speech_rate = float(tempo) * 1.5 if tempo > 0 else 150.0
            speech_rate_score = self._normalize(speech_rate, 80, 200)

            # Pauses
            rms = librosa.feature.rms(y=y)[0]
            threshold = np.percentile(rms, 20)
            is_speech = rms > threshold
            pauses = []
            in_pause = False
            pause_start = 0
            frame_dur = 512 / sr
            for i, sp in enumerate(is_speech):
                if not sp and not in_pause:
                    in_pause = True
                    pause_start = i
                elif sp and in_pause:
                    in_pause = False
                    pd = (i - pause_start) * frame_dur
                    if pd > 0.1:
                        pauses.append(pd)
            mean_pause = float(np.mean(pauses)) if pauses else 0.3
            pause_score = self._normalize(mean_pause, 0.2, 2.0, invert=True)

            # Pitch
            try:
                f0, voiced, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
                vf = f0[voiced]
                pitch_mean = float(np.mean(vf)) if len(vf) > 0 else 180.0
                pitch_std = float(np.std(vf)) if len(vf) > 0 else 20.0
            except Exception:
                pitch_mean = 180.0
                pitch_std = 20.0
            pitch_score = self._normalize(pitch_std, 0, 100)

            # Energy
            energy_mean = float(np.mean(rms))
            energy_std = float(np.std(rms))
            energy_score = self._normalize(energy_std, 0, 0.2)

            # Voice activity
            voiced_ratio = float(np.mean(is_speech))
            voice_score = self._normalize(voiced_ratio, 0.3, 0.9)

            # Quality
            sf = librosa.feature.spectral_flatness(y=y)[0]
            snr = 10 * np.log10(1 / (np.mean(sf) + 1e-10))
            snr = max(0, min(40, snr))
            quality = self._normalize(snr, 5, 30)

            return AudioFeatures(
                speech_rate_score=speech_rate_score,
                pause_score=pause_score,
                pitch_variation_score=pitch_score,
                energy_variation_score=energy_score,
                voice_activity_score=voice_score,
                audio_quality_score=quality,
                speech_rate_wpm=speech_rate,
                pause_duration_mean=mean_pause,
                pitch_mean=pitch_mean,
                pitch_std=pitch_std,
                energy_mean=energy_mean,
                energy_std=energy_std,
                voice_activity_ratio=voiced_ratio,
                duration_seconds=duration,
                snr_estimate=snr,
                processing_time_ms=int((time.time() - start) * 1000),
                model_name=self.model_name,
                confidence=min(1.0, (duration / 5.0) * quality) if duration > 0 else 0.0,
            )
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return self._fallback(start)


def get_audio_feature_extractor(sample_rate: int = 16000):
    return AudioFeatureExtractor(sample_rate)
