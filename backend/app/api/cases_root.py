"""
Root-level Cases API (without /api prefix)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from app.models.cases import Case, CaseStatus
from app.models.users import User
from app.services.case_service import CaseService
from app.api.auth import get_current_user, get_optional_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["Cases (Root)"])


class CaseCreateRequest(BaseModel):
    language: str = Field(default="en", min_length=2, max_length=10)


@router.post("")
async def create_case_root(
    case_data: CaseCreateRequest,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """POST /cases - Create a new case (works with or without auth)"""
    try:
        from app.schemas.cases import CaseCreate
        case_service = CaseService(use_demo=settings.demo_mode)
        case = case_service.create_case(
            CaseCreate(language=case_data.language),
            user_id=current_user.id if current_user else None,
        )
        return case
    except Exception as e:
        logger.error(f"Case creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_cases_root(
    skip: int = 0,
    limit: int = 100,
    risk_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """GET /cases - List cases"""
    from app.models.cases import RiskLevel
    from app.database import get_db
    db = next(get_db())
    try:
        query = db.query(Case)
        if risk_level:
            try:
                rl = RiskLevel(risk_level)
                query = query.filter(Case.risk_level == rl)
            except ValueError:
                pass
        cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
        return [
            {
                "id": c.id,
                "anonymous_case_id": c.anonymous_case_id,
                "language": c.language,
                "status": c.status.value if c.status else None,
                "risk_level": c.risk_level.value if c.risk_level else None,
                "svi": c.svi,
                "confidence": c.confidence,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in cases
        ]
    finally:
        db.close()
