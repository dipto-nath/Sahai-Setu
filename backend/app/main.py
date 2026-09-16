"""
Main FastAPI Application for SahaiSetu (SIH26093)

AI-Assisted Multimodal Stress and Vulnerability Assessment Platform
Hybrid AI architecture: Local processing + Gemini contextual analysis
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api import auth, cases, dashboard, analysis, recommendations, audit_log, users
from app.api import assessment as hybrid_assessment
from app.api import assessment_root as root_assessment
from app.api import cases_root as root_cases
from app.api import review as review_api
from app.api import dashboard as dashboard_api
from app.api import analytics as analytics_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting SahaiSetu backend...")
    logger.info("Architecture: Hybrid AI - Local Processing + Gemini Contextual Analysis")
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        # Seed demo users for Render deployment
        from app.database import SessionLocal
        from app.models.users import User, UserRole
        from app.services.auth_service import AuthService
        db = SessionLocal()
        try:
            auth = AuthService()
            demo_users = [
                ("Admin User", "admin@nhaa.local", "admin123", UserRole.ADMIN),
                ("Counsellor", "counsellor@nhaa.local", "counsellor123", UserRole.COUNSELLOR),
                ("Legal Officer", "legal@nhaa.local", "legal123", UserRole.LEGAL_OFFICER),
                ("Staff User", "officer1@nhaa.local", "demo123", UserRole.AUTHORIZED_STAFF),
            ]
            for name, email, password, role in demo_users:
                if not db.query(User).filter(User.email == email).first():
                    db.add(User(name=name, email=email, password_hash=auth.hash_password(password), role=role))
            db.commit()
            logger.info("Demo users seeded successfully")
        except Exception as seed_err:
            logger.error(f"Failed to seed demo users: {seed_err}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    yield
    # Shutdown
    logger.info("Shutting down SahaiSetu backend...")


app = FastAPI(
    title="SahaiSetu API",
    description="AI-Assisted Multimodal Stress and Vulnerability Assessment Platform for SIH26093. "
                "Hybrid AI architecture: Local processing (NLP, audio) + Gemini API contextual analysis. "
                "All AI outputs are labeled as AI-Assisted Assessment. "
                "Final decisions require authorized human review.",
    version="2.0.0-hybrid",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - service information."""
    return {
        "service": "SahaiSetu API",
        "version": "2.0.0-hybrid",
        "project": "SIH26093",
        "status": "running",
        "demo_mode": settings.demo_mode,
        "architecture": "Hybrid AI - Local Processing + Gemini Contextual Analysis",
        "important_notice": "AI-Assisted Assessment only. NOT a medical diagnosis. Final decisions require authorized human review.",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth/login, /auth/me",
            "cases": "/cases",
            "text_assessment": "/assessment/text",
            "voice_assessment": "/assessment/voice",
            "review": "/review/{case_id}",
            "dashboard": "/dashboard/overview",
            "analytics": "/analytics/risk-distribution, /analytics/case-volume",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.database import engine
    from sqlalchemy import text
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "demo_mode": settings.demo_mode,
        "version": "2.0.0-hybrid",
    }


# Add custom exception handler for better error visibility
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Response validation error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal response validation error", "errors": str(exc.errors()) if hasattr(exc, 'errors') else str(exc)},
    )

# Include API routers
app.include_router(auth.router, tags=["auth"])
app.include_router(cases.router, tags=["cases"])

# Hybrid assessment endpoints (per SIH26093 spec)
# Both /api/assessment/... and /assessment/... paths for compatibility
app.include_router(hybrid_assessment.router, tags=["hybrid-assessment"])
app.include_router(root_assessment.router, tags=["assessment"])

# Root-level cases endpoints
app.include_router(root_cases.router, tags=["cases-root"])

# Review, dashboard, analytics (both /api and root-level prefixes)
app.include_router(dashboard_api.router, prefix="/api", tags=["dashboard-api"])
app.include_router(dashboard_api.router, tags=["dashboard"])
app.include_router(analytics_api.router, prefix="/api", tags=["analytics-api"])
app.include_router(analytics_api.router, tags=["analytics"])
app.include_router(review_api.router, prefix="/api", tags=["review-api"])
app.include_router(review_api.router, tags=["review"])

from app.api import live_call
app.include_router(live_call.router, tags=["live-call"])

app.include_router(analysis.router, tags=["analysis"])
app.include_router(recommendations.router, tags=["recommendations"])
app.include_router(audit_log.router, tags=["audit-log"])
app.include_router(users.router, tags=["users"])

# Mount uploads directory for serving audio files
import os
from starlette.staticfiles import StaticFiles
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
