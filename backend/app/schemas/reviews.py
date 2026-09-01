"""
Review Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.reviews import ReviewDecision
from app.models.cases import RiskLevel


class ReviewBase(BaseSchema):
    """Base review schema"""
    pass


class ReviewCreate(ReviewBase):
    """Schema for creating a review"""
    case_id: Optional[int] = None
    ai_risk: Optional[RiskLevel] = None
    human_risk: Optional[RiskLevel] = None
    decision: ReviewDecision
    notes: Optional[str] = None
    assigned_counsellor: bool = False
    assigned_legal_support: bool = False
    escalated: bool = False


class ReviewResponse(ReviewBase, TimestampSchema):
    """Schema for review response"""
    id: int
    case_id: int
    reviewer_id: int
    ai_risk: RiskLevel
    human_risk: Optional[RiskLevel] = None
    decision: ReviewDecision
    notes: Optional[str] = None
    assigned_counsellor: bool
    assigned_legal_support: bool
    escalated: bool