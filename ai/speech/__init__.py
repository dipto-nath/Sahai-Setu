"""
Speech Service Registry
Factory for getting the configured speech service
"""
from typing import Optional

from ai.speech.speech_service import SpeechService
from ai.speech.demo_speech_service import DemoSpeechService


_speech_service: Optional[SpeechService] = None


def get_speech_service() -> SpeechService:
    """Get the configured speech service instance"""
    global _speech_service
    if _speech_service is None:
        from app.config import settings
        
        try:
            from ai.speech.routing_speech_service import RoutingSpeechService
            _speech_service = RoutingSpeechService(whisper_model=settings.speech_model_name)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to load WhisperSpeechService: {e}, attempting Gemini fallback")
            
            if not settings.demo_mode and settings.ai_api_key:
                try:
                    from ai.speech.real_speech_service import RealSpeechService
                    _speech_service = RealSpeechService(api_key=settings.ai_api_key)
                except Exception as e2:
                    logging.getLogger(__name__).warning(f"Failed to load RealSpeechService: {e2}, falling back to demo")
                    _speech_service = DemoSpeechService()
            else:
                _speech_service = DemoSpeechService()
    return _speech_service


def set_speech_service(service: SpeechService) -> None:
    """Set the speech service (for testing or configuration)"""
    global _speech_service
    _speech_service = service