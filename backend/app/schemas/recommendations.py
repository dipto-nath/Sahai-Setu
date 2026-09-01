"""
Recommendation Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.recommendations import RecommendationType, RecommendationPriority, RecommendationStatus


class RecommendationBase(BaseSchema):
    """Base recommendation schema"""
    type: RecommendationType
    priority: RecommendationPriority
    reason: str = Field(..., min_length=1)


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation"""
    case_id: int
    source: str = "AI"


class RecommendationUpdate(BaseSchema):
    """Schema for updating a recommendation"""
    status: Optional[RecommendationStatus] = None
    reason: Optional[str] = None


class RecommendationResponse(RecommendationBase, TimestampSchema):
    """Schema for recommendation response"""
    id: int
    case_id: int
    status: RecommendationStatus
    source: str