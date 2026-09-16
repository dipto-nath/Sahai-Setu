"""
Speech Service Interface
Modular speech-to-text service - replaceable implementation
"""
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class SpeechResult:
    """Result of speech-to-text processing"""
    transcript: str
    language: str
    language_confidence: float
    confidence: float
    duration_seconds: float
    processing_time_ms: int
    model_name: str


class SpeechService(ABC):
    """Abstract base class for speech-to-text services"""
    
    @abstractmethod
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> SpeechResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (auto-detected if not provided)
            
        Returns:
            SpeechResult with transcript and metadata
        """
        pass
    
    @abstractmethod
    async def transcribe_bytes(self, audio_data: bytes, language: Optional[str] = None) -> SpeechResult:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language code
            
        Returns:
            SpeechResult with transcript and metadata
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