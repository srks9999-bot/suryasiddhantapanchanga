"""
Pydantic response models for the Panchanga API.

This module defines the response schemas used by the FastAPI endpoints,
with full typing and OpenAPI documentation support.
"""

from typing import Optional, List, Tuple, Dict, Any
from pydantic import BaseModel, Field, RootModel
from datetime import date, datetime


class TimeInfo(BaseModel):
    """Time information as hours and minutes."""
    hours: int = Field(..., description="Hours (0-23)")
    minutes: int = Field(..., description="Minutes (0-59)")


class DateTimeInfo(BaseModel):
    """Full date and time information."""
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    day: int = Field(..., description="Day of month")
    hours: int = Field(..., description="Hours (0-23)")
    minutes: int = Field(..., description="Minutes (0-59)")


class SamkrantiInfo(BaseModel):
    """Solar ingress (Samkranti) information."""
    year: Optional[int] = Field(None, description="Year of samkranti")
    month: Optional[int] = Field(None, description="Month of samkranti")
    day: Optional[int] = Field(None, description="Day of samkranti")
    hour: Optional[int] = Field(None, description="Hour of samkranti")
    minute: Optional[int] = Field(None, description="Minute of samkranti")


class TithiDecision(BaseModel):
    """
    Result of tithi rule evaluation.
    
    Contains the determined tithi along with metadata about
    which rule made the decision and confidence level.
    """
    tithi: int = Field(..., description="Tithi day (1-15)")
    paksha: str = Field(..., description="Paksha (Suklapaksa or Krsnapaksa)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    rule_name: str = Field(..., description="Name of rule that made the decision")
    tradition: str = Field(..., description="Tradition used for calculation")
    is_ksaya: bool = Field(default=False, description="Whether this is a ksaya (skipped) tithi")
    is_vriddhi: bool = Field(default=False, description="Whether this is a vriddhi (extended) tithi")
    notes: Optional[List[str]] = Field(default=None, description="Additional notes about the decision")


class SettingsInfo(BaseModel):
    """Settings used for the calculation."""
    system: str = Field(..., description="Astronomical system used")
    tradition: str = Field(..., description="Calculation tradition")
    latitude: float = Field(..., description="Location latitude")
    longitude: float = Field(..., description="Location longitude")
    language: str = Field(..., description="Output language")


class BirthdayInfo(BaseModel):
    """Information about a future birthday occurrence."""
    year: Optional[int] = Field(None, description="Year of occurrence")
    month: Optional[int] = Field(None, description="Month of occurrence")
    day: Optional[int] = Field(None, description="Day of occurrence")
    days_ahead: Optional[int] = Field(None, description="Days from reference date")
    year_number: Optional[int] = Field(None, description="Which year in sequence")
    is_ksaya_tithi: bool = Field(default=False, description="Whether tithi was skipped")
    is_ksaya_masa: bool = Field(default=False, description="Whether masa was skipped")
    note: Optional[str] = Field(None, description="Additional notes")


class UgadiInfo(BaseModel):
    """Information about an Ugadi date."""
    year: int = Field(..., description="Year of Ugadi")
    month: int = Field(..., description="Month of Ugadi")
    day: int = Field(..., description="Day of Ugadi")
    days_ahead: int = Field(..., description="Days from reference date")
    tithi: int = Field(default=1, description="Tithi (always 1 for Ugadi)")
    tithi_name: str = Field(default="Pratipada", description="Tithi name")
    pratipada_starts_at: Optional[str] = Field(None, description="Time when Pratipada starts")
    exists_at_sunrise: bool = Field(default=True, description="Whether Pratipada exists at sunrise")


class PanchangaResponse(BaseModel):
    """
    Complete Panchanga response for a single date.
    
    Contains all five elements of Panchanga (Tithi, Nakshatra, Yoga, Karana, Vara)
    along with additional calendar information.
    """
    # Gregorian date
    gregorian_date: Tuple[int, int, int] = Field(..., description="(year, month, day)")
    weekday: str = Field(..., description="Weekday name")
    
    # Julian Day and Ahargana
    julian_day: int = Field(..., description="Julian Day number at noon")
    ahargana: int = Field(..., description="Kali Ahargana")
    
    # Ayanamsa
    ayanamsa: Tuple[int, int] = Field(..., description="(degrees, minutes)")
    
    # Sunrise/Sunset
    sunrise: Tuple[int, int] = Field(..., description="(hours, minutes)")
    sunset: Tuple[int, int] = Field(..., description="(hours, minutes)")
    
    # Era years
    year_saka: int = Field(..., description="Saka era year")
    year_vikrama: int = Field(..., description="Vikrama era year")
    year_kali: int = Field(..., description="Kali era year")
    
    # Jovian years
    jovian_year_north: str = Field(..., description="Jovian year (North Indian)")
    jovian_year_south: str = Field(..., description="Jovian year (South Indian)")
    
    # Lunar month (Masa)
    masa_num: int = Field(..., description="Lunar month number (0-11)")
    masa: str = Field(..., description="Lunar month name")
    adhimasa: str = Field(..., description="Adhimasa prefix if intercalary month")
    
    # Paksha and Tithi
    paksa: str = Field(..., description="Paksha key (Suklapaksa/Krsnapaksa)")
    paksha_name: str = Field(..., description="Paksha name in selected language")
    sukla_krsna: str = Field(..., description="Paksha identifier")
    tithi_day: int = Field(..., description="Tithi day (1-15)")
    tithi_name: str = Field(..., description="Tithi name in selected language")
    tithi_fraction: float = Field(..., description="Remaining fraction of tithi")
    
    # Solar month (Saura Masa)
    saura_masa_num: int = Field(..., description="Solar month number (0-11)")
    saura_masa: str = Field(..., description="Solar month name")
    saura_masa_day: int = Field(..., description="Day in solar month")
    samkranti: Optional[SamkrantiInfo] = Field(None, description="Samkranti info if applicable")
    
    # Nakshatra, Karana, Yoga
    nakshatra: str = Field(..., description="Nakshatra name")
    karana: str = Field(..., description="Karana name")
    yoga: str = Field(..., description="Yoga name")
    
    # Timing information
    tithi_start_time: Tuple[int, int] = Field(..., description="Tithi start (hours, minutes)")
    tithi_end_time: Tuple[int, int] = Field(..., description="Tithi end (hours, minutes)")
    tithi_start_datetime: Optional[DateTimeInfo] = Field(None, description="Tithi start datetime")
    tithi_end_datetime: Optional[DateTimeInfo] = Field(None, description="Tithi end datetime")
    
    nakshatra_start_time: Tuple[int, int] = Field(..., description="Nakshatra start (hours, minutes)")
    nakshatra_end_time: Tuple[int, int] = Field(..., description="Nakshatra end (hours, minutes)")
    nakshatra_start_datetime: Optional[DateTimeInfo] = Field(None, description="Nakshatra start datetime")
    nakshatra_end_datetime: Optional[DateTimeInfo] = Field(None, description="Nakshatra end datetime")
    
    yoga_start_time: Tuple[int, int] = Field(..., description="Yoga start (hours, minutes)")
    yoga_end_time: Tuple[int, int] = Field(..., description="Yoga end (hours, minutes)")
    yoga_start_datetime: Optional[DateTimeInfo] = Field(None, description="Yoga start datetime")
    yoga_end_datetime: Optional[DateTimeInfo] = Field(None, description="Yoga end datetime")
    
    karana_start_time: Tuple[int, int] = Field(..., description="Karana start (hours, minutes)")
    karana_end_time: Tuple[int, int] = Field(..., description="Karana end (hours, minutes)")
    karana_start_datetime: Optional[DateTimeInfo] = Field(None, description="Karana start datetime")
    karana_end_datetime: Optional[DateTimeInfo] = Field(None, description="Karana end datetime")
    
    masa_start_time: Tuple[int, int] = Field(..., description="Masa start (hours, minutes)")
    masa_end_time: Tuple[int, int] = Field(..., description="Masa end (hours, minutes)")
    masa_start_datetime: Optional[DateTimeInfo] = Field(None, description="Masa start datetime")
    masa_end_datetime: Optional[DateTimeInfo] = Field(None, description="Masa end datetime")
    
    # Planetary positions
    sun_longitude: float = Field(..., description="True solar longitude (degrees)")
    moon_longitude: float = Field(..., description="True lunar longitude (degrees)")
    
    # Birthday and Ugadi information (optional)
    next_year_birthday: Optional[BirthdayInfo] = Field(None, description="Next year's birthday")
    next_years_birthdays: Optional[List[BirthdayInfo]] = Field(None, description="Multiple future birthdays")
    next_ugadi_dates: Optional[List[UgadiInfo]] = Field(None, description="Upcoming Ugadi dates")
    
    # Rule decision (if rules engine was used)
    tithi_decision: Optional[TithiDecision] = Field(None, description="Tithi rule decision details")
    
    # Settings
    settings: SettingsInfo = Field(..., description="Settings used for calculation")


class DayPanchangaInfo(BaseModel):
    """Simplified Panchanga info for a single day in month view."""
    date: str = Field(..., description="Date string (YYYY-MM-DD)")
    weekday: str = Field(..., description="Weekday name")
    year_saka: int = Field(..., description="Saka year")
    masa: str = Field(..., description="Lunar month with adhimasa prefix")
    paksha: str = Field(..., description="Paksha (Sukla/Krsna)")
    tithi_day: int = Field(..., description="Tithi day (1-15)")
    tithi_name: str = Field(..., description="Tithi name")
    nakshatra: str = Field(..., description="Nakshatra name")
    yoga: str = Field(..., description="Yoga name")
    karana: str = Field(..., description="Karana name")


class MonthResponse(BaseModel):
    """Response containing Panchanga for an entire month."""
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    month_name: str = Field(..., description="Month name")
    days: List[DayPanchangaInfo] = Field(..., description="Panchanga for each day")
    settings: SettingsInfo = Field(..., description="Settings used for calculations")


class BirthdayResponse(BaseModel):
    """Response containing future birthday occurrences."""
    reference_date: Tuple[int, int, int] = Field(..., description="Reference date (year, month, day)")
    masa_num: int = Field(..., description="Lunar month number searched")
    masa_name: str = Field(..., description="Lunar month name")
    paksha: str = Field(..., description="Paksha searched")
    tithi_day: int = Field(..., description="Tithi day searched")
    tithi_name: str = Field(..., description="Tithi name")
    birthdays: List[BirthdayInfo] = Field(..., description="Future birthday occurrences")
    settings: SettingsInfo = Field(..., description="Settings used for calculations")


class UgadiResponse(BaseModel):
    """Response containing upcoming Ugadi dates."""
    reference_date: Tuple[int, int, int] = Field(..., description="Reference date (year, month, day)")
    ugadi_dates: List[UgadiInfo] = Field(..., description="Upcoming Ugadi dates")
    settings: SettingsInfo = Field(..., description="Settings used for calculations")


class RuleInfo(BaseModel):
    """Information about an available rule."""
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    priority: int = Field(..., description="Rule priority (lower = higher priority)")
    enabled_by_default: bool = Field(..., description="Whether rule is enabled by default")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Configurable parameters")


class TraditionInfo(BaseModel):
    """Information about an available tradition."""
    name: str = Field(..., description="Tradition identifier")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Tradition description")
    default_rules: List[str] = Field(..., description="Default rules for this tradition")


class RulesListResponse(BaseModel):
    """Response listing available rules."""
    rules: List[RuleInfo] = Field(..., description="Available rules")


class TraditionsListResponse(BaseModel):
    """Response listing available traditions."""
    traditions: List[TraditionInfo] = Field(..., description="Available traditions")
    default_tradition: str = Field(..., description="Default tradition name")


class RuleEvaluationResponse(BaseModel):
    """Response from rule evaluation debug endpoint."""
    date: Tuple[int, int, int] = Field(..., description="Date evaluated")
    tradition: str = Field(..., description="Tradition used")
    rules_evaluated: List[str] = Field(..., description="Rules that were evaluated")
    decision: TithiDecision = Field(..., description="Final tithi decision")
    evaluation_trace: List[Dict[str, Any]] = Field(..., description="Step-by-step evaluation trace")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    tradition: str = Field(..., description="Default tradition")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SlotPanchangaInfo(BaseModel):
    """Panchanga information for a computed slot."""
    tithi: str = Field(..., description="Tithi name")
    tithi_number: int = Field(..., description="Tithi number (1-15)")
    paksha: str = Field(..., description="Paksha (shukla/krishna)")
    tithi_quality: str = Field(..., description="auspicious/neutral/inauspicious")
    nakshatra: str = Field(..., description="Nakshatra name")
    nakshatra_quality: str = Field(..., description="Nakshatra quality")
    yoga: str = Field(..., description="Yoga name")
    karana: str = Field(..., description="Karana name")


class RahuKaalInfo(BaseModel):
    """Rahu Kaal information."""
    start: str = Field(..., description="Start time (HH:MM)")
    end: str = Field(..., description="End time (HH:MM)")
    overlaps_slot: bool = Field(..., description="Whether Rahu Kaal overlaps with slot")


class MuhurtaInfo(BaseModel):
    """Muhurta information."""
    name: str = Field(..., description="Muhurta name")
    start_time: Optional[str] = Field(None, description="Start time")
    end_time: Optional[str] = Field(None, description="End time")
    quality: str = Field(..., description="auspicious/neutral/inauspicious")


class ComputedSlot(BaseModel):
    """A computed time slot with panchanga data."""
    start: str = Field(..., description="Slot start (ISO format)")
    end: str = Field(..., description="Slot end (ISO format)")
    panchanga_score: float = Field(..., ge=0, le=1, description="Auspiciousness score (0-1)")
    panchanga: SlotPanchangaInfo = Field(..., description="Panchanga details")
    muhurta: Optional[MuhurtaInfo] = Field(None, description="Active muhurta")
    rahu_kaal: RahuKaalInfo = Field(..., description="Rahu Kaal info")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")


class ComputeSlotsResponse(BaseModel):
    """Response containing computed time slots."""
    slots: List[ComputedSlot] = Field(..., description="Ranked slots by score")
    computed_at: datetime = Field(..., description="Computation timestamp")
    settings: SettingsInfo = Field(..., description="Settings used")


class TimeSuggestion(BaseModel):
    """A suggested alternative time."""
    date_time: str = Field(..., description="Suggested time (ISO format)")
    reason: str = Field(..., description="Why this time is suggested")
    score: float = Field(..., ge=0, le=1, description="Auspiciousness score")


class ValidateTimeResponse(BaseModel):
    """Response from time validation."""
    is_auspicious: bool = Field(..., description="Whether time is considered auspicious")
    quality: str = Field(..., description="excellent/good/neutral/poor")
    score: float = Field(..., ge=0, le=1, description="Auspiciousness score")
    panchanga: PanchangaResponse = Field(..., description="Full Panchanga for the time")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    suggestions: List[TimeSuggestion] = Field(
        default_factory=list,
        description="Better alternative times"
    )


class PanchangaAtTimeResponse(RootModel[Dict[str, Any]]):
    """
    Generic response payload for calculate-at-time.
    
    This mirrors the combined output used by `console_debug.py`:
    - astronomical (epoch-consistent) fields
    - civil-day fields (tithi/nakshatra/yoga/karana/masa at the chosen time)
    - planetary positions including `planets_detailed`
    """
    pass


class PanchangaAtTimeBatchResponse(RootModel[List[Dict[str, Any]]]):
    """Batch response for calculate-at-time comparisons (order preserved)."""
    pass
