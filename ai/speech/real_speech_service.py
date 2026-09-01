"""
Real Speech Service using Gemini
Uses Gemini's multimodal capabilities for speech-to-text transcription
"""
import time
import base64
import logging
from typing import Optional
from google import genai
from google.genai import types

from ai.speech.speech_service import SpeechService, SpeechResult

logger = logging.getLogger(__name__)


class RealSpeechService(SpeechService):
    """Real speech-to-text service using Gemini's audio understanding"""
    
    def __init__(self, api_key: str):
        self._model_name = "gemini-3.6-flash"
        try:
            self.client = genai.Client(api_key=api_key)
            logger.info(f"Initialized Gemini Speech Service with model: {self._model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Speech client: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return False
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> SpeechResult:
        """Transcribe audio file to text"""
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        return await self.transcribe_bytes(audio_data, language)
    
    async def transcribe_bytes(self, audio_data: bytes, language: Optional[str] = None) -> SpeechResult:
        """Transcribe audio bytes to text using Gemini multimodal"""
        start_time = time.time()
        
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
        
        lang_hint = f" The audio is in {language} language." if language and language != "en" else ""
        
        prompt = f"""Transcribe the following audio recording exactly as spoken. 
Output ONLY the transcribed text, nothing else. No labels, no timestamps, no formatting.
If the audio is unclear or empty, output: [inaudible]{lang_hint}"""
        
        try:
            # Encode audio as base64 for Gemini
            audio_b64 = base64.b64encode(audio_data).decode("utf-8")
            
            # Detect mime type from audio data header
            mime_type = "audio/webm"
            if audio_data[:4] == b"RIFF":
                mime_type = "audio/wav"
            elif audio_data[:3] == b"ID3" or audio_data[:2] == b"\xff\xfb":
                mime_type = "audio/mp3"
            elif audio_data[:4] == b"fLaC":
                mime_type = "audio/flac"
            
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(data=audio_data, mime_type=mime_type),
                        ]
                    )
                ],
            )
            
            transcript = response.text.strip() if response.text else "[inaudible]"
            processing_time = int((time.time() - start_time) * 1000)
            
            # Estimate duration from data size (rough: ~16kbps for webm opus)
            estimated_duration = len(audio_data) / 2000.0
            
            return SpeechResult(
                transcript=transcript,
                language=language or "en",
                language_confidence=0.90,
                confidence=0.92,
                duration_seconds=estimated_duration,
                processing_time_ms=processing_time,
                model_name=self._model_name,
            )
            
        except Exception as e:
            logger.error(f"Gemini speech transcription failed: {e}")
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
