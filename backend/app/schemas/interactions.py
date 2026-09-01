"""
Interaction Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.interactions import InputType


class InteractionBase(BaseSchema):
    """Base interaction schema"""
    input_type: InputType
    language: str = Field(default="en", min_length=2, max_length=10)


class InteractionCreate(InteractionBase):
    """Schema for creating an interaction"""
    case_id: int
    text_content: Optional[str] = None
    audio_storage_ref: Optional[str] = None
    duration_seconds: Optional[float] = Field(None, ge=0)
    metadata_json: Optional[str] = None


class InteractionResponse(InteractionBase, TimestampSchema):
    """Schema for interaction response"""
    id: int
    case_id: int
    text_content: Optional[str] = None
    audio_storage_ref: Optional[str] = None
    duration_seconds: Optional[float] = None
    metadata_json: Optional[str] = None