"""
API route modules.
"""

from .health import router as health_router
from .panchanga import router as panchanga_router
from .birthdays import router as birthdays_router
from .rules import router as rules_router
from .debug import router as debug_router

__all__ = ["health_router", "panchanga_router", "birthdays_router", "rules_router", "debug_router"]
