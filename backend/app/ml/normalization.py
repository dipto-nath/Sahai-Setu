"""
Feature Normalization Module
Converts features from different sources into a common scale (0.0 to 1.0).
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class NormalizedTextFeatures:
    fear_signal: float = 0.0
    distress_signal: float = 0.0
    threat_context_signal: float = 0.0
    isolation_signal: float = 0.0
    urgency_signal: float = 0.0
    repetition_score: float = 0.0
    text_length: int = 0
    language: str = "en"
    language_confidence: float = 0.0
    text_score: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class NormalizedContextFeatures:
    fear: float = 0.0
    distress: float = 0.0
    threat_context: float = 0.0
    social_isolation: float = 0.0
    vulnerability: float = 0.0
    urgency: float = 0.0
    human_review_recommended: bool = False
    explanation: str = ""
    context_score: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class NormalizedAudioFeatures:
    speech_rate_score: float = 0.5
    pause_score: float = 0.5
    pitch_variation_score: float = 0.5
    energy_variation_score: float = 0.5
    voice_activity_score: float = 0.5
    audio_quality_score: float = 0.5
    duration_seconds: float = 0.0
    snr_estimate: float = 0.0
    confidence: float = 0.0
    model_name: str = ""
    audio_score: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class InputQualityMetrics:
    text_quality: float = 1.0
    audio_quality: float = 1.0
    transcription_quality: float = 1.0
    language_confidence: float = 1.0
    completeness: float = 1.0
    has_text: bool = False
    has_audio: bool = False
    has_transcript: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class NormalizedFeatureSet:
    text_features: NormalizedTextFeatures = field(default_factory=NormalizedTextFeatures)
    context_features: NormalizedContextFeatures = field(default_factory=NormalizedContextFeatures)
    audio_features: NormalizedAudioFeatures = field(default_factory=NormalizedAudioFeatures)
    input_quality: InputQualityMetrics = field(default_factory=InputQualityMetrics)

    def to_dict(self):
        return {
            "text_features": self.text_features.to_dict(),
            "context_features": self.context_features.to_dict(),
            "audio_features": self.audio_features.to_dict(),
            "input_quality": self.input_quality.to_dict(),
        }


class FeatureNormalizer:
    def __init__(self):
        self.text_weight = 1.0
        self.context_weight = 1.0
        self.audio_weight = 1.0

    def _clamp(self, value, min_v=0.0, max_v=1.0):
        return max(min_v, min(max_v, value))

    def normalize_text_features(self, raw: Dict[str, Any]) -> NormalizedTextFeatures:
        n = NormalizedTextFeatures()
        n.fear_signal = self._clamp(raw.get("fear_signal", 0.0))
        n.distress_signal = self._clamp(raw.get("distress_signal", 0.0))
        n.threat_context_signal = self._clamp(raw.get("threat_context_signal", 0.0))
        n.isolation_signal = self._clamp(raw.get("isolation_signal", 0.0))
        n.urgency_signal = self._clamp(raw.get("urgency_signal", 0.0))
        n.repetition_score = self._clamp(raw.get("repetition_score", 0.0))
        n.text_length = raw.get("text_length", 0)
        n.language = raw.get("language", "en")
        n.language_confidence = self._clamp(raw.get("language_confidence", 0.0))
        n.text_score = (
            n.fear_signal * 0.25 + n.distress_signal * 0.25
            + n.threat_context_signal * 0.20 + n.isolation_signal * 0.15
            + n.urgency_signal * 0.10 + n.repetition_score * 0.05
        )
        return n

    def normalize_context_features(self, gemini_resp: Dict[str, Any]) -> NormalizedContextFeatures:
        n = NormalizedContextFeatures()
        sev_map = {"none": 0.0, "low": 0.25, "moderate": 0.5, "high": 0.75, "critical": 1.0}
        cats = [("fear", "fear"), ("distress", "distress"),
                ("threat_context", "threat_context"), ("social_isolation", "social_isolation"),
                ("vulnerability", "vulnerability"), ("urgency", "urgency")]
        total_w, total_c = 0.0, 0.0
        for key, attr in cats:
            if key in gemini_resp:
                d = gemini_resp[key]
                sev = d.get("severity", "none").lower() if isinstance(d, dict) else "none"
                conf = self._clamp(d.get("confidence", 0.0) if isinstance(d, dict) else 0.0)
                val = sev_map.get(sev, 0.0) * conf
                setattr(n, attr, val)
                total_w += val
                total_c += conf
        n.human_review_recommended = gemini_resp.get("human_review_recommended", False)
        n.explanation = gemini_resp.get("explanation", "")
        n.context_score = total_w / total_c if total_c > 0 else 0.0
        return n

    def normalize_audio_features(self, raw: Dict[str, Any]) -> NormalizedAudioFeatures:
        n = NormalizedAudioFeatures()
        n.speech_rate_score = self._clamp(raw.get("speech_rate_score", 0.5))
        n.pause_score = self._clamp(raw.get("pause_score", 0.5))
        n.pitch_variation_score = self._clamp(raw.get("pitch_variation_score", 0.5))
        n.energy_variation_score = self._clamp(raw.get("energy_variation_score", 0.5))
        n.voice_activity_score = self._clamp(raw.get("voice_activity_score", 0.5))
        n.audio_quality_score = self._clamp(raw.get("audio_quality_score", 0.5))
        n.duration_seconds = raw.get("duration_seconds", 0.0)
        n.snr_estimate = raw.get("snr_estimate", 0.0)
        n.confidence = self._clamp(raw.get("confidence", 0.0))
        n.model_name = raw.get("model_name", "")
        voice_stress = 1.0 - n.voice_activity_score
        n.audio_score = (
            n.pause_score * 0.25 + n.pitch_variation_score * 0.20
            + n.energy_variation_score * 0.15 + voice_stress * 0.20
            + n.audio_quality_score * 0.20
        )
        return n

    def calculate_input_quality(self, text_features=None, audio_features=None, transcription_confidence=0.0):
        q = InputQualityMetrics()
        if text_features and text_features.text_length > 0:
            q.has_text = True
            length_score = min(1.0, text_features.text_length / 200.0)
            q.text_quality = (length_score + text_features.language_confidence) / 2.0
        if audio_features and audio_features.duration_seconds > 0:
            q.has_audio = True
            q.audio_quality = audio_features.audio_quality_score
        if transcription_confidence > 0:
            q.has_transcript = True
            q.transcription_quality = self._clamp(transcription_confidence)
        modalities = sum([q.has_text, q.has_audio, q.has_transcript])
        q.completeness = modalities / 3.0
        if text_features:
            q.language_confidence = text_features.language_confidence
        return q

    def normalize_all(self, text_features=None, gemini_response=None,
                      audio_features=None, transcription_confidence=0.0):
        result = NormalizedFeatureSet()
        if text_features:
            result.text_features = self.normalize_text_features(text_features)
        if gemini_response:
            result.context_features = self.normalize_context_features(gemini_response)
        if audio_features:
            result.audio_features = self.normalize_audio_features(audio_features)
        result.input_quality = self.calculate_input_quality(
            result.text_features, result.audio_features, transcription_confidence
        )
        return result


def get_feature_normalizer():
    return FeatureNormalizer()
