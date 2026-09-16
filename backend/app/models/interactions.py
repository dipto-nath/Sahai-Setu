"""
Interaction Model
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from app.models.base import Base, IDMixin, TimestampMixin


class InputType(str, enum.Enum):
    """Type of input received"""
    TEXT = "TEXT"
    VOICE = "VOICE"
    MULTIMODAL = "MULTIMODAL"


class Interaction(Base, IDMixin, TimestampMixin):
    """Interaction model for victim/complainant inputs"""
    __tablename__ = "interactions"
    
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    input_type: Mapped[InputType] = mapped_column(SQLEnum(InputType), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Content (text transcript or reference to audio file)
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audio_storage_ref: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Metadata
    duration_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string for additional metadata
    
    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="interactions")
    
    # Indexes
    __table_args__ = (
        Index('ix_interactions_case_created', 'case_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, case_id={self.case_id}, type='{self.input_type}')>"