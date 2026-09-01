"""
Dashboard API
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

from app.models.users import User
from app.models.cases import Case, RiskLevel, CaseStatus
from app.models.reviews import Review
from app.models.assessments import Assessment
from app.database import get_db
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


from app.services.dashboard_service import DashboardService

dashboard_service = DashboardService()


@router.get("", response_model=Dict[str, Any])
async def get_full_dashboard(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get full dashboard data with risk distribution, trends, and review stats"""
    return dashboard_service.get_full_dashboard()


@router.get("/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get dashboard summary statistics"""
    return dashboard_service.get_summary_stats()


@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get dashboard overview statistics"""
    db = next(get_db())
    try:
        total_cases = db.query(func.count(Case.id)).scalar() or 0
        risk_counts = db.query(Case.risk_level, func.count(Case.id)).group_by(Case.risk_level).all()
        risk_dist = {level.value: count for level, count in risk_counts}
        pending_review = db.query(func.count(Case.id)).filter(
            Case.status.in_([CaseStatus.REVIEW_RECOMMENDED, CaseStatus.PENDING, CaseStatus.IN_PROGRESS])
        ).scalar() or 0
        critical_cases = db.query(func.count(Case.id)).filter(
            Case.risk_level == RiskLevel.CRITICAL
        ).scalar() or 0
        return {
            "summary": {
                "total_cases": total_cases,
                "low": risk_dist.get("LOW", 0),
                "moderate": risk_dist.get("MODERATE", 0),
                "high": risk_dist.get("HIGH", 0),
                "critical": risk_dist.get("CRITICAL", 0),
                "pending_review": pending_review,
                "critical_cases": critical_cases,
            },
            "system_info": {
                "architecture": "Hybrid AI - Local Processing + Gemini Contextual Analysis",
                "disclaimer": "All metrics are AI-Assessed. Human review required for decisions.",
            },
        }
    finally:
        db.close()


@router.get("/priority-cases")
async def get_priority_cases(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """Get high priority cases (HIGH and CRITICAL)"""
    db = next(get_db())
    try:
        cases = db.query(Case).filter(
            Case.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).order_by(Case.created_at.desc()).limit(limit).all()
        return [
            {
                "id": c.id,
                "anonymous_case_id": c.anonymous_case_id,
                "language": c.language,
                "risk_level": c.risk_level.value if c.risk_level else None,
                "svi": c.svi,
                "confidence": c.confidence,
                "status": c.status.value if c.status else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in cases
        ]
    finally:
        db.close()
