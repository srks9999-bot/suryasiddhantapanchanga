"""
FastAPI dependency injection for Panchanga Service.

This module provides dependency functions for injecting the PanchangaService
into route handlers, allowing for easy testing and configuration.
"""

from typing import Optional
from functools import lru_cache

from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService


# Global service instance (can be replaced for testing)
_service_instance: Optional[PanchangaService] = None


def get_service() -> PanchangaService:
    """
    Get the PanchangaService instance.
    
    This is a dependency that can be injected into FastAPI route handlers.
    It returns a singleton service instance by default.
    
    Returns:
        PanchangaService instance
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = PanchangaService()
    
    return _service_instance


def set_service(service: PanchangaService) -> None:
    """
    Set the PanchangaService instance.
    
    Useful for testing or when you need to configure the service
    with custom settings.
    
    Args:
        service: PanchangaService instance to use
    """
    global _service_instance
    _service_instance = service


def reset_service() -> None:
    """
    Reset the service instance to None.
    
    The next call to get_service() will create a new instance.
    """
    global _service_instance
    _service_instance = None


@lru_cache()
def get_settings() -> PanchangaSettings:
    """
    Get cached PanchangaSettings instance.
    
    Returns:
        PanchangaSettings with default values
    """
    return PanchangaSettings()


def create_service_with_settings(
    tradition: str = "surya",
    language: str = "telugu",
    latitude: float = 23.2,
    longitude: float = 82.5
) -> PanchangaService:
    """
    Create a new PanchangaService with custom settings.
    
    Args:
        tradition: Calculation tradition
        language: Output language
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Configured PanchangaService instance
    """
    settings = PanchangaSettings(
        tradition=tradition,
        language=language,
        loc_lat=latitude,
        loc_lon=longitude
    )
    return PanchangaService(settings=settings)
