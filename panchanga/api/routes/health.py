"""
Health check endpoints.
"""

from fastapi import APIRouter
from panchanga.models.responses import HealthResponse
from panchanga.rules.traditions import DEFAULT_TRADITION

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the service is running and healthy."
)
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status, version, and default tradition.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        tradition=DEFAULT_TRADITION
    )
