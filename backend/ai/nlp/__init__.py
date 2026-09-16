"""
NLP Service Registry
Factory for getting the configured NLP service
"""
from typing import Optional

from ai.nlp.nlp_service import NLPService
from ai.nlp.demo_nlp_service import DemoNLPService


_nlp_service: Optional[NLPService] = None


def get_nlp_service() -> NLPService:
    """Get the configured NLP service instance"""
    global _nlp_service
    if _nlp_service is None:
        from app.config import settings
        if settings.ai_provider == "gemini" and not settings.demo_mode:
            try:
                from ai.nlp.real_nlp_service import RealNLPService
                _nlp_service = RealNLPService(api_key=settings.ai_api_key)
            except ImportError:
                _nlp_service = DemoNLPService()
        elif settings.ai_provider == "local" and not settings.demo_mode:
            try:
                from ai.nlp.real_nlp_service import RealNLPService
                _nlp_service = RealNLPService()
            except ImportError:
                _nlp_service = DemoNLPService()
        else:
            _nlp_service = DemoNLPService()
    return _nlp_service


def set_nlp_service(service: NLPService) -> None:
    """Set the NLP service (for testing or configuration)"""
    global _nlp_service
    _nlp_service = service