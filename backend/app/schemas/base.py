"""
Base Schemas
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseModel):
    """Schema with timestamps"""
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)