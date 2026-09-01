"""
Indicator Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.indicators import IndicatorSource, IndicatorSeverity


class IndicatorBase(BaseSchema):
    """Base indicator schema"""
    name: str = Field(..., min_length=1, max_length=100)
    severity: IndicatorSeverity
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: IndicatorSource


class IndicatorCreate(IndicatorBase):
    """Schema for creating an indicator"""
    assessment_id: int
    details_json: Optional[str] = None
    explanation: Optional[str] = None


class IndicatorResponse(IndicatorBase, TimestampSchema):
    """Schema for indicator response"""
    id: int
    assessment_id: int
    details_json: Optional[str] = None
    explanation: Optional[str] = None