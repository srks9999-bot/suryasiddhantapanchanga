#!/usr/bin/env python3
"""
Console Debug Tool for Panchanga Calculations.

A command-line tool for exploring and debugging panchanga calculations
without starting the full API server.

Usage:
    python console_debug.py                          # Today's panchanga
    python console_debug.py 2026 1 12                # Specific date
    python console_debug.py 2026 1 12 --detailed     # With intermediate calculations
    python console_debug.py 2026 1 12 --compare      # Compare midnight vs sunrise methods
    python console_debug.py --interactive            # Interactive mode
    python console_debug.py --month 2026 1           # Monthly calendar

Examples:
    python console_debug.py 2024 4 9 --lat 17.4 --lon 78.5 --lang telugu
    python console_debug.py --month 2024 3 --tradition surya
    python console_debug.py 2026 1 15 --drik         # Use Drik ephemeris for sunrise/sunset
    python console_debug.py 2026 1 15 --compare      # Compare calculation methods
"""

import argparse
import sys
from datetime import date, datetime
from typing import Optional, Dict, Any

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def c(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{Colors.END}"

def header(text: str) -> str:
    return c(f"\n{'═' * 60}\n  {text}\n{'═' * 60}", Colors.BOLD + Colors.CYAN)

def subheader(text: str) -> str:
    return c(f"\n┌─ {text} {'─' * (55 - len(text))}┐", Colors.YELLOW)

def label(text: str) -> str:
    return c(f"{text:>24}", Colors.DIM)

def value(text: str) -> str:
    return c(str(text), Colors.GREEN)

def highlight(text: str) -> str:
    return c(str(text), Colors.BOLD + Colors.YELLOW)

def dim(text: str) -> str:
    return c(str(text), Colors.DIM)


def format_time(time_tuple) -> str:
    """Format time tuple to readable string."""
    if time_tuple and len(time_tuple) == 2:
        hours, minutes = time_tuple
        if hours == 0:
            return f"12:{minutes:02d} AM"
        elif hours < 12:
            return f"{hours}:{minutes:02d} AM"
        elif hours == 12:
            return f"12:{minutes:02d} PM"
        else:
            return f"{hours - 12}:{minutes:02d} PM"
    return "N/A"


def format_datetime(dt_dict) -> str:
    """Format datetime dict to readable string."""
    if dt_dict and isinstance(dt_dict, dict):
        year = dt_dict.get('year')
        month = dt_dict.get('month')
        day = dt_dict.get('day')
        hours = dt_dict.get('hours', 0)
        minutes = dt_dict.get('minutes', 0)
        if year and month and day:
            time_str = format_time((hours, minutes))
            return f"{year}-{month:02d}-{day:02d} {time_str}"
    return "N/A"


def print_basic_panchanga(result: Dict[str, Any], settings=None):
    """Print basic panchanga output."""
    print(header("PANCHANGA"))
    
    # Date info
    print(subheader("Date & Time"))
    print(f"{label('Gregorian:')} {value(result['gregorian_date'])}")
    print(f"{label('Weekday:')} {value(result['weekday'])}")
    
    # Show calculation time
    calc_time = result.get('calculation_time')
    calc_point = result.get('calculation_point', result.get('calculation_point_civil', 'sunrise'))
    if calc_time:
        print(f"{label('Calculation Time:')} {value(format_time(calc_time))} {dim(f'({calc_point})')}")
    
    jd = result['julian_day']
    ahar = result['ahargana']
    print(f"{label('Julian Day:')} {value(f'{jd:.2f}')}")
    print(f"{label('Ahargana:')} {value(f'{ahar:.2f}')}")
    
    # Sun & Moon
    print(subheader("Sun & Moon"))
    sunrise_tuple = result.get('sunrise')
    sunset_tuple = result.get('sunset')
    print(f"{label('Sunrise:')} {value(format_time(sunrise_tuple))}")
    print(f"{label('Sunset:')} {value(format_time(sunset_tuple))}")
    
    # Show Drik comparison if enabled
    if settings and settings.use_drik_sunrise_sunset:
        print(f"{dim('  (Using Drik Ephemeris for accurate sunrise/sunset)')}")
    
    sun_lon = result['sun_longitude']
    moon_lon = result['moon_longitude']
    print(f"{label('Sun Longitude:')} {value(f'{sun_lon:.4f}°')}")
    print(f"{label('Moon Longitude:')} {value(f'{moon_lon:.4f}°')}")
    
    # Tithi
    print(subheader("Tithi"))
    tithi_name = result.get('tithi_name', '')
    paksha_name = result.get('paksha_name', result.get('paksa', ''))
    tithi_day = result['tithi_day']
    print(f"{label('Tithi:')} {highlight(f'{tithi_name} ({tithi_day})')}")
    print(f"{label('Paksha:')} {value(paksha_name)}")
    tithi_frac = result.get('tithi_fraction', 0)
    print(f"{label('Tithi Fraction:')} {value(f'{tithi_frac:.4f}')}")
    if result.get('tithi_start_time'):
        print(f"{label('Tithi Start:')} {value(format_time(result['tithi_start_time']))}")
    if result.get('tithi_end_time'):
        print(f"{label('Tithi End:')} {value(format_time(result['tithi_end_time']))}")
    
    # Nakshatra
    print(subheader("Nakshatra"))
    print(f"{label('Nakshatra:')} {highlight(result['nakshatra'])}")
    if result.get('nakshatra_start_time'):
        print(f"{label('Start:')} {value(format_time(result['nakshatra_start_time']))}")
    if result.get('nakshatra_end_time'):
        print(f"{label('End:')} {value(format_time(result['nakshatra_end_time']))}")
    
    # Yoga
    print(subheader("Yoga"))
    print(f"{label('Yoga:')} {highlight(result['yoga'])}")
    if result.get('yoga_start_time'):
        print(f"{label('Start:')} {value(format_time(result['yoga_start_time']))}")
    if result.get('yoga_end_time'):
        print(f"{label('End:')} {value(format_time(result['yoga_end_time']))}")
    
    # Karana
    print(subheader("Karana"))
    print(f"{label('Karana:')} {highlight(result['karana'])}")
    if result.get('karana_start_time'):
        print(f"{label('Start:')} {value(format_time(result['karana_start_time']))}")
    if result.get('karana_end_time'):
        print(f"{label('End:')} {value(format_time(result['karana_end_time']))}")
    
    # Masa & Year
    print(subheader("Masa & Year"))
    masa_display = f"{result.get('adhimasa', '')}{result['masa']}"
    print(f"{label('Masa:')} {highlight(masa_display)}")
    print(f"{label('Masa Number:')} {value(result.get('masa_num', 'N/A'))}")
    print(f"{label('Year (Saka):')} {value(result.get('year_saka', 'N/A'))}")
    print(f"{label('Year (Kali):')} {value(result.get('year_kali', 'N/A'))}")
    
    # Planetary Positions (if available)
    planets_detailed = result.get('planets_detailed')
    if planets_detailed:
        print(subheader("Planetary Positions (Navagraha)"))
        
        # Display header
        print(f"  {'Planet':<16} {'Mean Lon':>12} {'True Lon':>12} {'Rasi':<14}")
        print("  " + "─" * 58)
        
        # Planet display order and names
        planet_display = [
            ('sun', 'Surya (Sun)'),
            ('moon', 'Chandra (Moon)'),
            ('mars', 'Mangala (Mars)'),
            ('mercury', 'Budha (Mercury)'),
            ('jupiter', 'Guru (Jupiter)'),
            ('venus', 'Sukra (Venus)'),
            ('saturn', 'Sani (Saturn)'),
            ('rahu', 'Rahu (N.Node)'),
            ('ketu', 'Ketu (S.Node)'),
        ]
        
        for planet_key, planet_name in planet_display:
            planet_data = planets_detailed.get(planet_key, {})
            mean_lon = planet_data.get('mean_longitude', planet_data.get('planet_mean', 0))
            true_lon = planet_data.get('true_longitude', 0)
            rasi = get_rasi_name(true_lon)
            
            # Format: short rasi name (just the Sanskrit name)
            rasi_short = rasi.split(' ')[0] if ' ' in rasi else rasi
            
            mean_str = f"{mean_lon:>9.2f}°"
            true_str = f"{true_lon:>9.2f}°"
            
            print(f"  {planet_name:<16} {mean_str:>12} {true_str:>12} {dim(rasi_short):<14}")
    
    # Settings
    if settings:
        print(subheader("Settings"))
        print(f"{label('System:')} {value(settings.selected_system)}")
        print(f"{label('Tradition:')} {value(settings.tradition)}")
        loc_str = f"{settings.loc_lat:.2f}°N, {settings.loc_lon:.2f}°E"
        print(f"{label('Location:')} {value(loc_str)}")
        print(f"{label('Language:')} {value(settings.language)}")
    
    print()


def get_rasi_name(longitude: float) -> str:
    """Get rasi (zodiac sign) name from longitude."""
    rasis = [
        'Mesha (Aries)', 'Vrshabha (Taurus)', 'Mithuna (Gemini)',
        'Karkata (Cancer)', 'Simha (Leo)', 'Kanya (Virgo)',
        'Tula (Libra)', 'Vrschika (Scorpio)', 'Dhanus (Sagittarius)',
        'Makara (Capricorn)', 'Kumbha (Aquarius)', 'Meena (Pisces)'
    ]
    index = int(longitude / 30) % 12
    return rasis[index]


def print_method_comparison(year: int, month: int, day: int, calculator):
    """Compare midnight-based vs sunrise-based calculations."""
    print(header("CALCULATION METHOD COMPARISON"))
    print(dim("  Midnight = Epoch consistent (Kali Yuga accurate)"))
    print(dim("  Sunrise  = Civil day ruling elements (traditional panchanga)"))
    print()
    
    # Calculate both
    astronomical = calculator.calculate_astronomical(year, month, day)
    civil_day = calculator.calculate_civil_day(year, month, day, include_timing=False)
    
    # Date & Basic Info
    print(subheader("Date & Astronomical Framework"))
    date_str = f'{year}-{month:02d}-{day:02d}'
    ahar_mid_str = f"{astronomical['ahar_midnight']:.6f}"
    sunrise_frac_str = f"{civil_day['sunrise_fraction']:.6f}"
    ahar_sr_str = f"{civil_day['ahar_sunrise']:.6f}"
    
    print(f"{label('Gregorian Date:')} {value(date_str)}")
    print(f"{label('Weekday:')} {value(astronomical['weekday'])}")
    print(f"{label('Julian Day:')} {value(astronomical['julian_day'])}")
    print(f"{label('Ahargana:')} {value(astronomical['ahargana'])}")
    print(f"{label('Ahar (midnight):')} {value(ahar_mid_str)}")
    print(f"{label('Sunrise:')} {value(format_time(astronomical['sunrise']))}")
    print(f"{label('Sunrise fraction:')} {value(sunrise_frac_str)} {dim('days after midnight')}")
    print(f"{label('Ahar (sunrise):')} {value(ahar_sr_str)}")
    
    # Years & Eras (always midnight-based for epoch consistency)
    print(subheader("Years & Eras (Midnight-based for Epoch Consistency)"))
    print(f"{label('Year Kali:')} {highlight(astronomical['year_kali'])}")
    print(f"{label('Year Saka:')} {value(astronomical['year_saka'])}")
    print(f"{label('Year Vikrama:')} {value(astronomical['year_vikrama'])}")
    print(f"{label('Jovian Year (North):')} {value(astronomical['jovian_year_north'])}")
    print(f"{label('Jovian Year (South):')} {value(astronomical['jovian_year_south'])}")
    
    # Solar Month (midnight-based)
    print(subheader("Solar Month (Midnight-based)"))
    print(f"{label('Saura Masa:')} {highlight(astronomical['saura_masa'])}")
    print(f"{label('Saura Masa Day:')} {value(astronomical['saura_masa_day'])}")
    
    # Planetary Positions
    print(subheader("Sun & Moon Positions"))
    print(f"{'':<26} {'MIDNIGHT':<20} {'SUNRISE':<20} {'DIFFERENCE':<15}")
    print("─" * 80)
    
    sun_mid = astronomical['sun_longitude']
    sun_sr = civil_day['sun_longitude']
    sun_diff = sun_sr - sun_mid
    print(f"{label('Sun Longitude:')} {value(f'{sun_mid:.4f}°'):<20} {value(f'{sun_sr:.4f}°'):<20} {highlight(f'{sun_diff:+.4f}°')}")
    
    moon_mid = astronomical['moon_longitude']
    moon_sr = civil_day['moon_longitude']
    moon_diff = moon_sr - moon_mid
    print(f"{label('Moon Longitude:')} {value(f'{moon_mid:.4f}°'):<20} {value(f'{moon_sr:.4f}°'):<20} {highlight(f'{moon_diff:+.4f}°')}")
    
    # Lunar Calendar Elements (compare both)
    print(subheader("Lunar Calendar Elements (Sunrise vs Midnight)"))
    print()
    
    print(f"{'Element':<20} {'MIDNIGHT':<25} {'SUNRISE':<25} {'Match?':<10}")
    print("─" * 80)
    
    # For midnight calculation of lunar elements, we need to get them
    # We can't directly use astronomical dict as it doesn't have lunar elements
    # So we note that midnight would give different results
    
    # Tithi
    tithi_sr = f"{civil_day['tithi_name']} ({civil_day['tithi_day']})"
    match_icon = "✓" if True else "✗"  # We know they should be at sunrise
    print(f"{'Tithi:':<20} {dim('(use sunrise)'):<25} {highlight(tithi_sr):<25} {value('→')}")
    
    # Paksha
    paksha_sr = civil_day['paksha_name']
    print(f"{'Paksha:':<20} {dim('(use sunrise)'):<25} {value(paksha_sr):<25} {value('→')}")
    
    # Masa
    masa_sr = f"{civil_day['adhimasa']}{civil_day['masa']}"
    print(f"{'Masa:':<20} {dim('(use sunrise)'):<25} {highlight(masa_sr):<25} {value('→')}")
    
    # Nakshatra
    naks_sr = civil_day['nakshatra']
    print(f"{'Nakshatra:':<20} {dim('(use sunrise)'):<25} {highlight(naks_sr):<25} {value('→')}")
    
    # Yoga
    yoga_sr = civil_day['yoga']
    print(f"{'Yoga:':<20} {dim('(use sunrise)'):<25} {value(yoga_sr):<25} {value('→')}")
    
    # Karana
    karana_sr = civil_day['karana']
    print(f"{'Karana:':<20} {dim('(use sunrise)'):<25} {value(karana_sr):<25} {value('→')}")
    
    print()
    print(dim("  Note: Lunar elements (Tithi, Nakshatra, etc.) are determined at sunrise"))
    print(dim("        for civil day panchanga. Midnight would give different values."))
    print()
    
    # Summary
    print(subheader("Summary"))
    print(f"  {highlight('MIDNIGHT-BASED')} → Use for:")
    print(f"    • Epoch calculations (Kali Yuga start verification)")
    print(f"    • Historical astronomical research")
    print(f"    • Year, Era, Solar month determination")
    print(f"    • Planetary position calculations")
    print()
    print(f"  {highlight('SUNRISE-BASED')} → Use for:")
    print(f"    • Civil day panchanga (daily calendar)")
    print(f"    • Tithi, Nakshatra, Yoga, Karana")
    print(f"    • Lunar month (Masa) and Paksha")
    print(f"    • Religious observance determination")
    print()


def print_sunrise_sunset_comparison(year: int, month: int, day: int, settings, astro):
    """Compare traditional Surya Siddhanta vs Drik ephemeris sunrise/sunset."""
    from panchanga.core.date_utils import DateUtils
    
    print(header("SUNRISE/SUNSET COMPARISON"))
    
    # Calculate traditional (Surya Siddhanta) sunrise/sunset
    julian_day = DateUtils.modern_date_to_julian_day(year, month, day)
    ahar = DateUtils.julian_day_to_ahargana(julian_day)
    ahar = ahar + 0.25 - settings.desantara
    eqtime = astro.get_daylight_equation(year, settings.loc_lat, ahar)
    
    trad_sunrise = astro.get_sunrise_time(eqtime)
    trad_sunset = astro.get_sunset_time(eqtime)
    
    print(subheader("Traditional (Surya Siddhanta)"))
    print(f"{label('Sunrise:')} {value(format_time(trad_sunrise))}")
    print(f"{label('Sunset:')} {value(format_time(trad_sunset))}")
    
    # Try to calculate Drik ephemeris sunrise/sunset
    try:
        from panchanga.core.drik_ephemeris import DrikEphemeris, SWISSEPH_AVAILABLE
        
        if SWISSEPH_AVAILABLE:
            print(subheader("Drik (Swiss Ephemeris)"))
            drik = DrikEphemeris()
            drik_date = datetime(year, month, day)
            drik_sunrise, drik_sunset = drik.calculate_sunrise_sunset(
                drik_date,
                settings.loc_lat,
                settings.loc_lon,
                0.0,
                5.5
            )
            
            print(f"{label('Sunrise:')} {value(format_time(drik_sunrise))}")
            print(f"{label('Sunset:')} {value(format_time(drik_sunset))}")
            
            # Calculate difference
            trad_sunrise_minutes = trad_sunrise[0] * 60 + trad_sunrise[1]
            drik_sunrise_minutes = drik_sunrise[0] * 60 + drik_sunrise[1]
            sunrise_diff = drik_sunrise_minutes - trad_sunrise_minutes
            
            trad_sunset_minutes = trad_sunset[0] * 60 + trad_sunset[1]
            drik_sunset_minutes = drik_sunset[0] * 60 + drik_sunset[1]
            sunset_diff = drik_sunset_minutes - trad_sunset_minutes
            
            print(subheader("Difference (Drik - Traditional)"))
            print(f"{label('Sunrise Difference:')} {value(f'{sunrise_diff:+.1f} minutes')}")
            print(f"{label('Sunset Difference:')} {value(f'{sunset_diff:+.1f} minutes')}")
            print(dim("\n  Note: Drik accounts for atmospheric refraction and topocentric corrections"))
        else:
            print(subheader("Drik (Swiss Ephemeris)"))
            print(dim("  Swiss Ephemeris not available. Install with: pip install pyswisseph"))
    except Exception as e:
        print(subheader("Drik (Swiss Ephemeris)"))
        print(dim(f"  Error calculating Drik: {e}"))


def print_detailed_debug(result: Dict[str, Any], service, year: int, month: int, day: int):
    """Print detailed debug information with intermediate calculations."""
    from panchanga.core.date_utils import DateUtils
    from panchanga.core.math_utils import MathUtils
    from panchanga.data.planetary import calculate_derived_constants
    
    calculator = service.calculator
    astro = calculator.astro
    rotations = astro.rotations
    planetary = astro.planetary
    settings = service.settings
    
    # Basic info first
    print_basic_panchanga(result, settings)
    
    # Compare traditional vs Drik sunrise/sunset
    print_sunrise_sunset_comparison(year, month, day, settings, astro)
    
    # Date calculations - USE FRAMEWORK METHOD
    print(header("DEBUG: DATE CALCULATIONS"))
    
    # Get all intermediate values from calculator (single source of truth)
    ahar_info = calculator.get_ahar_at_sunrise(year, month, day)
    
    julian_day = ahar_info['julian_day']
    ahar = ahar_info['ahar_raw']
    desantara = ahar_info['desantara']
    eqtime = ahar_info['eqtime']
    ahar_final = ahar_info['ahar_final']  # FRACTIONAL - matches calculator.py!
    
    print(f"{label('Julian Day:')} {value(f'{julian_day:.6f}')}")
    print(f"{label('Kali Epoch JD:')} {value(ahar_info['kali_epoch_jd'])}")
    print(f"{label('Ahargana (raw):')} {value(f'{ahar:.6f}')} {dim('days since Kali epoch (midnight)')}")
    print(f"{label('Desantara:')} {value(f'{desantara:.6f}')} {dim(f'= ({settings.loc_lon} - 82.5) / 360')}")
    print(f"{label('Ahargana (final):')} {highlight(f'{ahar_final:.6f}')} {dim('= ahar - desantara (used for calculations)')}")
    print(f"{label('Daylight Equation:')} {value(f'{eqtime:.6f}')} {dim('(for sunrise/sunset display only)')}")
    
    # Yuga constants
    print(header("DEBUG: YUGA CONSTANTS"))
    derived = calculate_derived_constants(rotations)
    
    print(f"{label('Sun Rotations:')} {value(rotations.sun)}")
    print(f"{label('Moon Rotations:')} {value(rotations.moon)}")
    print(f"{label('Yuga Civil Days:')} {value(astro.yuga_civil_days)}")
    print(f"{label('Yuga Synodic Month:')} {value(astro.yuga_synodic_month)}")
    print(f"{label('Yuga Adhimasa:')} {value(astro.yuga_adhimasa)}")
    print(f"{label('Yuga Tithi:')} {value(astro.yuga_tithi)}")
    print(f"{label('Yuga Ksayadina:')} {value(astro.yuga_ksayadina)}")
    
    # Planetary calculations
    print(header("DEBUG: PLANETARY POSITIONS"))
    
    # Sun
    print(subheader("Sun"))
    mean_sun = astro.get_mean_longitude(ahar_final, rotations.sun)
    sun_apogee = planetary.sun_apogee
    sun_manda_arg = mean_sun - sun_apogee
    sun_manda_corr = astro.get_manda_equation(sun_manda_arg, 'sun')
    true_sun = astro.get_true_solar_longitude(ahar_final)
    
    print(f"{label('Mean Sun:')} {value(f'{mean_sun:.6f}°')}")
    print(f"{label('Sun Apogee:')} {value(f'{sun_apogee:.6f}°')}")
    print(f"{label('Manda Argument:')} {value(f'{sun_manda_arg:.6f}°')}")
    print(f"{label('Manda Correction:')} {value(f'{sun_manda_corr:.6f}°')}")
    print(f"{label('True Sun:')} {highlight(f'{true_sun:.6f}°')} {dim(get_rasi_name(true_sun))}")
    
    # Moon
    print(subheader("Moon"))
    mean_moon = astro.get_mean_longitude(ahar_final, rotations.moon)
    mean_candrocca = astro.get_mean_longitude(ahar_final, rotations.candrocca)
    moon_apogee = mean_candrocca + 90
    moon_manda_arg = mean_moon - moon_apogee
    moon_manda_corr = astro.get_manda_equation(moon_manda_arg, 'moon')
    true_moon = astro.get_true_lunar_longitude(ahar_final)
    
    print(f"{label('Mean Moon:')} {value(f'{mean_moon:.6f}°')}")
    print(f"{label('Mean Candrocca:')} {value(f'{mean_candrocca:.6f}°')}")
    print(f"{label('Moon Apogee:')} {value(f'{moon_apogee:.6f}°')} {dim('= Candrocca + 90')}")
    print(f"{label('Manda Argument:')} {value(f'{moon_manda_arg:.6f}°')}")
    print(f"{label('Manda Correction:')} {value(f'{moon_manda_corr:.6f}°')}")
    print(f"{label('True Moon:')} {highlight(f'{true_moon:.6f}°')} {dim(get_rasi_name(true_moon))}")
    
    # Helper to print 4-step planet calculation
    def print_planet_4step(name: str, planet_key: str, is_inferior: bool = False):
        print(subheader(name))
        detailed = astro.get_true_planet_longitude_detailed(ahar_final, planet_key)
        
        # Basic info
        planet_mean = detailed['planet_mean']
        sighra_mean = detailed['sighra_mean']
        apogee_val = detailed['apogee']
        
        if is_inferior:
            print(f"{label('Mean Longitude:')} {value(f'{planet_mean:.6f}°')} {dim('(follows Sun)')}")
        else:
            print(f"{label('Mean Longitude:')} {value(f'{planet_mean:.6f}°')}")
        print(f"{label('Mean Sighra:')} {value(f'{sighra_mean:.6f}°')}")
        print(f"{label('Apogee:')} {value(f'{apogee_val:.6f}°')}")
        
        # 4-step corrections
        equ1 = detailed['equ1_sighra_half']
        equ2 = detailed['equ2_manda_half']
        equ3 = detailed['equ3_manda']
        equ4 = detailed['equ4_sighra']
        
        print(dim("    ─── 4-Step Surya Siddhanta Corrections ───"))
        print(f"{label('Step 1 (½ Sighra):')} {value(f'{equ1:.6f}°')}")
        print(f"{label('Step 2 (½ Manda):')} {value(f'{equ2:.6f}°')}")
        print(f"{label('Step 3 (Manda):')} {value(f'{equ3:.6f}°')}")
        print(f"{label('Step 4 (Sighra):')} {value(f'{equ4:.6f}°')}")
        
        # Final result
        true_long = detailed['true_longitude']
        print(f"{label('True Longitude:')} {highlight(f'{true_long:.6f}°')} {dim(get_rasi_name(true_long))}")
    
    # Mercury (Inferior Planet)
    print_planet_4step("Mercury (Budha)", 'mercury', is_inferior=True)
    
    # Venus (Inferior Planet)
    print_planet_4step("Venus (Sukra)", 'venus', is_inferior=True)
    
    # Mars (Superior Planet)
    print_planet_4step("Mars (Mangala)", 'mars')
    
    # Jupiter (Superior Planet)
    print_planet_4step("Jupiter (Guru)", 'jupiter')
    
    # Saturn (Superior Planet)
    print_planet_4step("Saturn (Sani)", 'saturn')
    
    # Rahu and Ketu (Lunar Nodes)
    print(subheader("Rahu (North Node)"))
    rahu_true = astro.get_rahu_longitude(ahar_final)
    print(f"{label('Mean/True Longitude:')} {highlight(f'{rahu_true:.6f}°')} {dim(get_rasi_name(rahu_true))} {dim('(retrograde)')}")
    
    print(subheader("Ketu (South Node)"))
    ketu_true = astro.get_ketu_longitude(ahar_final)
    print(f"{label('Mean/True Longitude:')} {highlight(f'{ketu_true:.6f}°')} {dim(get_rasi_name(ketu_true))} {dim('(180° from Rahu)')}")
    
    # All planet positions summary
    print(subheader("Planetary Positions Summary (Navagraha)"))
    all_positions = astro.get_all_planet_positions(ahar_final)
    planet_names_display = {
        'sun': 'Surya (Sun)',
        'moon': 'Chandra (Moon)',
        'mars': 'Mangala (Mars)',
        'mercury': 'Budha (Mercury)',
        'jupiter': 'Guru (Jupiter)',
        'venus': 'Sukra (Venus)',
        'saturn': 'Sani (Saturn)',
        'rahu': 'Rahu (N.Node)',
        'ketu': 'Ketu (S.Node)'
    }
    # Traditional order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
    planet_order = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
    print(f"{'Planet':<20} {'Longitude':>12} {'Rasi':<20}")
    print("─" * 55)
    for p in planet_order:
        lon = all_positions[p]
        rasi = get_rasi_name(lon)
        deg_in_rasi = lon % 30
        print(f"{planet_names_display[p]:<20} {lon:>10.4f}° {rasi:<20} ({deg_in_rasi:.2f}° in sign)")
    
    # Element calculations
    print(header("DEBUG: ELEMENT CALCULATIONS"))
    
    # Tithi
    print(subheader("Tithi Derivation"))
    tithi_float = astro.get_tithi(true_moon, true_sun)
    elongation = MathUtils.zero360(true_moon - true_sun)
    tithi_day = MathUtils.trunc(tithi_float) + 1
    tithi_fraction = MathUtils.frac(tithi_float)
    
    print(f"{label('Elongation (raw):')} {value(f'{true_moon - true_sun:.6f}°')}")
    print(f"{label('Elongation (norm):')} {value(f'{elongation:.6f}°')}")
    print(f"{label('Tithi Float:')} {value(f'{tithi_float:.6f}')} {dim(f'= {elongation:.4f}° / 12°')}")
    print(f"{label('Tithi Day (1-30):')} {highlight(tithi_day)}")
    print(f"{label('Tithi Fraction:')} {value(f'{tithi_fraction:.6f}')}")
    
    # Nakshatra
    print(subheader("Nakshatra Derivation"))
    nakshatra_float = true_moon * 27 / 360
    nakshatra_index = MathUtils.trunc(nakshatra_float)
    nakshatra_fraction = MathUtils.frac(nakshatra_float)
    
    print(f"{label('Moon Longitude:')} {value(f'{true_moon:.6f}°')}")
    print(f"{label('Nakshatra Float:')} {value(f'{nakshatra_float:.6f}')} {dim('= moon * 27 / 360')}")
    print(f"{label('Nakshatra Index:')} {highlight(nakshatra_index)} {dim('(0-26)')}")
    print(f"{label('Nakshatra Fraction:')} {value(f'{nakshatra_fraction:.6f}')}")
    print(f"{label('Degrees per Nakshatra:')} {value(f'{360/27:.4f}°')}")
    
    # Yoga
    print(subheader("Yoga Derivation"))
    yoga_sum = MathUtils.zero360(true_sun + true_moon)
    yoga_float = yoga_sum * 27 / 360
    yoga_index = MathUtils.trunc(yoga_float)
    
    print(f"{label('Sun + Moon (raw):')} {value(f'{true_sun + true_moon:.6f}°')}")
    print(f"{label('Sun + Moon (norm):')} {value(f'{yoga_sum:.6f}°')}")
    print(f"{label('Yoga Float:')} {value(f'{yoga_float:.6f}')} {dim('= sum * 27 / 360')}")
    print(f"{label('Yoga Index:')} {highlight(yoga_index)} {dim('(0-26)')}")
    
    # Karana
    print(subheader("Karana Derivation"))
    karana_float = 2 * tithi_float
    karana_index = MathUtils.trunc(karana_float)
    
    print(f"{label('Tithi Float:')} {value(f'{tithi_float:.6f}')}")
    print(f"{label('Karana Float:')} {value(f'{karana_float:.6f}')} {dim('= 2 * tithi')}")
    print(f"{label('Karana Index:')} {highlight(karana_index)} {dim('(0-59)')}")
    
    print()


def print_monthly_calendar(result: Dict[str, Any]):
    """Print monthly calendar in tabular format."""
    print(header(f"PANCHANGA - {result['month_name']} {result['year']}"))
    
    # Settings
    settings = result.get('settings', {})
    sys_name = settings.get('system', 'N/A')
    trad_name = settings.get('tradition', 'N/A')
    lang_name = settings.get('language', 'N/A')
    print(dim(f"System: {sys_name} | Tradition: {trad_name} | Language: {lang_name}"))
    print()
    
    # Table header
    print(f"{'Date':<12} {'Week':<6} {'Tithi':<22} {'Nakshatra':<16} {'Yoga':<14} {'Karana':<12}")
    print("─" * 90)
    
    for day_data in result['days']:
        date_str = day_data['date']
        weekday = day_data['weekday'][:3]
        tithi_str = f"{day_data.get('tithi_name', '')} ({day_data['paksha'][0]}{day_data['tithi_day']})"
        nakshatra = day_data['nakshatra'][:15] if len(day_data['nakshatra']) > 15 else day_data['nakshatra']
        yoga = day_data['yoga'][:13] if len(day_data['yoga']) > 13 else day_data['yoga']
        karana = day_data['karana'][:11] if len(day_data['karana']) > 11 else day_data['karana']
        
        print(f"{date_str:<12} {weekday:<6} {tithi_str:<22} {nakshatra:<16} {yoga:<14} {karana:<12}")
    
    print()


def interactive_mode():
    """Run in interactive mode for experimentation."""
    from panchanga.models.settings import PanchangaSettings, LOCATION_PRESETS
    from panchanga.services.panchanga_service import PanchangaService
    
    print(header("PANCHANGA INTERACTIVE MODE"))
    print(dim("Type 'help' for commands, 'quit' to exit\n"))
    
    # Default settings
    settings = PanchangaSettings()
    service = PanchangaService(settings=settings)
    
    while True:
        try:
            cmd = input(c("panchanga> ", Colors.CYAN)).strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            command = parts[0].lower()
            
            if command in ('quit', 'exit', 'q'):
                print(dim("Goodbye!"))
                break
            
            elif command == 'help':
                print("""
Commands:
  date YYYY MM DD     Calculate panchanga for a date
  today               Calculate for today
  month YYYY MM       Show monthly calendar
  compare YYYY MM DD  Compare midnight vs sunrise calculation methods
  set location NAME   Set location (ujjain, delhi, mumbai, etc.)
  set lat LON         Set latitude
  set lon LON         Set longitude
  set lang LANG       Set language (telugu, english)
  set system SYS      Set system (SuryaSiddhanta, InPancasiddhantika)
  set tradition TRAD  Set tradition (surya, drik, lunar)
  show settings       Show current settings
  locations           List available location presets
  debug YYYY MM DD    Show detailed debug output
  quit                Exit interactive mode
""")
            
            elif command == 'today':
                today = date.today()
                # Use new methods
                calculator = service.calculator
                astronomical = calculator.calculate_astronomical(today.year, today.month, today.day)
                civil_day = calculator.calculate_civil_day(today.year, today.month, today.day, include_timing=True)
                result = {**astronomical, **civil_day}
                print_basic_panchanga(result, service.settings)
            
            elif command == 'date' and len(parts) == 4:
                y, m, d = int(parts[1]), int(parts[2]), int(parts[3])
                # Use new methods
                calculator = service.calculator
                astronomical = calculator.calculate_astronomical(y, m, d)
                civil_day = calculator.calculate_civil_day(y, m, d, include_timing=True)
                result = {**astronomical, **civil_day}
                print_basic_panchanga(result, service.settings)
            
            elif command == 'debug' and len(parts) == 4:
                y, m, d = int(parts[1]), int(parts[2]), int(parts[3])
                # Use new methods
                calculator = service.calculator
                astronomical = calculator.calculate_astronomical(y, m, d)
                civil_day = calculator.calculate_civil_day(y, m, d, include_timing=True)
                result = {**astronomical, **civil_day}
                print_detailed_debug(result, service, y, m, d)
            
            elif command == 'compare' and len(parts) == 4:
                y, m, d = int(parts[1]), int(parts[2]), int(parts[3])
                print_method_comparison(y, m, d, service.calculator)
            
            elif command == 'month' and len(parts) == 3:
                y, m = int(parts[1]), int(parts[2])
                result = service.calculate_month(y, m)
                print_monthly_calendar(result)
            
            elif command == 'set' and len(parts) >= 3:
                setting = parts[1].lower()
                val = parts[2]
                
                if setting == 'location':
                    if val.lower() in LOCATION_PRESETS:
                        preset = LOCATION_PRESETS[val.lower()]
                        settings.loc_lat = preset.loc_lat
                        settings.loc_lon = preset.loc_lon
                        service = PanchangaService(settings=settings)
                        print(f"Location set to {val}: {settings.loc_lat}°N, {settings.loc_lon}°E")
                    else:
                        print(f"Unknown location. Available: {', '.join(LOCATION_PRESETS.keys())}")
                
                elif setting == 'lat':
                    settings.loc_lat = float(val)
                    service = PanchangaService(settings=settings)
                    print(f"Latitude set to {settings.loc_lat}°")
                
                elif setting == 'lon':
                    settings.loc_lon = float(val)
                    service = PanchangaService(settings=settings)
                    print(f"Longitude set to {settings.loc_lon}°")
                
                elif setting == 'lang':
                    settings.language = val
                    service = PanchangaService(settings=settings)
                    print(f"Language set to {settings.language}")
                
                elif setting == 'system':
                    settings.selected_system = val
                    service = PanchangaService(settings=settings)
                    print(f"System set to {settings.selected_system}")
                
                elif setting == 'tradition':
                    settings.tradition = val
                    service = PanchangaService(settings=settings)
                    print(f"Tradition set to {settings.tradition}")
                
                else:
                    print(f"Unknown setting: {setting}")
            
            elif command == 'show' and len(parts) == 2 and parts[1] == 'settings':
                print(f"""
Current Settings:
  System:    {settings.selected_system}
  Tradition: {settings.tradition}
  Location:  {settings.loc_lat}°N, {settings.loc_lon}°E
  Language:  {settings.language}
  Ayanamsa:  {settings.ayanamsa}
""")
            
            elif command == 'locations':
                print("\nAvailable location presets:")
                for name, preset in LOCATION_PRESETS.items():
                    print(f"  {name:<12} {preset.loc_lat:.2f}°N, {preset.loc_lon:.2f}°E")
                print()
            
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print(dim("\nGoodbye!"))
            break
        except Exception as e:
            print(c(f"Error: {e}", Colors.RED))


def main():
    parser = argparse.ArgumentParser(
        description="Console debug tool for Panchanga calculations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Today's panchanga (at sunrise)
  %(prog)s 2026 1 12                    # Specific date (at sunrise)
  %(prog)s 2026 1 12 --hour 5 --minute 30   # At 5:30 AM IST
  %(prog)s 2026 1 12 --hour 12              # At noon
  %(prog)s 2026 1 12 --detailed         # With debug info
  %(prog)s 2026 1 12 --compare          # Compare midnight vs sunrise
  %(prog)s --month 2026 1               # Monthly calendar
  %(prog)s --interactive                # Interactive mode
  %(prog)s 2024 4 9 --lat 17.4 --lon 78.5 --lang telugu
        """
    )
    
    parser.add_argument('year', type=int, nargs='?', help='Year (e.g., 2024)')
    parser.add_argument('month', type=int, nargs='?', help='Month (1-12)')
    parser.add_argument('day', type=int, nargs='?', help='Day of month')
    
    # Time options
    parser.add_argument('--hour', type=int, default=None,
                        help='Hour of day (0-23). Default: sunrise for civil, midnight for astronomical')
    parser.add_argument('--minute', type=int, default=None,
                        help='Minute (0-59). Default: 0')
    
    # Calculation options
    parser.add_argument('--drik', action='store_true',
                       help='Use Drik ephemeris (Swiss Ephemeris) for sunrise/sunset')
    
    parser.add_argument('--detailed', '-d', action='store_true',
                        help='Show detailed debug calculations')
    parser.add_argument('--compare', '-c', action='store_true',
                        help='Compare midnight vs sunrise calculation methods')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Start interactive mode')
    parser.add_argument('--month-view', '-m', nargs=2, type=int, metavar=('YEAR', 'MONTH'),
                        help='Show monthly calendar')
    
    # Location
    parser.add_argument('--lat', type=float, default=23.2,
                        help='Latitude (default: 23.2 - Ujjain)')
    parser.add_argument('--lon', type=float, default=82.5,
                        help='Longitude (default: 82.5 - IST meridian)')
    parser.add_argument('--location', type=str, choices=[
        'ujjain', 'delhi', 'mumbai', 'chennai', 'kolkata', 'bengaluru', 'hyderabad', 'varanasi'
    ], help='Use preset location')
    
    # Calculation settings
    parser.add_argument('--system', type=str, default='SuryaSiddhanta',
                        choices=['SuryaSiddhanta', 'InPancasiddhantika'],
                        help='Calculation system')
    parser.add_argument('--tradition', type=str, default='surya',
                        choices=['surya', 'drik', 'lunar'],
                        help='Calculation tradition')
    parser.add_argument('--lang', type=str, default='telugu',
                        choices=['english', 'telugu', 'sanskrit'],
                        help='Output language')
    
    # Output options
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    
    args = parser.parse_args()
    
    # Disable colors if requested
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Import panchanga modules
    try:
        from panchanga.models.settings import PanchangaSettings, LOCATION_PRESETS
        from panchanga.services.panchanga_service import PanchangaService
    except ImportError as e:
        print(c(f"Error importing panchanga modules: {e}", Colors.RED))
        print(dim("Make sure you're running from the packages/panchanga directory"))
        print(dim("or have the panchanga package installed."))
        sys.exit(1)
    
    # Build settings
    settings = PanchangaSettings()
    
    if args.location and args.location in LOCATION_PRESETS:
        preset = LOCATION_PRESETS[args.location]
        settings.loc_lat = preset.loc_lat
        settings.loc_lon = preset.loc_lon
    else:
        settings.loc_lat = args.lat
        settings.loc_lon = args.lon
    
    settings.selected_system = args.system
    settings.tradition = args.tradition
    settings.language = args.lang
    settings.use_drik_sunrise_sunset = args.drik

    settings.language = 'english'
    
    # Create service
    service = PanchangaService(settings=settings)
    
    # Monthly view
    if args.month_view:
        year, month = args.month_view
        result = service.calculate_month(year, month)
        if args.json:
            import json
            print(json.dumps(result, indent=2, default=str))
        else:
            print_monthly_calendar(result)
        return
    
    # Determine date
    if args.year and args.month and args.day:
        year, month, day = args.year, args.month, args.day
    else:
        today = date.today()
        year, month, day = today.year, today.month, today.day
    
    # Calculate
    try:
        if args.compare:
            # Use new comparison method
            calculator = service.calculator
            print_method_comparison(year, month, day, calculator)
        else:
            # Use new methods: combine astronomical (midnight) + civil day (sunrise or specified time)
            calculator = service.calculator
            
            # Determine time for calculations
            # If hour specified, use it; otherwise astronomical uses midnight, civil uses sunrise
            calc_hour = args.hour
            calc_minute = args.minute if args.minute is not None else 0
            
            # Get astronomical elements (at specified hour or midnight)
            if calc_hour is not None:
                astronomical = calculator.calculate_astronomical(year, month, day, hour=calc_hour, minute=calc_minute)
            else:
                astronomical = calculator.calculate_astronomical(year, month, day)  # Default: midnight
            
            # Get civil day elements (at specified hour or sunrise)
            # Always include timing for basic panchanga display (tithi start/end times)
            if calc_hour is not None:
                civil_day = calculator.calculate_civil_day(year, month, day, hour=calc_hour, minute=calc_minute, include_timing=True)
            else:
                civil_day = calculator.calculate_civil_day(year, month, day, include_timing=True)  # Default: sunrise
            
            # Combine results for backward compatibility with existing print functions
            # Merge astronomical (epoch-consistent) and civil_day (panchanga elements)
            result = {
                **astronomical,  # Start with astronomical
                **civil_day,     # Override with civil_day for panchanga elements
                # Keep both calculation points for reference
                'calculation_point_astronomical': astronomical.get('calculation_point', 'midnight'),
                'calculation_point_civil': civil_day.get('calculation_point', 'sunrise'),
            }
            
            if args.json:
                import json
                print(json.dumps(result, indent=2, default=str))
            elif args.detailed:
                print_detailed_debug(result, service, year, month, day)
            else:
                print_basic_panchanga(result, service.settings)
    
    except Exception as e:
        print(c(f"Error calculating panchanga: {e}", Colors.RED))
        import traceback
        if args.detailed:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
