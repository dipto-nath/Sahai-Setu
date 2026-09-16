"""
Assessment Model
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from app.models.base import Base, IDMixin, TimestampMixin


class AssessmentStatus(str, enum.Enum):
    """Assessment status enumeration"""
    COMPLETED = "COMPLETED"
    REVIEW_RECOMMENDED = "REVIEW_RECOMMENDED"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAILED = "FAILED"


class Assessment(Base, IDMixin, TimestampMixin):
    """Assessment model for AI analysis results"""
    __tablename__ = "assessments"
    
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Component scores (0-100 each)
    text_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    audio_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    context_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    threat_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    distress_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Final scores
    final_svi: Mapped[Optional[int]] = mapped_column(nullable=True)  # 0-100
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # LOW, MODERATE, HIGH, CRITICAL
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assessment_status: Mapped[AssessmentStatus] = mapped_column(
        SQLEnum(AssessmentStatus), 
        default=AssessmentStatus.COMPLETED, 
        nullable=False
    )
    
    # Detailed analysis (JSON)
    analysis_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Full analysis details
    explanation_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Human-readable explanations
    
    # Processing metadata
    processing_time_ms: Mapped[Optional[int]] = mapped_column(nullable=True)
    model_versions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="assessments")
    indicators: Mapped[List["Indicator"]] = relationship("Indicator", back_populates="assessment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_assessments_case_created', 'case_id', 'created_at'),
        Index('ix_assessments_risk_level', 'risk_level'),
        Index('ix_assessments_status', 'assessment_status'),
    )
    
    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, case_id={self.case_id}, svi={self.final_svi}, risk='{self.risk_level}')>"