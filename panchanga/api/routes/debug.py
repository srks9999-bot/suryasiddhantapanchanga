"""
Debug API endpoints for Panchanga calculations.

This module provides detailed debug information for verifying the accuracy
of panchanga calculations. It uses the ACTUAL PanchangaService and calculator
classes, exposing intermediate values computed during the real calculation process.

NOTE: This module is for debugging and verification purposes only.
Do not use in production for normal panchanga queries.
"""

import math
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from panchanga.models.requests import CalculateRequest, LocationSettings, CalculationSettings
from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService
from panchanga.core.date_utils import DateUtils
from panchanga.core.math_utils import MathUtils
from panchanga.core.constants import PI, RAD, EPSILON
from panchanga.data.planetary import (
    SURYA_SIDDHANTA_ROTATIONS, SURYA_SIDDHANTA_PLANETARY,
    PANCASIDDHANTIKA_ROTATIONS, PANCASIDDHANTIKA_PLANETARY,
    calculate_derived_constants
)
from panchanga.data.names import (
    get_tithi_name, get_nakshatra_name, get_yoga_name, get_karana_name
)
from panchanga.rules.base import TithiContext, TithiDecisionData
from panchanga.core.debug_context import debug_context, debug_log
from api.dependencies import get_service

router = APIRouter()


class DebugValue(BaseModel):
    """A debug value with formula documentation."""
    name: str
    value: Any
    formula: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None


class PlanetaryDebugInfo(BaseModel):
    """Debug information for a planet's calculations."""
    planet: str
    mean_longitude: DebugValue
    apogee: Optional[DebugValue] = None
    manda_argument: Optional[DebugValue] = None
    manda_correction: Optional[DebugValue] = None
    true_longitude: Optional[DebugValue] = None


class ElementDebugInfo(BaseModel):
    """Debug information for a panchanga element."""
    name: str
    value: Any
    index: int
    formula: str
    intermediate_values: Dict[str, Any]
    start_time: Optional[Dict[str, Any]] = None
    end_time: Optional[Dict[str, Any]] = None


class RuleEvaluationDebug(BaseModel):
    """Debug information for rule-based tithi selection."""
    tradition: str
    active_rules: List[Dict[str, Any]]
    evaluation_trace: List[Dict[str, Any]]
    selected_rule: Optional[str]
    decision: Optional[Dict[str, Any]]
    explanation: str


class ExecutionTrace(BaseModel):
    """Execution trace capturing the control flow."""
    total_entries: int
    by_type: Dict[str, int]
    functions_called: List[str]
    max_depth: int
    trace_tree: str
    detailed_trace: List[Dict[str, Any]]


class DebugCalculateResponse(BaseModel):
    """Complete debug response with all intermediate calculations."""
    
    # Input parameters
    input_date: Dict[str, int]
    location: Dict[str, float]
    settings: Dict[str, str]
    
    # Execution trace - control flow
    execution_trace: ExecutionTrace
    
    # Epoch and date calculations
    date_calculations: Dict[str, DebugValue]
    
    # Yuga constants used
    yuga_constants: Dict[str, DebugValue]
    
    # Planetary calculations
    planetary_calculations: List[PlanetaryDebugInfo]
    
    # Panchanga elements with derivations
    tithi_debug: ElementDebugInfo
    nakshatra_debug: ElementDebugInfo
    yoga_debug: ElementDebugInfo
    karana_debug: ElementDebugInfo
    
    # Rule-based tithi selection
    rule_evaluation: RuleEvaluationDebug
    
    # Time calculations
    time_calculations: Dict[str, DebugValue]
    
    # Final panchanga result (same as regular API)
    panchanga_result: Dict[str, Any]


def _create_debug_value(name: str, value: Any, formula: str = None, 
                        description: str = None, unit: str = None) -> DebugValue:
    """Helper to create a DebugValue."""
    return DebugValue(
        name=name,
        value=value,
        formula=formula,
        description=description,
        unit=unit
    )


def _extract_planetary_debug(astro, ahar: float, rotations, planetary) -> List[PlanetaryDebugInfo]:
    """
    Extract planetary debug information using the ACTUAL AstronomicalCalculator methods.
    
    This ensures we're showing the exact same values computed by the service.
    """
    planetary_calculations = []
    yuga_civil_days = astro.yuga_civil_days
    
    # --- SUN ---
    # Call the actual methods used by the calculator
    mean_sun = astro.get_mean_sun_longitude(ahar, rotations.sun)
    sun_apogee = planetary.sun_apogee
    sun_manda_arg = mean_sun - sun_apogee
    sun_manda_corr = astro.get_manda_equation(sun_manda_arg, 'sun')
    true_sun = astro.get_true_solar_longitude(ahar)  # Uses the actual method
    
    planetary_calculations.append(PlanetaryDebugInfo(
        planet="Sun",
        mean_longitude=_create_debug_value(
            "Mean Sun Longitude",
            mean_sun,
            formula=f"MeanSun = 360 * frac({rotations.sun} * {ahar:.4f} / {yuga_civil_days})",
            description="Mean heliocentric longitude computed via AstronomicalCalculator.get_mean_longitude()",
            unit="degrees"
        ),
        apogee=_create_debug_value(
            "Sun Apogee (Mandocca)",
            sun_apogee,
            description=f"Sun's apogee from PlanetaryConstants (Surya Siddhanta: 77°17')",
            unit="degrees"
        ),
        manda_argument=_create_debug_value(
            "Manda Argument",
            sun_manda_arg,
            formula="MandaArg = MeanSun - SunApogee",
            description="Argument for equation of center",
            unit="degrees"
        ),
        manda_correction=_create_debug_value(
            "Manda Correction",
            sun_manda_corr,
            formula=f"MandaCorr = AstronomicalCalculator.get_manda_equation({sun_manda_arg:.4f}, 'sun')",
            description=f"Equation of center computed via get_manda_equation() with circumm={planetary.sun_circumm}°",
            unit="degrees"
        ),
        true_longitude=_create_debug_value(
            "True Sun Longitude",
            true_sun,
            formula="TrueSun = AstronomicalCalculator.get_true_solar_longitude(ahar)",
            description="True geocentric longitude via get_true_solar_longitude()",
            unit="degrees"
        )
    ))
    
    # --- MOON ---
    mean_moon = astro.get_mean_longitude(ahar, rotations.moon)
    mean_candrocca = astro.get_mean_longitude(ahar, rotations.candrocca)
    moon_apogee = mean_candrocca + 90  # As per Surya Siddhanta
    moon_manda_arg = mean_moon - moon_apogee
    moon_manda_corr = astro.get_manda_equation(moon_manda_arg, 'moon')
    true_moon = astro.get_true_lunar_longitude(ahar)  # Uses the actual method
    
    planetary_calculations.append(PlanetaryDebugInfo(
        planet="Moon",
        mean_longitude=_create_debug_value(
            "Mean Moon Longitude",
            mean_moon,
            formula=f"MeanMoon = 360 * frac({rotations.moon} * {ahar:.4f} / {yuga_civil_days})",
            description="Mean longitude computed via AstronomicalCalculator.get_mean_longitude()",
            unit="degrees"
        ),
        apogee=_create_debug_value(
            "Moon Apogee (Candrocca + 90°)",
            moon_apogee,
            formula=f"MoonApogee = get_mean_longitude(ahar, candrocca) + 90 = {mean_candrocca:.4f} + 90",
            description="Moon's apogee: Candrocca mean longitude + 90° (per Surya Siddhanta)",
            unit="degrees"
        ),
        manda_argument=_create_debug_value(
            "Manda Argument",
            moon_manda_arg,
            formula="MandaArg = MeanMoon - MoonApogee",
            unit="degrees"
        ),
        manda_correction=_create_debug_value(
            "Manda Correction",
            moon_manda_corr,
            formula=f"MandaCorr = AstronomicalCalculator.get_manda_equation({moon_manda_arg:.4f}, 'moon')",
            description=f"Equation of center computed via get_manda_equation() with circumm={planetary.moon_circumm}°",
            unit="degrees"
        ),
        true_longitude=_create_debug_value(
            "True Moon Longitude",
            true_moon,
            formula="TrueMoon = AstronomicalCalculator.get_true_lunar_longitude(ahar)",
            description="True geocentric longitude via get_true_lunar_longitude()",
            unit="degrees"
        )
    ))
    
    # --- CANDROCCA (Lunar Apogee) ---
    planetary_calculations.append(PlanetaryDebugInfo(
        planet="Candrocca (Lunar Apogee)",
        mean_longitude=_create_debug_value(
            "Mean Candrocca",
            mean_candrocca,
            formula=f"MeanCandrocca = 360 * frac({rotations.candrocca} * {ahar:.4f} / {yuga_civil_days})",
            description="Mean longitude of the lunar apogee",
            unit="degrees"
        )
    ))
    
    return planetary_calculations


@router.post(
    "/debug/calculate",
    response_model=DebugCalculateResponse,
    summary="Debug Panchanga Calculation",
    description="""
Calculate Panchanga with full debug information.

**IMPORTANT**: This endpoint uses the ACTUAL PanchangaService and AstronomicalCalculator
classes to compute values. All intermediate values shown are extracted from the real
calculation path, ensuring they match exactly what the production API computes.

### Returned Information:

1. **Date Calculations** - Julian Day, Ahargana, Desantara (from DateUtils)
2. **Yuga Constants** - Values from calculate_derived_constants()
3. **Planetary Calculations** - Values from AstronomicalCalculator methods:
   - get_mean_longitude(), get_manda_equation()
   - get_true_solar_longitude(), get_true_lunar_longitude()
4. **Panchanga Elements** - Derived from actual tithi/nakshatra/yoga/karana values
5. **Final Result** - Same as PanchangaService.calculate()
""",
    tags=["debug"]
)
async def debug_calculate(request: CalculateRequest):
    """
    Calculate Panchanga with comprehensive debug information.
    
    Uses the actual PanchangaService to ensure consistency with production results.
    """
    try:
        # Extract input parameters
        year, month, day = request.year, request.month, request.day
        
        # Build settings - same way as regular API
        settings = PanchangaSettings()
        
        if request.location:
            settings.loc_lat = request.location.latitude
            settings.loc_lon = request.location.longitude
        
        if request.settings:
            settings.tradition = request.settings.tradition
            settings.selected_system = request.settings.system
            settings.language = request.settings.language
        
        # Create the ACTUAL service - same as production
        service = PanchangaService(settings=settings)
        
        # Get the actual calculator and astro objects for debug extraction
        calculator = service.calculator
        astro = calculator.astro
        rotations = astro.rotations
        planetary = astro.planetary
        
        # ===========================================================
        # COMPUTE ACTUAL PANCHANGA RESULT with debug tracing enabled
        # ===========================================================
        debug_log("Starting panchanga calculation", 
                  year=year, month=month, day=day,
                  latitude=settings.loc_lat, longitude=settings.loc_lon)
        
        with debug_context.enabled():
            debug_log("Calculation started", 
                      date=f"{year}-{month:02d}-{day:02d}",
                      tradition=settings.tradition,
                      system=settings.selected_system)
            
            # Skip timing calculations to reduce trace entries (timing is expensive)
            # Set include_timing=False to dramatically reduce execution trace entries
            panchanga_result = service.calculate(year, month, day, include_timing=False)
            
            debug_log("Calculation completed",
                      tithi=panchanga_result.get('tithi_name'),
                      nakshatra=panchanga_result.get('nakshatra'),
                      yoga=panchanga_result.get('yoga'),
                      karana=panchanga_result.get('karana'))
            
            # Capture the execution trace
            trace_summary = debug_context.get_trace_summary()
            trace_tree = debug_context.format_trace_tree()
            detailed_trace = debug_context.get_traces()
        
        execution_trace = ExecutionTrace(
            total_entries=trace_summary['total_entries'],
            by_type=trace_summary['by_type'],
            functions_called=trace_summary['functions_called'],
            max_depth=trace_summary['max_depth'],
            trace_tree=trace_tree,
            detailed_trace=detailed_trace
        )
        
        # ===========================================================
        # EXTRACT DEBUG VALUES using actual calculator state
        # ===========================================================
        
        # Date calculations using DateUtils (same as calculator)
        julian_day = DateUtils.modern_date_to_julian_day(year, month, day)
        ahar = DateUtils.julian_day_to_ahargana(julian_day)
        
        # Desantara correction (longitude from IST meridian)
        desantara = (settings.loc_lon - 82.5) / 360
        
        # Ahargana at sunrise with corrections - SAME as calculator.calculate()
        ahar_sunrise = ahar + 0.25 - desantara
        
        # Daylight equation using actual astro method
        eqtime = astro.get_daylight_equation(year, settings.loc_lat, ahar_sunrise)
        ahar_at_sunrise = ahar_sunrise - eqtime  # Final ahar used for calculations
        ## lets trucate ahar_at_sunrise to a integer value

        ahar_at_sunrise = int(ahar_at_sunrise)
        
        date_calculations = {
            "julian_day": _create_debug_value(
                "Julian Day",
                julian_day,
                formula="DateUtils.modern_date_to_julian_day(year, month, day)",
                description="Julian Day number at noon",
                unit="days"
            ),
            "kali_epoch_jd": _create_debug_value(
                "Kali Epoch JD",
                DateUtils.KALI_EPOCH_JD,
                description="Julian Day of Kali Yuga epoch (Feb 18, 3102 BCE)",
                unit="days"
            ),
            "ahargana_raw": _create_debug_value(
                "Ahargana (raw)",
                ahar,
                formula="DateUtils.julian_day_to_ahargana(julian_day)",
                description="Days elapsed since Kali epoch (at noon)",
                unit="days"
            ),
            "desantara": _create_debug_value(
                "Desantara Correction",
                desantara,
                formula=f"(longitude - 82.5) / 360 = ({settings.loc_lon} - 82.5) / 360",
                description="Longitude correction from IST meridian",
                unit="days"
            ),
            "ahargana_6am": _create_debug_value(
                "Ahargana at 6 AM",
                ahar_sunrise,
                formula="ahar + 0.25 - desantara",
                description="Ahargana adjusted to 6 AM local time",
                unit="days"
            ),
            "daylight_equation": _create_debug_value(
                "Daylight Equation",
                eqtime,
                formula=f"AstronomicalCalculator.get_daylight_equation({year}, {settings.loc_lat}, ahar)",
                description="Time correction for actual sunrise (from astro.get_daylight_equation())",
                unit="day fraction"
            ),
            "ahargana_at_sunrise": _create_debug_value(
                "Ahargana at Sunrise (FINAL)",
                ahar_at_sunrise,
                formula="ahar_6am - eqtime",
                description="This is the ahargana value used for all planetary calculations",
                unit="days"
            ),
        }
        
        # ===========================================================
        # YUGA CONSTANTS from actual calculator
        # ===========================================================
        
        derived = calculate_derived_constants(rotations)
        
        yuga_constants = {
            "yuga_civil_days": _create_debug_value(
                "Yuga Civil Days",
                astro.yuga_civil_days,
                formula="calculate_derived_constants(rotations)['YugaCivilDays']",
                description=f"From astro.yuga_civil_days property",
                unit="days"
            ),
            "yuga_synodic_month": _create_debug_value(
                "Yuga Synodic Months",
                astro.yuga_synodic_month,
                formula="MoonRotations - SunRotations",
                description="From astro.yuga_synodic_month property",
                unit="months"
            ),
            "yuga_adhimasa": _create_debug_value(
                "Yuga Adhimasas",
                astro.yuga_adhimasa,
                formula="YugaSynodicMonth - 12*SunRotations",
                description="From astro.yuga_adhimasa property",
                unit="months"
            ),
            "yuga_tithi": _create_debug_value(
                "Yuga Tithis",
                astro.yuga_tithi,
                formula="30 * YugaSynodicMonth",
                description="From astro.yuga_tithi property",
                unit="tithis"
            ),
            "yuga_ksayadina": _create_debug_value(
                "Yuga Ksayadinas",
                astro.yuga_ksayadina,
                formula="YugaTithi - YugaCivilDays",
                description="From astro.yuga_ksayadina property",
                unit="days"
            ),
            "sun_rotations": _create_debug_value(
                "Sun Rotations",
                rotations.sun,
                description="From rotations.sun"
            ),
            "moon_rotations": _create_debug_value(
                "Moon Rotations",
                rotations.moon,
                description="From rotations.moon"
            ),
        }
        
        # ===========================================================
        # PLANETARY CALCULATIONS using actual AstronomicalCalculator
        # ===========================================================
        
        planetary_calculations = _extract_planetary_debug(
            astro, ahar_at_sunrise, rotations, planetary
        )
        
        # Get true longitudes for element calculations
        true_sun = astro.get_true_solar_longitude(ahar_at_sunrise)
        true_moon = astro.get_true_lunar_longitude(ahar_at_sunrise)
        
        # ===========================================================
        # TITHI CALCULATION - using actual astro.get_tithi()
        # ===========================================================
        
        tithi_float = astro.get_tithi(true_moon, true_sun)
        elongation = MathUtils.zero360(true_moon - true_sun)
        tithi_day = MathUtils.trunc(tithi_float) + 1
        tithi_fraction = MathUtils.frac(tithi_float)
        
        # From panchanga result
        paksha = panchanga_result['paksa']
        tithi_in_paksha = panchanga_result['tithi_day']
        tithi_name = panchanga_result.get('tithi_name', '')
        
        tithi_debug = ElementDebugInfo(
            name="Tithi",
            value=tithi_name,
            index=tithi_day,
            formula="tithi = AstronomicalCalculator.get_tithi(true_moon, true_sun) = zero360(moon - sun) / 12",
            intermediate_values={
                "true_moon_longitude": true_moon,
                "true_sun_longitude": true_sun,
                "elongation_raw": true_moon - true_sun,
                "elongation_normalized": elongation,
                "tithi_float_from_get_tithi": tithi_float,
                "tithi_day_1_to_30": tithi_day,
                "tithi_fraction": tithi_fraction,
                "paksha_from_result": paksha,
                "tithi_in_paksha_1_to_15": tithi_in_paksha,
                "formula_explanation": f"Each tithi spans 12° of elongation. {elongation:.4f}° / 12° = {tithi_float:.4f}"
            }
        )
        
        # ===========================================================
        # NAKSHATRA - derived from Moon longitude (same as get_nakshatra_name)
        # ===========================================================
        
        nakshatra_float = true_moon * 27 / 360
        nakshatra_index = MathUtils.trunc(nakshatra_float)
        nakshatra_fraction = MathUtils.frac(nakshatra_float)
        nakshatra_name = panchanga_result['nakshatra']
        
        nakshatra_debug = ElementDebugInfo(
            name="Nakshatra",
            value=nakshatra_name,
            index=nakshatra_index,
            formula="nakshatra_index = trunc(true_moon * 27 / 360) - see get_nakshatra_name()",
            intermediate_values={
                "true_moon_longitude": true_moon,
                "nakshatra_float": nakshatra_float,
                "nakshatra_index_0_to_26": nakshatra_index,
                "nakshatra_fraction": nakshatra_fraction,
                "degrees_per_nakshatra": 360 / 27,
                "moon_position_in_nakshatra_deg": nakshatra_fraction * (360 / 27),
                "formula_explanation": f"Each of 27 nakshatras spans {360/27:.4f}°. Moon at {true_moon:.4f}° → index {nakshatra_index}"
            }
        )
        
        # ===========================================================
        # YOGA - derived from Sun + Moon (same as get_yoga_name)
        # ===========================================================
        
        yoga_sum = MathUtils.zero360(true_sun + true_moon)
        yoga_float = yoga_sum * 27 / 360
        yoga_index = MathUtils.trunc(yoga_float)
        yoga_fraction = MathUtils.frac(yoga_float)
        yoga_name = panchanga_result['yoga']
        
        yoga_debug = ElementDebugInfo(
            name="Yoga",
            value=yoga_name,
            index=yoga_index,
            formula="yoga_index = trunc(zero360(sun + moon) * 27 / 360) - see get_yoga_name()",
            intermediate_values={
                "true_sun_longitude": true_sun,
                "true_moon_longitude": true_moon,
                "sum_raw": true_sun + true_moon,
                "sum_normalized": yoga_sum,
                "yoga_float": yoga_float,
                "yoga_index_0_to_26": yoga_index,
                "yoga_fraction": yoga_fraction,
                "formula_explanation": f"Sum of longitudes {yoga_sum:.4f}° * 27/360 = {yoga_float:.4f} → index {yoga_index}"
            }
        )
        
        # ===========================================================
        # KARANA - derived from tithi (same as get_karana_name)
        # ===========================================================
        
        karana_float = 2 * tithi_float
        karana_index = MathUtils.trunc(karana_float)
        karana_name = panchanga_result['karana']
        
        # Explain the karana mapping (from get_karana_name logic)
        if karana_index == 0:
            karana_type = "Kimstughna (fixed, index 0 - only at start of Sukla Paksha)"
        elif karana_index < 57:
            cycle_index = karana_index % 7
            if cycle_index == 0:
                cycle_index = 7
            karana_type = f"Movable karana (indices 1-56 cycle through 7 karanas), position in cycle: {cycle_index}"
        else:
            fixed_map = {57: "Sakuni (index 57)", 58: "Catuspada (index 58)", 59: "Naga (index 59)"}
            karana_type = f"Fixed karana: {fixed_map.get(karana_index, 'unknown')}"
        
        karana_debug = ElementDebugInfo(
            name="Karana",
            value=karana_name,
            index=karana_index,
            formula="karana_index = trunc(2 * tithi_float) - see get_karana_name()",
            intermediate_values={
                "tithi_float": tithi_float,
                "karana_float": karana_float,
                "karana_index_0_to_59": karana_index,
                "karana_type": karana_type,
                "formula_explanation": f"Each tithi has 2 karanas. {tithi_float:.4f} * 2 = {karana_float:.4f} → index {karana_index}"
            }
        )
        
        # ===========================================================
        # RULE-BASED TITHI SELECTION - Enable tracing and evaluate
        # ===========================================================
        
        # Enable tracing on the rule engine to see evaluation details
        rule_engine = service.rule_engine
        rule_engine.trace_enabled = True
        
        # Create TithiContext for rule evaluation (same as service._create_tithi_context)
        tithi_start_datetime = panchanga_result.get('tithi_start_datetime', {})
        tithi_end_datetime = panchanga_result.get('tithi_end_datetime', {})
        
        tithi_context = TithiContext(
            date=panchanga_result['gregorian_date'],
            sunrise_tithi=panchanga_result['tithi_day'],
            sunrise_paksha=panchanga_result['paksa'],
            tithi_start_ahar=0,  # Would need to extract from internal state
            tithi_end_ahar=0,
            sunrise_ahar=ahar_at_sunrise,
            next_sunrise_ahar=ahar_at_sunrise + 1,
            tradition=settings.tradition,
            sun_longitude=true_sun,
            moon_longitude=true_moon,
            masa_num=panchanga_result.get('masa_num'),
            language=settings.language
        )
        
        # Evaluate rules with tracing
        rule_decision = rule_engine.evaluate(tithi_context)
        rule_trace = rule_engine.get_trace()
        
        # Disable tracing
        rule_engine.trace_enabled = False
        
        # Get active rules info
        active_rules = rule_engine.get_active_rules()
        all_rules = rule_engine.get_all_rules()
        
        # Build explanation
        selected_rule_name = rule_decision.rule_name if rule_decision else "none"
        if rule_decision:
            decision_notes = rule_decision.notes if rule_decision.notes else []
            explanation = f"Rule '{selected_rule_name}' determined tithi {rule_decision.tithi} {rule_decision.paksha}"
            if rule_decision.is_ksaya:
                explanation += " (KSAYA - skipped tithi)"
            if rule_decision.is_vriddhi:
                explanation += " (VRIDDHI - extended tithi)"
            if decision_notes:
                explanation += f". Notes: {'; '.join(decision_notes)}"
        else:
            explanation = "No rule made a decision"
        
        # Also check if tithi_decision was already in panchanga_result
        existing_decision = panchanga_result.get('tithi_decision')
        
        rule_evaluation = RuleEvaluationDebug(
            tradition=settings.tradition,
            active_rules=active_rules,
            evaluation_trace=rule_trace,
            selected_rule=selected_rule_name,
            decision=rule_decision.to_dict() if rule_decision else None,
            explanation=explanation
        )
        
        # ===========================================================
        # TIME CALCULATIONS from actual methods
        # ===========================================================
        
        sunrise_h, sunrise_m = astro.get_sunrise_time(eqtime)
        sunset_h, sunset_m = astro.get_sunset_time(eqtime)
        
        # Also compute the underlying values
        mslong = astro.get_mean_longitude(ahar_at_sunrise, rotations.sun)
        samslong = mslong + (54 / 3600) * (year - 499)
        sdecl = astro.get_declination(samslong)
        
        time_calculations = {
            "mean_sun_precession_adjusted": _create_debug_value(
                "Mean Sun (Precession Adjusted)",
                samslong,
                formula="MeanSun + (54/3600) * (year - 499)",
                description="Precession adjustment from AD 499 reference",
                unit="degrees"
            ),
            "solar_declination": _create_debug_value(
                "Solar Declination",
                sdecl,
                formula="AstronomicalCalculator.get_declination(samslong)",
                description="From astro.get_declination()",
                unit="degrees"
            ),
            "sunrise_time": _create_debug_value(
                "Sunrise Time",
                f"{sunrise_h:02d}:{sunrise_m:02d}",
                formula="AstronomicalCalculator.get_sunrise_time(eqtime)",
                description="From astro.get_sunrise_time()",
                unit="HH:MM"
            ),
            "sunset_time": _create_debug_value(
                "Sunset Time",
                f"{sunset_h:02d}:{sunset_m:02d}",
                formula="AstronomicalCalculator.get_sunset_time(eqtime)",
                description="From astro.get_sunset_time()",
                unit="HH:MM"
            ),
        }
        
        # ===========================================================
        # BUILD FINAL RESPONSE
        # ===========================================================
        
        # Format time tuples to strings with AM/PM
        def format_time(time_tuple):
            if time_tuple and len(time_tuple) == 2:
                hours, minutes = time_tuple
                # Convert 24-hour to 12-hour format with AM/PM
                if hours == 0:
                    return f"12:{minutes:02d} AM"
                elif hours < 12:
                    return f"{hours}:{minutes:02d} AM"
                elif hours == 12:
                    return f"12:{minutes:02d} PM"
                else:
                    return f"{hours - 12}:{minutes:02d} PM"
            return None
        
        # Format datetime dict to string with AM/PM
        def format_datetime(dt_dict):
            if dt_dict and isinstance(dt_dict, dict):
                year = dt_dict.get('year')
                month = dt_dict.get('month')
                day = dt_dict.get('day')
                hours = dt_dict.get('hours', 0)
                minutes = dt_dict.get('minutes', 0)
                if year and month and day:
                    # Convert 24-hour to 12-hour format with AM/PM
                    if hours == 0:
                        time_str = f"12:{minutes:02d} AM"
                    elif hours < 12:
                        time_str = f"{hours}:{minutes:02d} AM"
                    elif hours == 12:
                        time_str = f"12:{minutes:02d} PM"
                    else:
                        time_str = f"{hours - 12}:{minutes:02d} PM"
                    return f"{year}-{month:02d}-{day:02d} {time_str}"
            return None
        
        # Simplify panchanga_result for the response
        simplified_result = {
            "gregorian_date": panchanga_result['gregorian_date'],
            "weekday": panchanga_result['weekday'],
            "julian_day": panchanga_result['julian_day'],
            "ahargana": panchanga_result['ahargana'],
            "sunrise": format_time(panchanga_result['sunrise']),
            "sunset": format_time(panchanga_result['sunset']),
            "tithi": {
                "name": panchanga_result.get('tithi_name', ''),
                "day": panchanga_result['tithi_day'],
                "paksha": panchanga_result['paksa'],
                "paksha_name": panchanga_result.get('paksha_name', ''),
                "fraction": round(panchanga_result['tithi_fraction'], 4),
                "start_time": format_time(panchanga_result.get('tithi_start_time')),
                "end_time": format_time(panchanga_result.get('tithi_end_time')),
                "start_datetime": format_datetime(panchanga_result.get('tithi_start_datetime')),
                "end_datetime": format_datetime(panchanga_result.get('tithi_end_datetime'))
            },
            "nakshatra": {
                "name": panchanga_result['nakshatra'],
                "start_time": format_time(panchanga_result.get('nakshatra_start_time')),
                "end_time": format_time(panchanga_result.get('nakshatra_end_time')),
                "start_datetime": format_datetime(panchanga_result.get('nakshatra_start_datetime')),
                "end_datetime": format_datetime(panchanga_result.get('nakshatra_end_datetime'))
            },
            "yoga": {
                "name": panchanga_result['yoga'],
                "start_time": format_time(panchanga_result.get('yoga_start_time')),
                "end_time": format_time(panchanga_result.get('yoga_end_time')),
                "start_datetime": format_datetime(panchanga_result.get('yoga_start_datetime')),
                "end_datetime": format_datetime(panchanga_result.get('yoga_end_datetime'))
            },
            "karana": {
                "name": panchanga_result['karana'],
                "start_time": format_time(panchanga_result.get('karana_start_time')),
                "end_time": format_time(panchanga_result.get('karana_end_time')),
                "start_datetime": format_datetime(panchanga_result.get('karana_start_datetime')),
                "end_datetime": format_datetime(panchanga_result.get('karana_end_datetime'))
            },
            "masa": panchanga_result['masa'],
            "adhimasa": panchanga_result['adhimasa'],
            "sun_longitude": round(panchanga_result['sun_longitude'], 4),
            "moon_longitude": round(panchanga_result['moon_longitude'], 4),
            "year_saka": panchanga_result['year_saka'],
            "year_kali": panchanga_result['year_kali'],
        }
        
        return DebugCalculateResponse(
            input_date={"year": year, "month": month, "day": day},
            location={"latitude": settings.loc_lat, "longitude": settings.loc_lon},
            settings={
                "tradition": settings.tradition,
                "system": settings.selected_system,
                "language": settings.language
            },
            execution_trace=execution_trace,
            date_calculations=date_calculations,
            yuga_constants=yuga_constants,
            planetary_calculations=planetary_calculations,
            tithi_debug=tithi_debug,
            nakshatra_debug=nakshatra_debug,
            yoga_debug=yoga_debug,
            karana_debug=karana_debug,
            rule_evaluation=rule_evaluation,
            time_calculations=time_calculations,
            panchanga_result=simplified_result
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500, 
            detail=f"Debug calculation error: {str(e)}\n{traceback.format_exc()}"
        )


@router.get(
    "/debug/constants",
    summary="Get Calculation Constants",
    description="""
Returns all constants used in Panchanga calculations.

These are the actual constants from the panchanga.data.planetary module
that the AstronomicalCalculator uses.
""",
    tags=["debug"]
)
async def get_debug_constants(system: str = "SuryaSiddhanta"):
    """
    Get all constants used in calculations.
    """
    if system == "InPancasiddhantika":
        rotations = PANCASIDDHANTIKA_ROTATIONS
        planetary = PANCASIDDHANTIKA_PLANETARY
    else:
        rotations = SURYA_SIDDHANTA_ROTATIONS
        planetary = SURYA_SIDDHANTA_PLANETARY
    
    derived = calculate_derived_constants(rotations)
    
    return {
        "system": system,
        "source": "panchanga.data.planetary module",
        "yuga_rotations": {
            "star": rotations.star,
            "sun": rotations.sun,
            "moon": rotations.moon,
            "mercury": rotations.mercury,
            "venus": rotations.venus,
            "mars": rotations.mars,
            "jupiter": rotations.jupiter,
            "saturn": rotations.saturn,
            "candrocca": rotations.candrocca,
            "rahu": rotations.rahu,
        },
        "planetary_constants": {
            "sun_apogee": planetary.sun_apogee,
            "sun_circumm": planetary.sun_circumm,
            "moon_circumm": planetary.moon_circumm,
            "mercury_apogee": planetary.mercury_apogee,
            "mercury_circumm": planetary.mercury_circumm,
            "mercury_circums": planetary.mercury_circums,
            "venus_apogee": planetary.venus_apogee,
            "venus_circumm": planetary.venus_circumm,
            "venus_circums": planetary.venus_circums,
            "mars_apogee": planetary.mars_apogee,
            "mars_circumm": planetary.mars_circumm,
            "mars_circums": planetary.mars_circums,
            "jupiter_apogee": planetary.jupiter_apogee,
            "jupiter_circumm": planetary.jupiter_circumm,
            "jupiter_circums": planetary.jupiter_circums,
            "saturn_apogee": planetary.saturn_apogee,
            "saturn_circumm": planetary.saturn_circumm,
            "saturn_circums": planetary.saturn_circums,
        },
        "derived_constants": {
            "YugaCivilDays": derived['YugaCivilDays'],
            "YugaSynodicMonth": derived['YugaSynodicMonth'],
            "YugaAdhimasa": derived['YugaAdhimasa'],
            "YugaTithi": derived['YugaTithi'],
            "YugaKsayadina": derived['YugaKsayadina'],
        },
        "mathematical_constants": {
            "PI": PI,
            "RAD": RAD,
            "EPSILON": EPSILON,
        },
        "epoch": {
            "kali_epoch_jd": DateUtils.KALI_EPOCH_JD,
            "kali_epoch_date": "February 18, 3102 BCE (midnight)",
            "gregorian_reform_jd": DateUtils.GREGORIAN_REFORM_JD,
        }
    }


@router.post(
    "/debug/compare-timing",
    summary="Compare Timing Search Algorithms",
    description="""
Compare the optimized (heuristic + binary search) vs linear timing search methods.

Returns timing results from both approaches along with:
- Execution time for each approach
- Difference in results (should be very small, < 1 second)
- Speedup factor (optimized should be 100-400x faster)

Use this to validate the optimized approach produces correct results.
""",
    tags=["debug"]
)
async def compare_timing_methods(request: CalculateRequest):
    """
    Compare optimized vs linear timing search methods.
    """
    try:
        year, month, day = request.year, request.month, request.day
        
        # Build settings
        settings = PanchangaSettings()
        if request.location:
            settings.loc_lat = request.location.latitude
            settings.loc_lon = request.location.longitude
        if request.settings:
            settings.tradition = request.settings.tradition
            settings.selected_system = request.settings.system
            settings.language = request.settings.language
        
        # Create service
        service = PanchangaService(settings=settings)
        calculator = service.calculator
        
        # Compute basic panchanga to get tithi info
        julian_day = DateUtils.modern_date_to_julian_day(year, month, day)
        ahar = DateUtils.julian_day_to_ahargana(julian_day)
        ahar = ahar + 0.25 - settings.desantara
        eqtime = calculator.astro.get_daylight_equation(year, settings.loc_lat, ahar)
        ahar = ahar - eqtime
        
        # Get tithi
        tslong = calculator.astro.get_true_solar_longitude(ahar)
        tllong = calculator.astro.get_true_lunar_longitude(ahar)
        tithi = calculator.astro.get_tithi(tllong, tslong)
        tithi_day, ftithi = calculator.get_tithi_set(tithi)
        tithi_day, sukla_krsna, paksa = calculator.set_sukla_krsna(tithi_day)
        
        language = settings.language or 'telugu'
        
        # Run comparison
        comparison = calculator.compare_timing_methods(
            ahar, tithi_day, paksa, language, ftithi
        )
        
        return {
            "input": {
                "date": f"{year}-{month:02d}-{day:02d}",
                "tithi_day": tithi_day,
                "paksa": paksa,
                "tithi_fraction": ftithi,
                "ahar": ahar
            },
            "comparison": comparison,
            "summary": {
                "tithi_start_diff_seconds": comparison['tithi']['difference']['start_seconds_diff'],
                "tithi_end_diff_seconds": comparison['tithi']['difference']['end_seconds_diff'],
                "speedup_factor": comparison['tithi']['difference']['speedup'],
                "optimized_ms": comparison['tithi']['optimized']['duration_ms'],
                "linear_ms": comparison['tithi']['linear']['duration_ms'],
                "results_match": (
                    comparison['tithi']['difference']['start_seconds_diff'] < 1 and
                    comparison['tithi']['difference']['end_seconds_diff'] < 1
                )
            }
        }
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Comparison error: {str(e)}\n{traceback.format_exc()}"
        )
