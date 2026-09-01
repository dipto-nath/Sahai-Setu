"""
Multimodal Fusion Engine
Combines normalized text, context, and audio features.
Weights are configurable.
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FusionWeights:
    voice_text_weight: float = 0.40
    voice_context_weight: float = 0.35
    voice_audio_weight: float = 0.25
    text_only_text_weight: float = 0.50
    text_only_context_weight: float = 0.50
    text_only_audio_weight: float = 0.0

    def get_weights(self, has_audio):
        if has_audio:
            return {"text": self.voice_text_weight,
                    "context": self.voice_context_weight,
                    "audio": self.voice_audio_weight}
        return {"text": self.text_only_text_weight,
                "context": self.text_only_context_weight,
                "audio": self.text_only_audio_weight}


@dataclass
class FusionResult:
    combined_score: float = 0.0
    component_scores: Dict[str, float] = field(default_factory=dict)
    weights_used: Dict[str, float] = field(default_factory=dict)
    has_audio: bool = False
    modality: str = "text_only"
    confidence: float = 0.0
    contributing_factors: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


class FusionEngine:
    def __init__(self, config_path: Optional[str] = None):
        self.weights = FusionWeights()
        self.config_path = config_path
        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            v = config.get("voice_interaction", {})
            t = config.get("text_only_interaction", {})
            self.weights.voice_text_weight = v.get("text_nlp_weight", 0.40)
            self.weights.voice_context_weight = v.get("context_nlp_weight", 0.35)
            self.weights.voice_audio_weight = v.get("audio_weight", 0.25)
            self.weights.text_only_text_weight = t.get("text_nlp_weight", 0.50)
            self.weights.text_only_context_weight = t.get("context_nlp_weight", 0.50)
            self.weights.text_only_audio_weight = t.get("audio_weight", 0.0)
        except Exception as e:
            logger.warning(f"Failed to load fusion config: {e}")

    def fuse(self, text_score, context_score, audio_score, has_audio=False,
             text_features=None, context_features=None, audio_features=None,
             input_quality=None):
        weights = self.weights.get_weights(has_audio)
        combined = (text_score * weights["text"]
                    + context_score * weights["context"]
                    + audio_score * weights["audio"])
        combined = max(0.0, min(1.0, combined))
        modality = "voice" if has_audio else "text_only"
        factors = self._build_factors(text_features, context_features, audio_features, weights)
        confidence = self._calculate_confidence(text_score, context_score, audio_score, has_audio, input_quality)
        return FusionResult(
            combined_score=combined,
            component_scores={"text": text_score, "context": context_score, "audio": audio_score},
            weights_used=weights,
            has_audio=has_audio,
            modality=modality,
            confidence=confidence,
            contributing_factors=factors,
        )

    def _build_factors(self, text_features, context_features, audio_features, weights):
        factors = {
            "text_indicators": [],
            "context_indicators": [],
            "audio_indicators": [],
            "weight_contribution": weights,
        }
        if text_features:
            for name, key in [("fear", "fear_signal"), ("distress", "distress_signal"),
                              ("threat", "threat_context_signal"), ("isolation", "isolation_signal"),
                              ("urgency", "urgency_signal")]:
                v = text_features.get(key, 0)
                if v > 0.5:
                    factors["text_indicators"].append({
                        "indicator": name, "severity": "HIGH" if v > 0.7 else "MODERATE",
                        "score": round(v, 3),
                    })
        if context_features:
            for name, key in [("fear", "fear"), ("distress", "distress"),
                              ("threat_context", "threat_context"), ("social_isolation", "social_isolation"),
                              ("vulnerability", "vulnerability"), ("urgency", "urgency")]:
                v = context_features.get(key, 0)
                if v > 0.3:
                    factors["context_indicators"].append({
                        "indicator": name, "severity": "HIGH" if v > 0.6 else "MODERATE",
                        "score": round(v, 3),
                    })
        if audio_features:
            if audio_features.get("pause_score", 0) > 0.6:
                factors["audio_indicators"].append({
                    "indicator": "prolonged_pauses",
                    "severity": "HIGH" if audio_features["pause_score"] > 0.8 else "MODERATE",
                    "score": round(audio_features["pause_score"], 3),
                })
            if audio_features.get("voice_activity_score", 1.0) < 0.5:
                factors["audio_indicators"].append({
                    "indicator": "low_voice_activity",
                    "severity": "HIGH" if audio_features["voice_activity_score"] < 0.3 else "MODERATE",
                    "score": round(1.0 - audio_features["voice_activity_score"], 3),
                })
        return factors

    def _calculate_confidence(self, text_score, context_score, audio_score, has_audio, input_quality):
        base = 0.7
        if input_quality:
            base = input_quality.get("completeness", 0.7)
        scores = [text_score, context_score]
        if has_audio:
            scores.append(audio_score)
        try:
            import numpy as np
            var = np.var(scores) if len(scores) > 1 else 0.0
        except ImportError:
            mean = sum(scores) / len(scores)
            var = sum((s - mean) ** 2 for s in scores) / len(scores)
        agreement = max(0.0, 1.0 - var * 4)
        return max(0.0, min(1.0, (base + agreement) / 2.0))


def get_fusion_engine(config_path=None):
    if config_path is None:
        config_path = str(Path(__file__).parent.parent / "config" / "model_weights.json")
    return FusionEngine(config_path)
