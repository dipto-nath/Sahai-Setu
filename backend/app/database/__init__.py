"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator

from app.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Disable pooling for development
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session outside of FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database - create all tables"""
    from app.models.base import Base
    from app.models import users, cases, interactions, assessments, indicators, recommendations, reviews, audit_log
    
    Base.metadata.create_all(bind=engine)