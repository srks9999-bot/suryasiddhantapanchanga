"""
Panchanga calculation endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List

from panchanga.core.date_utils import DateUtils
from panchanga.models.requests import (
    CalculateRequest,
    MonthRequest,
    CalculateAtRequest,
    CalculateAtBatchRequest,
    CalculateRangeRequest,
)
from panchanga.models.responses import (
    PanchangaResponse,
    MonthResponse,
    ErrorResponse,
    PanchangaAtTimeResponse,
    PanchangaAtTimeBatchResponse,
)
from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService
from api.dependencies import get_service

router = APIRouter()


@router.post(
    "/calculate",
    response_model=PanchangaResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Calculate Panchanga",
    description="""
Calculate complete Panchanga for a specific date.

Returns all five elements of Panchanga:
- **Tithi**: Lunar day (1-15 in each paksha)
- **Nakshatra**: Lunar mansion
- **Yoga**: Angular relationship between Sun and Moon
- **Karana**: Half of a tithi
- **Vara**: Weekday

Also includes:
- Lunar month (Masa) with Adhimasa indication
- Solar month (Saura Masa)
- Era years (Saka, Vikrama, Kali)
- Sunrise and sunset times
- Timing information for each element
"""
)
async def calculate_panchanga(
    request: CalculateRequest,
    service: PanchangaService = Depends(get_service)
):
    """
    Calculate Panchanga for a specific date.
    """
    try:
        # Apply request settings if provided
        if request.location:
            service.settings.loc_lat = request.location.latitude
            service.settings.loc_lon = request.location.longitude
        
        if request.settings:
            service.settings.tradition = request.settings.tradition
            service.settings.selected_system = request.settings.system
            service.settings.language = request.settings.language
        
        result = service.calculate(
            request.year,
            request.month,
            request.day
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post(
    "/month",
    response_model=MonthResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Get Monthly Panchanga",
    description="""
Get Panchanga for an entire month.

Returns a list of daily Panchanga summaries including:
- Date and weekday
- Masa (lunar month)
- Paksha and Tithi
- Nakshatra
- Yoga
- Karana
"""
)
async def calculate_month(
    request: MonthRequest,
    service: PanchangaService = Depends(get_service)
):
    """
    Calculate Panchanga for an entire month.
    """
    try:
        # Apply request settings if provided
        if request.location:
            service.settings.loc_lat = request.location.latitude
            service.settings.loc_lon = request.location.longitude
        
        if request.settings:
            service.settings.tradition = request.settings.tradition
            service.settings.selected_system = request.settings.system
            service.settings.language = request.settings.language
        
        result = service.calculate_month(request.year, request.month)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post(
    "/calculate_range",
    response_model=List[PanchangaResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Calculate Panchanga for a consecutive range of days",
    description="Calculate Panchanga for `n` consecutive days starting from the provided date."
)
async def calculate_panchanga_range(request: CalculateRangeRequest):
    try:
        service = _build_service_from_request(request.location, request.settings)

        year, month, day = request.year, request.month, request.day
        results = []
        for _ in range(request.days):
            results.append(service.calculate(year, month, day))
            year, month, day = DateUtils.next_date(year, month, day)

        return results

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get(
    "/today",
    response_model=PanchangaResponse,
    summary="Get Today's Panchanga",
    description="Get Panchanga for the current date using default settings."
)
async def today_panchanga(
    language: Optional[str] = "telugu",
    tradition: Optional[str] = "surya",
    service: PanchangaService = Depends(get_service)
):
    """
    Get Panchanga for today's date.
    """
    from datetime import date
    
    try:
        today = date.today()
        service.settings.language = language
        service.settings.tradition = tradition
        
        result = service.calculate(
            today.year,
            today.month,
            today.day
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


def _build_service_from_request(location, settings) -> PanchangaService:
    """Build an isolated service instance from request payload (avoids cross-request mutation)."""
    svc_settings = PanchangaSettings()
    
    if location:
        svc_settings.loc_lat = location.latitude
        svc_settings.loc_lon = location.longitude
    
    if settings:
        svc_settings.tradition = settings.tradition
        svc_settings.selected_system = settings.system
        svc_settings.language = settings.language
        # Optional fields (supported by PanchangaSettings)
        if getattr(settings, "ayanamsa", None):
            svc_settings.ayanamsa = settings.ayanamsa
        if getattr(settings, "use_drik_sunrise_sunset", None) is not None:
            svc_settings.use_drik_sunrise_sunset = settings.use_drik_sunrise_sunset
        if getattr(settings, "use_sunrise_for_tithi", None) is not None:
            svc_settings.use_sunrise_for_tithi = settings.use_sunrise_for_tithi
    
    return PanchangaService(settings=svc_settings)


@router.post(
    "/calculate_at",
    response_model=PanchangaAtTimeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Calculate Panchanga + planetary positions at a specific datetime",
    description="""
Calculate Panchanga and planetary positions at an **exact datetime**.

This endpoint is designed to support the web UI comparison cards and mirrors the combined
output style used by `console_debug.py` (astronomical + civil day + `planets_detailed`).
"""
)
async def calculate_panchanga_at_time(request: CalculateAtRequest):
    try:
        service = _build_service_from_request(request.location, request.settings)
        calculator = service.calculator
        
        # Use get_date_components() to support BCE dates
        year, month, day, hour, minute = request.get_date_components()
        
        astronomical = calculator.calculate_astronomical(year, month, day, hour=hour, minute=minute)
        civil_day = calculator.calculate_civil_day(year, month, day, hour=hour, minute=minute,
                                                       include_timing=True,
                                                       tslong=astronomical['sun_longitude'],
                                                       tllong=astronomical['moon_longitude'],
                                                       ahar_at_time=astronomical['ahar_at_time'],
                                                       sunrise_hour=astronomical["sunrise"][0],
                                                       sunrise_minute=astronomical["sunrise"][1],
                                                       sunset_hour=astronomical["sunset"][0],
                                                       sunset_minute=astronomical["sunset"][1]
                                                       )
        # Merge for console-debug compatibility: civil fields override for panchanga elements
        result = {
            **astronomical,
            **civil_day,
            'calculation_point_astronomical': astronomical.get('calculation_point', 'midnight'),
            'calculation_point_civil': civil_day.get('calculation_point', 'sunrise'),
        }
        
        if request.client_id:
            result['client_id'] = request.client_id
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post(
    "/calculate_at/batch",
    response_model=PanchangaAtTimeBatchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Batch calculate Panchanga + planetary positions for multiple datetimes",
    description="Compute multiple `calculate_at` results in one request (order preserved)."
)
async def calculate_panchanga_at_time_batch(request: CalculateAtBatchRequest):
    try:
        results = []
        for entry in request.entries:
            service = _build_service_from_request(entry.location, entry.settings)
            calculator = service.calculator
            
            # Use get_date_components() to support BCE dates
            year, month, day, hour, minute = entry.get_date_components()
            
            astronomical = calculator.calculate_astronomical(year, month, day, hour=hour, minute=minute)
            civil_day = calculator.calculate_civil_day(year, month, day, hour=hour, minute=minute,
                                                       include_timing=True,
                                                       tslong=astronomical['sun_longitude'],
                                                       tllong=astronomical['moon_longitude'],
                                                       ahar_at_time=astronomical['ahar_at_time'],
                                                       sunrise_hour=astronomical["sunrise"][0],
                                                       sunrise_minute=astronomical["sunrise"][1],
                                                       sunset_hour=astronomical["sunset"][0],
                                                       sunset_minute=astronomical["sunset"][1]
                                                       )
            
            result = {
                **astronomical,
                **civil_day,
                'calculation_point_astronomical': astronomical.get('calculation_point', 'midnight'),
                'calculation_point_civil': civil_day.get('calculation_point', 'sunrise'),
            }
            
            if entry.client_id:
                result['client_id'] = entry.client_id
            
            results.append(result)
        
        return results
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
