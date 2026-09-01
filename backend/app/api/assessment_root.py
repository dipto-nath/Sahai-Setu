"""
Root Assessment Endpoints (without /api prefix)
For compatibility with SIH26093 spec endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.models.users import User
from app.services.hybrid_assessment_service import get_hybrid_assessment_service
from app.api.auth import get_optional_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessment", tags=["Assessment (Root)"])


class TextAssessmentRequest(BaseModel):
    case_id: str = Field(..., description="Case ID (e.g., CASE-2026-00124)")
    text: str = Field(..., min_length=1, description="User text input")
    language: str = Field(default="en", description="Language code")


@router.post("/text")
async def assess_text_root(
    request: TextAssessmentRequest,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """POST /assessment/text - Text-based AI-Assisted Assessment"""
    try:
        service = get_hybrid_assessment_service(
            use_gemini=bool(settings.ai_api_key) or settings.demo_mode,
            demo_mode=settings.demo_mode,
        )
        result = await service.assess_text(
            text=request.text,
            language=request.language,
            case_id=request.case_id,
        )
        return result
    except Exception as e:
        logger.error(f"Text assessment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice")
async def assess_voice_root(
    case_id: str = Form(...),
    language: str = Form("en"),
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """POST /assessment/voice - Voice-based AI-Assisted Assessment"""
    try:
        if not audio and not text:
            raise HTTPException(status_code=400, detail="Either audio file or text is required")
        audio_data = None
        filename = ""
        if audio:
            audio_data = await audio.read()
            filename = audio.filename or "audio.wav"
        service = get_hybrid_assessment_service(
            use_gemini=bool(settings.ai_api_key) or settings.demo_mode,
            demo_mode=settings.demo_mode,
        )
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
        raise HTTPException(status_code=500, detail=str(e))
