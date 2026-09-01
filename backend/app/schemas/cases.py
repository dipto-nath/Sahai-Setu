"""
Case Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.cases import CaseStatus, RiskLevel
from app.schemas.users import UserResponse


class CaseBase(BaseSchema):
    """Base case schema"""
    language: str = Field(default="en", min_length=2, max_length=10)


class CaseCreate(CaseBase):
    """Schema for creating a case"""
    pass


class LiveCaseSave(BaseModel):
    """Schema for saving a live call as a case"""
    transcript: str
    language: str
    final_svi: int
    risk_level: str
    guidance: List[str]


class CaseUpdate(BaseSchema):
    """Schema for updating a case"""
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    status: Optional[CaseStatus] = None
    risk_level: Optional[RiskLevel] = None
    svi: Optional[int] = Field(None, ge=0, le=100)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    assigned_user_id: Optional[int] = None


class CaseResponse(CaseBase, TimestampSchema):
    """Schema for case response"""
    id: int
    anonymous_case_id: str
    status: CaseStatus
    risk_level: Optional[RiskLevel] = None
    svi: Optional[int] = None
    confidence: Optional[float] = None
    assigned_user_id: Optional[int] = None
    assigned_user: Optional[UserResponse] = None


class CaseListResponse(BaseSchema):
    """Schema for paginated case list response"""
    cases: List[CaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CaseDetailResponse(BaseSchema):
    """Schema for detailed case response with all related data"""
    case: CaseResponse
    assessment: Optional[Any] = None
    indicators: List[Any] = []
    recommendations: List[Any] = []
    reviews: List[Any] = []
    interactions: List[Any] = []


class CaseStats(BaseSchema):
    """Schema for case statistics"""
    total_cases: int
    low: int
    moderate: int
    high: int
    critical: int
    pending_review: int