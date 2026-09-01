"""
Audio Analysis Service Interface
Modular audio feature extraction service - replaceable implementation
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AudioFeatures:
    """Extracted audio features for stress/vulnerability analysis"""
    # Prosodic features
    speech_rate: float          # Words per minute
    pause_duration_mean: float  # Average pause duration (seconds)
    pause_duration_std: float   # Std deviation of pause duration
    pitch_mean: float           # Mean fundamental frequency (Hz)
    pitch_std: float            # Std deviation of pitch
    pitch_range: float          # Pitch range (max - min)
    energy_mean: float          # Mean energy/RMS
    energy_std: float           # Std deviation of energy
    
    # Voice quality features
    jitter: float               # Pitch period variability
    shimmer: float              # Amplitude variability
    hnr: float                  # Harmonics-to-noise ratio
    
    # Spectral features
    spectral_centroid_mean: float
    spectral_centroid_std: float
    spectral_rolloff_mean: float
    spectral_bandwidth_mean: float
    
    # Voice activity
    voice_activity_ratio: float  # Ratio of voiced to total duration
    num_pauses: int
    total_duration: float
    
    # Quality assessment
    audio_quality: str          # GOOD, FAIR, POOR
    snr_estimate: float         # Signal-to-noise ratio estimate
    
    # Confidence and metadata
    confidence: float
    processing_time_ms: int
    model_name: str


class AudioService(ABC):
    """Abstract base class for audio analysis services"""
    
    @abstractmethod
    async def analyze(self, audio_path: str) -> AudioFeatures:
        """
        Analyze audio file for prosodic and acoustic features
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioFeatures with extracted features
        """
        pass
    
    @abstractmethod
    async def analyze_bytes(self, audio_data: bytes) -> AudioFeatures:
        """
        Analyze audio bytes for prosodic and acoustic features
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            AudioFeatures with extracted features
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model/library name being used"""
        pass
    
    @property
    @abstractmethod
    def is_demo(self) -> bool:
        """Return True if this is a demo/mock implementation"""
        pass