"""
Stress Vulnerability Index (SVI) Engine
Calculates the SVI score (0-100) from fused features.
SVI is calculated by backend logic - NOT by Gemini.
Uses configurable prototype thresholds.
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RiskThresholds:
    LOW_MAX: int = 24
    MODERATE_MAX: int = 49
    HIGH_MAX: int = 74
    CRITICAL_MAX: int = 100
    confidence_high: float = 0.80
    confidence_medium: float = 0.50
    confidence_low: float = 0.30
    inconclusive_threshold: float = 0.50

    def get_risk_level(self, svi: int) -> str:
        if svi <= self.LOW_MAX:
            return "LOW"
        elif svi <= self.MODERATE_MAX:
            return "MODERATE"
        elif svi <= self.HIGH_MAX:
            return "HIGH"
        else:
            return "CRITICAL"

    def get_assessment_status(self, confidence: float, svi: int) -> str:
        if confidence < self.inconclusive_threshold:
            return "INCONCLUSIVE"
        elif svi >= self.HIGH_MAX and confidence >= self.confidence_high:
            return "HUMAN_REVIEW_RECOMMENDED"
        elif svi >= self.MODERATE_MAX:
            return "REVIEW_RECOMMENDED"
        else:
            return "COMPLETED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "LOW_MAX": self.LOW_MAX,
            "MODERATE_MAX": self.MODERATE_MAX,
            "HIGH_MAX": self.HIGH_MAX,
            "CRITICAL_MAX": self.CRITICAL_MAX,
            "confidence_high": self.confidence_high,
            "confidence_medium": self.confidence_medium,
            "confidence_low": self.confidence_low,
            "inconclusive_threshold": self.inconclusive_threshold,
        }


@dataclass
class SVIResult:
    svi_score: int = 0
    risk_level: str = "LOW"
    confidence: float = 0.0
    confidence_level: str = "LOW"
    assessment_status: str = "COMPLETED"
    human_review_required: bool = False
    combined_score: float = 0.0
    component_scores: Dict[str, float] = field(default_factory=dict)
    thresholds_used: Dict[str, Any] = field(default_factory=dict)
    explanation: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SVIEngine:
    """
    Stress Vulnerability Index calculation engine.
    Calculates SVI from fusion results using backend logic only.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.thresholds = RiskThresholds()
        self.config_path = config_path
        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            thresholds = config.get("risk_thresholds", {})
            self.thresholds.LOW_MAX = thresholds.get("LOW", {}).get("max", 24)
            self.thresholds.MODERATE_MAX = thresholds.get("MODERATE", {}).get("max", 49)
            self.thresholds.HIGH_MAX = thresholds.get("HIGH", {}).get("max", 74)
            self.thresholds.CRITICAL_MAX = thresholds.get("CRITICAL", {}).get("max", 100)
            conf = config.get("confidence_thresholds", {})
            self.thresholds.confidence_high = conf.get("HIGH", 0.80)
            self.thresholds.confidence_medium = conf.get("MEDIUM", 0.50)
            self.thresholds.confidence_low = conf.get("LOW", 0.30)
            self.thresholds.inconclusive_threshold = conf.get("inconclusive_threshold", 0.50)
        except Exception as e:
            logger.warning(f"Failed to load SVI config: {e}. Using defaults.")

    def calculate(self, fusion_result) -> SVIResult:
        combined_score = getattr(fusion_result, 'combined_score', 0.0)
        if isinstance(fusion_result, dict):
            combined_score = fusion_result.get('combined_score', 0.0)
        svi_score = int(round(combined_score * 100))
        svi_score = max(0, min(100, svi_score))
        confidence = getattr(fusion_result, 'confidence', 0.0)
        if isinstance(fusion_result, dict):
            confidence = fusion_result.get('confidence', 0.0)
        risk_level = self.thresholds.get_risk_level(svi_score)
        confidence_level = self._get_confidence_level(confidence)
        assessment_status = self.thresholds.get_assessment_status(confidence, svi_score)
        human_review_required = assessment_status in ["INCONCLUSIVE", "HUMAN_REVIEW_RECOMMENDED"]
        component_scores = getattr(fusion_result, 'component_scores', {})
        if isinstance(fusion_result, dict):
            component_scores = fusion_result.get('component_scores', {})
        weights_used = getattr(fusion_result, 'weights_used', {})
        if isinstance(fusion_result, dict):
            weights_used = fusion_result.get('weights_used', {})
        contributing_factors = getattr(fusion_result, 'contributing_factors', {})
        if isinstance(fusion_result, dict):
            contributing_factors = fusion_result.get('contributing_factors', {})
        explanation = self._build_explanation(
            svi_score, risk_level, confidence, confidence_level,
            component_scores, weights_used, contributing_factors, assessment_status
        )
        return SVIResult(
            svi_score=int(svi_score),
            risk_level=str(risk_level),
            confidence=float(confidence),
            confidence_level=str(confidence_level),
            assessment_status=str(assessment_status),
            human_review_required=bool(human_review_required),
            combined_score=float(combined_score),
            component_scores={k: float(v) for k, v in component_scores.items()} if component_scores else {},
            thresholds_used=self.thresholds.to_dict(),
            explanation=explanation,
        )

    def _get_confidence_level(self, confidence: float) -> str:
        if confidence >= self.thresholds.confidence_high:
            return "HIGH"
        elif confidence >= self.thresholds.confidence_medium:
            return "MEDIUM"
        else:
            return "LOW"

    def _build_explanation(
        self, svi_score, risk_level, confidence, confidence_level,
        component_scores, weights_used, contributing_factors, assessment_status
    ):
        return {
            "svi_breakdown": {
                "raw_fusion_score": round(component_scores.get("text", 0) * weights_used.get("text", 0)
                                           + component_scores.get("context", 0) * weights_used.get("context", 0)
                                           + component_scores.get("audio", 0) * weights_used.get("audio", 0), 4),
                "scaled_to_100": svi_score,
            },
            "risk_classification": {
                "level": risk_level,
                "thresholds_note": "Prototype-configured thresholds requiring domain-expert validation. NOT clinically validated.",
            },
            "confidence_assessment": {
                "score": round(confidence, 3),
                "level": confidence_level,
            },
            "component_contributions": {
                "text": round(component_scores.get("text", 0) * weights_used.get("text", 0), 3),
                "context": round(component_scores.get("context", 0) * weights_used.get("context", 0), 3),
                "audio": round(component_scores.get("audio", 0) * weights_used.get("audio", 0), 3),
            },
            "contributing_factors": contributing_factors,
            "weights_used": weights_used,
            "assessment_status": assessment_status,
            "human_review_required": assessment_status in ["INCONCLUSIVE", "HUMAN_REVIEW_RECOMMENDED"],
            "disclaimer": "AI-Assisted Assessment - NOT a medical diagnosis. Final decisions require authorized human review.",
        }

    def update_thresholds(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.thresholds, key.upper()):
                setattr(self.thresholds, key.upper(), value)
        logger.info(f"Updated SVI thresholds: {kwargs}")


def get_svi_engine(config_path: Optional[str] = None) -> SVIEngine:
    if config_path is None:
        config_path = str(Path(__file__).parent.parent / "config" / "risk_thresholds.json")
    return SVIEngine(config_path)
