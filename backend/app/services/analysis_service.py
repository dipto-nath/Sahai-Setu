"""
Backend Services for SIH26093

Integrates AI services for case analysis, SVI calculation, and recommendations.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalysisService:
    """Main service for coordinating analysis pipeline."""
    
    def __init__(self, use_demo: bool = True):
        self.use_demo = use_demo
        # Initialize AI services (Wrap in try-except so missing legacy deps don't crash the whole service)
        try:
            from ai.nlp import get_nlp_service
            from ai.speech import get_speech_service
            from ai.audio import get_audio_service
            from ai.fusion import get_fusion_service
            from ai.svi import get_svi_service
            from ai.recommendation import get_recommendation_service
            
            self.nlp_service = get_nlp_service()
            self.speech_service = get_speech_service()
            self.audio_service = get_audio_service()
            self.fusion_service = get_fusion_service()
            self.svi_service = get_svi_service()
            self.recommendation_service = get_recommendation_service()
        except ImportError as e:
            logger.warning(f"Could not load legacy AI services: {e}")
            self.nlp_service = None
            self.speech_service = None
            self.audio_service = None
            self.fusion_service = None
            self.svi_service = None
            self.recommendation_service = None
            
        logger.info(f"Initialized AnalysisService (demo_mode={use_demo})")
    async def analyze_text(
        self,
        case_id: str,
        text: str,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text input and return complete assessment."""
        from app.services.hybrid_assessment_service import get_hybrid_assessment_service
        hybrid_svc = get_hybrid_assessment_service(use_gemini=not self.use_demo, demo_mode=self.use_demo)
        
        result = await hybrid_svc.assess_text(text=text, language=language, case_id=case_id)
        return self._adapt_hybrid_result(result, case_id)

    async def analyze_audio(
        self,
        case_id: str,
        audio_data: bytes,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze audio input and return complete assessment."""
        from app.services.hybrid_assessment_service import get_hybrid_assessment_service
        hybrid_svc = get_hybrid_assessment_service(use_gemini=not self.use_demo, demo_mode=self.use_demo)
        
        result = await hybrid_svc.assess_voice(audio_data=audio_data, language=language, case_id=case_id)
        return self._adapt_hybrid_result(result, case_id)

    async def analyze_multimodal(
        self,
        case_id: str,
        text: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze both text and audio inputs."""
        from app.services.hybrid_assessment_service import get_hybrid_assessment_service
        hybrid_svc = get_hybrid_assessment_service(use_gemini=not self.use_demo, demo_mode=self.use_demo)
        
        if audio_data:
            result = await hybrid_svc.assess_voice(audio_data=audio_data, text=text or "", language=language, case_id=case_id)
        elif text:
            result = await hybrid_svc.assess_text(text=text, language=language, case_id=case_id)
        else:
            raise ValueError("No text or audio provided")
            
        return self._adapt_hybrid_result(result, case_id)

    def _adapt_hybrid_result(self, result: Dict[str, Any], case_id: str) -> Dict[str, Any]:
        """Adapt HybridAssessmentService output to expected case_service format."""
        if not result.get("success"):
            return {
                "case_id": case_id,
                "svi": 0,
                "risk_level": "LOW",
                "confidence": 0.0,
                "assessment_status": "INCONCLUSIVE",
                "indicators": [],
                "recommendations": [],
                "explanation": {"error": result.get("error")},
                "analysis_mode": "REAL"
            }
        
        final = result.get("final_assessment", {})
        
        # Adapt indicators
        adapted_indicators = []
        for ind in result.get("indicators", []):
            # Hybrid engine returns dict, we need to return something that case_service expects.
            # case_service expects a dict with name, severity, confidence, source if it's not a Pydantic model
            # Actually case_service looks for `.to_dict()` when we return it!
            # Wait, case_service uses the returned indicators from this method and saves them!
            # Let's return objects that have `to_dict()` or just dicts.
            # case_service parses them from result["indicators"]
            pass # we'll handle this differently by creating dummy objects

        class DummyIndicator:
            def __init__(self, data):
                self.__dict__.update(data)
            def to_dict(self):
                return self.__dict__
                
        class DummyRecommendation:
            def __init__(self, data):
                self.__dict__.update(data)
            def to_dict(self):
                return self.__dict__
                
        indicators = [DummyIndicator(i) for i in result.get("indicators", [])]
        recommendations = [DummyRecommendation(r) for r in result.get("recommendations", [])]
        
        return {
            "case_id": case_id,
            "svi": final.get("svi", 0),
            "risk_level": final.get("risk_level", "LOW"),
            "confidence": final.get("confidence", 0) / 100.0,
            "assessment_status": final.get("assessment_status", "INCONCLUSIVE"),
            "text_score": int(result.get("normalized_features", {}).get("text_features", {}).get("text_score", 0) * 100),
            "audio_score": int(result.get("normalized_features", {}).get("audio_features", {}).get("audio_score", 0) * 100) if result.get("normalized_features", {}).get("audio_features") else 0,
            "context_score": int(result.get("normalized_features", {}).get("context_features", {}).get("context_score", 0) * 100),
            "threat_score": int(result.get("normalized_features", {}).get("context_features", {}).get("threat_context", 0) * 100),
            "distress_score": int(result.get("normalized_features", {}).get("context_features", {}).get("distress", 0) * 100),
            "indicators": [i.to_dict() for i in indicators],
            "recommendations": [r.to_dict() for r in recommendations],
            "explanation": result.get("processing_steps", []),
            "nlp_analysis": result.get("text_features", {}),
            "analysis_mode": "REAL",
            "transcript": result.get("transcript", "")
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all AI services."""
        def get_info(service, default_name):
            if hasattr(service, 'get_service_info'):
                return service.get_service_info()
            return {
                "model_name": getattr(service, 'model_name', default_name),
                "is_demo": getattr(service, 'is_demo', True)
            }
        
        return {
            "nlp": get_info(self.nlp_service, "NLP"),
            "speech": get_info(self.speech_service, "Speech"),
            "audio": get_info(self.audio_service, "Audio"),
            "fusion": get_info(self.fusion_service, "Fusion"),
            "svi": get_info(self.svi_service, "SVI"),
            "recommendation": get_info(self.recommendation_service, "Recommendation"),
            "demo_mode": self.use_demo
        }
