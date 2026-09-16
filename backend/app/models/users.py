"""
User Model
"""
from sqlalchemy import String, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
import enum

from app.models.base import Base, IDMixin, TimestampMixin


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "ADMIN"
    COUNSELLOR = "COUNSELLOR"
    LEGAL_OFFICER = "LEGAL_OFFICER"
    AUTHORIZED_STAFF = "AUTHORIZED_STAFF"


class User(Base, IDMixin, TimestampMixin):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), 
        default=UserRole.AUTHORIZED_STAFF, 
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    assigned_cases: Mapped[List["Case"]] = relationship("Case", back_populates="assigned_user", foreign_keys="Case.assigned_user_id")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="reviewer")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('ix_users_email_active', 'email', 'is_active'),
        Index('ix_users_role', 'role'),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"