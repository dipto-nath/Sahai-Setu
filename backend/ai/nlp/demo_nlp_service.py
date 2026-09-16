"""
Demo NLP Service
Rule-based mock implementation for demonstration purposes
"""
import time
from typing import Optional

from ai.nlp.nlp_service import NLPService, NLPFeatures


class DemoNLPService(NLPService):
    """Demo/Mock NLP service for demonstration purposes - CLEARLY LABELED AS DEMO"""
    
    def __init__(self):
        self._model_name = "DEMO-RULE-BASED-ANALYSIS"
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return True
    
    async def detect_language(self, text: str) -> tuple[str, float]:
        """Simple demo language detection"""
        hindi_words = {"मैं", "है", "के", "को", "से", "पर", "में", "का", "की", "के", "और", "या", "नहीं", "हैं", "था", "थी", "थे"}
        bengali_words = {"আমি", "হیں", "কে", "কে", "থেকে", "এ", "এই", "সে", "তার", "এবং", "না", "হয়", "ছিল", "ছিলে"}
        
        text_words = set(text.lower().split())
        
        hindi_count = len(text_words & hindi_words)
        bengali_count = len(text_words & bengali_words)
        
        if hindi_count > bengali_count and hindi_count > 0:
            return "hi", 0.85
        elif bengali_count > 0:
            return "bn", 0.85
        return "en", 0.90
    
    async def analyze(self, text: str, language: Optional[str] = None) -> NLPFeatures:
        start_time = time.time()
        
        # Detect language if not provided
        if language is None:
            language, lang_conf = await self.detect_language(text)
        else:
            lang_conf = 0.95
        
        text_lower = text.lower()
        
        # Demo rule-based analysis (CLEARLY LABELED AS DEMO)
        emotional = {
            "fear": 0.0,
            "anxiety": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "distress": 0.0,
        }
        safety = {
            "threat": 0.0,
            "intimidation": 0.0,
            "ongoing_danger": 0.0,
            "family_safety": 0.0,
        }
        social = {
            "isolation": 0.0,
            "displacement": 0.0,
            "social_boycott": 0.0,
            "lack_of_support": 0.0,
        }
        trauma = {
            "severe_distress": 0.0,
            "traumatic_events": 0.0,
            "repeated_fear": 0.0,
            "difficulty_communicating": 0.0,
        }
        
        # Keyword dictionaries for demo
        fear_keywords = ["afraid", "scared", "fear", "terrified", "panic", "frightened", "darr", "bhay", "ভয়", "ভয়", "ডর"]
        anxiety_keywords = ["anxious", "worried", "nervous", "tense", "stress", "chinta", "চিন্তা", "উদ্বেগ"]
        distress_keywords = ["distress", "suffering", "pain", "hurt", "agon", "पीड़ा", "দুঃখ", "কষ্ট"]
        threat_keywords = ["threat", "threaten", "danger", "harm", "kill", "murder", "rape", "violence", "धमकी", "হত্যা", "বলাত্কার", "হিংসা"]
        isolation_keywords = ["alone", "isolated", "lonely", "abandoned", "no one", "nobody", "अकेला", "একা", "অकेला"]
        
        # Score indicators based on keyword presence (DEMO ONLY)
        for kw in fear_keywords:
            if kw in text_lower:
                emotional["fear"] = max(emotional["fear"], 0.7)
                emotional["anxiety"] = max(emotional["anxiety"], 0.5)
        
        for kw in anxiety_keywords:
            if kw in text_lower:
                emotional["anxiety"] = max(emotional["anxiety"], 0.6)
        
        for kw in distress_keywords:
            if kw in text_lower:
                emotional["distress"] = max(emotional["distress"], 0.6)
                emotional["sadness"] = max(emotional["sadness"], 0.5)
        
        for kw in threat_keywords:
            if kw in text_lower:
                safety["threat"] = max(safety["threat"], 0.8)
                safety["ongoing_danger"] = max(safety["ongoing_danger"], 0.6)
        
        for kw in isolation_keywords:
            if kw in text_lower:
                social["isolation"] = max(social["isolation"], 0.7)
                social["lack_of_support"] = max(social["lack_of_support"], 0.6)
        
        # Trauma indicators for repeated/severe patterns
        if emotional["fear"] > 0.5 and emotional["distress"] > 0.5:
            trauma["severe_distress"] = 0.7
            trauma["repeated_fear"] = 0.6
        
        if any(kw in text_lower for kw in ["rape", "बलात्कार", "বলাত্কার", "murder", "हत्या", "হত্যা"]):
            trauma["traumatic_events"] = 0.9
            safety["threat"] = max(safety["threat"], 0.9)
        
        # Normalize scores to 0-1 range
        for category in [emotional, safety, social, trauma]:
            for key in category:
                category[key] = min(category[key], 1.0)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return NLPFeatures(
            emotional_indicators=emotional,
            safety_indicators=safety,
            social_indicators=social,
            trauma_indicators=trauma,
            confidence=0.75,  # Demo confidence
            language_detected=language,
            language_confidence=lang_conf,
            text_length=len(text),
            processing_time_ms=processing_time,
        )