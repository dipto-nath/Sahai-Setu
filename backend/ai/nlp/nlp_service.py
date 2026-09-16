"""
NLP Service Interface
Modular NLP analysis service - replaceable implementation
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class NLPFeatures:
    """Structured NLP features extracted from text"""
    emotional_indicators: Dict[str, float]  # fear, anxiety, sadness, anger, distress
    safety_indicators: Dict[str, float]     # threat, intimidation, ongoing_danger, family_safety
    social_indicators: Dict[str, float]     # isolation, displacement, social_boycott, lack_of_support
    trauma_indicators: Dict[str, float]     # severe_distress, traumatic_events, repeated_fear, difficulty_communicating
    confidence: float
    language_detected: str
    language_confidence: float
    text_length: int
    processing_time_ms: int


class NLPService(ABC):
    """Abstract base class for NLP services"""
    
    @abstractmethod
    async def analyze(self, text: str, language: Optional[str] = None) -> NLPFeatures:
        """Analyze text for psychological indicators"""
        pass
    
    @abstractmethod
    async def detect_language(self, text: str) -> tuple[str, float]:
        """Detect language of text"""
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