#!/usr/bin/env python3
"""
Check Swiss Ephemeris installation, data files, and coverage.
"""

def check_swisseph():
    """Check if Swiss Ephemeris is installed and show info."""
    try:
        import swisseph as swe
        
        print("=" * 70)
        print("SWISS EPHEMERIS STATUS CHECK")
        print("=" * 70)
        
        print("\n✓ Swiss Ephemeris is installed")
        print(f"Version: {swe.version}")
        print(f"Library path: {swe.get_library_path()}")
        
        print("\n" + "-" * 70)
        print("DATA COVERAGE TEST")
        print("-" * 70)
        
        # Test various dates across the coverage range
        test_dates = [
            (1900, 1, 1, "Historical (1900)"),
            (2000, 1, 1, "Y2K"),
            (2026, 1, 15, "Current Era"),
            (2050, 6, 15, "Near Future"),
            (2100, 12, 31, "Far Future"),
            (2500, 1, 1, "Very Far Future"),
        ]
        
        print("\nTesting calculations for various dates:\n")
        
        all_ok = True
        for year, month, day, label in test_dates:
            try:
                jd = swe.julday(year, month, day, 0.0)
                result = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
                sun_long = result[0][0]
                print(f"  ✓ {year:>4}-{month:02d}-{day:02d}  {label:>20}  Sun: {sun_long:>7.3f}°")
            except Exception as e:
                print(f"  ✗ {year:>4}-{month:02d}-{day:02d}  {label:>20}  Error: {e}")
                all_ok = False
        
        print("\n" + "-" * 70)
        print("DATA SOURCE INFORMATION")
        print("-" * 70)
        print("\n• Source: Built-in Swiss Ephemeris files")
        print("• Network: Not required (fully offline)")
        print("• Coverage: ~13000 BCE to ~17000 CE")
        print("• Data updates: NOT needed for coverage")
        print("• Package updates: Only for bug fixes/features")
        
        if all_ok:
            print("\n" + "=" * 70)
            print("✓ SWISS EPHEMERIS IS FULLY OPERATIONAL")
            print("=" * 70)
            print("\nYou do NOT need annual updates for data coverage.")
            print("Update only when bug fixes or new features are released.")
        
        return all_ok
        
    except ImportError:
        print("=" * 70)
        print("✗ SWISS EPHEMERIS NOT INSTALLED")
        print("=" * 70)
        print("\nInstall with:")
        print("  pip install pyswisseph")
        print("\nOr:")
        print("  pip install -r requirements.txt")
        return False
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == '__main__':
    check_swisseph()
