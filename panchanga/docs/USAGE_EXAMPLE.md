# Quick Start: Using Drik Ephemeris for Sunrise/Sunset

## Installation

```bash
cd packages/panchanga
pip install -r requirements.txt
```

This will install `pyswisseph` for accurate Drik-based calculations.

## Basic Usage

### 1. Calculate Panchanga with Drik Sunrise/Sunset

```python
from datetime import datetime
from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService

# Configure with Drik enabled
settings = PanchangaSettings(
    loc_lat=17.4,                    # Hyderabad latitude
    loc_lon=78.5,                    # Hyderabad longitude
    use_drik_sunrise_sunset=True     # Enable Drik for sunrise/sunset
)

# Create service and calculate
service = PanchangaService(settings=settings)
result = service.calculate(2026, 1, 15)

# Display results
print(f"Date: {result['gregorian_date']}")
print(f"Sunrise: {result['sunrise'][0]:02d}:{result['sunrise'][1]:02d}")
print(f"Sunset: {result['sunset'][0]:02d}:{result['sunset'][1]:02d}")
print(f"Tithi: {result['tithi_name']}")
print(f"Nakshatra: {result['nakshatra']}")
```

### 2. Compare Traditional vs Drik

```python
# Traditional calculation
settings_trad = PanchangaSettings(
    loc_lat=17.4,
    loc_lon=78.5,
    use_drik_sunrise_sunset=False  # Traditional
)
service_trad = PanchangaService(settings=settings_trad)
result_trad = service_trad.calculate(2026, 1, 15)

# Drik calculation
settings_drik = PanchangaSettings(
    loc_lat=17.4,
    loc_lon=78.5,
    use_drik_sunrise_sunset=True   # Drik
)
service_drik = PanchangaService(settings=settings_drik)
result_drik = service_drik.calculate(2026, 1, 15)

print("Traditional Sunrise:", result_trad['sunrise'])
print("Drik Sunrise:", result_drik['sunrise'])
```

### 3. Direct Drik API

```python
from datetime import datetime
from panchanga.core.drik_ephemeris import DrikEphemeris

drik = DrikEphemeris()

# Calculate sunrise/sunset
sunrise, sunset = drik.calculate_sunrise_sunset(
    date=datetime(2026, 1, 15),
    latitude=17.4,
    longitude=78.5,
    elevation=0.0,
    timezone_offset=5.5  # IST
)

print(f"Sunrise: {sunrise[0]:02d}:{sunrise[1]:02d}")
print(f"Sunset: {sunset[0]:02d}:{sunset[1]:02d}")

# Get planetary positions (for future tithi calculations)
from panchanga.core.date_utils import DateUtils
jd = DateUtils.modern_date_to_julian_day(2026, 1, 15)

sun_long = drik.get_sun_longitude(jd, ayanamsa='lahiri')
moon_long = drik.get_moon_longitude(jd, ayanamsa='lahiri')

print(f"Sun Longitude: {sun_long:.4f}°")
print(f"Moon Longitude: {moon_long:.4f}°")
```

## Console Testing

```bash
# Calculate with Drik
python console_debug.py 2026 1 15 --drik

# Show comparison in detailed mode
python console_debug.py 2026 1 15 --drik --detailed

# Test different locations
python console_debug.py 2026 1 15 --drik --location delhi
python console_debug.py 2026 1 15 --drik --lat 28.6 --lon 77.2

# Run comprehensive test
python test_drik.py
```

## Important Notes

### What Changes with Drik

- ✅ **Sunrise/Sunset Times**: More accurate (accounts for refraction, etc.)
- ❌ **Tithi Calculations**: Still use traditional Surya Siddhanta
- ❌ **Nakshatra**: Still use traditional Surya Siddhanta
- ❌ **Other Elements**: Still use traditional Surya Siddhanta

### Why This Design?

The Drik integration is **only for reporting sunrise/sunset** at this stage:

1. **Accuracy**: Users get accurate civil sunrise/sunset times
2. **Consistency**: Traditional calculations remain unchanged for ritual timing
3. **Flexibility**: Can be enabled/disabled per calculation
4. **Future-Ready**: Easy to extend to tithi calculations later

### Future Extensions

When you're ready to use Drik for tithi calculations:

```python
# This is for future use - not yet implemented
from panchanga.core.drik_ephemeris import DrikEphemeris

drik = DrikEphemeris()

# Calculate precise tithi at a given time
jd = DateUtils.modern_date_to_julian_day(2026, 1, 15)
sun_long = drik.get_sun_longitude(jd, ayanamsa='lahiri')
moon_long = drik.get_moon_longitude(jd, ayanamsa='lahiri')

# Tithi = (Moon - Sun) / 12
elongation = (moon_long - sun_long) % 360
tithi = elongation / 12
print(f"Tithi (Drik): {tithi:.4f}")
```

## See Also

- [DRIK_INTEGRATION.md](./DRIK_INTEGRATION.md) - Full documentation
- [test_drik.py](./test_drik.py) - Test and comparison script
- [console_debug.py](./console_debug.py) - Interactive debugging tool
