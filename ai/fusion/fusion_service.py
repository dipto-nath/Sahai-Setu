"""
Multimodal Fusion Service
Combines text, audio, and context features into unified assessment
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ai.nlp.nlp_service import NLPFeatures
from ai.audio.audio_service import AudioFeatures


@dataclass
class ContextFeatures:
    """Contextual features from case metadata"""
    threat_level: float = 0.0
    vulnerability_level: float = 0.0
    urgency_level: float = 0.0
    language_confidence: float = 1.0
    text_quality: float = 1.0
    audio_quality: float = 1.0
    case_history_risk: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FusionResult:
    """Result of multimodal fusion"""
    component_scores: Dict[str, float]  # text, audio, threat, vulnerability
    final_svi: int  # 0-100
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    confidence: float
    contributing_factors: Dict[str, Any]
    weights_used: Dict[str, float]
    assessment_status: str  # COMPLETED, REVIEW_RECOMMENDED, INCONCLUSIVE
    processing_time_ms: int
    model_name: str


class FusionService(ABC):
    """Abstract base class for multimodal fusion services"""
    
    @abstractmethod
    async def fuse(
        self,
        text_features: Optional[NLPFeatures],
        audio_features: Optional[AudioFeatures],
        context_features: Optional[ContextFeatures]
    ) -> FusionResult:
        """
        Fuse multimodal features into unified assessment
        
        Args:
            text_features: NLP features from text analysis
            audio_features: Audio features from prosodic analysis
            context_features: Contextual features from case metadata
            
        Returns:
            FusionResult with SVI, risk level, and explanations
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name being used"""
        pass
    
    @property
    @abstractmethod
    def is_demo(self) -> bool:
        """Return True if this is a demo/mock implementation"""
        pass