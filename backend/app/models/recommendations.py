"""
Recommendation Model
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from app.models.base import Base, IDMixin, TimestampMixin


class RecommendationType(str, enum.Enum):
    """Type of recommendation"""
    GENERAL_SUPPORT = "GENERAL_SUPPORT"
    COUNSELLING_REFERRAL = "COUNSELLING_REFERRAL"
    FOLLOW_UP = "FOLLOW_UP"
    PRIORITY_HUMAN_REVIEW = "PRIORITY_HUMAN_REVIEW"
    LEGAL_SUPPORT = "LEGAL_SUPPORT"
    SAFETY_ASSESSMENT = "SAFETY_ASSESSMENT"
    EMERGENCY_PROTOCOL = "EMERGENCY_PROTOCOL"
    PROTECTION_PATHWAY = "PROTECTION_PATHWAY"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"


class RecommendationPriority(str, enum.Enum):
    """Priority of the recommendation"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class RecommendationStatus(str, enum.Enum):
    """Status of the recommendation"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISMISSED = "DISMISSED"


class Recommendation(Base, IDMixin, TimestampMixin):
    """Recommendation model for AI-generated recommendations"""
    __tablename__ = "recommendations"
    
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[RecommendationType] = mapped_column(SQLEnum(RecommendationType), nullable=False)
    priority: Mapped[RecommendationPriority] = mapped_column(SQLEnum(RecommendationPriority), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)  # Explanation for the recommendation
    status: Mapped[RecommendationStatus] = mapped_column(
        SQLEnum(RecommendationStatus), 
        default=RecommendationStatus.PENDING, 
        nullable=False
    )
    
    # Source of recommendation
    source: Mapped[str] = mapped_column(String(50), default="AI", nullable=False)  # AI or HUMAN
    
    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="recommendations")
    
    # Indexes
    __table_args__ = (
        Index('ix_recommendations_case_status', 'case_id', 'status'),
        Index('ix_recommendations_priority', 'priority'),
    )
    
    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, case_id={self.case_id}, type='{self.type}', priority='{self.priority}')>"