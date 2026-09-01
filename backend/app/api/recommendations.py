"""
Recommendations API Routes for SIH26093
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from app.models.users import User
from app.models.recommendations import Recommendation as RecommendationModel
from app.database import get_db
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/{case_id}", response_model=List[Dict[str, Any]])
async def get_recommendations(case_id: int, current_user: User = Depends(get_current_user)):
    """Get recommendations for a case."""
    db = next(get_db())
    try:
        recommendations = db.query(RecommendationModel).filter(RecommendationModel.case_id == case_id).all()
        return [
            {
                "id": r.id,
                "type": r.type,
                "priority": r.priority,
                "reason": r.reason,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in recommendations
        ]
    finally:
        db.close()
