"""
Indicator Model
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from app.models.base import Base, IDMixin, TimestampMixin


class IndicatorSource(str, enum.Enum):
    """Source of the indicator detection"""
    TEXT = "TEXT"
    AUDIO = "AUDIO"
    CONTEXT = "CONTEXT"
    FUSION = "FUSION"


class IndicatorSeverity(str, enum.Enum):
    """Severity of the indicator"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Indicator(Base, IDMixin, TimestampMixin):
    """Indicator model for detected psychological/behavioral indicators"""
    __tablename__ = "indicators"
    
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "fear", "distress", "threat", "isolation"
    severity: Mapped[IndicatorSeverity] = mapped_column(SQLEnum(IndicatorSeverity), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[IndicatorSource] = mapped_column(SQLEnum(IndicatorSource), nullable=False)
    
    # Additional details
    details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Raw detection details
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Human-readable explanation
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="indicators")
    
    # Indexes
    __table_args__ = (
        Index('ix_indicators_assessment_name', 'assessment_id', 'name'),
        Index('ix_indicators_severity', 'severity'),
    )
    
    def __repr__(self) -> str:
        return f"<Indicator(id={self.id}, name='{self.name}', severity='{self.severity}', confidence={self.confidence})>"