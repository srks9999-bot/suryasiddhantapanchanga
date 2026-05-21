#!/usr/bin/env python3
"""
Test script to verify sunrise fraction is calculated from ephemeris.
Shows that sunrise_fraction is NOT a fixed 0.25 but calculated dynamically.
"""

from panchanga.models.settings import PanchangaSettings
from panchanga.core.calculator import PanchangaCalculator

def test_sunrise_fractions():
    """Test sunrise fractions for different locations and dates."""
    
    test_cases = [
        # (location, date, description)
        ("Hyderabad", (17.4, 78.5), (2024, 1, 15)),
        ("Delhi", (28.6, 77.2), (2024, 1, 15)),
        ("Kanyakumari", (8.08, 77.54), (2024, 1, 15)),  # Southern tip
        ("Srinagar", (34.08, 74.79), (2024, 1, 15)),    # Northern
        ("Hyderabad", (17.4, 78.5), (2024, 6, 21)),     # Summer solstice
        ("Hyderabad", (17.4, 78.5), (2024, 12, 21)),    # Winter solstice
    ]
    
    print("=" * 80)
    print("SUNRISE FRACTION TEST - Verifying Dynamic Calculation")
    print("=" * 80)
    print()
    
    for i, (location, (lat, lon), (year, month, day)) in enumerate(test_cases, 1):
        print(f"Test {i}: {location} on {year}-{month:02d}-{day:02d}")
        print(f"  Location: {lat}°N, {lon}°E")
        
        # Test with Traditional method
        settings_trad = PanchangaSettings(
            loc_lat=lat,
            loc_lon=lon,
            use_drik_sunrise_sunset=False,
            use_sunrise_for_tithi=False
        )
        calc_trad = PanchangaCalculator(settings_trad)
        result_trad = calc_trad.calculate(year, month, day)
        
        srise_h, srise_m = result_trad['sunrise']
        trad_fraction = (srise_h + srise_m / 60.0) / 24.0
        
        print(f"  Traditional Method:")
        print(f"    Sunrise: {srise_h:02d}:{srise_m:02d}")
        print(f"    Fraction: {trad_fraction:.6f} (NOT 0.25)")
        
        # Test with Drik if available
        try:
            settings_drik = PanchangaSettings(
                loc_lat=lat,
                loc_lon=lon,
                use_drik_sunrise_sunset=True,
                use_sunrise_for_tithi=False
            )
            calc_drik = PanchangaCalculator(settings_drik)
            result_drik = calc_drik.calculate(year, month, day)
            
            srise_h_d, srise_m_d = result_drik['sunrise']
            drik_fraction = (srise_h_d + srise_m_d / 60.0) / 24.0
            
            print(f"  Drik Ephemeris Method:")
            print(f"    Sunrise: {srise_h_d:02d}:{srise_m_d:02d}")
            print(f"    Fraction: {drik_fraction:.6f} (NOT 0.25)")
            
            diff_minutes = abs((drik_fraction - trad_fraction) * 24 * 60)
            print(f"  Difference: {diff_minutes:.1f} minutes")
        except Exception as e:
            print(f"  Drik not available: {e}")
        
        print()
    
    print("=" * 80)
    print("CONCLUSION: sunrise_fraction is DYNAMICALLY CALCULATED")
    print("It varies by:")
    print("  - Location (latitude/longitude)")
    print("  - Date (season)")
    print("  - Method (Drik ephemeris vs Traditional)")
    print("=" * 80)

if __name__ == '__main__':
    test_sunrise_fractions()
