"""
Audit Log Model
"""
from sqlalchemy import String, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, IDMixin, TimestampMixin


class AuditLog(Base, IDMixin, TimestampMixin):
    """Audit log for important system actions"""
    __tablename__ = "audit_logs"
    
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., CASE_CREATED, CASE_REVIEWED, LOGIN
    case_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cases.id"), nullable=True, index=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Additional context
    
    # IP and user agent for security
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    case: Mapped[Optional["Case"]] = relationship("Case", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('ix_audit_logs_user_created', 'user_id', 'created_at'),
        Index('ix_audit_logs_case_created', 'case_id', 'created_at'),
        Index('ix_audit_logs_action', 'action'),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, case_id={self.case_id})>"