"""
Cases API Routes for SIH26093
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional

from app.schemas.cases import CaseCreate, CaseUpdate, CaseResponse, CaseDetailResponse
from app.schemas.assessments import AssessmentResponse
from app.schemas.reviews import ReviewCreate, ReviewResponse
from app.models.users import User, UserRole
from app.services.case_service import CaseService
from app.api.auth import get_current_user, get_current_admin, get_optional_user

from app.config import settings

router = APIRouter(prefix="/api/cases", tags=["Cases"])
case_service = CaseService(use_demo=settings.demo_mode)


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreate, current_user: User = Depends(get_current_user)):
    """Create a new case (authenticated - for officers)."""
    case = case_service.create_case(case_data, current_user.id)
    return case


from app.schemas.cases import LiveCaseSave
from datetime import datetime
from app.models.cases import Case, CaseStatus, RiskLevel
from app.models.interactions import Interaction, InputType
from app.models.assessments import Assessment, AssessmentStatus
from app.models.recommendations import Recommendation as RecommendationModel
from app.database import get_db

@router.post("/live/save")
async def save_live_case(data: LiveCaseSave, current_user: User = Depends(get_current_user)):
    """Save a live call transcript and analysis as a new case."""
    db = next(get_db())
    try:
        # Create Case
        case_id = case_service.generate_case_id()
        case = Case(
            anonymous_case_id=case_id,
            language=data.language,
            status=CaseStatus.REVIEW_RECOMMENDED,
            risk_level=RiskLevel(data.risk_level) if data.risk_level in [r.value for r in RiskLevel] else RiskLevel.MODERATE,
            svi=data.final_svi,
            confidence=0.9,
            assigned_user_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        
        # Add interaction
        interaction = Interaction(
            case_id=case.id,
            input_type=InputType.VOICE,
            language=data.language,
            text_content=data.transcript,
            created_at=datetime.utcnow()
        )
        db.add(interaction)
        
        # Add assessment
        assessment = Assessment(
            case_id=case.id,
            text_score=data.final_svi,
            audio_score=data.final_svi,
            context_score=data.final_svi,
            threat_score=data.final_svi,
            distress_score=data.final_svi,
            final_svi=data.final_svi,
            risk_level=case.risk_level.value,
            confidence=0.9,
            assessment_status=AssessmentStatus.COMPLETED,
            created_at=datetime.utcnow()
        )
        db.add(assessment)
        
        # Add recommendations from guidance
        for tip in data.guidance:
            rec = RecommendationModel(
                case_id=case.id,
                type="OFFICER_GUIDANCE",
                priority="HIGH",
                reason=tip,
                status="PENDING",
                created_at=datetime.utcnow()
            )
            db.add(rec)
            
        db.commit()
        return {"id": case.id, "anonymous_case_id": case.anonymous_case_id}
    finally:
        db.close()


@router.post("/anonymous", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_anonymous_case(case_data: CaseCreate):
    """Create a new case anonymously (for victims without authentication)."""
    case = case_service.create_case(case_data, user_id=None)
    return case


@router.get("", response_model=List[CaseResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 100,
    risk_level: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List cases with optional filtering."""
    from app.models.cases import RiskLevel
    rl = RiskLevel(risk_level) if risk_level else None
    cases = case_service.list_cases(skip, limit, rl)
    return cases


@router.get("/priority", response_model=List[CaseResponse])
async def get_priority_cases(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Get high priority cases (HIGH and CRITICAL)."""
    cases = case_service.get_priority_cases(limit)
    return cases


@router.get("/{case_id}", response_model=CaseDetailResponse)
async def get_case(case_id: int, current_user: User = Depends(get_current_user)):
    """Get case details with all related data."""
    details = case_service.get_case_details(case_id)
    if not details:
        raise HTTPException(status_code=404, detail="Case not found")
    return details


@router.get("/anonymous/{anonymous_id}", response_model=CaseDetailResponse)
async def get_case_by_anonymous_id(anonymous_id: str, current_user: User = Depends(get_current_user)):
    """Get case by anonymous case ID."""
    case = case_service.get_case_by_anonymous_id(anonymous_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case_service.get_case_details(case.id)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, case_data: CaseUpdate, current_user: User = Depends(get_current_user)):
    """Update a case."""
    case = case_service.update_case(case_id, case_data, current_user.id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/analyze/text", response_model=AssessmentResponse)
async def analyze_text(
    case_id: int,
    text: str = Form(...),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user)
):
    """Analyze text input for a case."""
    from app.models.cases import Case
    from app.database import get_db
    
    db = next(get_db())
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
    finally:
        db.close()
    
    assessment = await case_service.analyze_case(case_id, text=text, language=language, user_id=current_user.id)
    return assessment


@router.post("/{case_id}/analyze/audio", response_model=AssessmentResponse)
async def analyze_audio(
    case_id: int,
    audio: UploadFile = File(...),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user)
):
    """Analyze audio input for a case."""
    from app.models.cases import Case
    from app.database import get_db
    
    db = next(get_db())
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
    finally:
        db.close()
    
    audio_data = await audio.read()
    assessment = await case_service.analyze_case(case_id, audio_data=audio_data, language=language, user_id=current_user.id)
    return assessment


@router.post("/{case_id}/analyze", response_model=AssessmentResponse)
async def analyze_multimodal(
    case_id: int,
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user)
):
    """Analyze both text and audio for a case."""
    from app.models.cases import Case
    from app.database import get_db
    
    db = next(get_db())
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
    finally:
        db.close()
    
    audio_data = await audio.read() if audio else None
    assessment = await case_service.analyze_case(case_id, text=text, audio_data=audio_data, language=language, user_id=current_user.id)
    return assessment


@router.post("/{case_id}/review", response_model=ReviewResponse)
async def add_review(case_id: int, review_data: ReviewCreate, current_user: User = Depends(get_current_user)):
    """Add human review to a case."""
    review = case_service.add_review(case_id, review_data, current_user.id)
    return review


@router.post("/{case_id}/assign")
async def assign_case(case_id: int, assigned_user_id: int, current_user: User = Depends(get_current_admin)):
    """Assign case to a user (admin only)."""
    case = case_service.assign_case(case_id, assigned_user_id, current_user.id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"message": "Case assigned successfully", "case": case}
