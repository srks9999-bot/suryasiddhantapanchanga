"""
Birthday and Ugadi search endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends

from panchanga.models.requests import BirthdayRequest, UgadiRequest
from panchanga.models.responses import BirthdayResponse, UgadiResponse, ErrorResponse
from panchanga.services.panchanga_service import PanchangaService
from api.dependencies import get_service

router = APIRouter()


@router.post(
    "/next",
    response_model=BirthdayResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Find Future Birthdays",
    description="""
Find future birthday dates based on tithi, masa, and paksha.

In the Hindu calendar, birthdays are traditionally celebrated on the same
**tithi** (lunar day) in the same **masa** (lunar month) and **paksha** (fortnight)
as the birth date.

This endpoint finds when these conditions will occur in future years.

### Parameters

If `masa_num`, `paksha`, or `tithi_day` are not provided, the values from
the reference date will be used.

### Special Cases

- **Ksaya Tithi**: When a tithi is skipped (doesn't span any sunrise)
- **Ksaya Masa**: When a lunar month is skipped (rare)
- **Adhika Masa**: Intercalary (leap) months
"""
)
async def find_birthdays(
    request: BirthdayRequest,
    service: PanchangaService = Depends(get_service)
):
    """
    Find future birthdays based on tithi, masa, and paksha.
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
        
        result = service.find_birthdays(
            request.year,
            request.month,
            request.day,
            masa_num=request.masa_num,
            paksha=request.paksha,
            tithi_day=request.tithi_day,
            number_of_years=request.number_of_years
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post(
    "/ugadi",
    response_model=UgadiResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Calculation error"}
    },
    summary="Find Ugadi Dates",
    description="""
Find upcoming Ugadi (Telugu/Kannada New Year) dates.

**Ugadi** marks the beginning of the Hindu lunar calendar year and falls on
**Chaitra Shukla Pratipada** - the first day of the bright fortnight of the
Chaitra month.

### Regional Names

- **Ugadi**: Telugu, Kannada
- **Gudi Padwa**: Marathi
- **Cheti Chand**: Sindhi
"""
)
async def find_ugadi(
    request: UgadiRequest,
    service: PanchangaService = Depends(get_service)
):
    """
    Find upcoming Ugadi dates.
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
        
        result = service.find_ugadi_dates(
            request.year,
            request.month,
            request.day,
            number_of_years=request.number_of_years
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
