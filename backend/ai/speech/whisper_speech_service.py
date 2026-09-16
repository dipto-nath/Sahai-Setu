"""
Local Speech Service using OpenAI Whisper
Uses whisper models for local speech-to-text transcription
"""
import time
import logging
import tempfile
import os
from typing import Optional

from ai.speech.speech_service import SpeechService, SpeechResult

logger = logging.getLogger(__name__)


class WhisperSpeechService(SpeechService):
    """Real speech-to-text service using OpenAI Whisper locally"""
    
    def __init__(self, model_name: str = "base"):
        self._model_name = f"whisper-{model_name}"
        logger.info(f"Initializing Whisper Speech Service with model: {self._model_name}")
        try:
            import whisper
            import ssl
            import os
            # Ensure local ffmpeg is in PATH
            venv_bin = "/Users/diptonath/Documents/coding/nhaa-ai-triage/.venv/bin"
            if venv_bin not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
                
            # Disable SSL certificate verification for downloading models on mac
            ssl._create_default_https_context = ssl._create_unverified_context
            # Load the whisper model locally (base or small recommended for speed)
            self.model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return False
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> SpeechResult:
        """Transcribe audio file to text using Whisper"""
        start_time = time.time()
        
        try:
            # Whisper handles the audio path directly
            # We can pass language hint if available
            options = {
                "fp16": False,
                "condition_on_previous_text": False,
                "no_speech_threshold": 0.6,
                "logprob_threshold": -1.0
            }
            import asyncio
            
            if language and language != "en":
                options["language"] = language
                # Force translation to English to prevent Indic script hallucination
                # and to ensure compatibility with the English-only NLP pipeline
                options["task"] = "translate"
                
            # Run the CPU-bound transcription in a thread to prevent blocking the FastAPI event loop
            result = await asyncio.to_thread(self.model.transcribe, audio_path, **options)
            
            transcript = result["text"].strip() if "text" in result else "[inaudible]"
            processing_time = int((time.time() - start_time) * 1000)
            
            # Extract detected language if available
            detected_lang = result.get("language", language or "en")
            
            return SpeechResult(
                transcript=transcript,
                language=detected_lang,
                language_confidence=0.90,
                confidence=0.90, # Whisper doesn't provide aggregate confidence natively easily, assuming high
                duration_seconds=0.0, # We'll rely on the audio feature extractor for duration
                processing_time_ms=processing_time,
                model_name=self._model_name,
            )
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            processing_time = int((time.time() - start_time) * 1000)
            return SpeechResult(
                transcript="[transcription failed]",
                language=language or "en",
                language_confidence=0.0,
                confidence=0.0,
                duration_seconds=0.0,
                processing_time_ms=processing_time,
                model_name=self._model_name,
            )
    
    async def transcribe_bytes(self, audio_data: bytes, language: Optional[str] = None) -> SpeechResult:
        """Transcribe audio bytes to text using Whisper"""
        if not audio_data or len(audio_data) < 100:
            return SpeechResult(
                transcript="",
                language=language or "en",
                language_confidence=0.0,
                confidence=0.0,
                duration_seconds=0.0,
                processing_time_ms=0,
                model_name=self._model_name,
            )
            
        # Whisper requires a file on disk or a numpy array
        # Using .tmp suffix allows FFmpeg to auto-probe the format (e.g. mp4 from Safari or webm from Chrome)
        try:
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
                
            result = await self.transcribe(tmp_path, language)
            
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
                
            return result
        except Exception as e:
            logger.error(f"Failed to process audio bytes for Whisper: {e}")
            return SpeechResult(
                transcript="[transcription failed]",
                language=language or "en",
                language_confidence=0.0,
                confidence=0.0,
                duration_seconds=0.0,
                processing_time_ms=0,
                model_name=self._model_name,
            )
