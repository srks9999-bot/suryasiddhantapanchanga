#!/usr/bin/env python3
"""
Drik Ephemeris Debug Tool for Historical Dates

This standalone script helps understand planetary positions using Swiss Ephemeris
for historical dates, particularly the Kali Yuga epoch (3101 BC - Jan 23).

Usage:
    python3 console_drik_debug.py                    # Default: Kali Yuga epoch
    python3 console_drik_debug.py -3100 1 23         # Specific historical date
    python3 console_drik_debug.py 2026 1 15          # Modern date
    python3 console_drik_debug.py --compare -3100 1 23  # Compare Drik vs Traditional

Features:
    - Swiss Ephemeris planetary positions
    - Traditional Surya Siddhanta positions (for comparison)
    - Sunrise/sunset times
    - Sidereal and tropical longitudes
    - Multiple ayanamsa systems
    - Zodiac signs and nakshatras
"""

import sys
import argparse
from datetime import datetime
from typing import Tuple, Dict, Optional, List

# ANSI color codes
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

def color(text: str, color_code: str) -> str:
    """Colorize text."""
    return f"{color_code}{text}{Colors.END}"

def header(text: str) -> str:
    return color(f"\n{'═' * 80}\n  {text}\n{'═' * 80}", Colors.BOLD + Colors.CYAN)

def subheader(text: str) -> str:
    return color(f"\n┌─ {text} {'─' * (75 - len(text))}┐", Colors.YELLOW)

def label(text: str, width: int = 30) -> str:
    return color(f"{text:>{width}}", Colors.DIM)

def value(text: str) -> str:
    return color(str(text), Colors.GREEN)

def highlight(text: str) -> str:
    return color(str(text), Colors.BOLD + Colors.YELLOW)

def dim(text: str) -> str:
    return color(str(text), Colors.DIM)

def error(text: str) -> str:
    return color(str(text), Colors.RED)


# ============================================================================
# SWISS EPHEMERIS (DRIK) FUNCTIONS
# ============================================================================

def check_swisseph_available() -> bool:
    """Check if Swiss Ephemeris is available."""
    try:
        import swisseph as swe
        return True
    except ImportError:
        return False


def get_drik_planetary_positions(
    year: int,
    month: int,
    day: int,
    hour: float = 0.0,
    ayanamsa: str = 'lahiri'
) -> Dict[str, Dict[str, float]]:
    """
    Get planetary positions using Swiss Ephemeris (Drik method).
    
    Args:
        year: Year (negative for BCE, e.g., -3100 for 3101 BC)
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-24, decimal)
        ayanamsa: Ayanamsa system ('lahiri', 'raman', 'krishnamurti', 'none')
    
    Returns:
        Dictionary with planetary positions
    """
    import swisseph as swe
    import os
    
    # Set ephemeris path to use downloaded Swiss Ephemeris files
    # These files support historical dates back to ~13000 BCE
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eph_path = os.path.join(script_dir, 'eph_data')
    
    if os.path.exists(eph_path):
        swe.set_ephe_path(eph_path)
    else:
        # Fallback to current directory or None
        swe.set_ephe_path(None)
    
    # Convert to Julian Day
    jd = swe.julday(year, month, day, hour)
    
    # Set ayanamsa
    ayanamsa_map = {
        'lahiri': swe.SIDM_LAHIRI,
        'raman': swe.SIDM_RAMAN,
        'krishnamurti': swe.SIDM_KRISHNAMURTI,
        'fagan_bradley': swe.SIDM_FAGAN_BRADLEY,
    }
    
    if ayanamsa.lower() != 'none':
        ayanamsa_id = ayanamsa_map.get(ayanamsa.lower(), swe.SIDM_LAHIRI)
        swe.set_sid_mode(ayanamsa_id)
        ayanamsa_value = swe.get_ayanamsa_ut(jd)
    else:
        ayanamsa_value = 0.0
    
    # Calculate positions for all planets
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,  # Mean North Node
    }
    
    positions = {}
    
    # Use FLG_SWIEPH to use Swiss Ephemeris data files
    # This supports historical dates back to ~13000 BCE
    calc_flag = swe.FLG_SWIEPH  # Use Swiss Ephemeris files
    
    for name, planet_id in planets.items():
        try:
            result = swe.calc_ut(jd, planet_id, calc_flag)
            tropical_long = result[0][0]
            sidereal_long = (tropical_long - ayanamsa_value) % 360
            
            # Calculate latitude and distance
            latitude = result[0][1]
            distance = result[0][2]
            speed = result[0][3]
            
            positions[name] = {
                'tropical': tropical_long,
                'sidereal': sidereal_long,
                'latitude': latitude,
                'distance': distance,
                'speed': speed,
                'retrograde': speed < 0
            }
        except Exception as e:
            positions[name] = {
                'error': str(e)
            }
    
    # Ketu is 180° opposite to Rahu
    if 'Rahu' in positions and 'error' not in positions['Rahu']:
        rahu = positions['Rahu']
        positions['Ketu'] = {
            'tropical': (rahu['tropical'] + 180) % 360,
            'sidereal': (rahu['sidereal'] + 180) % 360,
            'latitude': -rahu['latitude'],
            'distance': rahu['distance'],
            'speed': rahu['speed'],
            'retrograde': True
        }
    
    return {
        'julian_day': jd,
        'ayanamsa': ayanamsa_value,
        'positions': positions
    }


def get_drik_sunrise_sunset(
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float = 0.0
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Calculate sunrise and sunset using Swiss Ephemeris.
    
    Args:
        year: Year (negative for BCE)
        month: Month (1-12)
        day: Day (1-31)
        latitude: Geographic latitude in degrees
        longitude: Geographic longitude in degrees
        timezone_offset: Timezone offset in hours from UTC
    
    Returns:
        ((sunrise_hour, sunrise_minute), (sunset_hour, sunset_minute))
    """
    import swisseph as swe
    import os
    
    # Set ephemeris path to use downloaded Swiss Ephemeris files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eph_path = os.path.join(script_dir, 'eph_data')
    
    if os.path.exists(eph_path):
        swe.set_ephe_path(eph_path)
    else:
        swe.set_ephe_path(None)
    
    # Set geographic location
    swe.set_topo(longitude, latitude, 0)
    
    # Get Julian Day at midnight
    jd = swe.julday(year, month, day, 0.0)
    
    # Use Swiss Ephemeris files for historical dates
    calc_flag = swe.FLG_SWIEPH | swe.FLG_TOPOCTR
    
    try:
        # Calculate sunrise
        result_rise = swe.rise_trans(
            jd,
            swe.SUN,
            '',
            calc_flag,
            swe.CALC_RISE,
            [longitude, latitude, 0],
            1013.25,
            15.0
        )
        
        # Calculate sunset
        result_set = swe.rise_trans(
            jd,
            swe.SUN,
            '',
            calc_flag,
            swe.CALC_SET,
            [longitude, latitude, 0],
            1013.25,
            15.0
        )
        
        # Convert JD to time
        def jd_to_time(jd_val):
            year, month, day, hour_dec = swe.revjul(jd_val)
            hour_dec += timezone_offset
            if hour_dec >= 24:
                hour_dec -= 24
            elif hour_dec < 0:
                hour_dec += 24
            hours = int(hour_dec)
            minutes = int((hour_dec - hours) * 60)
            return (hours, minutes)
        
        sunrise = jd_to_time(result_rise[1])
        sunset = jd_to_time(result_set[1])
        
        return sunrise, sunset
        
    except Exception as e:
        return (0, 0), (0, 0)


# ============================================================================
# TRADITIONAL SURYA SIDDHANTA FUNCTIONS
# ============================================================================

def get_traditional_positions(
    year: int,
    month: int,
    day: int
) -> Optional[Dict]:
    """
    Get planetary positions using traditional Surya Siddhanta method.
    
    Returns None if panchanga modules are not available.
    """
    try:
        from panchanga.models.settings import PanchangaSettings
        from panchanga.services.panchanga_service import PanchangaService
        
        # For BCE dates, we need to handle them carefully
        # Traditional panchanga may not support BCE dates directly
        if year < 1:
            return None
        
        settings = PanchangaSettings()
        service = PanchangaService(settings=settings)
        result = service.calculate(year, month, day)
        
        return result
        
    except Exception as e:
        return None


# ============================================================================
# FORMATTING FUNCTIONS
# ============================================================================

def format_longitude(longitude: float) -> str:
    """Format longitude as sign + degrees."""
    signs = [
        'Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
        'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis'
    ]
    sign_num = int(longitude / 30) % 12
    deg_in_sign = longitude % 30
    return f"{signs[sign_num]} {deg_in_sign:>6.2f}°"


def format_longitude_detailed(longitude: float) -> str:
    """Format longitude as sign degrees:minutes:seconds."""
    signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    sign_num = int(longitude / 30) % 12
    deg_in_sign = longitude % 30
    degrees = int(deg_in_sign)
    minutes_dec = (deg_in_sign - degrees) * 60
    minutes = int(minutes_dec)
    seconds = int((minutes_dec - minutes) * 60)
    
    return f"{signs[sign_num]:>12} {degrees:>2}° {minutes:>2}' {seconds:>2}\""


def get_nakshatra(longitude: float) -> str:
    """Get nakshatra name from longitude."""
    nakshatras = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]
    nakshatra_num = int(longitude / (360/27)) % 27
    return nakshatras[nakshatra_num]


def format_time(time_tuple: Tuple[int, int]) -> str:
    """Format time tuple to readable string."""
    hours, minutes = time_tuple
    if hours == 0:
        return f"12:{minutes:02d} AM"
    elif hours < 12:
        return f"{hours}:{minutes:02d} AM"
    elif hours == 12:
        return f"12:{minutes:02d} PM"
    else:
        return f"{hours - 12}:{minutes:02d} PM"


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_date_info(year: int, month: int, day: int):
    """Display date information."""
    print(header("DATE INFORMATION"))
    
    # Handle BCE dates
    if year < 0:
        year_display = f"{abs(year) + 1} BC"
        year_astro = year
        print(f"\n{label('Gregorian Date:')} {value(f'{year_display}, {month:02d}-{day:02d}')}")
        print(f"{label('Astronomical Year:')} {value(year_astro)}")
        print(f"{dim('  Note: Historical year ' + str(abs(year) + 1) + ' BC = astronomical year ' + str(year))}")
        print(f"{dim('  Formula: astronomical_year = -(historical_bc_year - 1)')}")
    else:
        year_display = f"{year} AD"
        year_astro = year
        print(f"\n{label('Gregorian Date:')} {value(f'{year_display}, {month:02d}-{day:02d}')}")
        print(f"{label('Year:')} {value(year_astro)}")
    
    # Special dates
    if year == -3100 and month == 1 and day == 23:
        print(f"\n{highlight('⭐ SPECIAL DATE: Kali Yuga Epoch (Traditional Start)')}")
        print(f"{dim('This is the traditional beginning of Kali Yuga in Hindu astronomy')}")


def display_drik_positions(drik_data: Dict, ayanamsa: str = 'lahiri'):
    """Display Drik (Swiss Ephemeris) planetary positions."""
    print(header(f"DRIK EPHEMERIS PLANETARY POSITIONS ({ayanamsa.upper()})"))
    
    jd_val = drik_data['julian_day']
    ayan_val = drik_data['ayanamsa']
    print(f"\n{label('Julian Day:')} {value(f'{jd_val:.6f}')}")
    print(f"{label('Ayanamsa Value:')} {value(f'{ayan_val:.4f}°')}")
    
    positions = drik_data['positions']
    
    # Display each planet
    for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']:
        if planet_name not in positions:
            continue
            
        planet = positions[planet_name]
        
        if 'error' in planet:
            print(subheader(planet_name))
            err_msg = planet['error']
            print(f"{error(f'Error: {err_msg}')}")
            continue
        
        print(subheader(planet_name))
        
        # Tropical longitude
        trop_long = planet['tropical']
        print(f"{label('Tropical Longitude:')} {value(f'{trop_long:.4f}°')} "
              f"{dim(f'= {format_longitude(trop_long)}')}")
        
        # Sidereal longitude
        sid_long = planet['sidereal']
        print(f"{label('Sidereal Longitude:')} {value(f'{sid_long:.4f}°')} "
              f"{dim(f'= {format_longitude(sid_long)}')}")
        
        # Detailed position
        print(f"{label('Zodiac Position:')} {value(format_longitude_detailed(sid_long))}")
        
        # Nakshatra (for Moon)
        if planet_name == 'Moon':
            nakshatra = get_nakshatra(planet['sidereal'])
            print(f"{label('Nakshatra:')} {highlight(nakshatra)}")
        
        # Additional info
        if 'latitude' in planet:
            lat = planet['latitude']
            print(f"{label('Latitude:')} {value(f'{lat:.4f}°')}")
        
        if 'speed' in planet:
            speed_val = planet['speed']
            retro = " (Retrograde)" if planet.get('retrograde', False) else ""
            print(f"{label('Speed:')} {value(f'{speed_val:.4f}°/day')}{dim(retro)}")


def display_sunrise_sunset(
    year: int, month: int, day: int,
    latitude: float, longitude: float,
    timezone_offset: float
):
    """Display sunrise and sunset times."""
    print(header("SUNRISE & SUNSET (DRIK)"))
    
    print(f"\n{label('Location:')} {value(f'{latitude}°N, {longitude}°E')}")
    print(f"{label('Timezone:')} {value(f'UTC{timezone_offset:+.1f}')}")
    
    sunrise, sunset = get_drik_sunrise_sunset(
        year, month, day, latitude, longitude, timezone_offset
    )
    
    print(f"\n{label('Sunrise:')} {highlight(format_time(sunrise))}")
    print(f"{label('Sunset:')} {highlight(format_time(sunset))}")
    
    # Calculate day length
    sunrise_min = sunrise[0] * 60 + sunrise[1]
    sunset_min = sunset[0] * 60 + sunset[1]
    day_length_min = sunset_min - sunrise_min
    if day_length_min < 0:
        day_length_min += 24 * 60
    
    hours = day_length_min // 60
    minutes = day_length_min % 60
    
    print(f"{label('Day Length:')} {value(f'{hours}h {minutes}m')}")


def display_comparison(drik_data: Dict, traditional_data: Optional[Dict]):
    """Display comparison between Drik and traditional methods."""
    if traditional_data is None:
        print(header("COMPARISON: DRIK vs TRADITIONAL"))
        print(f"\n{dim('Traditional calculations not available for this date.')}")
        print(f"{dim('(BCE dates or panchanga modules not installed)')}")
        return
    
    print(header("COMPARISON: DRIK vs TRADITIONAL SURYA SIDDHANTA"))
    
    print(subheader("Solar Longitude"))
    drik_sun = drik_data['positions']['Sun']['sidereal']
    trad_sun = traditional_data.get('sun_longitude', 0)
    diff_sun = drik_sun - trad_sun
    
    print(f"{label('Drik (Sidereal):')} {value(f'{drik_sun:.4f}°')} = {dim(format_longitude(drik_sun))}")
    print(f"{label('Traditional:')} {value(f'{trad_sun:.4f}°')} = {dim(format_longitude(trad_sun))}")
    print(f"{label('Difference:')} {value(f'{diff_sun:+.4f}°')}")
    
    print(subheader("Lunar Longitude"))
    drik_moon = drik_data['positions']['Moon']['sidereal']
    trad_moon = traditional_data.get('moon_longitude', 0)
    diff_moon = drik_moon - trad_moon
    
    print(f"{label('Drik (Sidereal):')} {value(f'{drik_moon:.4f}°')} = {dim(format_longitude(drik_moon))}")
    print(f"{label('Traditional:')} {value(f'{trad_moon:.4f}°')} = {dim(format_longitude(trad_moon))}")
    print(f"{label('Difference:')} {value(f'{diff_moon:+.4f}°')}")


def display_tithi_info(drik_data: Dict):
    """Display tithi calculation from Drik positions."""
    print(header("TITHI CALCULATION (FROM DRIK)"))
    
    sun = drik_data['positions']['Sun']['sidereal']
    moon = drik_data['positions']['Moon']['sidereal']
    
    elongation = (moon - sun) % 360
    tithi = elongation / 12
    tithi_day = int(tithi) + 1
    
    # Determine paksha
    if tithi_day <= 15:
        paksha = "Shukla Paksha"
    else:
        paksha = "Krishna Paksha"
        tithi_day -= 15
    
    # Tithi names
    tithi_names = [
        'Pratipad', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
        'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
        'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Purnima/Amavasya'
    ]
    
    tithi_name = tithi_names[tithi_day - 1] if tithi_day <= 15 else tithi_names[14]
    
    print(f"\n{label('Sun Longitude:')} {value(f'{sun:.4f}°')}")
    print(f"{label('Moon Longitude:')} {value(f'{moon:.4f}°')}")
    print(f"{label('Elongation:')} {value(f'{elongation:.4f}°')}")
    print(f"{label('Tithi (decimal):')} {value(f'{tithi:.4f}')}")
    print(f"\n{label('Tithi Day:')} {highlight(f'{tithi_day}')}")
    print(f"{label('Tithi Name:')} {highlight(tithi_name)}")
    print(f"{label('Paksha:')} {highlight(paksha)}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Drik Ephemeris Debug Tool for Historical Dates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Kali Yuga epoch (3101 BC Jan 23)
  %(prog)s -3100 1 23                # Same as above (astronomical year)
  %(prog)s 2026 1 15                 # Modern date
  %(prog)s --compare -3100 1 23      # Compare with traditional
  %(prog)s --ayanamsa raman -3100 1 23  # Use different ayanamsa

Note: For BCE dates, use negative astronomical year numbering:
  3101 BC = -3100 (astronomical)
  2 BC = -1
  1 BC = 0
  1 AD = 1
        """
    )
    
    parser.add_argument('year', type=int, nargs='?', default=-3100,
                       help='Year (negative for BCE, e.g., -3100 = 3101 BC)')
    parser.add_argument('month', type=int, nargs='?', default=1,
                       help='Month (1-12)')
    parser.add_argument('day', type=int, nargs='?', default=23,
                       help='Day (1-31)')
    
    parser.add_argument('--lat', type=float, default=23.2,
                       help='Latitude (default: 23.2 - Ujjain)')
    parser.add_argument('--lon', type=float, default=75.8,
                       help='Longitude (default: 75.8 - Ujjain)')
    parser.add_argument('--tz', type=float, default=5.5,
                       help='Timezone offset from UTC (default: 5.5 for IST)')
    
    parser.add_argument('--ayanamsa', type=str, default='lahiri',
                       choices=['lahiri', 'raman', 'krishnamurti', 'fagan_bradley', 'none'],
                       help='Ayanamsa system (default: lahiri)')
    
    parser.add_argument('--compare', action='store_true',
                       help='Compare with traditional Surya Siddhanta')
    
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    
    args = parser.parse_args()
    
    # Disable colors if requested
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # Check if Swiss Ephemeris is available
    if not check_swisseph_available():
        print(error("\n✗ Swiss Ephemeris not installed!"))
        print("\nInstall with:")
        print("  pip install pyswisseph")
        sys.exit(1)
    
    year, month, day = args.year, args.month, args.day
    
    # Display date information
    display_date_info(year, month, day)
    
    # Get Drik positions
    try:
        drik_data = get_drik_planetary_positions(
            year, month, day, hour=6.0, ayanamsa=args.ayanamsa
        )
        display_drik_positions(drik_data, args.ayanamsa)
    except Exception as e:
        print(error(f"\n✗ Error calculating Drik positions: {e}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display sunrise/sunset
    try:
        display_sunrise_sunset(year, month, day, args.lat, args.lon, args.tz)
    except Exception as e:
        print(error(f"\n✗ Error calculating sunrise/sunset: {e}"))
    
    # Display tithi calculation
    try:
        display_tithi_info(drik_data)
    except Exception as e:
        print(error(f"\n✗ Error calculating tithi: {e}"))
    
    # Comparison with traditional (if requested and available)
    if args.compare:
        traditional_data = get_traditional_positions(year, month, day)
        display_comparison(drik_data, traditional_data)
    
    print("\n" + "=" * 80)
    print(value("✓ Calculations complete!"))
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
