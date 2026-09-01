"""
Hybrid Assessment API Routes
Implements the /assessment/text and /assessment/voice endpoints
following the SIH26093 hybrid AI architecture.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, Field
import json
import logging

from app.models.users import User
from app.services.hybrid_assessment_service import get_hybrid_assessment_service
from app.api.auth import get_current_user, get_optional_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assessment", tags=["Hybrid Assessment"])


class TextAssessmentRequest(BaseModel):
    case_id: str = Field(..., description="Anonymous case ID")
    text: str = Field(..., min_length=1, description="User text input")
    language: str = Field(default="en", description="Language code (en, bn, hi)")


class AssessmentResponse(BaseModel):
    case_id: str
    success: bool
    input_type: str
    language: str
    timestamp: str
    processing_time_ms: int
    processing_steps: list = []
    
    # Final assessment (for frontend)
    final_assessment: Optional[dict] = None
    indicators: list = []
    recommendations: list = []
    
    # Optional detailed data
    svi_result: Optional[dict] = None
    confidence_result: Optional[dict] = None
    fusion_result: Optional[dict] = None
    text_features: Optional[dict] = None
    audio_features: Optional[dict] = None
    transcript: Optional[str] = None
    error: Optional[str] = None


def get_service():
    return get_hybrid_assessment_service(
        use_gemini=bool(settings.ai_api_key) or settings.demo_mode,
        demo_mode=settings.demo_mode,
    )


@router.post("/text", response_model=AssessmentResponse)
async def assess_text(
    request: TextAssessmentRequest,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Text-based AI-Assessed Assessment.
    
    Flow:
    1. Validate request
    2. Detect/validate language
    3. Normalize text
    4. Extract local NLP features
    5. Send minimized text to Gemini
    6. Validate Gemini JSON response
    7. Normalize features
    8. Run text-only fusion
    9. Calculate SVI
    10. Calculate confidence
    11. Generate recommendations
    12. Return structured result
    """
    try:
        service = get_service()
        result = await service.assess_text(
            text=request.text,
            language=request.language,
            case_id=request.case_id,
        )
        return result
    except Exception as e:
        logger.error(f"Text assessment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/voice", response_model=AssessmentResponse)
async def assess_voice(
    case_id: str = Form(...),
    language: str = Form("en"),
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Voice-based AI-Assessed Assessment.
    
    Flow:
    1. Receive audio file
    2. Validate format
    3. Perform audio preprocessing
    4. Calculate audio quality
    5. Run Speech-to-Text
    6. Generate transcript
    7. Extract local audio features
    8. Extract local NLP features from transcript
    9. Send minimized transcript to Gemini
    10. Validate Gemini response
    11. Normalize all features
    12. Run multimodal fusion
    13. Calculate SVI
    14. Calculate confidence
    15. Generate recommendations
    16. Return result
    """
    try:
        if not audio and not text:
            raise HTTPException(status_code=400, detail="Either audio file or text is required")
        
        audio_data = None
        filename = ""
        if audio:
            audio_data = await audio.read()
            filename = audio.filename or "audio.wav"
        
        service = get_service()
        result = await service.assess_voice(
            audio_data=audio_data or b"",
            text=text or "",
            language=language,
            case_id=case_id,
            filename=filename,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice assessment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/{case_id}")
async def get_assessment(
    case_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get the latest assessment for a case"""
    # This will be implemented in case_service integration
    return {"case_id": case_id, "message": "Use /api/cases/{case_id} for full details"}


@router.get("/info/services")
async def get_services_info():
    """Get information about all AI services in the hybrid pipeline"""
    return {
        "architecture": "Hybrid AI - Local Processing + Gemini Contextual Analysis",
        "components": {
            "local_nlp": {
                "name": "Local NLP Feature Extractor",
                "purpose": "Extracts communication/context indicators from text",
                "type": "Rule-based with configurable patterns",
                "languages": ["en", "bn", "hi"],
            },
            "local_audio": {
                "name": "Local Audio Feature Extractor",
                "purpose": "Extracts measurable audio characteristics (NOT diagnostic)",
                "library": "librosa",
            },
            "local_speech_to_text": {
                "name": "Local Speech-to-Text",
                "purpose": "Transcribe audio to text (placeholder for faster-whisper)",
                "type": "local",
            },
            "gemini_context": {
                "name": "Gemini API Contextual Analysis",
                "purpose": "Multilingual contextual NLP - does NOT make final decisions",
                "note": "Only analyzes predefined contextual categories",
            },
            "multimodal_fusion": {
                "name": "Multimodal Fusion Engine",
                "purpose": "Combines text, context, and audio scores with configurable weights",
                "config": "config/model_weights.json",
            },
            "svi_engine": {
                "name": "Stress Vulnerability Index Engine",
                "purpose": "Calculates SVI (0-100) using backend logic only",
                "config": "config/risk_thresholds.json",
            },
            "confidence_engine": {
                "name": "Confidence Engine",
                "purpose": "Calculates assessment confidence separately from risk",
            },
            "recommendation_engine": {
                "name": "Rule-Based Recommendation Engine",
                "purpose": "Transparent, rule-based recommendations",
                "note": "All recommendations are AI-Assisted and require human review",
            },
        },
        "principles": [
            "AI-assisted decision-support, NOT a medical diagnosis",
            "SVI calculated by backend logic, not Gemini",
            "All final decisions require authorized human review",
            "Data minimization before Gemini calls",
            "Configurable weights and thresholds",
        ],
        "demo_mode": settings.demo_mode,
    }
