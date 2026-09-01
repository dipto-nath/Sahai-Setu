"""
Authentication API Routes for SIH26093
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

from app.schemas.users import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.models.users import User, UserRole
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
auth_service = AuthService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user."""
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[User]:
    """Get authenticated user if token present, else None."""
    if not token:
        return None
    return auth_service.get_current_user(token)


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login - returns JWT token."""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect identifier or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60,
    }


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, current_user: User = Depends(get_current_admin)):
    """Register new user (admin only)."""
    try:
        user = auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user
