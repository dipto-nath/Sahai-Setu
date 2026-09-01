"""
Demo Fusion Service
Mock implementation for demonstration purposes
"""
import time
from typing import Dict, Any, Optional

from ai.fusion.fusion_service import FusionService, FusionResult, ContextFeatures
from ai.nlp.nlp_service import NLPFeatures
from ai.audio.audio_service import AudioFeatures


class DemoFusionService(FusionService):
    """Demo/Mock fusion service for demonstration purposes - CLEARLY LABELED AS DEMO"""
    
    def __init__(self):
        self._model_name = "DEMO-MULTIMODAL-FUSION"
        # Prototype weights (NOT clinically validated)
        self.weights = {
            "text": 0.30,
            "audio": 0.20,
            "threat": 0.25,
            "vulnerability": 0.25,
        }
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def is_demo(self) -> bool:
        return True
    
    async def fuse(
        self,
        text_features: Optional[NLPFeatures],
        audio_features: Optional[AudioFeatures],
        context_features: Optional[ContextFeatures]
    ) -> FusionResult:
        start_time = time.time()
        
        # Simulate processing
        await self._simulate_processing()
        
        # Calculate component scores
        component_scores = {}
        
        # Text score from NLP features
        if text_features:
            text_score = self._calculate_text_score(text_features)
        else:
            text_score = 0.0
        component_scores["text"] = text_score
        
        # Audio score from audio features
        if audio_features:
            audio_score = self._calculate_audio_score(audio_features)
        else:
            audio_score = 0.0
        component_scores["audio"] = audio_score
        
        # Threat score from context or text fallback
        if context_features and (context_features.threat_level > 0 or context_features.vulnerability_level > 0):
            threat_score = context_features.threat_level * 100
            vulnerability_score = context_features.vulnerability_level * 100
        else:
            if text_features:
                threat_score = max(text_features.safety_indicators.values()) * 100 if text_features.safety_indicators else 0.0
                trauma_max = max(text_features.trauma_indicators.values()) if text_features.trauma_indicators else 0.0
                social_max = max(text_features.social_indicators.values()) if text_features.social_indicators else 0.0
                vulnerability_score = max(trauma_max, social_max) * 100
            else:
                threat_score = 0.0
                vulnerability_score = 0.0
        component_scores["threat"] = threat_score
        component_scores["vulnerability"] = vulnerability_score
        
        # Calculate weighted SVI
        final_svi = int(
            text_score * self.weights["text"] +
            audio_score * self.weights["audio"] +
            threat_score * self.weights["threat"] +
            vulnerability_score * self.weights["vulnerability"]
        )
        final_svi = min(max(final_svi, 0), 100)  # Clamp to 0-100
        
        # Determine risk level
        risk_level = self._get_risk_level(final_svi)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(text_features, audio_features, context_features)
        
        # Determine assessment status
        assessment_status = self._determine_status(
            text_features, audio_features, context_features, confidence
        )
        
        # Build contributing factors
        contributing_factors = self._build_contributing_factors(
            text_features, audio_features, context_features, component_scores
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return FusionResult(
            component_scores=component_scores,
            final_svi=final_svi,
            risk_level=risk_level,
            confidence=confidence,
            contributing_factors=contributing_factors,
            weights_used=self.weights.copy(),
            assessment_status=assessment_status,
            processing_time_ms=processing_time,
            model_name=self._model_name,
        )
    def _calculate_text_score(self, features: NLPFeatures) -> float:
        """Calculate text component score from NLP features"""
        emotional_weight = 0.35
        safety_weight = 0.30
        social_weight = 0.20
        trauma_weight = 0.15
        
        emotional_score = max(features.emotional_indicators.values()) if features.emotional_indicators else 0
        safety_score = max(features.safety_indicators.values()) if features.safety_indicators else 0
        social_score = max(features.social_indicators.values()) if features.social_indicators else 0
        trauma_score = max(features.trauma_indicators.values()) if features.trauma_indicators else 0
        
        score = (
            emotional_score * emotional_weight +
            safety_score * safety_weight +
            social_score * social_weight +
            trauma_score * trauma_weight
        ) * 100
        
        return min(score, 100.0)
    
    def _calculate_audio_score(self, features: AudioFeatures) -> float:
        """Calculate audio component score from audio features"""
        stress_indicators = 0.0
        
        if features.speech_rate < 120:
            stress_indicators += (120 - features.speech_rate) / 120 * 0.2
        elif features.speech_rate > 180:
            stress_indicators += (features.speech_rate - 180) / 180 * 0.15
        
        if features.pause_duration_mean > 1.0:
            stress_indicators += min(features.pause_duration_mean / 2.0, 0.25)
        
        if features.pitch_std > 30:
            stress_indicators += min(features.pitch_std / 50, 0.2)
        
        stress_indicators += features.jitter * 5
        stress_indicators += features.shimmer * 3
        
        if features.hnr < 12:
            stress_indicators += (12 - features.hnr) / 12 * 0.15
        
        if features.voice_activity_ratio < 0.6:
            stress_indicators += (0.6 - features.voice_activity_ratio) / 0.6 * 0.15
        
        return min(stress_indicators * 100, 100.0)
    
    def _get_risk_level(self, svi: int) -> str:
        """Get risk level from SVI score"""
        from app.config import settings
        
        if svi <= settings.svi_threshold_low:
            return "LOW"
        elif svi <= settings.svi_threshold_moderate:
            return "MODERATE"
        elif svi <= settings.svi_threshold_high:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _calculate_confidence(
        self,
        text_features: Optional[NLPFeatures],
        audio_features: Optional[AudioFeatures],
        context_features: Optional[ContextFeatures]
    ) -> float:
        """Calculate overall confidence"""
        confidences = []
        
        if text_features:
            confidences.append(text_features.confidence)
        if audio_features:
            confidences.append(audio_features.confidence)
        if context_features:
            confidences.append(context_features.language_confidence)
            confidences.append(context_features.text_quality)
            confidences.append(context_features.audio_quality)
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)
    
    def _determine_status(
        self,
        text_features: Optional[NLPFeatures],
        audio_features: Optional[AudioFeatures],
        context_features: Optional[ContextFeatures],
        confidence: float
    ) -> str:
        """Determine assessment status"""
        from app.config import settings
        
        if confidence < settings.confidence_threshold_low:
            return "INCONCLUSIVE"
        
        if text_features is None and audio_features is None:
            return "INCONCLUSIVE"
        
        if text_features and text_features.language_confidence < 0.5:
            return "INCONCLUSIVE"
        
        if audio_features and audio_features.audio_quality == "POOR":
            return "INCONCLUSIVE"
        
        if text_features and audio_features:
            text_risk = self._get_risk_level(int(self._calculate_text_score(text_features)))
            audio_risk = self._get_risk_level(int(self._calculate_audio_score(audio_features)))
            risk_levels = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}
            if abs(risk_levels.get(text_risk, 0) - risk_levels.get(audio_risk, 0)) >= 2:
                return "INCONCLUSIVE"
        
        if confidence >= settings.confidence_threshold_high:
            svi_estimate = sum([
                self._calculate_text_score(text_features) * self.weights["text"] if text_features else 0,
                self._calculate_audio_score(audio_features) * self.weights["audio"] if audio_features else 0,
            ])
            if svi_estimate > settings.svi_threshold_moderate:
                return "REVIEW_RECOMMENDED"
        
        return "COMPLETED"
    
    def _build_contributing_factors(
        self,
        text_features: Optional[NLPFeatures],
        audio_features: Optional[AudioFeatures],
        context_features: Optional[ContextFeatures],
        component_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Build explanation of contributing factors"""
        factors = {
            "text_indicators": [],
            "audio_indicators": [],
            "context_indicators": [],
        }
        
        if text_features:
            for category, indicators in [
                ("emotional", text_features.emotional_indicators),
                ("safety", text_features.safety_indicators),
                ("social", text_features.social_indicators),
                ("trauma", text_features.trauma_indicators),
            ]:
                for name, value in indicators.items():
                    if value > 0.5:
                        factors["text_indicators"].append({
                            "category": category,
                            "indicator": name,
                            "severity": "HIGH" if value > 0.7 else "MODERATE",
                            "score": value,
                        })
        
        if audio_features:
            if audio_features.pause_duration_mean > 1.0:
                factors["audio_indicators"].append({
                    "indicator": "prolonged_pauses",
                    "severity": "HIGH" if audio_features.pause_duration_mean > 1.5 else "MODERATE",
                    "value": audio_features.pause_duration_mean,
                })
            if audio_features.pitch_std > 30:
                factors["audio_indicators"].append({
                    "indicator": "pitch_variability",
                    "severity": "HIGH" if audio_features.pitch_std > 40 else "MODERATE",
                    "value": audio_features.pitch_std,
                })
            if audio_features.jitter > 0.03:
                factors["audio_indicators"].append({
                    "indicator": "voice_jitter",
                    "severity": "HIGH" if audio_features.jitter > 0.05 else "MODERATE",
                    "value": audio_features.jitter,
                })
        
        if context_features:
            if context_features.threat_level > 0.5:
                factors["context_indicators"].append({
                    "indicator": "threat_context",
                    "severity": "HIGH" if context_features.threat_level > 0.7 else "MODERATE",
                    "value": context_features.threat_level,
                })
            if context_features.vulnerability_level > 0.5:
                factors["context_indicators"].append({
                    "indicator": "vulnerability_context",
                    "severity": "HIGH" if context_features.vulnerability_level > 0.7 else "MODERATE",
                    "value": context_features.vulnerability_level,
                })
        
        return factors
    
    async def _simulate_processing(self):
        """Simulate processing time"""
        import asyncio
        await asyncio.sleep(0.1)