"""
Hybrid Assessment Service
Orchestrates the complete hybrid AI analysis pipeline:
- Local NLP feature extraction
- Local audio feature extraction
- Gemini API contextual analysis
- Multimodal fusion
- SVI calculation
- Confidence calculation
- Recommendation generation
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.ml.text_features import get_text_feature_extractor
from app.ml.audio_features import get_audio_feature_extractor
from app.ml.normalization import get_feature_normalizer
from app.ml.fusion import get_fusion_engine
from app.ml.svi_engine import get_svi_engine
from app.ml.confidence_engine import get_confidence_engine
from app.services.gemini_service import get_gemini_service
from app.services.recommendation_service import get_recommendation_service
from ai.speech import get_speech_service
from ai.translation.translation_service import TranslationService

logger = logging.getLogger(__name__)


class HybridAssessmentService:
    """
    Main orchestrator for the hybrid AI assessment pipeline.
    Combines local processing, Gemini API, and backend logic.
    """

    def __init__(self, use_gemini: bool = True, demo_mode: bool = True):
        self.text_extractor = get_text_feature_extractor()
        self.audio_extractor = get_audio_feature_extractor()
        self.normalizer = get_feature_normalizer()
        self.fusion_engine = get_fusion_engine()
        self.svi_engine = get_svi_engine()
        self.confidence_engine = get_confidence_engine()
        self.recommendation_service = get_recommendation_service()
        self.use_gemini = use_gemini
        self.demo_mode = demo_mode
        self.gemini_service = get_gemini_service() if use_gemini else None
        self.speech_service = get_speech_service()
        self.translation_service = TranslationService()

    async def assess_text(
        self,
        text: str,
        language: str = "en",
        case_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Complete text-based assessment.
        
        Flow:
        1. Extract local NLP features
        2. Send minimized text to Gemini
        3. Normalize features
        4. Run text-only fusion
        5. Calculate SVI
        6. Calculate confidence
        7. Generate recommendations
        8. Return structured result
        """
        start_time = datetime.utcnow()
        result = {
            "case_id": case_id,
            "input_type": "TEXT",
            "language": language,
            "timestamp": start_time.isoformat(),
            "processing_steps": [],
        }

        try:
            # Step 1: Local NLP feature extraction
            logger.info("Step 1: Local NLP feature extraction")
            
            # 1. Native language NLP extraction
            native_features = self.text_extractor.extract(text, language=language)
            text_features_dict = native_features.to_dict()
            
            # 2. Translated English NLP extraction (if applicable)
            if language != "en":
                logger.info(f"Translating {language} text to English for secondary NLP extraction")
                translated_text = await self.translation_service.translate(text, source_lang=language)
                result["translated_text"] = translated_text
                
                english_features = self.text_extractor.extract(translated_text, language="en")
                english_dict = english_features.to_dict()
                
                # Merge native and english features by taking the maximum of both signals
                for key in ["fear_signal", "distress_signal", "threat_context_signal", "isolation_signal", "urgency_signal", "repetition_score"]:
                    text_features_dict[key] = max(text_features_dict.get(key, 0.0), english_dict.get(key, 0.0))
                
            result["processing_steps"].append("local_nlp_extraction")
            result["text_features"] = text_features_dict

            # Step 2: Gemini contextual analysis
            gemini_response = None
            if self.gemini_service:
                logger.info("Step 2: Gemini API contextual analysis")
                gemini_result = await self.gemini_service.analyze(text, language)
                if gemini_result.success:
                    gemini_response = gemini_result.response
                    result["processing_steps"].append("gemini_context_analysis")
                    result["gemini_response"] = gemini_response
                    result["gemini_is_mock"] = gemini_result.is_mock
                else:
                    logger.warning(f"Gemini analysis failed: {gemini_result.error}")
                    result["gemini_error"] = gemini_result.error

            # Step 3: Normalize features
            logger.info("Step 3: Feature normalization")
            normalized = self.normalizer.normalize_all(
                text_features=text_features_dict,
                gemini_response=gemini_response,
                audio_features=None,
                transcription_confidence=0.0,
            )
            result["processing_steps"].append("feature_normalization")
            result["normalized_features"] = normalized.to_dict()

            # Step 4: Run text-only fusion
            logger.info("Step 4: Multimodal fusion (text-only)")
            fusion_result = self.fusion_engine.fuse(
                text_score=normalized.text_features.text_score,
                context_score=normalized.context_features.context_score,
                audio_score=0.0,
                has_audio=False,
                text_features=normalized.text_features.to_dict(),
                context_features=normalized.context_features.to_dict(),
                audio_features=None,
                input_quality=normalized.input_quality.to_dict(),
            )
            result["processing_steps"].append("multimodal_fusion")
            result["fusion_result"] = fusion_result.to_dict()

            # Step 5: Calculate SVI
            logger.info("Step 5: SVI calculation")
            svi_result = self.svi_engine.calculate(fusion_result)
            result["processing_steps"].append("svi_calculation")
            result["svi_result"] = svi_result.to_dict()

            # Step 6: Calculate confidence
            logger.info("Step 6: Confidence calculation")
            confidence_result = self.confidence_engine.calculate(
                text_features=normalized.text_features.to_dict(),
                audio_features=None,
                context_features=normalized.context_features.to_dict(),
                input_quality=normalized.input_quality.to_dict(),
                gemini_response=gemini_response,
            )
            result["processing_steps"].append("confidence_calculation")
            result["confidence_result"] = confidence_result.to_dict()

            # Override SVI confidence with confidence engine result
            svi_result.confidence = confidence_result.assessment_confidence
            svi_result.confidence_level = confidence_result.confidence_level
            if confidence_result.inconclusive:
                svi_result.assessment_status = "INCONCLUSIVE"
                svi_result.human_review_required = True
            result["svi_result"] = svi_result.to_dict()

            # Step 7: Generate indicators for recommendation
            indicators = self._extract_indicators(
                normalized.text_features.to_dict(),
                normalized.context_features.to_dict(),
                None,
            )

            # Step 8: Generate recommendations
            logger.info("Step 7: Recommendation generation")
            recommendations = self.recommendation_service.generate_recommendations(
                svi_score=svi_result.svi_score,
                risk_level=svi_result.risk_level,
                confidence=confidence_result.assessment_confidence,
                assessment_status=svi_result.assessment_status,
                indicators=indicators,
                text_features=normalized.text_features.to_dict(),
                context_features=normalized.context_features.to_dict(),
            )
            result["processing_steps"].append("recommendation_generation")
            result["recommendations"] = [r.to_dict() for r in recommendations]

            # Final response
            result["success"] = True
            result["final_assessment"] = {
                "svi": svi_result.svi_score,
                "risk_level": svi_result.risk_level,
                "confidence": int(confidence_result.assessment_confidence * 100),
                "assessment_status": svi_result.assessment_status,
                "human_review_required": svi_result.human_review_required,
            }
            result["indicators"] = indicators

        except Exception as e:
            logger.error(f"Assessment failed: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)

        # Processing time
        end_time = datetime.utcnow()
        result["processing_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
        return result

    async def assess_voice(
        self,
        audio_data: bytes,
        text: str = "",
        language: str = "en",
        case_id: Optional[str] = None,
        filename: str = "",
    ) -> Dict[str, Any]:
        """
        Complete voice-based assessment.
        Includes speech-to-text and all multimodal features.
        """
        start_time = datetime.utcnow()
        result = {
            "case_id": case_id,
            "input_type": "VOICE",
            "language": language,
            "timestamp": start_time.isoformat(),
            "processing_steps": [],
        }

        try:
            # Step 1: Audio validation & preprocessing
            logger.info("Step 1: Audio validation")
            from app.services.audio_service import get_audio_preprocessing_service
            preprocessor = get_audio_preprocessing_service()
            validation = preprocessor.validate(audio_data, filename)
            result["audio_validation"] = {
                "is_valid": validation.is_valid,
                "duration_seconds": validation.duration_seconds,
                "sample_rate": validation.sample_rate,
                "audio_quality": validation.audio_quality,
                "has_speech": validation.has_speech,
            }
            if not validation.is_valid:
                result["success"] = False
                result["error"] = f"Audio validation failed: {validation.error}"
                return result
            result["processing_steps"].append("audio_validation")

            # Step 2: Speech-to-text
            logger.info("Step 2: Speech-to-text")
            if text and text.strip():
                # If text was explicitly provided along with voice
                transcript = text
                transcription_confidence = 0.90
            else:
                # Transcribe the audio using the real speech service
                speech_result = await self.speech_service.transcribe_bytes(audio_data, language)
                transcript = speech_result.transcript
                transcription_confidence = speech_result.confidence
                
            result["transcript"] = transcript
            result["transcription_confidence"] = transcription_confidence
            result["processing_steps"].append("speech_to_text")

            # Step 3: Local audio feature extraction
            logger.info("Step 3: Local audio feature extraction")
            audio_features = self.audio_extractor.extract(audio_data, validation.file_format)
            audio_features_dict = audio_features.to_dict()
            result["audio_features"] = audio_features_dict
            result["processing_steps"].append("local_audio_extraction")

            # Step 4: Local NLP feature extraction from transcript
            logger.info("Step 4: Local NLP feature extraction from transcript")
            
            # 1. Native language NLP extraction
            native_features = self.text_extractor.extract(transcript, language=language)
            text_features_dict = native_features.to_dict()

            # 2. Translated English NLP extraction (if applicable)
            if language != "en":
                logger.info(f"Translating {language} transcript to English for secondary NLP extraction")
                translated_text = await self.translation_service.translate(transcript, source_lang=language)
                result["translated_transcript"] = translated_text
                
                english_features = self.text_extractor.extract(translated_text, language="en")
                english_dict = english_features.to_dict()
                
                # Merge native and english features by taking the maximum of both signals
                for key in ["fear_signal", "distress_signal", "threat_context_signal", "isolation_signal", "urgency_signal", "repetition_score"]:
                    text_features_dict[key] = max(text_features_dict.get(key, 0.0), english_dict.get(key, 0.0))

            result["text_features"] = text_features_dict
            result["processing_steps"].append("local_nlp_extraction")

            # Step 5: Gemini contextual analysis
            gemini_response = None
            if self.gemini_service:
                logger.info("Step 5: Gemini API contextual analysis")
                gemini_result = await self.gemini_service.analyze(transcript, language)
                if gemini_result.success:
                    gemini_response = gemini_result.response
                    result["processing_steps"].append("gemini_context_analysis")
                    result["gemini_response"] = gemini_response
                    result["gemini_is_mock"] = gemini_result.is_mock

            # Step 6: Normalize features
            logger.info("Step 6: Feature normalization")
            normalized = self.normalizer.normalize_all(
                text_features=text_features_dict,
                gemini_response=gemini_response,
                audio_features=audio_features_dict,
                transcription_confidence=transcription_confidence,
            )
            result["processing_steps"].append("feature_normalization")
            result["normalized_features"] = normalized.to_dict()

            # Step 7: Multimodal fusion (voice)
            logger.info("Step 7: Multimodal fusion (voice)")
            fusion_result = self.fusion_engine.fuse(
                text_score=normalized.text_features.text_score,
                context_score=normalized.context_features.context_score,
                audio_score=normalized.audio_features.audio_score,
                has_audio=True,
                text_features=normalized.text_features.to_dict(),
                context_features=normalized.context_features.to_dict(),
                audio_features=normalized.audio_features.to_dict(),
                input_quality=normalized.input_quality.to_dict(),
            )
            result["processing_steps"].append("multimodal_fusion")
            result["fusion_result"] = fusion_result.to_dict()

            # Step 8: SVI calculation
            logger.info("Step 8: SVI calculation")
            svi_result = self.svi_engine.calculate(fusion_result)
            result["processing_steps"].append("svi_calculation")
            result["svi_result"] = svi_result.to_dict()

            # Step 9: Confidence calculation
            logger.info("Step 9: Confidence calculation")
            confidence_result = self.confidence_engine.calculate(
                text_features=normalized.text_features.to_dict(),
                audio_features=normalized.audio_features.to_dict(),
                context_features=normalized.context_features.to_dict(),
                input_quality=normalized.input_quality.to_dict(),
                gemini_response=gemini_response,
                transcription_confidence=transcription_confidence,
            )
            result["processing_steps"].append("confidence_calculation")
            result["confidence_result"] = confidence_result.to_dict()

            # Override SVI confidence
            svi_result.confidence = confidence_result.assessment_confidence
            svi_result.confidence_level = confidence_result.confidence_level
            if confidence_result.inconclusive:
                svi_result.assessment_status = "INCONCLUSIVE"
                svi_result.human_review_required = True
            result["svi_result"] = svi_result.to_dict()

            # Step 10: Generate indicators
            indicators = self._extract_indicators(
                normalized.text_features.to_dict(),
                normalized.context_features.to_dict(),
                normalized.audio_features.to_dict(),
            )

            # Step 11: Recommendations
            logger.info("Step 10: Recommendation generation")
            recommendations = self.recommendation_service.generate_recommendations(
                svi_score=svi_result.svi_score,
                risk_level=svi_result.risk_level,
                confidence=confidence_result.assessment_confidence,
                assessment_status=svi_result.assessment_status,
                indicators=indicators,
                text_features=normalized.text_features.to_dict(),
                context_features=normalized.context_features.to_dict(),
                audio_features=normalized.audio_features.to_dict(),
            )
            result["processing_steps"].append("recommendation_generation")
            result["recommendations"] = [r.to_dict() for r in recommendations]

            # Final response
            result["success"] = True
            result["final_assessment"] = {
                "svi": svi_result.svi_score,
                "risk_level": svi_result.risk_level,
                "confidence": int(confidence_result.assessment_confidence * 100),
                "assessment_status": svi_result.assessment_status,
                "human_review_required": svi_result.human_review_required,
            }
            result["indicators"] = indicators

        except Exception as e:
            logger.error(f"Voice assessment failed: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)

        end_time = datetime.utcnow()
        result["processing_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
        return result

    def _extract_indicators(
        self,
        text_features: Dict[str, Any],
        context_features: Dict[str, Any],
        audio_features: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extract indicators from features for recommendations"""
        indicators = []
        # Text indicators
        for key, label in [
            ("fear_signal", "fear-related communication"),
            ("distress_signal", "distress-related communication"),
            ("threat_context_signal", "threat context"),
            ("isolation_signal", "social isolation"),
            ("urgency_signal", "urgency"),
        ]:
            value = text_features.get(key, 0)
            if value > 0.5:
                indicators.append({
                    "name": label,
                    "severity": "HIGH" if value > 0.7 else "MODERATE",
                    "confidence": round(value, 3),
                    "source": "TEXT",
                })
        # Context indicators
        for key, label in [
            ("fear", "fear-related context"),
            ("distress", "distress-related context"),
            ("threat_context", "threat context"),
            ("social_isolation", "social isolation"),
            ("vulnerability", "vulnerability"),
            ("urgency", "urgency"),
        ]:
            value = context_features.get(key, 0)
            if value > 0.3:
                indicators.append({
                    "name": label,
                    "severity": "HIGH" if value > 0.6 else "MODERATE",
                    "confidence": round(value, 3),
                    "source": "CONTEXT",
                })
        # Audio indicators
        if audio_features:
            if audio_features.get("pause_score", 0) > 0.6:
                indicators.append({
                    "name": "prolonged pauses",
                    "severity": "HIGH" if audio_features["pause_score"] > 0.8 else "MODERATE",
                    "confidence": round(audio_features["pause_score"], 3),
                    "source": "AUDIO",
                })
            if audio_features.get("voice_activity_score", 1.0) < 0.5:
                indicators.append({
                    "name": "low voice activity",
                    "severity": "HIGH" if audio_features["voice_activity_score"] < 0.3 else "MODERATE",
                    "confidence": round(1.0 - audio_features["voice_activity_score"], 3),
                    "source": "AUDIO",
                })
        return indicators


def get_hybrid_assessment_service(use_gemini: bool = True, demo_mode: bool = True) -> HybridAssessmentService:
    return HybridAssessmentService(use_gemini=use_gemini, demo_mode=demo_mode)
