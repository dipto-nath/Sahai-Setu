"""
Case Model
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
import enum

from app.models.base import Base, IDMixin, TimestampMixin


class CaseStatus(str, enum.Enum):
    """Case status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW_RECOMMENDED = "REVIEW_RECOMMENDED"
    REVIEWED = "REVIEWED"
    CLOSED = "CLOSED"
    INCONCLUSIVE = "INCONCLUSIVE"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Case(Base, IDMixin, TimestampMixin):
    """Case model for victim/complainant cases"""
    __tablename__ = "cases"
    
    # Anonymous case identifier (e.g., CASE-2026-000123)
    anonymous_case_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Language of interaction
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Case status
    status: Mapped[CaseStatus] = mapped_column(
        SQLEnum(CaseStatus), 
        default=CaseStatus.PENDING, 
        nullable=False
    )
    
    # Risk assessment
    risk_level: Mapped[Optional[RiskLevel]] = mapped_column(SQLEnum(RiskLevel), nullable=True)
    svi: Mapped[Optional[int]] = mapped_column(nullable=True)  # Stress Vulnerability Index (0-100)
    confidence: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Assignment
    assigned_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Relationships
    assigned_user: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_user_id], lazy="noload")
    interactions: Mapped[List["Interaction"]] = relationship("Interaction", back_populates="case", cascade="all, delete-orphan")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="case", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="case", cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="case", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_cases_status_risk', 'status', 'risk_level'),
        Index('ix_cases_assigned_user', 'assigned_user_id'),
        Index('ix_cases_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Case(id={self.id}, anonymous_case_id='{self.anonymous_case_id}', risk='{self.risk_level}')>"