"""
AI Recommendation Module for SIH26093

Provides recommendation services for risk assessment follow-up actions.
"""

from ai.recommendation.recommendation_service import (
    RecommendationService,
    RuleBasedRecommendationService,
    Recommendation,
    Indicator,
    RiskLevel,
    RecommendationType,
    RecommendationPriority,
    get_recommendation_service
)

__all__ = [
    "RecommendationService",
    "RuleBasedRecommendationService",
    "Recommendation",
    "Indicator",
    "RiskLevel",
    "RecommendationType",
    "RecommendationPriority",
    "get_recommendation_service"
]