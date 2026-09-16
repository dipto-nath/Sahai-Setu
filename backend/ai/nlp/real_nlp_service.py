"""
Gemini NLP Service
Implementation using Google GenAI SDK for text classification
"""
import time
import json
import logging
from typing import Optional
from langdetect import detect, detect_langs
from google import genai
from google.genai import types

from ai.nlp.nlp_service import NLPService, NLPFeatures

logger = logging.getLogger(__name__)

class RealNLPService(NLPService):
    """Real NLP service using Gemini API"""
    
    def __init__(self, api_key: str):
        self._model_name = "gemini-3.6-flash"
        logger.info(f"Initializing Gemini NLP Service with model: {self._model_name}")
        
        try:
            self.client = genai.Client(api_key=api_key)
            logger.info("Successfully configured Gemini API.")
        except Exception as e:
            logger.error(f"Failed to initialize google-genai client: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return False
        
    async def detect_language(self, text: str) -> tuple[str, float]:
        try:
            langs = detect_langs(text)
            if langs:
                top_lang = langs[0]
                return top_lang.lang, top_lang.prob
            return "en", 1.0
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en", 0.5

    async def analyze(self, text: str, language: Optional[str] = None) -> NLPFeatures:
        start_time = time.time()
        
        if not text or not text.strip():
            return self._empty_features()

        if language is None:
            language, lang_conf = await self.detect_language(text)
        else:
            lang_conf = 0.95
            
        prompt = f"""
You are an expert psychological and safety triage AI. Analyze the following victim statement and rate the presence of specific indicators on a scale from 0.0 (not present at all) to 1.0 (extremely evident).

Victim Statement:
"{text}"

Output strictly valid JSON with the following schema:
{{
    "emotional": {{"fear": float, "anxiety": float, "sadness": float, "anger": float, "distress": float}},
    "safety": {{"threat": float, "intimidation": float, "ongoing_danger": float, "family_safety": float}},
    "social": {{"isolation": float, "displacement": float, "social_boycott": float, "lack_of_support": float}},
    "trauma": {{"severe_distress": float, "traumatic_events": float, "repeated_fear": float, "difficulty_communicating": float}}
}}
Return ONLY the JSON. No markdown formatting or backticks.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            response_text = response.text.strip()
            
            scores = json.loads(response_text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return NLPFeatures(
                emotional_indicators=scores.get("emotional", self._empty_features().emotional_indicators),
                safety_indicators=scores.get("safety", self._empty_features().safety_indicators),
                social_indicators=scores.get("social", self._empty_features().social_indicators),
                trauma_indicators=scores.get("trauma", self._empty_features().trauma_indicators),
                confidence=0.90, 
                language_detected=language,
                language_confidence=lang_conf,
                text_length=len(text),
                processing_time_ms=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Error during Gemini NLP inference: {e}")
            return self._empty_features()
            
    def _empty_features(self) -> NLPFeatures:
        return NLPFeatures(
            emotional_indicators={"fear": 0.0, "anxiety": 0.0, "sadness": 0.0, "anger": 0.0, "distress": 0.0},
            safety_indicators={"threat": 0.0, "intimidation": 0.0, "ongoing_danger": 0.0, "family_safety": 0.0},
            social_indicators={"isolation": 0.0, "displacement": 0.0, "social_boycott": 0.0, "lack_of_support": 0.0},
            trauma_indicators={"severe_distress": 0.0, "traumatic_events": 0.0, "repeated_fear": 0.0, "difficulty_communicating": 0.0},
            confidence=0.0,
            language_detected="en",
            language_confidence=0.0,
            text_length=0,
            processing_time_ms=0,
        )
