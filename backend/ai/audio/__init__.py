"""
Audio Service Registry
Factory for getting the configured audio service
"""
from typing import Optional

from ai.audio.audio_service import AudioService
from ai.audio.demo_audio_service import DemoAudioService


_audio_service: Optional[AudioService] = None


def get_audio_service() -> AudioService:
    """Get the configured audio service instance"""
    global _audio_service
    if _audio_service is None:
        from app.config import settings
        if settings.ai_provider == "local" and not settings.demo_mode:
            # Try to load real model
            try:
                from ai.audio.real_audio_service import RealAudioService
                _audio_service = RealAudioService()
            except ImportError:
                _audio_service = DemoAudioService()
        else:
            _audio_service = DemoAudioService()
    return _audio_service


def set_audio_service(service: AudioService) -> None:
    """Set the audio service (for testing or configuration)"""
    global _audio_service
    _audio_service = service