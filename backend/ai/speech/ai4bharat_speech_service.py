import time
import logging
import os
import tempfile
from typing import Optional
import asyncio
import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

from ai.speech.speech_service import SpeechService, SpeechResult

logger = logging.getLogger(__name__)

class AI4BharatSpeechService(SpeechService):
    """Speech service that uses AI4Bharat Wav2Vec2 models via Hugging Face Transformers"""
    
    def __init__(self, default_model: str = "arijitx/wav2vec2-large-xlsr-bengali"):
        self._model_name = default_model
        logger.info(f"Initializing AI4Bharat Speech Service with model: {self._model_name}")
        
        # Load processor and model
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(self._model_name)
            self.model = Wav2Vec2ForCTC.from_pretrained(self._model_name)
            self.device = torch.device("cpu")
            self.model.to(self.device)
            logger.info("AI4Bharat model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load AI4Bharat model: {e}")
            raise e

    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return False
        
    def _process_audio(self, audio_path: str) -> str:
        """Synchronous CPU-bound processing method"""
        try:
            import subprocess
            import tempfile
            
            # Use ffmpeg to convert webm/mp4 to 16kHz mono wav for librosa
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                wav_path = tmp_wav.name
                
            try:
                subprocess.run([
                    "ffmpeg", "-y", "-i", audio_path, 
                    "-ac", "1", "-ar", "16000", "-f", "wav", wav_path
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # AI4Bharat models expect 16kHz mono audio
                speech_array, sampling_rate = librosa.load(wav_path, sr=16000)
            finally:
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
            
            # Preprocess the input
            inputs = self.processor(speech_array, sampling_rate=16000, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Perform inference
            with torch.no_grad():
                logits = self.model(inputs["input_values"], attention_mask=inputs.get("attention_mask")).logits
                
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]
            
            return transcription
        except Exception as e:
            logger.error(f"Error in _process_audio: {e}")
            raise e
            
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> SpeechResult:
        """Transcribe audio file to text using AI4Bharat model"""
        start_time = time.time()
        
        try:
            # Run the CPU-bound transcription in a thread
            transcription = await asyncio.to_thread(self._process_audio, audio_path)
            
            transcript = transcription.strip() if transcription else "[inaudible]"
            processing_time = int((time.time() - start_time) * 1000)
            
            return SpeechResult(
                transcript=transcript,
                language=language or "bn",
                language_confidence=0.90,
                confidence=0.85, # AI4Bharat baseline confidence
                duration_seconds=0.0,
                processing_time_ms=processing_time,
                model_name=self._model_name,
            )
            
        except Exception as e:
            logger.error(f"AI4Bharat transcription failed: {e}")
            processing_time = int((time.time() - start_time) * 1000)
            return SpeechResult(
                transcript="[transcription failed]",
                language=language or "bn",
                language_confidence=0.0,
                confidence=0.0,
                duration_seconds=0.0,
                processing_time_ms=processing_time,
                model_name=self._model_name,
            )
            
    async def transcribe_bytes(self, audio_data: bytes, language: Optional[str] = None) -> SpeechResult:
        """Transcribe audio bytes to text using AI4Bharat model"""
        if not audio_data or len(audio_data) < 100:
            return SpeechResult(
                transcript="",
                language=language or "bn",
                language_confidence=0.0,
                confidence=0.0,
                duration_seconds=0.0,
                processing_time_ms=0,
                model_name=self._model_name,
            )
            
        try:
            # Save audio bytes to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
                
            result = await self.transcribe(tmp_path, language)
            
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
            return result
        except Exception as e:
            logger.error(f"Failed to process audio bytes for AI4Bharat: {e}")
            return SpeechResult(
                transcript="[transcription failed]",
                language=language or "bn",
                language_confidence=0.0,
                confidence=0.0,
                duration_seconds=0.0,
                processing_time_ms=0,
                model_name=self._model_name,
            )
