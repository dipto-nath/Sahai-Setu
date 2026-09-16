"""
SVI Service Registry
"""
from typing import Optional

from ai.svi.svi_service import SVIService, DemoSVIService


_svi_service: Optional[SVIService] = None


def get_svi_service() -> SVIService:
    global _svi_service
    if _svi_service is None:
        from app.config import settings
        if settings.ai_provider == "local" and not settings.demo_mode:
            try:
                from ai.svi.real_svi_service import RealSVIService
                _svi_service = RealSVIService()
            except ImportError:
                _svi_service = DemoSVIService()
        else:
            _svi_service = DemoSVIService()
    return _svi_service


def set_svi_service(service: SVIService) -> None:
    global _svi_service
    _svi_service = service