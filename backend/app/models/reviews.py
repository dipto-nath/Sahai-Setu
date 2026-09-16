"""
Review Model
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from app.models.base import Base, IDMixin, TimestampMixin
from app.models.cases import RiskLevel


class ReviewDecision(str, enum.Enum):
    """Human review decision"""
    CONFIRM_AI = "CONFIRM_AI"
    MODIFY_RISK = "MODIFY_RISK"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    FALSE_NEGATIVE = "FALSE_NEGATIVE"
    REQUEST_REASSESSMENT = "REQUEST_REASSESSMENT"
    ESCALATE = "ESCALATE"


class Review(Base, IDMixin, TimestampMixin):
    """Review model for human review of AI assessments"""
    __tablename__ = "reviews"
    
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # AI vs Human assessment
    ai_risk: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), nullable=False)
    human_risk: Mapped[Optional[RiskLevel]] = mapped_column(SQLEnum(RiskLevel), nullable=True)
    
    # Decision
    decision: Mapped[ReviewDecision] = mapped_column(SQLEnum(ReviewDecision), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Actions taken
    assigned_counsellor: Mapped[Optional[bool]] = mapped_column(default=False, nullable=False)
    assigned_legal_support: Mapped[Optional[bool]] = mapped_column(default=False, nullable=False)
    escalated: Mapped[Optional[bool]] = mapped_column(default=False, nullable=False)
    
    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index('ix_reviews_case_created', 'case_id', 'created_at'),
        Index('ix_reviews_reviewer', 'reviewer_id'),
    )
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, case_id={self.case_id}, decision='{self.decision}')>"