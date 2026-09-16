"""
Fusion Service Registry
Factory for getting the configured fusion service
"""
from typing import Optional

from ai.fusion.fusion_service import FusionService
from ai.fusion.demo_fusion_service import DemoFusionService


_fusion_service: Optional[FusionService] = None


def get_fusion_service() -> FusionService:
    """Get the configured fusion service instance"""
    global _fusion_service
    if _fusion_service is None:
        from app.config import settings
        if settings.ai_provider == "local" and not settings.demo_mode:
            # Try to load real model
            try:
                from ai.fusion.real_fusion_service import RealFusionService
                _fusion_service = RealFusionService()
            except ImportError:
                _fusion_service = DemoFusionService()
        else:
            _fusion_service = DemoFusionService()
    return _fusion_service


def set_fusion_service(service: FusionService) -> None:
    """Set the fusion service (for testing or configuration)"""
    global _fusion_service
    _fusion_service = service