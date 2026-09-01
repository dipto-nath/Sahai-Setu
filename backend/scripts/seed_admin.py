"""Create a default admin user for development."""
import sys
import os

# Add paths
sys.path.insert(0, '/Users/diptonath/Documents/coding/nhaa-ai-triage/backend')
sys.path.insert(0, '/Users/diptonath/Documents/coding/nhaa-ai-triage')

from app.database import SessionLocal, init_db, engine
from app.models.users import User, UserRole
from app.services.auth_service import AuthService
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed():
    init_db()
    db = SessionLocal()
    try:
        auth = AuthService()
        # Create demo users
        users_to_create = [
            ("Admin User", "admin", "admin123", UserRole.ADMIN),
            ("Counsellor User", "counsellor", "counsellor123", UserRole.COUNSELLOR),
            ("Legal Officer", "legal", "legal123", UserRole.LEGAL_OFFICER),
            ("Staff User", "officer1", "demo123", UserRole.AUTHORIZED_STAFF),
        ]
        for name, email, password, role in users_to_create:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                logger.info(f"User {email} already exists")
                continue
            user = User(
                name=name,
                email=email,
                password_hash=auth.hash_password(password),
                role=role,
                is_active=True,
            )
            db.add(user)
            db.commit()
            logger.info(f"Created user: {email} ({role.value})")
        logger.info("Seed complete!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
