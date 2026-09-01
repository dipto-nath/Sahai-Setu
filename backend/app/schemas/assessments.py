"""
Assessment Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.assessments import AssessmentStatus
from app.schemas.indicators import IndicatorResponse
from app.schemas.recommendations import RecommendationResponse


class AssessmentBase(BaseSchema):
    """Base assessment schema"""
    pass


class AssessmentCreate(AssessmentBase):
    """Schema for creating an assessment"""
    case_id: int
    text_score: Optional[int] = Field(None, ge=0, le=100)
    audio_score: Optional[int] = Field(None, ge=0, le=100)
    context_score: Optional[int] = Field(None, ge=0, le=100)
    threat_score: Optional[int] = Field(None, ge=0, le=100)
    distress_score: Optional[int] = Field(None, ge=0, le=100)
    final_svi: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    assessment_status: AssessmentStatus = AssessmentStatus.COMPLETED
    analysis_json: Optional[str] = None
    explanation_json: Optional[str] = None
    processing_time_ms: Optional[int] = None
    model_versions_json: Optional[str] = None


class AssessmentResponse(AssessmentBase, TimestampSchema):
    """Schema for assessment response"""
    id: int
    case_id: int
    text_score: Optional[int] = None
    audio_score: Optional[int] = None
    context_score: Optional[int] = None
    threat_score: Optional[int] = None
    distress_score: Optional[int] = None
    final_svi: Optional[int] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    assessment_status: AssessmentStatus
    analysis_json: Optional[str] = None
    explanation_json: Optional[str] = None
    processing_time_ms: Optional[int] = None
    model_versions_json: Optional[str] = None
    indicators: List[IndicatorResponse] = []
    recommendations: List[RecommendationResponse] = []


class TextAnalysisRequest(BaseSchema):
    """Schema for text analysis request"""
    case_id: str
    language: str = Field(default="en", min_length=2, max_length=10)
    text: str = Field(..., min_length=1)


class AudioAnalysisRequest(BaseSchema):
    """Schema for audio analysis request"""
    case_id: str
    language: str = Field(default="en", min_length=2, max_length=10)
    # Audio file will be handled via multipart/form-data


class AnalysisRequest(BaseSchema):
    """Schema for multimodal analysis request"""
    case_id: str
    language: str = Field(default="en", min_length=2, max_length=10)
    text: Optional[str] = None
    # Audio file will be handled via multipart/form-data
    context_metadata: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseSchema):
    """Schema for analysis response"""
    case_id: str
    transcript: Optional[str] = None
    svi: int
    risk_level: str
    confidence: float
    assessment_status: str
    audio_quality: Optional[str] = None
    indicators: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    explanation: List[str] = []