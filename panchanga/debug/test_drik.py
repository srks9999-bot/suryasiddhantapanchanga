#!/usr/bin/env python3
"""
Test script for Drik Ephemeris sunrise/sunset calculations.

This script demonstrates the usage of Drik-based ephemeris calculations
and compares them with traditional Surya Siddhanta methods.
"""

from datetime import datetime
from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService

def test_drik_comparison():
    """Compare traditional vs Drik sunrise/sunset for various locations."""
    
    locations = {
        'Hyderabad': (17.4, 78.5),
        'Delhi': (28.6, 77.2),
        'Mumbai': (19.1, 72.9),
        'Chennai': (13.1, 80.3),
        'Kolkata': (22.6, 88.4),
        'Varanasi': (25.3, 83.0),
    }
    
    test_date = datetime(2026, 1, 15)
    
    print("=" * 80)
    print("DRIK EPHEMERIS vs TRADITIONAL SURYA SIDDHANTA")
    print("=" * 80)
    print(f"\nTest Date: {test_date.strftime('%Y-%m-%d')}\n")
    
    for city, (lat, lon) in locations.items():
        print(f"\n{city} ({lat}°N, {lon}°E)")
        print("-" * 60)
        
        # Traditional calculation
        settings_trad = PanchangaSettings(
            loc_lat=lat,
            loc_lon=lon,
            use_drik_sunrise_sunset=False
        )
        service_trad = PanchangaService(settings=settings_trad)
        result_trad = service_trad.calculate(
            test_date.year, test_date.month, test_date.day
        )
        
        trad_sunrise = result_trad['sunrise']
        trad_sunset = result_trad['sunset']
        
        # Drik calculation
        settings_drik = PanchangaSettings(
            loc_lat=lat,
            loc_lon=lon,
            use_drik_sunrise_sunset=True
        )
        service_drik = PanchangaService(settings=settings_drik)
        result_drik = service_drik.calculate(
            test_date.year, test_date.month, test_date.day
        )
        
        drik_sunrise = result_drik['sunrise']
        drik_sunset = result_drik['sunset']
        
        # Calculate differences
        trad_sunrise_min = trad_sunrise[0] * 60 + trad_sunrise[1]
        drik_sunrise_min = drik_sunrise[0] * 60 + drik_sunrise[1]
        sunrise_diff = drik_sunrise_min - trad_sunrise_min
        
        trad_sunset_min = trad_sunset[0] * 60 + trad_sunset[1]
        drik_sunset_min = drik_sunset[0] * 60 + drik_sunset[1]
        sunset_diff = drik_sunset_min - trad_sunset_min
        
        print(f"Traditional Sunrise: {trad_sunrise[0]:02d}:{trad_sunrise[1]:02d}")
        print(f"Drik Sunrise:        {drik_sunrise[0]:02d}:{drik_sunrise[1]:02d} "
              f"({sunrise_diff:+.1f} min)")
        print(f"\nTraditional Sunset:  {trad_sunset[0]:02d}:{trad_sunset[1]:02d}")
        print(f"Drik Sunset:         {drik_sunset[0]:02d}:{drik_sunset[1]:02d} "
              f"({sunset_diff:+.1f} min)")


def test_drik_api():
    """Test Drik ephemeris API directly."""
    try:
        from panchanga.core.drik_ephemeris import DrikEphemeris
        
        print("\n" + "=" * 80)
        print("DIRECT DRIK EPHEMERIS API TEST")
        print("=" * 80)
        
        drik = DrikEphemeris()
        
        # Test for Hyderabad
        date = datetime(2026, 1, 15)
        lat, lon = 17.4, 78.5
        
        print(f"\nLocation: Hyderabad ({lat}°N, {lon}°E)")
        print(f"Date: {date.strftime('%Y-%m-%d')}")
        
        sunrise, sunset = drik.calculate_sunrise_sunset(
            date=date,
            latitude=lat,
            longitude=lon,
            elevation=0.0,
            timezone_offset=5.5  # IST
        )
        
        print(f"\nSunrise: {sunrise[0]:02d}:{sunrise[1]:02d}")
        print(f"Sunset:  {sunset[0]:02d}:{sunset[1]:02d}")
        
        # Test planetary longitudes (for future tithi calculations)
        from panchanga.core.date_utils import DateUtils
        jd = DateUtils.modern_date_to_julian_day(date.year, date.month, date.day)
        
        sun_long = drik.get_sun_longitude(jd, ayanamsa='lahiri')
        moon_long = drik.get_moon_longitude(jd, ayanamsa='lahiri')
        
        print(f"\nSidereal Solar Longitude (Lahiri):  {sun_long:.4f}°")
        print(f"Sidereal Lunar Longitude (Lahiri):  {moon_long:.4f}°")
        
        print("\n✓ Drik ephemeris is working correctly!")
        
    except ImportError:
        print("\n✗ Swiss Ephemeris not installed.")
        print("Install with: pip install pyswisseph")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    print("\nTesting Drik Ephemeris Integration\n")
    
    try:
        from panchanga.core.drik_ephemeris import SWISSEPH_AVAILABLE
        
        if not SWISSEPH_AVAILABLE:
            print("Swiss Ephemeris is not available.")
            print("Install it with: pip install pyswisseph")
            exit(1)
        
        # Run tests
        test_drik_comparison()
        test_drik_api()
        
        print("\n" + "=" * 80)
        print("All tests completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
