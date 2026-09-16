"""
Demo Audio Service
Mock implementation for demonstration purposes
"""
import time
import random
from typing import Dict, Any

from ai.audio.audio_service import AudioService, AudioFeatures


class DemoAudioService(AudioService):
    """Demo/Mock audio service for demonstration purposes - CLEARLY LABELED AS DEMO"""

    def __init__(self):
        self._model_name = "DEMO-LIBROSA-AUDIO-ANALYSIS"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def is_demo(self) -> bool:
        return True

    async def analyze(self, audio_path: str) -> AudioFeatures:
        start_time = time.time()
        await self._simulate_processing()

        scenario = "moderate"
        if "low" in audio_path.lower():
            scenario = "low"
        elif "high" in audio_path.lower():
            scenario = "high"
        elif "critical" in audio_path.lower():
            scenario = "critical"
        else:
            scenario = random.choice(["low", "moderate", "high", "critical"])

        features = self._get_demo_features(scenario)
        processing_time = int((time.time() - start_time) * 1000)

        return AudioFeatures(
            **features,
            processing_time_ms=processing_time,
            model_name=self._model_name,
        )

    async def analyze_bytes(self, audio_data: bytes) -> AudioFeatures:
        start_time = time.time()
        await self._simulate_processing()
        scenario = random.choice(["low", "moderate", "high", "critical"])
        features = self._get_demo_features(scenario)
        processing_time = int((time.time() - start_time) * 1000)
        return AudioFeatures(
            **features,
            processing_time_ms=processing_time,
            model_name=self._model_name,
        )

    def _get_demo_features(self, scenario: str) -> Dict[str, Any]:
        base_features = {
            "speech_rate": 150.0,
            "pause_duration_mean": 0.5,
            "pause_duration_std": 0.2,
            "pitch_mean": 180.0,
            "pitch_std": 20.0,
            "pitch_range": 80.0,
            "energy_mean": 0.1,
            "energy_std": 0.05,
            "jitter": 0.02,
            "shimmer": 0.03,
            "hnr": 15.0,
            "spectral_centroid_mean": 2000.0,
            "spectral_centroid_std": 300.0,
            "spectral_rolloff_mean": 4000.0,
            "spectral_bandwidth_mean": 1500.0,
            "voice_activity_ratio": 0.7,
            "num_pauses": 10,
            "total_duration": 20.0,
            "audio_quality": "GOOD",
            "snr_estimate": 20.0,
            "confidence": 0.85,
        }

        if scenario == "low":
            return {
                **base_features,
                "speech_rate": 140.0,
                "pause_duration_mean": 0.4,
                "pause_duration_std": 0.15,
                "pitch_mean": 170.0,
                "pitch_std": 15.0,
                "pitch_range": 60.0,
                "energy_mean": 0.12,
                "energy_std": 0.04,
                "jitter": 0.015,
                "shimmer": 0.02,
                "hnr": 18.0,
                "voice_activity_ratio": 0.75,
                "num_pauses": 8,
                "audio_quality": "GOOD",
                "snr_estimate": 25.0,
                "confidence": 0.90,
            }
        elif scenario == "moderate":
            return {
                **base_features,
                "speech_rate": 130.0,
                "pause_duration_mean": 0.7,
                "pause_duration_std": 0.3,
                "pitch_mean": 190.0,
                "pitch_std": 25.0,
                "pitch_range": 100.0,
                "energy_mean": 0.09,
                "energy_std": 0.06,
                "jitter": 0.025,
                "shimmer": 0.04,
                "hnr": 13.0,
                "voice_activity_ratio": 0.65,
                "num_pauses": 12,
                "audio_quality": "GOOD",
                "snr_estimate": 18.0,
                "confidence": 0.85,
            }
        elif scenario == "high":
            return {
                **base_features,
                "speech_rate": 110.0,
                "pause_duration_mean": 1.2,
                "pause_duration_std": 0.5,
                "pitch_mean": 210.0,
                "pitch_std": 35.0,
                "pitch_range": 140.0,
                "energy_mean": 0.07,
                "energy_std": 0.08,
                "jitter": 0.04,
                "shimmer": 0.06,
                "hnr": 10.0,
                "voice_activity_ratio": 0.55,
                "num_pauses": 18,
                "audio_quality": "FAIR",
                "snr_estimate": 12.0,
                "confidence": 0.80,
            }
        else:  # critical
            return {
                **base_features,
                "speech_rate": 90.0,
                "pause_duration_mean": 2.0,
                "pause_duration_std": 0.8,
                "pitch_mean": 230.0,
                "pitch_std": 50.0,
                "pitch_range": 200.0,
                "energy_mean": 0.05,
                "energy_std": 0.1,
                "jitter": 0.06,
                "shimmer": 0.08,
                "hnr": 7.0,
                "voice_activity_ratio": 0.4,
                "num_pauses": 25,
                "audio_quality": "POOR",
                "snr_estimate": 8.0,
                "confidence": 0.70,
            }

    async def _simulate_processing(self):
        import asyncio
        await asyncio.sleep(0.3)
