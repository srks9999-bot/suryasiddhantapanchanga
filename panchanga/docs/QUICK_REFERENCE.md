# Drik Ephemeris - Quick Reference Card

## Installation
```bash
pip install pyswisseph
```

**Note**: Bundled data covers ~13000 BCE to ~17000 CE. No annual updates needed!

## Enable Drik in Settings
```python
settings = PanchangaSettings(
    loc_lat=17.4,
    loc_lon=78.5,
    use_drik_sunrise_sunset=True  # ← Enable here
)
```

## Console Commands
```bash
# Use Drik for sunrise/sunset
python3 console_debug.py 2026 1 15 --drik

# Show detailed comparison
python3 console_debug.py 2026 1 15 --drik --detailed

# Different location
python3 console_debug.py 2026 1 15 --drik --lat 28.6 --lon 77.2

# Run tests
python3 test_drik.py
```

## Direct API
```python
from datetime import datetime
from panchanga.core.drik_ephemeris import DrikEphemeris

drik = DrikEphemeris()
sunrise, sunset = drik.calculate_sunrise_sunset(
    date=datetime(2026, 1, 15),
    latitude=17.4,
    longitude=78.5,
    timezone_offset=5.5
)
```

## What Uses Drik?
- ✅ Sunrise time (when enabled)
- ✅ Sunset time (when enabled)
- ❌ Tithi (still traditional - for now)
- ❌ Nakshatra (still traditional)
- ❌ Other calculations (still traditional)

## Key Differences
- **Accuracy**: ±2-5 minutes more accurate
- **Accounts For**: Refraction, solar diameter, topocentric corrections
- **Use When**: You need accurate civil sunrise/sunset times
- **Traditional When**: You need consistency with traditional panchanga

## Files to Know
- `panchanga/core/drik_ephemeris.py` - Core implementation
- `panchanga/models/settings.py` - Settings (use_drik_sunrise_sunset)
- `DRIK_INTEGRATION.md` - Full documentation
- `test_drik.py` - Test script

## Check if Available
```python
from panchanga.core.drik_ephemeris import DrikEphemeris
if DrikEphemeris.is_available():
    print("Drik is ready!")
```

## Future Use: Tithi Calculations
```python
# Not yet implemented, but API is ready:
jd = DateUtils.modern_date_to_julian_day(2026, 1, 15)
sun = drik.get_sun_longitude(jd, ayanamsa='lahiri')
moon = drik.get_moon_longitude(jd, ayanamsa='lahiri')
tithi = ((moon - sun) % 360) / 12
```

## Supported Ayanamsas
- `'lahiri'` - Lahiri (default, widely used)
- `'raman'` - B.V. Raman
- `'krishnamurti'` - Krishnamurti
- `'fagan_bradley'` - Fagan-Bradley
- `'none'` - Tropical (no ayanamsa)

## Troubleshooting
```bash
# If pyswisseph not installed:
pip install pyswisseph

# Check installation & coverage:
python3 check_ephemeris.py

# Quick check:
python3 -c "import swisseph; print('OK')"
```

## Do I Need Annual Updates?
**No!** Data covers thousands of years. Update only for bug fixes.

## Documentation
- `DRIK_INTEGRATION.md` - Complete guide
- `USAGE_EXAMPLE.md` - Code examples
- `IMPLEMENTATION_SUMMARY.md` - Technical details
