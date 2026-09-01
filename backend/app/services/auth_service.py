"""
Authentication Service for SIH26093

Handles JWT token generation, validation, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
import bcrypt
import logging

from app.config import settings
from app.models.users import User, UserRole
from app.database import get_db
from app.schemas.users import UserCreate, UserLogin

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and authorization service."""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.jwt_expire_minutes
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user with identifier and password."""
        db = next(get_db())
        try:
            user = db.query(User).filter(
                (User.email == identifier) | (User.email == f"{identifier}@nhaa.local")
            ).first()
            if not user:
                return None
            if not self.verify_password(password, user.password_hash):
                return None
            return user
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        db = next(get_db())
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        db = next(get_db())
        try:
            # Check if user already exists
            existing = db.query(User).filter(User.email == user_data.identifier).first()
            if existing:
                raise ValueError("User with this identifier already exists")
            
            user = User(
                name=user_data.name,
                identifier=user_data.identifier,
                password_hash=self.hash_password(user_data.password),
                role=user_data.role,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = self.decode_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        return self.get_user_by_id(user_id)
    
    def has_permission(self, user: User, required_roles: list) -> bool:
        """Check if user has required role."""
        return user.role in required_roles
