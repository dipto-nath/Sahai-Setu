"""
Users API Routes for SIH26093
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.models.users import User, UserRole
from app.schemas.users import UserResponse, UserCreate
from app.services.auth_service import AuthService
from app.database import get_db
from app.api.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/users", tags=["Users"])
auth_service = AuthService()


@router.get("", response_model=List[UserResponse])
async def list_users(current_user: User = Depends(get_current_admin)):
    """List all users (admin only)."""
    db = next(get_db())
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: User = Depends(get_current_admin)):
    """Get user by ID (admin only)."""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()


@router.post("", response_model=UserResponse)
async def create_user(user_data: UserCreate, current_user: User = Depends(get_current_admin)):
    """Create new user (admin only)."""
    try:
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/roles/list")
async def list_roles(current_user: User = Depends(get_current_user)):
    """List available roles."""
    return [{"value": role.value, "label": role.value.replace('_', ' ').title()} for role in UserRole]
