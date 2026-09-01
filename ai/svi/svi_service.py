"""
SVI (Stress Vulnerability Index) Service
Calculates the transparent SVI score from fused features
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ai.fusion.fusion_service import FusionResult


@dataclass
class SVIComponents:
    """Individual SVI component scores"""
    distress: int = 0          # 0-20
    fear_anxiety: int = 0      # 0-15
    threat: int = 0            # 0-20
    isolation: int = 0         # 0-10
    trauma_related: int = 0    # 0-15
    audio_stress: int = 0      # 0-10
    urgency: int = 0           # 0-10
    
    def total(self) -> int:
        return sum([
            self.distress, self.fear_anxiety, self.threat,
            self.isolation, self.trauma_related, self.audio_stress, self.urgency
        ])


@dataclass
class SVIResult:
    """Complete SVI result"""
    svi_score: int  # 0-100
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    components: SVIComponents
    confidence: float
    assessment_status: str
    explanation: Dict[str, Any]
    thresholds_used: Dict[str, int]


class SVIService(ABC):
    """Abstract base class for SVI calculation services"""
    
    @abstractmethod
    def calculate(self, fusion_result: FusionResult) -> SVIResult:
        """
        Calculate SVI from fusion result
        
        Args:
            fusion_result: Result from multimodal fusion
            
        Returns:
            SVIResult with score, risk level, and explanations
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def is_demo(self) -> bool:
        pass


class DemoSVIService(SVIService):
    """Demo SVI service - prototype implementation"""
    
    def __init__(self):
        self._model_name = "DEMO-SVI-CALCULATOR"
        # Prototype thresholds (NOT clinically validated)
        self.thresholds = {
            "LOW": 25,
            "MODERATE": 50,
            "HIGH": 75,
            "CRITICAL": 100,
        }
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return True
    
    def calculate(self, fusion_result: FusionResult) -> SVIResult:
        """Calculate SVI from fusion result"""
        # Map fusion component scores to SVI components
        components = SVIComponents()
        
        # Distress (0-20) - from text emotional indicators
        text_score = fusion_result.component_scores.get("text", 0)
        components.distress = min(int(text_score * 0.2), 20)
        
        # Fear/Anxiety (0-15) - from text safety indicators
        components.fear_anxiety = min(int(text_score * 0.15), 15)
        
        # Threat (0-20) - from context threat level
        threat_score = fusion_result.component_scores.get("threat", 0)
        components.threat = min(int(threat_score * 0.2), 20)
        
        # Isolation (0-10) - from text social indicators
        components.isolation = min(int(text_score * 0.1), 10)
        
        # Trauma-related (0-15) - from text trauma indicators
        components.trauma_related = min(int(text_score * 0.15), 15)
        
        # Audio stress (0-10) - from audio features
        audio_score = fusion_result.component_scores.get("audio", 0)
        components.audio_stress = min(int(audio_score * 0.1), 10)
        
        # Urgency (0-10) - from context urgency
        vulnerability_score = fusion_result.component_scores.get("vulnerability", 0)
        components.urgency = min(int(vulnerability_score * 0.1), 10)
        
        # Calculate final SVI
        svi_score = components.total()
        
        # Scale up slightly if audio is missing so text-only can still reach 100
        if audio_score == 0 and svi_score > 0:
            svi_score = int(svi_score * (100.0 / 90.0))
            
        svi_score = min(max(svi_score, 0), 100)
        
        # Determine risk level
        risk_level = self._get_risk_level(svi_score)
        
        # Build explanation
        explanation = self._build_explanation(components, fusion_result)
        
        return SVIResult(
            svi_score=svi_score,
            risk_level=risk_level,
            components=components,
            confidence=fusion_result.confidence,
            assessment_status=fusion_result.assessment_status,
            explanation=explanation,
            thresholds_used=self.thresholds.copy(),
        )
    
    def _get_risk_level(self, svi: int) -> str:
        if svi <= self.thresholds["LOW"]:
            return "LOW"
        elif svi <= self.thresholds["MODERATE"]:
            return "MODERATE"
        elif svi <= self.thresholds["HIGH"]:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _build_explanation(self, components: SVIComponents, fusion_result: FusionResult) -> Dict[str, Any]:
        """Build human-readable explanation"""
        return {
            "component_breakdown": {
                "distress": {"score": components.distress, "max": 20},
                "fear_anxiety": {"score": components.fear_anxiety, "max": 15},
                "threat": {"score": components.threat, "max": 20},
                "isolation": {"score": components.isolation, "max": 10},
                "trauma_related": {"score": components.trauma_related, "max": 15},
                "audio_stress": {"score": components.audio_stress, "max": 10},
                "urgency": {"score": components.urgency, "max": 10},
            },
            "total_svi": f"{components.total()}/100",
            "risk_level": self._get_risk_level(components.total()),
            "confidence": f"{fusion_result.confidence:.0%}",
            "contributing_factors": fusion_result.contributing_factors,
            "weights_used": fusion_result.weights_used,
            "note": "Prototype thresholds - NOT clinically validated",
        }