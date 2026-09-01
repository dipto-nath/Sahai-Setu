"""
Confidence Engine
Calculates confidence scores for AI-assisted assessments.
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceFactors:
    input_completeness: float = 1.0
    audio_quality: float = 1.0
    transcription_quality: float = 1.0
    language_confidence: float = 1.0
    component_agreement: float = 1.0
    gemini_response_validity: float = 1.0
    text_length_sufficiency: float = 1.0

    def to_dict(self):
        return asdict(self)


@dataclass
class ConfidenceResult:
    assessment_confidence: float = 0.0
    confidence_percentage: int = 0
    confidence_level: str = "LOW"
    inconclusive: bool = False
    human_review_required: bool = False
    factors: ConfidenceFactors = field(default_factory=ConfidenceFactors)
    reason: str = ""

    def to_dict(self):
        return asdict(self)


class ConfidenceEngine:
    def __init__(self, config_path=None):
        self.high_confidence_threshold = 0.80
        self.medium_confidence_threshold = 0.50
        self.low_confidence_threshold = 0.30
        self.inconclusive_threshold = 0.50
        self.weights = {
            "input_completeness": 0.20,
            "audio_quality": 0.10,
            "transcription_quality": 0.10,
            "language_confidence": 0.10,
            "component_agreement": 0.25,
            "gemini_response_validity": 0.15,
            "text_length_sufficiency": 0.10,
        }
        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            conf = config.get("confidence_thresholds", {})
            self.high_confidence_threshold = conf.get("HIGH", 0.80)
            self.medium_confidence_threshold = conf.get("MEDIUM", 0.50)
            self.low_confidence_threshold = conf.get("LOW", 0.30)
            self.inconclusive_threshold = conf.get("inconclusive_threshold", 0.50)
        except Exception as e:
            logger.warning(f"Failed to load confidence config: {e}")

    def calculate(self, text_features=None, audio_features=None, context_features=None,
                  input_quality=None, gemini_response=None, transcription_confidence=0.0):
        factors = ConfidenceFactors()
        factors.input_completeness = self._input_completeness(text_features, audio_features, gemini_response)
        if audio_features:
            factors.audio_quality = audio_features.get("audio_quality_score", 0.5)
        factors.transcription_quality = transcription_confidence if transcription_confidence > 0 else 1.0
        if text_features:
            factors.language_confidence = text_features.get("language_confidence", 0.5)
        if input_quality:
            factors.language_confidence = input_quality.get("language_confidence", factors.language_confidence)
        factors.component_agreement = self._component_agreement(text_features, context_features, audio_features)
        factors.gemini_response_validity = self._validate_gemini(gemini_response)
        if text_features:
            text_len = text_features.get("text_length", 0)
            factors.text_length_sufficiency = min(1.0, text_len / 50.0) if text_len > 0 else 0.3
        else:
            factors.text_length_sufficiency = 0.5

        confidence = sum(
            getattr(factors, k) * w for k, w in self.weights.items()
        )
        confidence = max(0.0, min(1.0, confidence))
        if confidence >= self.high_confidence_threshold:
            confidence_level = "HIGH"
        elif confidence >= self.medium_confidence_threshold:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        inconclusive = confidence < self.inconclusive_threshold
        return ConfidenceResult(
            assessment_confidence=float(round(confidence, 3)),
            confidence_percentage=int(round(confidence * 100)),
            confidence_level=str(confidence_level),
            inconclusive=bool(inconclusive),
            human_review_required=bool(inconclusive),
            factors=factors,
            reason=str(self._build_reason(factors, inconclusive)),
        )

    def _input_completeness(self, text_features, audio_features, gemini_response):
        score = 0.0
        if text_features and text_features.get("text_length", 0) > 0:
            score += 0.4
        if audio_features and audio_features.get("duration_seconds", 0) > 0:
            score += 0.3
        if gemini_response:
            score += 0.3
        return min(1.0, score)

    def _component_agreement(self, text_features, context_features, audio_features):
        scores = []
        if text_features and text_features.get("text_score"):
            scores.append(text_features.get("text_score", 0.0))
        if context_features and context_features.get("context_score"):
            scores.append(context_features.get("context_score", 0.0))
        if audio_features and audio_features.get("audio_score"):
            scores.append(audio_features.get("audio_score", 0.0))
        if len(scores) < 2:
            return 0.7
        import numpy as np
        variance = np.var(scores)
        return max(0.0, 1.0 - variance * 4)

    def _validate_gemini(self, gemini_response):
        if not gemini_response:
            return 0.3
        required = ["fear", "distress", "threat_context", "social_isolation", "urgency"]
        present = sum(1 for c in required if c in gemini_response)
        return present / len(required)

    def _build_reason(self, factors, inconclusive):
        reasons = []
        if inconclusive:
            reasons.append("Assessment is inconclusive - human review required")
        if factors.input_completeness < 0.7:
            reasons.append("Incomplete input data")
        if factors.audio_quality < 0.5:
            reasons.append("Low audio quality")
        if factors.text_length_sufficiency < 0.5:
            reasons.append("Text input too short")
        if not reasons:
            reasons.append("Confidence within acceptable range")
        return "; ".join(reasons)


def get_confidence_engine(config_path=None):
    if config_path is None:
        config_path = str(Path(__file__).parent.parent / "config" / "risk_thresholds.json")
    return ConfidenceEngine(config_path)
