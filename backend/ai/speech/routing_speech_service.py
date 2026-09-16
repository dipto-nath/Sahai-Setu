from typing import Optional
import logging
from ai.speech.speech_service import SpeechService, SpeechResult
from ai.speech.whisper_speech_service import WhisperSpeechService

logger = logging.getLogger(__name__)

class RoutingSpeechService(SpeechService):
    """Routes speech transcription to the appropriate model based on language.
    Currently uses Whisper for all languages as it provides the best baseline transcription,
    which is then translated to English by the TranslationService.
    """
    
    def __init__(self, whisper_model: str = "medium"):
        self.whisper = WhisperSpeechService(model_name=whisper_model)
        
    @property
    def model_name(self) -> str:
        return "whisper-routing-service"
        
    @property
    def is_demo(self) -> bool:
        return False
        
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> SpeechResult:
        # We use Whisper for everything now, as it provides better transcription
        # than the Wav2Vec2 models, and we handle the translation to English later in the pipeline.
        return await self.whisper.transcribe(audio_path, language)

    async def transcribe_bytes(self, audio_data: bytes, language: Optional[str] = None) -> SpeechResult:
        return await self.whisper.transcribe_bytes(audio_data, language)
