#!/usr/bin/env python3
"""
Demonstration: Two Calculation Methods
Shows the difference between midnight-based and sunrise-based calculations.
"""

from panchanga.models.settings import PanchangaSettings
from panchanga.core.calculator import PanchangaCalculator

def demonstrate_two_methods():
    print("=" * 80)
    print("DEMONSTRATION: Midnight vs Sunrise Calculation Methods")
    print("=" * 80)
    print()
    print("Note: Drik ephemeris only works for years 1-9999 CE")
    print("      BCE dates automatically use traditional Surya Siddhanta method")
    print()
    
    # Setup
    settings = PanchangaSettings(
        loc_lat=17.4,  # Hyderabad
        loc_lon=78.5,
        use_drik_sunrise_sunset=True,  # Will auto-fallback to traditional for BCE dates
        language='english'
    )
    
    calc = PanchangaCalculator(settings)
    
    # Test dates
    test_dates = [
        (2024, 1, 15, "Modern Date (Winter)"),
        (2024, 6, 21, "Summer Solstice"),
        (-3100, 1, 23, "Kali Yuga Epoch"),
    ]
    
    for year, month, day, description in test_dates:
        print(f"\n{'─' * 80}")
        print(f"  DATE: {year}-{month:02d}-{day:02d} ({description})")
        print(f"{'─' * 80}\n")
        
        # Method 1: Astronomical (Midnight)
        astro = calc.calculate_astronomical(year, month, day)
        
        print("METHOD 1: ASTRONOMICAL (Midnight-based)")
        print("  Purpose: Epoch consistent, Kali Yuga accurate")
        print(f"  Calculation Point: {astro['calculation_point']}")
        print(f"  Ahargana (midnight): {astro['ahar_midnight']:.6f}")
        print()
        print(f"  Year Kali:     {astro['year_kali']}")
        print(f"  Year Saka:     {astro['year_saka']}")
        print(f"  Jovian Year:   {astro['jovian_year_north']}")
        print(f"  Weekday:       {astro['weekday']}")
        print(f"  Saura Masa:    {astro['saura_masa']} (day {astro['saura_masa_day']})")
        print()
        print(f"  Sun (midnight):  {astro['sun_longitude']:.4f}°")
        print(f"  Moon (midnight): {astro['moon_longitude']:.4f}°")
        print()
        print(f"  All Planets (midnight):")
        for planet, longitude in astro['planets'].items():
            print(f"    {planet.capitalize():10s}: {longitude:8.4f}°")
        print()
        
        # Method 2: Civil Day (Sunrise)
        try:
            civil = calc.calculate_civil_day(year, month, day, include_timing=False)
            
            sunrise_h, sunrise_m = civil['sunrise']
            print("METHOD 2: CIVIL DAY (Sunrise-based)")
            print("  Purpose: Traditional panchanga, ruling tithi")
            print(f"  Calculation Point: {civil['calculation_point']}")
            print(f"  Sunrise: {sunrise_h:02d}:{sunrise_m:02d}")
            print(f"  Sunrise fraction: {civil['sunrise_fraction']:.6f} days after midnight")
            print(f"  Ahargana (sunrise): {civil['ahar_sunrise']:.6f}")
            print()
            print(f"  Masa:        {civil['adhimasa']}{civil['masa']}")
            print(f"  Paksha:      {civil['paksha_name']}")
            print(f"  Tithi:       {civil['tithi_name']} ({civil['tithi_day']})")
            print(f"  Nakshatra:   {civil['nakshatra']}")
            print(f"  Yoga:        {civil['yoga']}")
            print(f"  Karana:      {civil['karana']}")
            print()
            print(f"  Sun (sunrise):   {civil['sun_longitude']:.4f}°")
            print(f"  Moon (sunrise):  {civil['moon_longitude']:.4f}°")
            print()
            
            # Show differences
            sun_diff = civil['sun_longitude'] - astro['sun_longitude']
            moon_diff = civil['moon_longitude'] - astro['moon_longitude']
            time_diff = civil['sunrise_fraction'] * 24  # hours
            
            print("DIFFERENCES (Sunrise - Midnight):")
            print(f"  Time difference: {time_diff:.2f} hours")
            print(f"  Sun moved:       {sun_diff:+.4f}°")
            print(f"  Moon moved:      {moon_diff:+.4f}°")
            print()
            
            print("INTERPRETATION:")
            if abs(moon_diff) > 6:  # Moon moves ~12°/day, so 6° is significant
                print("  ⚠️  Moon moved significantly - tithi may differ from midnight!")
            else:
                print("  ✓  Moon movement moderate - tithi likely same as midnight")
            print()
            
        except Exception as e:
            print(f"  Error calculating civil day: {e}")
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("MIDNIGHT METHOD (calculate_astronomical):")
    print("  ✓ Use for: Epoch verification, historical dates, year calculations")
    print("  ✓ Returns: Years, eras, solar month, planetary positions")
    print("  ✓ Accurate for: Kali Yuga epoch, astronomical research")
    print()
    print("SUNRISE METHOD (calculate_civil_day):")
    print("  ✓ Use for: Daily panchangas, religious observance")
    print("  ✓ Returns: Tithi, nakshatra, yoga, karana, lunar month")
    print("  ✓ Accurate for: Civil day ruling elements")
    print()
    print("Both methods are correct for their respective purposes!")
    print("=" * 80)

if __name__ == '__main__':
    demonstrate_two_methods()
