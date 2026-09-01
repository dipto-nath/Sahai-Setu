"""
Recommendation Engine
Rule-based, transparent recommendations for AI-assisted assessments.
Does NOT automatically dispatch emergency services.
All recommendations require authorized human review.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RecommendationType(str, Enum):
    GENERAL_SUPPORT = "GENERAL_SUPPORT"
    COUNSELLING_REFERRAL = "COUNSELLING_REFERRAL"
    FOLLOW_UP = "FOLLOW_UP"
    PRIORITY_HUMAN_REVIEW = "PRIORITY_HUMAN_REVIEW"
    LEGAL_SUPPORT = "LEGAL_SUPPORT"
    SAFETY_ASSESSMENT = "SAFETY_ASSESSMENT"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"


class RecommendationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


@dataclass
class Recommendation:
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    reasoning: str
    source: str = "AI"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "reasoning": self.reasoning,
            "source": self.source,
        }


class RecommendationService:
    """Rule-based recommendation engine"""

    def generate_recommendations(
        self,
        svi_score: int,
        risk_level: str,
        confidence: float,
        assessment_status: str,
        indicators: List[Dict[str, Any]] = None,
        text_features: Optional[Dict[str, Any]] = None,
        context_features: Optional[Dict[str, Any]] = None,
        audio_features: Optional[Dict[str, Any]] = None,
    ) -> List[Recommendation]:
        """
        Generate recommendations based on assessment results.
        
        IMPORTANT: This is AI-Assisted Recommendation only.
        Does NOT automatically dispatch police, medical, or emergency services.
        """
        recommendations = []
        indicators = indicators or []
        indicator_names = [i.get("name", "").lower() for i in indicators]

        # Always recommend human review if assessment is inconclusive
        if assessment_status == "INCONCLUSIVE":
            recommendations.append(Recommendation(
                type=RecommendationType.HUMAN_REVIEW_REQUIRED,
                priority=RecommendationPriority.HIGH,
                title="Human Review Required",
                description="Assessment confidence is below threshold. Authorized human review required.",
                reasoning="Confidence below inconclusive threshold",
            ))

        # Always recommend human review for CRITICAL risk
        if risk_level == "CRITICAL":
            recommendations.append(Recommendation(
                type=RecommendationType.PRIORITY_HUMAN_REVIEW,
                priority=RecommendationPriority.URGENT,
                title="Priority Human Review Recommended",
                description="Critical stress/vulnerability indicators detected. Immediate review by authorized human professional recommended.",
                reasoning=f"Critical risk level (SVI: {svi_score}) with high concern indicators",
            ))

        # HIGH risk - Priority human review
        elif risk_level == "HIGH":
            recommendations.append(Recommendation(
                type=RecommendationType.PRIORITY_HUMAN_REVIEW,
                priority=RecommendationPriority.HIGH,
                title="Priority Human Review Recommended",
                description="High stress/vulnerability indicators detected. Human review recommended.",
                reasoning=f"High risk level (SVI: {svi_score})",
            ))

        # Threat-related indicators
        if any("threat" in n or "intimid" in n for n in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.SAFETY_ASSESSMENT,
                priority=RecommendationPriority.HIGH,
                title="Safety Assessment Recommended",
                description="Safety assessment recommended for authorized review based on detected threat indicators.",
                reasoning="Threat or intimidation indicators present",
            ))

        # Distress-related indicators
        if any("distress" in n for n in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.MEDIUM,
                title="Counselling Support Pathway",
                description="Counselling support pathway recommended for authorized review.",
                reasoning="Distress-related communication indicators detected",
            ))

        # Isolation indicators
        if any("isola" in n or "social" in n for n in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.GENERAL_SUPPORT,
                priority=RecommendationPriority.MEDIUM,
                title="Social Support Connection",
                description="Connection with social support services recommended for authorized review.",
                reasoning="Social isolation indicators detected",
            ))

        # Fear-related indicators
        if any("fear" in n for n in indicator_names):
            recommendations.append(Recommendation(
                type=RecommendationType.COUNSELLING_REFERRAL,
                priority=RecommendationPriority.MEDIUM,
                title="Trauma-Informed Support",
                description="Trauma-informed support pathway recommended for authorized review.",
                reasoning="Fear-related communication indicators detected",
            ))

        # If low risk, suggest monitoring
        if risk_level == "LOW" and assessment_status == "COMPLETED":
            recommendations.append(Recommendation(
                type=RecommendationType.CONTINUE_MONITORING,
                priority=RecommendationPriority.LOW,
                title="Continue Standard Monitoring",
                description="Continue with standard monitoring protocols.",
                reasoning="Low risk indicators - standard protocols apply",
            ))

        # If moderate risk, suggest follow-up
        elif risk_level == "MODERATE" and assessment_status == "COMPLETED":
            recommendations.append(Recommendation(
                type=RecommendationType.FOLLOW_UP,
                priority=RecommendationPriority.MEDIUM,
                title="Scheduled Follow-up Recommended",
                description="Scheduled follow-up recommended for further assessment.",
                reasoning="Moderate risk indicators - follow-up recommended",
            ))

        # If no recommendations generated, add a default
        if not recommendations:
            recommendations.append(Recommendation(
                type=RecommendationType.GENERAL_SUPPORT,
                priority=RecommendationPriority.LOW,
                title="Standard Support Protocol",
                description="Apply standard support protocols. Authorized review at discretion.",
                reasoning="Default recommendation based on assessment outcome",
            ))

        logger.info(f"Generated {len(recommendations)} recommendations for risk={risk_level}, svi={svi_score}")
        return recommendations

    def get_service_info(self) -> Dict[str, Any]:
        return {
            "service_name": "Rule-Based Recommendation Engine",
            "version": "1.0.0-hybrid",
            "type": "rule-based",
            "description": "Transparent rule-based recommendation engine. All recommendations are AI-Assisted only.",
            "disclaimer": "AI-Assisted Recommendation - NOT a medical diagnosis. Final decisions require authorized human review.",
        }


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()
