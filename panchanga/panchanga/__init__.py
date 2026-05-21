"""
Panchanga Service - Hindu Calendar Calculator

A comprehensive Panchanga calculator based on Surya Siddhanta and other traditions.
"""

__version__ = "1.0.0"

from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService

__all__ = ["PanchangaSettings", "PanchangaService", "__version__"]
