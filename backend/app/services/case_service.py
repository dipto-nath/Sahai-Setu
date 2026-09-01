"""
Case Service for SIH26093

Handles case management operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import logging
import json

from app.models.cases import Case, CaseStatus, RiskLevel
from app.models.interactions import Interaction, InputType
from app.models.assessments import Assessment
from app.models.indicators import Indicator as IndicatorModel
from app.models.recommendations import Recommendation as RecommendationModel
from app.models.reviews import Review, ReviewDecision
from app.models.audit_log import AuditLog
from app.database import get_db
from app.schemas.cases import CaseCreate, CaseUpdate
from app.schemas.assessments import AssessmentCreate
from app.schemas.reviews import ReviewCreate
# Lazy import for AnalysisService to avoid old ai module dependency

logger = logging.getLogger(__name__)


class CaseService:
    """Service for managing cases."""

    def __init__(self, use_demo: bool = True):
        self.use_demo = use_demo
        self._analysis_service = None

    @property
    def analysis_service(self):
        """Lazy-load analysis service to avoid import errors"""
        if self._analysis_service is None:
            try:
                from app.services.analysis_service import AnalysisService
                self._analysis_service = AnalysisService(use_demo=self.use_demo)
            except ImportError:
                # Fallback to hybrid service
                from app.services.hybrid_assessment_service import get_hybrid_assessment_service
                self._analysis_service = get_hybrid_assessment_service(
                    use_gemini=self.use_demo,
                    demo_mode=self.use_demo
                )
        return self._analysis_service
    
    def generate_case_id(self) -> str:
        """Generate anonymous case ID."""
        return f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    def create_case(self, case_data: CaseCreate, user_id: Optional[int] = None) -> Case:
        """Create a new case."""
        db = next(get_db())
        try:
            case = Case(
                anonymous_case_id=self.generate_case_id(),
                language=case_data.language,
                status=CaseStatus.PENDING,
                risk_level=RiskLevel.LOW,
                svi=0,
                confidence=0.0,
                assigned_user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            
            # Log audit
            self._log_audit(db, user_id, "CASE_CREATED", case.id, {"language": case_data.language})
            
            # Convert to dict to avoid DetachedInstanceError
            return {
                "id": case.id,
                "anonymous_case_id": case.anonymous_case_id,
                "language": case.language,
                "status": case.status.value if hasattr(case.status, "value") else case.status,
                "risk_level": case.risk_level.value if hasattr(case.risk_level, "value") else case.risk_level,
                "svi": case.svi,
                "confidence": case.confidence,
                "assigned_user_id": case.assigned_user_id,
                "created_at": case.created_at.isoformat() if case.created_at else None,
                "updated_at": case.updated_at.isoformat() if case.updated_at else None,
            }
        finally:
            db.close()
    
    def get_case(self, case_id: int) -> Optional[Case]:
        """Get case by ID."""
        db = next(get_db())
        try:
            return db.query(Case).filter(Case.id == case_id).first()
        finally:
            db.close()
    
    def get_case_by_anonymous_id(self, anonymous_id: str) -> Optional[Case]:
        """Get case by anonymous case ID."""
        db = next(get_db())
        try:
            return db.query(Case).filter(Case.anonymous_case_id == anonymous_id).first()
        finally:
            db.close()
    
    def list_cases(self, skip: int = 0, limit: int = 100, risk_level: Optional[RiskLevel] = None) -> List[Case]:
        """List cases with optional filtering."""
        db = next(get_db())
        try:
            query = db.query(Case)
            if risk_level:
                query = query.filter(Case.risk_level == risk_level)
            return query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
        finally:
            db.close()
    
    def get_priority_cases(self, limit: int = 50) -> List[Case]:
        """Get high priority cases (HIGH and CRITICAL)."""
        db = next(get_db())
        try:
            return db.query(Case).filter(
                Case.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
            ).order_by(Case.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    def update_case(self, case_id: int, case_data: CaseUpdate, user_id: Optional[int] = None) -> Optional[Case]:
        """Update a case."""
        db = next(get_db())
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return None
            
            update_data = case_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(case, field, value)
            
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
            
            # Log audit
            self._log_audit(db, user_id, "CASE_UPDATED", case.id, update_data)
            
            return case
        finally:
            db.close()
    
    def add_interaction(self, case_id: int, interaction_type: InputType, language: str, content: str, user_id: Optional[int] = None) -> Interaction:
        """Add an interaction to a case."""
        db = next(get_db())
        try:
            interaction = Interaction(
                case_id=case_id,
                input_type=interaction_type,
                language=language,
                content=content,
                created_at=datetime.utcnow()
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            # Log audit
            self._log_audit(db, user_id, "INTERACTION_ADDED", case_id, {"type": interaction_type.value})
            
            return interaction
        finally:
            db.close()
    
    async def analyze_case(self, case_id: int, text: Optional[str] = None, audio_data: Optional[bytes] = None, language: str = "en", context: Optional[Dict[str, Any]] = None, user_id: Optional[int] = None, audio_storage_ref: Optional[str] = None) -> Assessment:
        """Analyze a case and create assessment."""
        db = next(get_db())
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                raise ValueError("Case not found")
            
            # Save the interaction (the actual text/audio from victim) BEFORE analysis
            if text and text.strip():
                text_interaction = Interaction(
                    case_id=case_id,
                    input_type=InputType.TEXT,
                    language=language,
                    text_content=text,
                    created_at=datetime.utcnow()
                )
                db.add(text_interaction)
                db.flush()
                self._log_audit(db, user_id, "INTERACTION_TEXT_ADDED", case_id, {
                    "interaction_id": text_interaction.id,
                    "language": language,
                    "length": len(text)
                })

            if audio_data:
                audio_interaction = Interaction(
                    case_id=case_id,
                    input_type=InputType.VOICE if not text else InputType.MULTIMODAL,
                    language=language,
                    audio_storage_ref=audio_storage_ref or f"audio_{case_id}_{int(datetime.utcnow().timestamp())}.webm",
                    duration_seconds=len(audio_data) / 32000,
                    created_at=datetime.utcnow()
                )
                db.add(audio_interaction)
                db.flush()
                self._log_audit(db, user_id, "INTERACTION_AUDIO_ADDED", case_id, {
                    "interaction_id": audio_interaction.id,
                    "size_bytes": len(audio_data)
                })

            # Run analysis
            if audio_data:
                if text:
                    result = await self.analysis_service.analyze_multimodal(case.anonymous_case_id, text, audio_data, language, context)
                else:
                    result = await self.analysis_service.analyze_audio(case.anonymous_case_id, audio_data, language, context)
            else:
                result = await self.analysis_service.analyze_text(case.anonymous_case_id, text, language, context)
            
            # Update audio interaction with transcript if available
            if audio_data and 'transcript' in result and result.get('transcript'):
                audio_interaction.text_content = result['transcript']
                # Removed: Overwriting audio_storage_ref with transcribed json name

            # Create assessment record
            assessment = Assessment(
                case_id=case_id,
                text_score=result.get("text_score", 0),
                audio_score=result.get("audio_score", 0),
                context_score=result.get("context_score", 0),
                threat_score=result.get("threat_score", 0),
                distress_score=result.get("distress_score", 0),
                final_svi=result["svi"],
                risk_level=RiskLevel(result["risk_level"]).value,
                confidence=result["confidence"],
                assessment_status=result["assessment_status"],
                analysis_json=json.dumps(result.get("gemini_response", {})) if "gemini_response" in result else None,
                explanation_json=json.dumps({
                    "summary": result.get("gemini_response", {}).get("summary", ""),
                    "care": result.get("gemini_response", {}).get("care", ""),
                    "action": result.get("gemini_response", {}).get("action", "")
                }) if "gemini_response" in result else None,
                created_at=datetime.utcnow()
            )
            db.add(assessment)
            
            # Update case
            case.svi = result["svi"]
            case.risk_level = RiskLevel(result["risk_level"])
            case.confidence = result["confidence"]
            case.status = CaseStatus.REVIEW_RECOMMENDED
            case.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(assessment)
            
            # Save indicators
            for ind_data in result.get("indicators", []):
                indicator = IndicatorModel(
                    assessment_id=assessment.id,
                    name=ind_data["name"],
                    severity=ind_data["severity"].upper() if ind_data.get("severity") else "MODERATE",
                    confidence=ind_data["confidence"],
                    source=ind_data["source"]
                )
                db.add(indicator)
            
            # Save recommendations
            for rec_data in result.get("recommendations", []):
                recommendation = RecommendationModel(
                    case_id=case_id,
                    type=rec_data["type"],
                    priority=rec_data["priority"],
                    reason=rec_data["reasoning"],
                    status="PENDING",
                    created_at=datetime.utcnow()
                )
                db.add(recommendation)
            
            db.commit()
            
            # Log audit
            self._log_audit(db, user_id, "CASE_ANALYZED", case_id, {
                "svi": result["svi"],
                "risk_level": result["risk_level"],
                "confidence": result["confidence"]
            })
            
            # Snapshot to dict to avoid DetachedInstanceError after session close
            db.refresh(assessment)
            return {
                "id": assessment.id,
                "case_id": assessment.case_id,
                "text_score": assessment.text_score,
                "audio_score": assessment.audio_score,
                "context_score": assessment.context_score,
                "threat_score": assessment.threat_score,
                "distress_score": assessment.distress_score,
                "final_svi": assessment.final_svi,
                "risk_level": assessment.risk_level.value if hasattr(assessment.risk_level, "value") else assessment.risk_level,
                "confidence": assessment.confidence,
                "assessment_status": assessment.assessment_status.value if hasattr(assessment.assessment_status, "value") else assessment.assessment_status,
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
                "updated_at": assessment.updated_at.isoformat() if assessment.updated_at else None,
            }
        finally:
            db.close()
    
    def add_review(self, case_id: int, review_data: ReviewCreate, reviewer_id: int) -> dict:
        """Add a human review to a case."""
        db = next(get_db())
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                raise ValueError("Case not found")
            
            ai_risk = case.risk_level or RiskLevel.LOW
            human_risk = RiskLevel(review_data.human_risk) if review_data.human_risk else ai_risk
            
            review = Review(
                case_id=case_id,
                reviewer_id=reviewer_id,
                ai_risk=ai_risk,
                human_risk=human_risk,
                decision=review_data.decision,
                notes=review_data.notes,
                assigned_counsellor=review_data.assigned_counsellor,
                assigned_legal_support=review_data.assigned_legal_support,
                escalated=review_data.escalated,
                created_at=datetime.utcnow()
            )
            db.add(review)
            
            # Update case with human decision
            case.risk_level = human_risk
            case.status = CaseStatus.REVIEWED
            case.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(review)
            
            # Log audit
            self._log_audit(db, reviewer_id, "CASE_REVIEWED", case_id, {
                "ai_risk": ai_risk.value if hasattr(ai_risk, "value") else str(ai_risk),
                "human_risk": human_risk.value if hasattr(human_risk, "value") else str(human_risk),
                "decision": review_data.decision.value if hasattr(review_data.decision, "value") else str(review_data.decision)
            })
            
            return {
                "id": review.id,
                "case_id": review.case_id,
                "reviewer_id": review.reviewer_id,
                "ai_risk": review.ai_risk,
                "human_risk": review.human_risk,
                "decision": review.decision,
                "notes": review.notes,
                "assigned_counsellor": review.assigned_counsellor,
                "assigned_legal_support": review.assigned_legal_support,
                "escalated": review.escalated,
                "created_at": review.created_at,
                "updated_at": review.updated_at,
            }
        finally:
            db.close()
    
    def assign_case(self, case_id: int, assigned_user_id: int, user_id: Optional[int] = None) -> Optional[Case]:
        """Assign a case to a user."""
        db = next(get_db())
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return None
            
            case.assigned_user_id = assigned_user_id
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
            
            # Log audit
            self._log_audit(db, user_id, "CASE_ASSIGNED", case_id, {"assigned_to": assigned_user_id})
            
            return case
        finally:
            db.close()
    
    def get_case_details(self, case_id: int) -> Optional[Dict[str, Any]]:
        """Get complete case details with assessments, indicators, recommendations, reviews."""
        db = next(get_db())
        try:
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return None
            
            # Get latest assessment
            assessment = db.query(Assessment).filter(Assessment.case_id == case_id).order_by(Assessment.created_at.desc()).first()
            
            # Get indicators
            indicators = []
            if assessment:
                indicators = db.query(IndicatorModel).filter(IndicatorModel.assessment_id == assessment.id).all()
            
            # Get recommendations
            recommendations = db.query(RecommendationModel).filter(RecommendationModel.case_id == case_id).all()
            
            # Get reviews
            reviews = db.query(Review).filter(Review.case_id == case_id).order_by(Review.created_at.desc()).all()
            
            # Get interactions
            interactions = db.query(Interaction).filter(Interaction.case_id == case_id).order_by(Interaction.created_at.desc()).all()
            
            # Convert to dicts to avoid DetachedInstanceError
            def to_dict(obj, fields):
                if obj is None:
                    return None
                result = {}
                for f in fields:
                    v = getattr(obj, f, None)
                    if v is None:
                        result[f] = None
                    elif hasattr(v, 'value'):
                        result[f] = v.value
                    elif isinstance(v, list):
                        result[f] = [to_dict(x, ['id', 'name', 'severity', 'confidence', 'source', 'type', 'priority', 'reason', 'status', 'language', 'text_content', 'input_type', 'created_at']) if x else None for x in v]
                    elif hasattr(v, 'isoformat'):
                        result[f] = v.isoformat()
                    else:
                        result[f] = v
                return result

            return {
                "case": to_dict(case, ['id', 'anonymous_case_id', 'language', 'status', 'risk_level', 'svi', 'confidence', 'assigned_user_id', 'created_at', 'updated_at']),
                "assessment": to_dict(assessment, ['id', 'case_id', 'text_score', 'audio_score', 'context_score', 'threat_score', 'distress_score', 'final_svi', 'risk_level', 'confidence', 'assessment_status', 'explanation_json', 'analysis_json', 'created_at', 'updated_at']) if assessment else None,
                "indicators": [to_dict(i, ['id', 'name', 'severity', 'confidence', 'source', 'created_at']) for i in indicators],
                "recommendations": [to_dict(r, ['id', 'type', 'priority', 'reason', 'status', 'created_at']) for r in recommendations],
                "reviews": [to_dict(r, ['id', 'ai_risk', 'human_risk', 'decision', 'notes', 'reviewer_id', 'created_at']) for r in reviews],
                "interactions": [to_dict(i, ['id', 'input_type', 'language', 'text_content', 'audio_storage_ref', 'created_at']) for i in interactions]
            }
        finally:
            db.close()
    
    def _log_audit(self, db, user_id: Optional[int], action: str, case_id: int, metadata: Dict[str, Any]):
        """Log audit entry."""
        audit = AuditLog(
            user_id=user_id,
            action=action,
            case_id=case_id,
            metadata=metadata
        )
        db.add(audit)
        db.commit()
