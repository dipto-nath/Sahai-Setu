"""
Human Review API
Human-in-the-loop review system.
Both AI and human assessments are preserved.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app.models.users import User, UserRole
from app.models.cases import Case, CaseStatus, RiskLevel
from app.models.reviews import Review, ReviewDecision
from app.models.audit_log import AuditLog
from app.database import get_db
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/review", tags=["Human Review"])


class ReviewCreateRequest(BaseModel):
    case_id: int
    human_risk: RiskLevel
    decision: ReviewDecision
    notes: Optional[str] = None
    assigned_counsellor: bool = False
    assigned_legal_support: bool = False
    escalated: bool = False


@router.post("/{case_id}")
async def submit_review(
    case_id: int,
    review_data: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Submit human review for a case.
    Preserves both AI assessment and human assessment.
    """
    db = next(get_db())
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Get AI risk from case
        ai_risk = case.risk_level or RiskLevel.LOW

        # Create review
        review = Review(
            case_id=case_id,
            reviewer_id=current_user.id,
            ai_risk=ai_risk,
            human_risk=review_data.human_risk,
            decision=review_data.decision,
            notes=review_data.notes,
            assigned_counsellor=review_data.assigned_counsellor,
            assigned_legal_support=review_data.assigned_legal_support,
            escalated=review_data.escalated,
        )
        db.add(review)

        # Update case status and human risk (do NOT overwrite AI output)
        case.risk_level = review_data.human_risk  # Final risk from human
        case.status = CaseStatus.REVIEWED
        case.updated_at = datetime.utcnow()

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            action="HUMAN_REVIEW_COMPLETED",
            case_id=case_id,
            metadata_json=str({
                "ai_risk": ai_risk.value,
                "human_risk": review_data.human_risk.value,
                "decision": review_data.decision.value,
            })
        )
        db.add(audit)
        db.commit()
        db.refresh(review)

        return {
            "review_id": review.id,
            "case_id": case_id,
            "ai_assessment": {
                "risk_level": ai_risk.value,
                "svi": case.svi,
                "confidence": case.confidence,
            },
            "human_assessment": {
                "risk_level": review_data.human_risk.value,
                "decision": review_data.decision.value,
                "notes": review_data.notes,
                "reviewer_id": current_user.id,
                "reviewed_at": review.created_at.isoformat() if review.created_at else None,
            },
            "final_status": "HUMAN_REVIEW_COMPLETED",
            "important_note": "AI and human assessments are both preserved. Final decision reflects authorized human review.",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Review submission failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{case_id}")
async def get_review(
    case_id: int,
    current_user: User = Depends(get_current_user),
):
    """Get all reviews for a case"""
    db = next(get_db())
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        reviews = db.query(Review).filter(Review.case_id == case_id).order_by(Review.created_at.desc()).all()
        return {
            "case_id": case_id,
            "ai_assessment": {
                "risk_level": case.risk_level.value if case.risk_level else None,
                "svi": case.svi,
                "confidence": case.confidence,
            },
            "human_reviews": [
                {
                    "id": r.id,
                    "reviewer_id": r.reviewer_id,
                    "ai_risk": r.ai_risk.value,
                    "human_risk": r.human_risk.value if r.human_risk else None,
                    "decision": r.decision.value,
                    "notes": r.notes,
                    "assigned_counsellor": r.assigned_counsellor,
                    "assigned_legal_support": r.assigned_legal_support,
                    "escalated": r.escalated,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reviews
            ],
        }
    finally:
        db.close()
