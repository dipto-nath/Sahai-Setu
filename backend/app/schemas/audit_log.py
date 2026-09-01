"""
Audit Log Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema


class AuditLogBase(BaseSchema):
    """Base audit log schema"""
    action: str = Field(..., min_length=1, max_length=100)


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log"""
    user_id: Optional[int] = None
    case_id: Optional[int] = None
    metadata_json: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(AuditLogBase, TimestampSchema):
    """Schema for audit log response"""
    id: int
    user_id: Optional[int] = None
    case_id: Optional[int] = None
    metadata_json: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogListResponse(BaseSchema):
    """Schema for paginated audit log list"""
    logs: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int