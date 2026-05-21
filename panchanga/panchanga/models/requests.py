"""
Pydantic request models for the Panchanga API.

This module defines the request schemas used by the FastAPI endpoints,
with full validation and OpenAPI documentation support.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime


class LocationSettings(BaseModel):
    """Location settings for calculations."""
    latitude: float = Field(
        default=23.2,
        ge=-90,
        le=90,
        description="Latitude in degrees (-90 to 90)"
    )
    longitude: float = Field(
        default=82.5,
        ge=-180,
        le=180,
        description="Longitude in degrees (-180 to 180)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 17.4,
                "longitude": 78.5
            }
        }


class CalculationSettings(BaseModel):
    """Settings for Panchanga calculations."""
    tradition: Literal["surya", "drik", "lunar"] = Field(
        default="surya",
        description="Calculation tradition to use"
    )
    system: Literal["SuryaSiddhanta", "InPancasiddhantika"] = Field(
        default="SuryaSiddhanta",
        description="Astronomical system for constants"
    )
    language: Literal["telugu", "english"] = Field(
        default="telugu",
        description="Language for output names"
    )
    ayanamsa: Literal["lahiri", "raman", "krishnamurti", "none"] = Field(
        default="lahiri",
        description="Ayanamsa system for sidereal calculations"
    )
    use_drik_sunrise_sunset: bool = Field(
        default=True,
        description="Use Drik ephemeris to compute sunrise/sunset timings (more accurate than classic formulas)"
    )
    use_sunrise_for_tithi: bool = Field(
        default=False,
        description="Calculate tithi at sunrise instead of midnight (not recommended for epoch consistency)"
    )


class CalculateRequest(BaseModel):
    """
    Request model for calculating Panchanga for a specific date.
    
    Provides complete Panchanga details including tithi, nakshatra,
    yoga, karana, masa, and timing information.
    """
    year: int = Field(
        ...,
        ge=1,
        le=3000,
        description="Year (1-3000)"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Month (1-12)"
    )
    day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Day of month (1-31)"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings (defaults to Ujjain)"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    include_next_year_birthday: bool = Field(
        default=False,
        description="Include next year's birthday calculation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 1,
                "day": 15,
                "location": {
                    "latitude": 17.4,
                    "longitude": 78.5
                },
                "settings": {
                    "tradition": "surya",
                    "language": "telugu"
                }
            }
        }


class CalculateAtRequest(BaseModel):
    """
    Request model for calculating Panchanga + planetary positions at an exact datetime.
    
    Supports BCE dates by accepting year/month/day/hour/minute as separate fields.
    For BCE dates, use negative years (e.g., -3101 for 3102 BCE).
    """
    # Accept either datetime string OR separate fields for BCE support
    date_time: Optional[datetime] = Field(
        default=None,
        description="Date/time to calculate at (ISO format). Use for CE dates only."
    )
    # Separate fields for BCE support
    year: Optional[int] = Field(
        default=None,
        description="Year (negative for BCE, e.g., -3101 for 3102 BCE)"
    )
    month: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="Month (1-12)"
    )
    day: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="Day of month (1-31)"
    )
    hour: Optional[int] = Field(
        default=0,
        ge=0,
        le=23,
        description="Hour (0-23)"
    )
    minute: Optional[int] = Field(
        default=0,
        ge=0,
        le=59,
        description="Minute (0-59)"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings (defaults to framework defaults if omitted)"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    client_id: Optional[str] = Field(
        default=None,
        description="Optional client-provided identifier to correlate results in batch comparisons"
    )
    
    @field_validator('year', 'month', 'day', mode='before')
    @classmethod
    def validate_date_fields(cls, v, info):
        return v
    
    def get_date_components(self) -> tuple[int, int, int, int, int]:
        """Extract year, month, day, hour, minute from either date_time or separate fields."""
        if self.date_time is not None:
            year = self.date_time.year
            month = self.date_time.month
            day = self.date_time.day
            hour = self.date_time.hour
            minute = self.date_time.minute
        elif self.year is not None and self.month is not None and self.day is not None:
            year = self.year
            month = self.month
            day = self.day
            hour = self.hour or 0
            minute = self.minute or 0
        else:
            raise ValueError("Either 'date_time' or 'year/month/day' fields must be provided")
        
        # Validate year range to prevent calculation overflow/underflow
        # Reasonable limits: -100,000 to +100,000 years (covers all practical use cases)
        if year < -180000 or year > 100000:
            raise ValueError(
                f"Year {year} is outside the supported range (-100,000 to 100,000). "
                "Dates beyond this range may cause calculation errors due to numerical precision limits."
            )
        
        return (year, month, day, hour, minute)
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "date_time": "2026-01-16T09:30:00",
                    "location": {"latitude": 23.2, "longitude": 75.8},
                    "settings": {"tradition": "surya", "system": "SuryaSiddhanta", "language": "telugu"},
                    "client_id": "entry-1"
                },
                {
                    "year": -3101,
                    "month": 2,
                    "day": 18,
                    "hour": 0,
                    "minute": 0,
                    "location": {"latitude": 23.2, "longitude": 75.8},
                    "client_id": "kali-epoch"
                }
            ]
        }


class CalculateAtBatchRequest(BaseModel):
    """Batch request for calculating multiple date_time entries for comparison."""
    entries: List[CalculateAtRequest] = Field(
        ...,
        min_length=1,
        description="Entries to calculate (order preserved in response)"
    )


class MonthRequest(BaseModel):
    """
    Request model for calculating Panchanga for an entire month.
    """
    year: int = Field(
        ...,
        ge=1,
        le=3000,
        description="Year (1-3000)"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Month (1-12)"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 3,
                "location": {
                    "latitude": 17.4,
                    "longitude": 78.5
                }
            }
        }


class CalculateRangeRequest(BaseModel):
    """Request model for calculating Panchanga for a consecutive range of days."""

    year: int = Field(
        ...,
        ge=1,
        le=3000,
        description="Starting year (1-3000)"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Starting month (1-12)"
    )
    day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Starting day of month (1-31)"
    )
    days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of consecutive days to calculate (max 365)"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2026,
                "month": 3,
                "day": 15,
                "days": 30,
                "location": {
                    "latitude": 17.4,
                    "longitude": 78.5
                },
                "settings": {
                    "tradition": "surya",
                    "language": "telugu"
                }
            }
        }


class BirthdayRequest(BaseModel):
    """
    Request model for finding future birthdays based on tithi, masa, and paksha.
    
    Calculates when the same tithi/masa/paksha combination will occur
    in future years based on the Hindu lunar calendar.
    """
    year: int = Field(
        ...,
        ge=1,
        le=3000,
        description="Reference year"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Reference month"
    )
    day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Reference day"
    )
    masa_num: Optional[int] = Field(
        default=None,
        ge=0,
        le=11,
        description="Lunar month number (0-11, 0=Chaitra). If not provided, uses the date's masa."
    )
    paksha: Optional[Literal["Suklapaksa", "Krsnapaksa"]] = Field(
        default=None,
        description="Paksha (fortnight). If not provided, uses the date's paksha."
    )
    tithi_day: Optional[int] = Field(
        default=None,
        ge=1,
        le=15,
        description="Tithi day (1-15). If not provided, uses the date's tithi."
    )
    number_of_years: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of future years to search"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 1983,
                "month": 9,
                "day": 8,
                "number_of_years": 5
            }
        }


class UgadiRequest(BaseModel):
    """
    Request model for finding Ugadi (Telugu New Year) dates.
    
    Ugadi is celebrated on Chaitra Shukla Pratipada, the first day
    of the Hindu lunar calendar year.
    """
    year: int = Field(
        ...,
        ge=1,
        le=3000,
        description="Starting year"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Starting month"
    )
    day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Starting day"
    )
    number_of_years: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of Ugadi dates to find"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 1,
                "day": 1,
                "number_of_years": 5
            }
        }


class RuleEvaluateRequest(BaseModel):
    """
    Request model for evaluating tithi rules for debugging.
    
    Returns detailed information about which rules were applied
    and how the tithi was determined.
    """
    year: int = Field(
        ...,
        ge=1,
        le=3000,
        description="Year"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Month"
    )
    day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Day"
    )
    tradition: Literal["surya", "drik", "lunar"] = Field(
        default="surya",
        description="Tradition to use for rule evaluation"
    )
    rules: Optional[list[str]] = Field(
        default=None,
        description="Specific rules to evaluate (if None, uses tradition defaults)"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 3,
                "day": 25,
                "tradition": "surya"
            }
        }


class ComputeSlotsRequest(BaseModel):
    """
    Request model for computing auspicious time slots.
    Used by Temporal workflow for ritual allocation.
    """
    ritual_id: str = Field(
        ...,
        description="Ritual identifier for preference lookup"
    )
    window_start: datetime = Field(
        ...,
        description="Start of preferred time window (ISO format)"
    )
    window_end: datetime = Field(
        ...,
        description="End of preferred time window (ISO format)"
    )
    duration_minutes: int = Field(
        default=120,
        ge=30,
        le=480,
        description="Duration of ritual in minutes"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location for calculations"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    # Ritual-specific preferences (optional overrides)
    preferred_tithis: Optional[List[str]] = Field(
        default=None,
        description="Preferred tithi names"
    )
    preferred_nakshatras: Optional[List[str]] = Field(
        default=None,
        description="Preferred nakshatra names"
    )
    avoided_tithis: Optional[List[str]] = Field(
        default=None,
        description="Tithis to avoid"
    )
    avoid_rahu_kaal: bool = Field(
        default=True,
        description="Whether to avoid Rahu Kaal"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "ritual_id": "satyanarayan-puja",
                "window_start": "2025-02-15T06:00:00+05:30",
                "window_end": "2025-02-15T18:00:00+05:30",
                "duration_minutes": 120,
                "location": {
                    "latitude": 28.6139,
                    "longitude": 77.2090
                },
                "preferred_tithis": ["purnima", "ekadashi"],
                "avoided_tithis": ["amavasya"]
            }
        }


class ValidateTimeRequest(BaseModel):
    """
    Request model for validating a specific time.
    Used by frontend for advisory guidance.
    """
    ritual_id: Optional[str] = Field(
        default=None,
        description="Ritual identifier for context"
    )
    date_time: datetime = Field(
        ...,
        description="Date/time to validate (ISO format)"
    )
    location: Optional[LocationSettings] = Field(
        default=None,
        description="Location for calculations"
    )
    settings: Optional[CalculationSettings] = Field(
        default=None,
        description="Calculation settings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "ritual_id": "satyanarayan-puja",
                "date_time": "2025-02-15T09:00:00+05:30",
                "location": {
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
            }
        }
