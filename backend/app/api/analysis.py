"""
Analysis API Routes for SIH26093

Standalone analysis endpoints (without case creation).
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
import logging

from app.models.users import User
from app.api.auth import get_current_user, get_optional_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

# Lazy-load services to avoid import errors
def get_analysis_service():
    try:
        from app.services.analysis_service import AnalysisService
        return AnalysisService(use_demo=settings.demo_mode)
    except ImportError:
        from app.services.hybrid_assessment_service import get_hybrid_assessment_service
        return get_hybrid_assessment_service(
            use_gemini=bool(settings.ai_api_key) or settings.demo_mode,
            demo_mode=settings.demo_mode,
        )

def get_case_service():
    from app.services.case_service import CaseService
    return CaseService(use_demo=settings.demo_mode)


async def _analyze_and_save(
    case_id: Optional[str],
    analysis_func,
    *args,
    audio_ref: Optional[str] = None,
    text: Optional[str] = None,
    audio_data: Optional[bytes] = None,
    language: str = "en",
) -> dict:
    """Analyze and optionally save to database case."""
    db_case_id = None
    if case_id and str(case_id).isdigit():
        db_case_id = int(case_id)
    
    cid = case_id or f"TEMP-{language.upper()}-001"
    result = await analysis_func(cid, *args)
    
    if db_case_id:
        try:
            case_service = get_case_service()
            case = case_service.get_case(db_case_id)
            if case:
                assessment = await case_service.analyze_case(
                    case_id=db_case_id,
                    text=text,
                    audio_data=audio_data,
                    language=language,
                    user_id=None,  # Anonymous
                    audio_storage_ref=audio_ref
                )
                result["case_id"] = db_case_id
                result["saved_to_database"] = True
                result["anonymous_case_id"] = case.anonymous_case_id
        except Exception as e:
            logger.warning(f"Could not save analysis to case {db_case_id}: {e}")
    
    return result


@router.post("/text")
async def analyze_text(
    text: str = Form(...),
    language: str = Form("en"),
    case_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Analyze text input. If case_id is a valid database case ID, save results."""
    svc = get_analysis_service()
    return await _analyze_and_save(
        case_id,
        svc.analyze_text,
        text,
        language,
        text=text,
        language=language,
    )


@router.post("/audio")
async def analyze_audio(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    case_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Analyze audio input. If case_id is a valid database case ID, save results."""
    audio_data = await audio.read()
    
    # Save audio file to disk for playback
    audio_ref = None
    if case_id and str(case_id).isdigit():
        import os, uuid
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        ext = audio.filename.rsplit(".", 1)[-1] if audio.filename and "." in audio.filename else "webm"
        filename = f"case_{case_id}_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, "wb") as f:
            f.write(audio_data)
        audio_ref = f"/uploads/{filename}"
    
    svc = get_analysis_service()
    result = await _analyze_and_save(
        case_id,
        svc.analyze_audio,
        audio_data,
        language,
        audio_ref=audio_ref,
        audio_data=audio_data,
        language=language,
    )
    if audio_ref:
        result["audio_ref"] = audio_ref
    return result


@router.post("")
async def analyze_multimodal(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    language: str = Form("en"),
    case_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Analyze both text and audio. If case_id is a valid database case ID, save results."""
    audio_data = None
    audio_ref = None
    
    if audio:
        audio_data = await audio.read()
        # Save audio file to disk for playback
        if case_id and str(case_id).isdigit():
            import os, uuid
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            ext = audio.filename.rsplit(".", 1)[-1] if audio.filename and "." in audio.filename else "webm"
            filename = f"case_{case_id}_{uuid.uuid4().hex[:8]}.{ext}"
            filepath = os.path.join(uploads_dir, filename)
            with open(filepath, "wb") as f:
                f.write(audio_data)
            audio_ref = f"/uploads/{filename}"
    
    svc = get_analysis_service()
    result = await _analyze_and_save(
        case_id,
        svc.analyze_multimodal,
        text or "",
        audio_data,
        language,
        audio_ref=audio_ref,
        text=text,
        audio_data=audio_data,
        language=language,
    )
    if audio_ref:
        result["audio_ref"] = audio_ref
    return result


@router.get("/services/info")
async def get_service_info(current_user: Optional[User] = Depends(get_optional_user)):
    """Get information about AI services."""
    svc = get_analysis_service()
    return svc.get_service_info()

