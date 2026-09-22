"""
Recommendation Service for SIH26093

Provides explainable, rule-based recommendations based on SVI risk level and detected indicators.
This is a prototype decision-support system - NOT a medical diagnosis tool.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk classification levels."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    INCONCLUSIVE = "INCONCLUSIVE"


class RecommendationType(str, Enum):
    """Types of recommendations."""
    GENERAL_SUPPORT = "GENERAL_SUPPORT"
    COUNSELLING_REFERRAL = "COUNSELLING_REFERRAL"
    FOLLOW_UP = "FOLLOW_UP"
    PRIORITY_HUMAN_REVIEW = "PRIORITY_HUMAN_REVIEW"
    LEGAL_SUPPORT = "LEGAL_SUPPORT"
    SAFETY_ASSESSMENT = "SAFETY_ASSESSMENT"
    EMERGENCY_PROTOCOL = "EMERGENCY_PROTOCOL"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    OFFICER_GUIDANCE = "OFFICER_GUIDANCE"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


@dataclass
class Recommendation:
    """A single recommendation with explanation."""
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    reasoning: str
    applicable_roles: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "reasoning": self.reasoning,
            "applicable_roles": self.applicable_roles
        }


@dataclass
class Indicator:
    """Detected indicator from analysis."""
    name: str
    severity: str  # low, moderate, high, severe
    confidence: float
    source: str  # text, audio, context

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "severity": self.severity,
            "confidence": self.confidence,
            "source": self.source
        }


class RecommendationService(ABC):
    """Abstract base class for recommendation services."""
    
    @abstractmethod
    def generate_recommendations(
        self,
        svi_score: int,
        risk_level: RiskLevel,
        confidence: float,
        indicators: List[Indicator],
        assessment_status: str,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate recommendations based on analysis results."""
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about this recommendation service."""
        pass


class RuleBasedRecommendationService(RecommendationService):
    """
    Rule-based recommendation engine for prototype/demo purposes.
    
    IMPORTANT: This is a transparent rule-based system for demonstration.
    It is NOT a trained ML model. Do not present as AI/ML analysis.
    """
    
    def __init__(self):
        self.service_name = "Rule-Based Recommendation Engine"
        self.version = "1.0.0-prototype"
        logger.info("Initialized RuleBasedRecommendationService (DEMO MODE)")
    
    def generate_recommendations(
        self,
        svi_score: int,
        risk_level: RiskLevel,
        confidence: float,
        indicators: List[Indicator],
        assessment_status: str,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """Generate recommendations based on risk level and indicators."""
        
        recommendations = []
        
        # Handle inconclusive/low confidence cases first
        if assessment_status == "INCONCLUSIVE" or confidence < 0.5:
            recommendations.append(Recommendation(
                type=RecommendationType.HUMAN_REVIEW_REQUIRED,
                priority=RecommendationPriority.HIGH,
                title="Human Review Required",
                description="Automated assessment is inconclusive. A qualified human professional should review this case.",
                reasoning=f"Assessment status: {assessment_status}. Confidence: {confidence:.2f}. "
                         f"Automated analysis could not reliably determine risk level.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF", "ADMIN"]
            ))
            return recommendations
        
        # Generate recommendations based on risk level
        if risk_level == RiskLevel.LOW:
            recommendations.extend(self._get_low_risk_recommendations(indicators))
        elif risk_level == RiskLevel.MODERATE:
            recommendations.extend(self._get_moderate_risk_recommendations(indicators))
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend(self._get_high_risk_recommendations(indicators))
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.extend(self._get_critical_risk_recommendations(indicators))
        
        # Add indicator-specific recommendations
        recommendations.extend(self._get_indicator_specific_recommendations(indicators))
        
        # Add language-specific note if not English
        if language != "en":
            recommendations.append(Recommendation(
                type=RecommendationType.GENERAL_SUPPORT,
                priority=RecommendationPriority.LOW,
                title="Language Support Note",
                description=f"Case recorded in {language}. Ensure appropriate language support for follow-up.",
                reasoning=f"Interaction was in {language} (non-English).",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF", "LEGAL_OFFICER"]
            ))
        
        return recommendations
    
    def _get_low_risk_recommendations(self, indicators: List[Indicator]) -> List[Recommendation]:
        """Recommendations for LOW risk (SVI 0-25)."""
        return [
            Recommendation(
                type=RecommendationType.GENERAL_SUPPORT,
                priority=RecommendationPriority.LOW,
                title="General Support Information",
                description="Provide information about available support services and helplines.",
                reasoning="Low SVI score with minimal distress indicators detected.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF"]
            ),
            Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.LOW,
                title="Optional Counselling Information",
                description="Share information about counselling services available through the helpline.",
                reasoning="Proactive support information for general wellbeing.",
                applicable_roles=["COUNSELLOR"]
            )
        ]
    
    def _get_moderate_risk_recommendations(self, indicators: List[Indicator]) -> List[Recommendation]:
        """Recommendations for MODERATE risk (SVI 26-50)."""
        return [
            Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.MEDIUM,
                title="Counselling Referral Recommended",
                description="Refer to qualified counsellor for psychological support assessment.",
                reasoning="Moderate SVI score with detectable distress/fear indicators.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF"]
            ),
            Recommendation(
                type=RecommendationType.FOLLOW_UP,
                priority=RecommendationPriority.MEDIUM,
                title="Scheduled Follow-up",
                description="Schedule follow-up contact within 48-72 hours to reassess situation.",
                reasoning="Moderate risk level warrants proactive follow-up.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF"]
            ),
            Recommendation(
                type=RecommendationType.GENERAL_SUPPORT,
                priority=RecommendationPriority.LOW,
                title="Support Services Information",
                description="Provide comprehensive information about available support services.",
                reasoning="Moderate indicators suggest benefit from support service awareness.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF"]
            )
        ]
    
    def _get_high_risk_recommendations(self, indicators: List[Indicator]) -> List[Recommendation]:
        """Recommendations for HIGH risk (SVI 51-75)."""
        return [
            Recommendation(
                type=RecommendationType.PRIORITY_HUMAN_REVIEW,
                priority=RecommendationPriority.HIGH,
                title="Priority Human Review",
                description="Case requires immediate review by qualified human professional.",
                reasoning="High SVI score with elevated distress, fear, and/or threat indicators.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF", "ADMIN"]
            ),
            Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.HIGH,
                title="Urgent Counselling Referral",
                description="Immediate referral to trauma-informed counsellor or mental health professional.",
                reasoning="High distress and fear indicators detected requiring professional intervention.",
                applicable_roles=["COUNSELLOR"]
            ),
            Recommendation(
                type=RecommendationType.LEGAL_SUPPORT,
                priority=RecommendationPriority.MEDIUM,
                title="Legal Support Pathway",
                description="Connect with legal aid services for guidance on protection and rights.",
                reasoning="Threat and intimidation indicators suggest need for legal guidance.",
                applicable_roles=["LEGAL_OFFICER", "AUTHORIZED_STAFF"]
            ),
            Recommendation(
                type=RecommendationType.SAFETY_ASSESSMENT,
                priority=RecommendationPriority.HIGH,
                title="Safety Assessment Required",
                description="Conduct immediate safety assessment for complainant and family.",
                reasoning="Elevated threat and vulnerability indicators present.",
                applicable_roles=["AUTHORIZED_STAFF", "ADMIN"]
            )
        ]
    
    def _get_critical_risk_recommendations(self, indicators: List[Indicator]) -> List[Recommendation]:
        """Recommendations for CRITICAL risk (SVI 76-100)."""
        return [
            Recommendation(
                type=RecommendationType.PRIORITY_HUMAN_REVIEW,
                priority=RecommendationPriority.URGENT,
                title="Immediate Human Review Required",
                description="URGENT: Case requires immediate review by senior qualified professional.",
                reasoning="Critical SVI score with severe distress, threat, and vulnerability indicators.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF", "ADMIN"]
            ),
            Recommendation(
                type=RecommendationType.SAFETY_ASSESSMENT,
                priority=RecommendationPriority.URGENT,
                title="Immediate Safety Assessment",
                description="URGENT: Conduct immediate safety assessment and protection planning.",
                reasoning="Severe threat and safety indicators detected.",
                applicable_roles=["AUTHORIZED_STAFF", "ADMIN"]
            ),
            Recommendation(
                type=RecommendationType.EMERGENCY_PROTOCOL,
                priority=RecommendationPriority.URGENT,
                title="Emergency Support Protocol",
                description="Activate appropriate emergency support and protection protocols.",
                reasoning="Critical vulnerability indicators requiring immediate protective action.",
                applicable_roles=["ADMIN", "AUTHORIZED_STAFF"]
            ),
            Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.URGENT,
                title="Emergency Counselling/Trauma Support",
                description="Immediate connection to trauma-informed crisis support services.",
                reasoning="Severe distress and trauma-related indicators detected.",
                applicable_roles=["COUNSELLOR"]
            ),
            Recommendation(
                type=RecommendationType.LEGAL_SUPPORT,
                priority=RecommendationPriority.HIGH,
                title="Emergency Legal Protection",
                description="Expedite legal protection measures and witness protection if applicable.",
                reasoning="Critical threat and intimidation indicators present.",
                applicable_roles=["LEGAL_OFFICER", "ADMIN"]
            )
        ]
    
    def _get_indicator_specific_recommendations(self, indicators: List[Indicator]) -> List[Recommendation]:
        """Add recommendations based on specific detected indicators."""
        recommendations = []
        indicator_names = [i.name.lower() for i in indicators]
        
        # Threat-specific
        if any("threat" in name or "intimidat" in name for name in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.SAFETY_ASSESSMENT,
                priority=RecommendationPriority.HIGH,
                title="Threat-Specific Safety Planning",
                description="Develop specific safety plan addressing reported threats and intimidation.",
                reasoning="Threat/intimidation indicators detected in analysis.",
                applicable_roles=["AUTHORIZED_STAFF", "LEGAL_OFFICER"]
            ))
        
        # Isolation-specific
        if any("isola" in name or "boycott" in name or "displac" in name for name in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.GENERAL_SUPPORT,
                priority=RecommendationPriority.MEDIUM,
                title="Social Support Connection",
                description="Connect with community support organizations and social services.",
                reasoning="Social isolation/displacement indicators detected.",
                applicable_roles=["COUNSELLOR", "AUTHORIZED_STAFF"]
            ))
        
        # Trauma-specific
        if any("trauma" in name or "severe" in name for name in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.HIGH,
                title="Trauma-Informed Specialist Referral",
                description="Refer to specialist trauma counselling services.",
                reasoning="Trauma-related indicators detected requiring specialized support.",
                applicable_roles=["COUNSELLOR"]
            ))
        
        return recommendations
    
    def get_service_info(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "version": self.version,
            "type": "rule-based",
            "description": "Transparent rule-based recommendation engine for prototype demonstration. NOT an ML model.",
            "disclaimer": "DEMO RULE-BASED ANALYSIS - Recommendations are based on prototype rules, not validated clinical models."
        }


# Factory function for getting recommendation service
def get_recommendation_service(use_demo: bool = True) -> RecommendationService:
    """
    Factory function to get the appropriate recommendation service.
    
    Args:
        use_demo: If True, returns demo rule-based service.
                  If False, would return ML-based service (future implementation).
    
    Returns:
        RecommendationService instance
    """
    if use_demo:
        return RuleBasedRecommendationService()
    else:
        # Future: return ML-based service
        # For now, fall back to rule-based with warning
        logger.warning("ML-based recommendation service not implemented, falling back to rule-based")
        return RuleBasedRecommendationService()
