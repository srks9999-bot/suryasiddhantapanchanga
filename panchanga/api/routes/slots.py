"""
Slot computation and time validation endpoints.
These endpoints support the Ritual Allocation System.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from panchanga.models.requests import ComputeSlotsRequest, ValidateTimeRequest
from panchanga.models.responses import (
    ComputeSlotsResponse, ComputedSlot, SlotPanchangaInfo,
    RahuKaalInfo, MuhurtaInfo, ValidateTimeResponse, TimeSuggestion, SettingsInfo
)
from panchanga.services.panchanga_service import PanchangaService
from api.dependencies import get_service

router = APIRouter()

# Tithi quality mappings
AUSPICIOUS_TITHIS = {
    'pratipada', 'dwitiya', 'tritiya', 'panchami', 'saptami',
    'dashami', 'ekadashi', 'dwadashi', 'trayodashi', 'purnima'
}

INAUSPICIOUS_TITHIS = {'amavasya', 'chaturthi', 'ashtami', 'chaturdashi', 'navami'}

AUSPICIOUS_NAKSHATRAS = {
    'ashwini', 'rohini', 'mrigashira', 'pushya', 'uttara phalguni',
    'hasta', 'chitra', 'swati', 'anuradha', 'uttara ashadha',
    'shravana', 'dhanishta', 'uttara bhadrapada', 'revati'
}

# Muhurta names (15 muhurtas in a day, starting from sunrise)
MUHURTA_INFO = [
    {'name': 'Rudra', 'quality': 'inauspicious'},
    {'name': 'Ahi', 'quality': 'inauspicious'},
    {'name': 'Mitra', 'quality': 'auspicious'},
    {'name': 'Pitru', 'quality': 'neutral'},
    {'name': 'Vasu', 'quality': 'auspicious'},
    {'name': 'Vara', 'quality': 'auspicious'},
    {'name': 'Vishwedeva', 'quality': 'auspicious'},
    {'name': 'Vidhi', 'quality': 'auspicious'},
    {'name': 'Satamukhi', 'quality': 'auspicious'},
    {'name': 'Puruhuta', 'quality': 'neutral'},
    {'name': 'Vahini', 'quality': 'inauspicious'},
    {'name': 'Naktancara', 'quality': 'inauspicious'},
    {'name': 'Varuna', 'quality': 'auspicious'},
    {'name': 'Aryaman', 'quality': 'auspicious'},
    {'name': 'Bhaga', 'quality': 'auspicious'},
]

# Rahu Kaal order by weekday (Monday=0)
RAHU_KAAL_ORDER = [1, 6, 4, 5, 3, 2, 0]  # Position in 8 parts of day


def get_tithi_quality(tithi_name: str) -> str:
    """Determine tithi quality."""
    name_lower = tithi_name.lower()
    for t in AUSPICIOUS_TITHIS:
        if t in name_lower:
            return 'auspicious'
    for t in INAUSPICIOUS_TITHIS:
        if t in name_lower:
            return 'inauspicious'
    return 'neutral'


def get_nakshatra_quality(nakshatra_name: str) -> str:
    """Determine nakshatra quality."""
    name_lower = nakshatra_name.lower()
    for n in AUSPICIOUS_NAKSHATRAS:
        if n in name_lower:
            return 'auspicious'
    return 'neutral'


def calculate_rahu_kaal(dt: datetime, sunrise: tuple, sunset: tuple) -> RahuKaalInfo:
    """Calculate Rahu Kaal for a given date."""
    sunrise_minutes = sunrise[0] * 60 + sunrise[1]
    sunset_minutes = sunset[0] * 60 + sunset[1]
    day_duration = sunset_minutes - sunrise_minutes
    segment_duration = day_duration // 8
    
    weekday = dt.weekday()
    rahu_position = RAHU_KAAL_ORDER[weekday]
    
    rahu_start_minutes = sunrise_minutes + (segment_duration * rahu_position)
    rahu_end_minutes = rahu_start_minutes + segment_duration
    
    return RahuKaalInfo(
        start=f"{rahu_start_minutes // 60:02d}:{rahu_start_minutes % 60:02d}",
        end=f"{rahu_end_minutes // 60:02d}:{rahu_end_minutes % 60:02d}",
        overlaps_slot=False  # Will be set by caller
    )


def get_muhurta_at_time(dt: datetime, sunrise: tuple, sunset: tuple) -> Optional[MuhurtaInfo]:
    """Get the muhurta for a given time."""
    sunrise_minutes = sunrise[0] * 60 + sunrise[1]
    sunset_minutes = sunset[0] * 60 + sunset[1]
    day_duration = sunset_minutes - sunrise_minutes
    muhurta_duration = day_duration / 15
    
    current_minutes = dt.hour * 60 + dt.minute
    time_from_sunrise = current_minutes - sunrise_minutes
    
    if time_from_sunrise < 0 or time_from_sunrise >= day_duration:
        return None  # Outside day muhurtas
    
    muhurta_index = int(time_from_sunrise / muhurta_duration)
    if 0 <= muhurta_index < 15:
        info = MUHURTA_INFO[muhurta_index]
        start_minutes = int(sunrise_minutes + muhurta_index * muhurta_duration)
        end_minutes = int(start_minutes + muhurta_duration)
        
        return MuhurtaInfo(
            name=info['name'],
            start_time=f"{start_minutes // 60:02d}:{start_minutes % 60:02d}",
            end_time=f"{end_minutes // 60:02d}:{end_minutes % 60:02d}",
            quality=info['quality']
        )
    return None


def calculate_score(
    panchanga_data: dict,
    muhurta: Optional[MuhurtaInfo],
    rahu_overlaps: bool,
    preferred_tithis: List[str],
    preferred_nakshatras: List[str],
    avoided_tithis: List[str]
) -> float:
    """Calculate auspiciousness score (0-1)."""
    score = 0.5  # Base score
    
    tithi_name = panchanga_data.get('tithi_name', '').lower()
    nakshatra_name = panchanga_data.get('nakshatra', '').lower()
    
    # Tithi scoring
    if any(t.lower() in tithi_name for t in preferred_tithis):
        score += 0.15
    if any(t.lower() in tithi_name for t in avoided_tithis):
        score -= 0.25
    if get_tithi_quality(tithi_name) == 'auspicious':
        score += 0.1
    elif get_tithi_quality(tithi_name) == 'inauspicious':
        score -= 0.1
    
    # Nakshatra scoring
    if any(n.lower() in nakshatra_name for n in preferred_nakshatras):
        score += 0.15
    if get_nakshatra_quality(nakshatra_name) == 'auspicious':
        score += 0.1
    
    # Muhurta scoring
    if muhurta:
        if muhurta.quality == 'auspicious':
            score += 0.1
        elif muhurta.quality == 'inauspicious':
            score -= 0.15
    
    # Rahu Kaal penalty
    if rahu_overlaps:
        score -= 0.2
    
    return max(0.0, min(1.0, score))


def time_ranges_overlap(
    start1: datetime, end1: datetime,
    start2_str: str, end2_str: str,
    base_date: datetime
) -> bool:
    """Check if two time ranges overlap."""
    start2_parts = [int(x) for x in start2_str.split(':')]
    end2_parts = [int(x) for x in end2_str.split(':')]
    
    start2 = base_date.replace(hour=start2_parts[0], minute=start2_parts[1])
    end2 = base_date.replace(hour=end2_parts[0], minute=end2_parts[1])
    
    return start1 < end2 and start2 < end1


@router.post(
    "/slots/compute",
    response_model=ComputeSlotsResponse,
    summary="Compute Valid Time Slots",
    description="""
Compute auspicious time slots within a preferred window.

Used by Temporal workflows for ritual allocation. Returns slots
ranked by Panchanga auspiciousness score.

Factors considered:
- Tithi quality and preferences
- Nakshatra quality and preferences
- Muhurta (auspicious moments)
- Rahu Kaal avoidance
"""
)
async def compute_slots(
    request: ComputeSlotsRequest,
    service: PanchangaService = Depends(get_service)
):
    """Compute valid time slots within the preferred window."""
    try:
        # Apply location settings
        if request.location:
            service.settings.loc_lat = request.location.latitude
            service.settings.loc_lon = request.location.longitude
        
        if request.settings:
            service.settings.tradition = request.settings.tradition
            service.settings.language = request.settings.language
        
        # Default preferences
        preferred_tithis = request.preferred_tithis or []
        preferred_nakshatras = request.preferred_nakshatras or []
        avoided_tithis = request.avoided_tithis or []
        
        slots: List[ComputedSlot] = []
        current = request.window_start
        duration = timedelta(minutes=request.duration_minutes)
        step = timedelta(minutes=30)  # Check every 30 minutes
        
        while current + duration <= request.window_end:
            slot_end = current + duration
            
            # Get Panchanga for this time
            panchanga = service.calculate(
                current.year, current.month, current.day
            )
            
            # Calculate Rahu Kaal
            rahu_kaal = calculate_rahu_kaal(
                current,
                panchanga['sunrise'],
                panchanga['sunset']
            )
            
            # Check Rahu Kaal overlap
            rahu_overlaps = time_ranges_overlap(
                current, slot_end,
                rahu_kaal.start, rahu_kaal.end,
                current
            )
            rahu_kaal.overlaps_slot = rahu_overlaps
            
            # Skip if Rahu Kaal overlaps and avoidance is requested
            if request.avoid_rahu_kaal and rahu_overlaps:
                current += step
                continue
            
            # Get muhurta
            muhurta = get_muhurta_at_time(
                current,
                panchanga['sunrise'],
                panchanga['sunset']
            )
            
            # Calculate score
            score = calculate_score(
                panchanga,
                muhurta,
                rahu_overlaps,
                preferred_tithis,
                preferred_nakshatras,
                avoided_tithis
            )
            
            # Only include slots above threshold
            if score >= 0.3:
                warnings = []
                if rahu_overlaps:
                    warnings.append("Overlaps with Rahu Kaal")
                
                tithi_quality = get_tithi_quality(panchanga.get('tithi_name', ''))
                nakshatra_quality = get_nakshatra_quality(panchanga.get('nakshatra', ''))
                
                slots.append(ComputedSlot(
                    start=current.isoformat(),
                    end=slot_end.isoformat(),
                    panchanga_score=round(score, 2),
                    panchanga=SlotPanchangaInfo(
                        tithi=panchanga.get('tithi_name', ''),
                        tithi_number=panchanga.get('tithi_day', 1),
                        paksha='shukla' if panchanga.get('paksa') == 'Suklapaksa' else 'krishna',
                        tithi_quality=tithi_quality,
                        nakshatra=panchanga.get('nakshatra', ''),
                        nakshatra_quality=nakshatra_quality,
                        yoga=panchanga.get('yoga', ''),
                        karana=panchanga.get('karana', '')
                    ),
                    muhurta=muhurta,
                    rahu_kaal=rahu_kaal,
                    warnings=warnings
                ))
            
            current += step
        
        # Sort by score descending
        slots.sort(key=lambda s: s.panchanga_score, reverse=True)
        
        return ComputeSlotsResponse(
            slots=slots[:15],  # Return top 15 slots
            computed_at=datetime.now(ZoneInfo('UTC')),
            settings=SettingsInfo(
                system=service.settings.selected_system,
                tradition=service.settings.tradition,
                latitude=service.settings.loc_lat,
                longitude=service.settings.loc_lon,
                language=service.settings.language
            )
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Computation error: {str(e)}")


@router.post(
    "/time/validate",
    response_model=ValidateTimeResponse,
    summary="Validate Time (Advisory)",
    description="""
Validate a specific date/time for auspiciousness.

Used by frontend for pre-submission guidance. Returns
Panchanga details, warnings, and alternative suggestions.

This is advisory only and does NOT affect allocation.
"""
)
async def validate_time(
    request: ValidateTimeRequest,
    service: PanchangaService = Depends(get_service)
):
    """Validate a specific time for auspiciousness."""
    try:
        # Apply settings
        if request.location:
            service.settings.loc_lat = request.location.latitude
            service.settings.loc_lon = request.location.longitude
        
        if request.settings:
            service.settings.tradition = request.settings.tradition
            service.settings.language = request.settings.language
        
        dt = request.date_time
        
        # Get full Panchanga
        panchanga_result = service.calculate(
            dt.year, dt.month, dt.day
        )
        
        # Convert to PanchangaResponse format
        from panchanga.models.responses import PanchangaResponse
        panchanga = PanchangaResponse(**panchanga_result)
        
        # Calculate Rahu Kaal
        rahu_kaal = calculate_rahu_kaal(
            dt,
            panchanga_result['sunrise'],
            panchanga_result['sunset']
        )
        
        # Check if time is in Rahu Kaal
        rahu_start_parts = [int(x) for x in rahu_kaal.start.split(':')]
        rahu_end_parts = [int(x) for x in rahu_kaal.end.split(':')]
        current_minutes = dt.hour * 60 + dt.minute
        rahu_start_minutes = rahu_start_parts[0] * 60 + rahu_start_parts[1]
        rahu_end_minutes = rahu_end_parts[0] * 60 + rahu_end_parts[1]
        in_rahu_kaal = rahu_start_minutes <= current_minutes < rahu_end_minutes
        
        # Get muhurta
        muhurta = get_muhurta_at_time(
            dt,
            panchanga_result['sunrise'],
            panchanga_result['sunset']
        )
        
        # Calculate score
        score = calculate_score(
            panchanga_result, muhurta, in_rahu_kaal,
            [], [], []  # No ritual-specific preferences for validation
        )
        
        # Determine quality
        if score >= 0.7:
            quality = 'excellent'
        elif score >= 0.5:
            quality = 'good'
        elif score >= 0.35:
            quality = 'neutral'
        else:
            quality = 'poor'
        
        # Generate warnings
        warnings = []
        if in_rahu_kaal:
            warnings.append(f"Selected time falls within Rahu Kaal ({rahu_kaal.start}-{rahu_kaal.end})")
        
        tithi_quality = get_tithi_quality(panchanga_result.get('tithi_name', ''))
        if tithi_quality == 'inauspicious':
            warnings.append(f"Tithi ({panchanga_result.get('tithi_name', '')}) is not favorable")
        
        if muhurta and muhurta.quality == 'inauspicious':
            warnings.append(f"Current muhurta ({muhurta.name}) is inauspicious")
        
        # Generate suggestions
        suggestions = []
        
        # Suggest Abhijit muhurta (middle of day)
        sunrise_minutes = panchanga_result['sunrise'][0] * 60 + panchanga_result['sunrise'][1]
        sunset_minutes = panchanga_result['sunset'][0] * 60 + panchanga_result['sunset'][1]
        abhijit_start_minutes = (sunrise_minutes + sunset_minutes) // 2 - 24
        abhijit_end_minutes = abhijit_start_minutes + 48
        
        if not (abhijit_start_minutes <= current_minutes < abhijit_end_minutes):
            abhijit_dt = dt.replace(
                hour=abhijit_start_minutes // 60,
                minute=abhijit_start_minutes % 60
            )
            suggestions.append(TimeSuggestion(
                date_time=abhijit_dt.isoformat(),
                reason="Abhijit muhurta - most auspicious time of day",
                score=0.9
            ))
        
        return ValidateTimeResponse(
            is_auspicious=score >= 0.5,
            quality=quality,
            score=round(score, 2),
            panchanga=panchanga,
            warnings=warnings,
            suggestions=suggestions
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
