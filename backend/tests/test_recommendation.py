"""Tests for the recommendation service."""

import pytest
from ai.recommendation import (
    RuleBasedRecommendationService,
    RiskLevel,
    RecommendationPriority,
    Indicator,
)


def test_critical_risk_generates_immediate_review():
    """A critical risk assessment should produce at least one URGENT recommendation."""
    service = RuleBasedRecommendationService()
    indicators = [
        Indicator(name="threat", severity="severe", confidence=0.9, source="text"),
        Indicator(name="fear", severity="high", confidence=0.85, source="text"),
        Indicator(name="distress", severity="severe", confidence=0.9, source="text"),
    ]
    recommendations = service.generate_recommendations(
        risk_level=RiskLevel.CRITICAL,
        svi_score=90,
        confidence=0.95,
        indicators=indicators,
        assessment_status="COMPLETE",
        language="en",
        context={},
    )
    assert len(recommendations) > 0
    assert any(r.priority == RecommendationPriority.URGENT for r in recommendations)


def test_low_risk_recommends_standard_followup():
    """A low risk case should produce LOW priority recommendations."""
    service = RuleBasedRecommendationService()
    recommendations = service.generate_recommendations(
        risk_level=RiskLevel.LOW,
        svi_score=20,
        confidence=0.95,
        indicators=[],
        assessment_status="COMPLETE",
        language="en",
        context={},
    )
    assert len(recommendations) > 0
    assert all(
        r.priority == RecommendationPriority.LOW for r in recommendations
    )


def test_recommendation_service_factory_returns_instance():
    """The factory function should return a service instance."""
    from ai.recommendation import get_recommendation_service
    service = get_recommendation_service()
    assert service is not None
