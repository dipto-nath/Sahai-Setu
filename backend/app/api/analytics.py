"""
Analytics API
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

from app.models.users import User
from app.models.cases import Case, RiskLevel
from app.models.reviews import Review
from app.models.assessments import Assessment
from app.database import get_db
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/risk-distribution")
async def get_risk_distribution(
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get risk level distribution"""
    db = next(get_db())
    try:
        risk_counts = db.query(Case.risk_level, func.count(Case.id)).group_by(Case.risk_level).all()
        return [{"risk_level": level.value, "count": count} for level, count in risk_counts]
    finally:
        db.close()


@router.get("/case-volume")
async def get_case_volume(
    days: int = 30,
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get case volume over time"""
    db = next(get_db())
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        results = db.query(
            func.date(Case.created_at).label('date'),
            func.count(Case.id).label('count')
        ).filter(Case.created_at >= cutoff).group_by(func.date(Case.created_at)).all()
        return [{"date": str(date), "count": count} for date, count in results]
    finally:
        db.close()


@router.get("/language-distribution")
async def get_language_distribution(
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get language distribution"""
    db = next(get_db())
    try:
        lang_counts = db.query(Case.language, func.count(Case.id)).group_by(Case.language).all()
        return [{"language": lang, "count": count} for lang, count in lang_counts]
    finally:
        db.close()


@router.get("/ai-vs-human")
async def get_ai_vs_human(
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Get AI vs human classification comparison"""
    db = next(get_db())
    try:
        reviews = db.query(Review.ai_risk, Review.human_risk).all()
        comparison = {}
        for ai_risk, human_risk in reviews:
            if human_risk:
                key = f"{ai_risk.value} -> {human_risk.value}"
                comparison[key] = comparison.get(key, 0) + 1
        return [{"comparison": k, "count": v} for k, v in comparison.items()]
    finally:
        db.close()
