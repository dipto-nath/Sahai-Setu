"""
Dashboard Service for SIH26093

Provides analytics and dashboard data.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from app.models.cases import Case, RiskLevel
from app.models.reviews import Review, ReviewDecision
from app.models.audit_log import AuditLog
from app.database import get_db
from sqlalchemy import func

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard analytics."""
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard."""
        db = next(get_db())
        try:
            total_cases = db.query(func.count(Case.id)).scalar() or 0
            
            # Risk distribution
            risk_counts = db.query(Case.risk_level, func.count(Case.id)).group_by(Case.risk_level).all()
            risk_dist = {level.value: count for level, count in risk_counts}
            
            # Pending human review
            pending_review = db.query(func.count(Case.id)).filter(Case.status == "PENDING_REVIEW").scalar() or 0
            
            return {
                "total_cases": total_cases,
                "low": risk_dist.get("LOW", 0),
                "moderate": risk_dist.get("MODERATE", 0),
                "high": risk_dist.get("HIGH", 0),
                "critical": risk_dist.get("CRITICAL", 0),
                "pending_human_review": pending_review
            }
        finally:
            db.close()
    
    def get_risk_distribution(self) -> List[Dict[str, Any]]:
        """Get risk level distribution for charts."""
        db = next(get_db())
        try:
            risk_counts = db.query(Case.risk_level, func.count(Case.id)).group_by(Case.risk_level).all()
            return [{"risk_level": level.value, "count": count} for level, count in risk_counts]
        finally:
            db.close()
    
    def get_language_distribution(self) -> List[Dict[str, Any]]:
        """Get language distribution for charts."""
        db = next(get_db())
        try:
            lang_counts = db.query(Case.language, func.count(Case.id)).group_by(Case.language).all()
            return [{"language": lang, "count": count} for lang, count in lang_counts]
        finally:
            db.close()
    
    def get_cases_over_time(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get cases over time for charts."""
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
    
    def get_average_processing_time(self) -> float:
        """Get average processing time in minutes."""
        db = next(get_db())
        try:
            # This would need actual processing time tracking
            # For now return a placeholder
            return 5.0
        finally:
            db.close()
    
    def get_human_review_outcomes(self) -> List[Dict[str, Any]]:
        """Get human review outcomes."""
        db = next(get_db())
        try:
            outcomes = db.query(Review.decision, func.count(Review.id)).group_by(Review.decision).all()
            return [{"decision": decision.value, "count": count} for decision, count in outcomes]
        finally:
            db.close()
    
    def get_ai_vs_human_comparison(self) -> List[Dict[str, Any]]:
        """Get AI vs human classification comparison."""
        db = next(get_db())
        try:
            reviews = db.query(Review.ai_risk, Review.human_risk).all()
            comparison = {}
            for ai_risk, human_risk in reviews:
                key = f"{ai_risk} -> {human_risk}"
                comparison[key] = comparison.get(key, 0) + 1
            
            return [{"comparison": k, "count": v} for k, v in comparison.items()]
        finally:
            db.close()
    
    def get_confidence_distribution(self) -> List[Dict[str, Any]]:
        """Get model confidence distribution."""
        db = next(get_db())
        try:
            from app.models.assessments import Assessment
            assessments = db.query(Assessment.confidence).all()
            
            # Bucket confidences
            buckets = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
            for (conf,) in assessments:
                if conf < 0.2:
                    buckets["0.0-0.2"] += 1
                elif conf < 0.4:
                    buckets["0.2-0.4"] += 1
                elif conf < 0.6:
                    buckets["0.4-0.6"] += 1
                elif conf < 0.8:
                    buckets["0.6-0.8"] += 1
                else:
                    buckets["0.8-1.0"] += 1
            
            return [{"range": k, "count": v} for k, v in buckets.items()]
        finally:
            db.close()
    
    def get_full_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard data."""
        return {
            "summary": self.get_summary_stats(),
            "risk_distribution": self.get_risk_distribution(),
            "language_distribution": self.get_language_distribution(),
            "cases_over_time": self.get_cases_over_time(),
            "average_processing_time": self.get_average_processing_time(),
            "human_review_outcomes": self.get_human_review_outcomes(),
            "ai_vs_human_comparison": self.get_ai_vs_human_comparison(),
            "confidence_distribution": self.get_confidence_distribution()
        }
