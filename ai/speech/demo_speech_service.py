"""
Demo Speech Service
Mock implementation for demonstration purposes
"""
import time
import random
from typing import Optional

from ai.speech.speech_service import SpeechService, SpeechResult


class DemoSpeechService(SpeechService):
    """Demo/Mock speech service for demonstration purposes - CLEARLY LABELED AS DEMO"""
    
    def __init__(self):
        self._model_name = "DEMO-SPEECH-TO-TEXT"
        # Demo transcripts for different scenarios
        self.demo_transcripts = {
            "low": "Hello, I am calling to inquire about the process for filing a complaint. I would like to know what documents are required.",
            "moderate": "I am feeling very worried and anxious about my situation. I have been facing discrimination at my workplace and I don't know what to do. I feel alone and helpless.",
            "high": "I am afraid to go back to my village. They have threatened to kill me and my family. I have been socially boycotted and no one is helping me. I am terrified for my safety.",
            "critical": "They raped my daughter and killed my husband. The police are not helping us. The upper caste people are threatening to burn our house. We have nowhere to go. I am begging for help.",
        }
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return True
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> SpeechResult:
        """Mock transcription - returns a demo transcript based on filename or random"""
        start_time = time.time()
        
        # Simulate processing delay
        await self._simulate_processing()
        
        # Determine which demo transcript to use based on filename or random
        scenario = "moderate"
        if "low" in audio_path.lower():
            scenario = "low"
        elif "high" in audio_path.lower():
            scenario = "high"
        elif "critical" in audio_path.lower():
            scenario = "critical"
        else:
            scenario = random.choice(list(self.demo_transcripts.keys()))
        
        transcript = self.demo_transcripts[scenario]
        duration = random.uniform(5.0, 30.0)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return SpeechResult(
            transcript=transcript,
            language=language or "en",
            language_confidence=0.95,
            confidence=0.88,
            duration_seconds=duration,
            processing_time_ms=processing_time,
            model_name=self._model_name,
        )
    
    async def transcribe_bytes(self, audio_data: bytes, language: Optional[str] = None) -> SpeechResult:
        """Mock transcription from bytes"""
        start_time = time.time()
        
        # Simulate processing delay
        await self._simulate_processing()
        
        # Random demo transcript
        scenario = random.choice(list(self.demo_transcripts.keys()))
        transcript = self.demo_transcripts[scenario]
        duration = random.uniform(5.0, 30.0)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return SpeechResult(
            transcript=transcript,
            language=language or "en",
            language_confidence=0.95,
            confidence=0.88,
            duration_seconds=duration,
            processing_time_ms=processing_time,
            model_name=self._model_name,
        )
    
    async def _simulate_processing(self):
        """Simulate processing time"""
        import asyncio
        await asyncio.sleep(0.5)  # Simulate 500ms processing