"""
User Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampSchema
from app.models.users import UserRole


class UserBase(BaseSchema):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    role: UserRole = UserRole.AUTHORIZED_STAFF


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase, TimestampSchema):
    """Schema for user response"""
    id: int
    is_active: bool


class UserLogin(BaseSchema):
    """Schema for user login"""
    email: str
    password: str


class Token(BaseSchema):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseSchema):
    """Schema for token payload"""
    user_id: int
    email: str
    role: UserRole
    exp: int