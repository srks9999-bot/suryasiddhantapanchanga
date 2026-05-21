# Drik Ephemeris Integration for Sunrise/Sunset

## Overview

This integration adds high-accuracy sunrise/sunset calculations using the Swiss Ephemeris library (via `pyswisseph`). These calculations are based on the **Drik** (observational) method and provide more accurate times compared to traditional Surya Siddhanta calculations.

### Key Features

- **Accurate Sunrise/Sunset**: Uses modern ephemeris data with atmospheric refraction corrections
- **Topocentric Corrections**: Accounts for observer's geographic location
- **Configurable**: Can be enabled/disabled via settings
- **Separate from Astronomical Calculations**: Traditional Surya Siddhanta methods remain unchanged for other calculations
- **Future-Ready**: Includes methods for planetary longitudes that can be used for tithi calculations

## Installation

Install the Swiss Ephemeris library:

```bash
cd packages/panchanga
pip install pyswisseph
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### About Data Updates

**Important**: Swiss Ephemeris includes ephemeris data covering **~13000 BCE to ~17000 CE**. You do **NOT** need to update the package annually for data coverage. The bundled data is:

- ✅ **Pre-computed** for thousands of years
- ✅ **Offline** - no downloads or network required
- ✅ **Stable** - based on astronomical calculations, not observations
- ✅ **Complete** - covers all practical panchanga use cases

Update `pyswisseph` only for:
- Bug fixes in the calculation library
- New features
- Performance improvements
- Security patches

**Not** for ephemeris data updates (already complete)!

## Usage

### 1. Using PanchangaSettings

Enable Drik-based sunrise/sunset in your settings:

```python
from panchanga.models.settings import PanchangaSettings
from panchanga.services.panchanga_service import PanchangaService

# Create settings with Drik enabled
settings = PanchangaSettings(
    loc_lat=17.4,  # Hyderabad
    loc_lon=78.5,
    use_drik_sunrise_sunset=True  # Enable Drik ephemeris
)

service = PanchangaService(settings=settings)
result = service.calculate(2026, 1, 15)

print(f"Sunrise: {result['sunrise']}")  # Uses Drik ephemeris
print(f"Sunset: {result['sunset']}")    # Uses Drik ephemeris
```

### 2. Using Console Debug Tool

Test with the console debug tool:

```bash
# Use Drik for sunrise/sunset
python console_debug.py 2026 1 15 --drik

# Compare traditional vs Drik (shown in detailed mode)
python console_debug.py 2026 1 15 --drik --detailed

# Test with different location
python console_debug.py 2026 1 15 --drik --lat 28.6 --lon 77.2
```

### 3. Direct API Usage

Use the Drik ephemeris API directly:

```python
from datetime import datetime
from panchanga.core.drik_ephemeris import DrikEphemeris

drik = DrikEphemeris()

sunrise, sunset = drik.calculate_sunrise_sunset(
    date=datetime(2026, 1, 15),
    latitude=17.4,
    longitude=78.5,
    elevation=0.0,        # meters above sea level
    timezone_offset=5.5   # IST = UTC+5:30
)

print(f"Sunrise: {sunrise[0]:02d}:{sunrise[1]:02d}")
print(f"Sunset: {sunset[0]:02d}:{sunset[1]:02d}")
```

### 4. Planetary Longitudes (Future Use)

The Drik module also provides methods for calculating planetary longitudes:

```python
from panchanga.core.date_utils import DateUtils

# Calculate Julian Day
jd = DateUtils.modern_date_to_julian_day(2026, 1, 15)

# Get sidereal solar longitude (with Lahiri ayanamsa)
sun_long = drik.get_sun_longitude(jd, ayanamsa='lahiri')

# Get sidereal lunar longitude
moon_long = drik.get_moon_longitude(jd, ayanamsa='lahiri')

print(f"Sun: {sun_long:.4f}°")
print(f"Moon: {moon_long:.4f}°")
```

## Architecture

### Module Structure

```
panchanga/
├── core/
│   ├── astronomical.py          # Traditional Surya Siddhanta calculations
│   ├── drik_ephemeris.py        # NEW: Drik ephemeris calculations
│   ├── calculator.py            # Main calculator (integrates both)
│   └── ...
├── models/
│   └── settings.py              # UPDATED: Added use_drik_sunrise_sunset flag
└── services/
    └── panchanga_service.py     # Service layer
```

### Integration Points

1. **Settings**: `PanchangaSettings.use_drik_sunrise_sunset` boolean flag
2. **Calculator**: `PanchangaCalculator._calculate_drik_sunrise_sunset()` method
3. **Fallback**: If Drik calculation fails, falls back to traditional method
4. **Separation**: Drik is ONLY used for sunrise/sunset reporting; all other astronomical calculations remain unchanged

### Design Decisions

#### Why Separate from Traditional Calculations?

- **Preservation**: Traditional Surya Siddhanta methods remain intact for astronomical calculations (tithi, nakshatra, etc.)
- **Accuracy**: Drik provides more accurate sunrise/sunset times for user reporting
- **Flexibility**: Users can choose between traditional or modern methods
- **Future-Ready**: Easy to extend Drik usage to tithi calculations later

#### Why Swiss Ephemeris?

- **Industry Standard**: Used by professional astrology software worldwide
- **High Accuracy**: Based on JPL ephemeris data
- **Well-Maintained**: Active development and support
- **Comprehensive**: Supports all planets, nodes, and various ayanamsa systems

## Comparison: Traditional vs Drik

### Typical Differences

For Indian locations, the differences are typically:
- **Sunrise**: ±2-5 minutes
- **Sunset**: ±2-5 minutes

The exact difference depends on:
- Geographic location (latitude/longitude)
- Time of year (declination of Sun)
- Atmospheric conditions (refraction)

### What Drik Accounts For

1. **Atmospheric Refraction**: Light bending in Earth's atmosphere (~34 arcminutes at horizon)
2. **Solar Semidiameter**: Sun's visible disk size (~16 arcminutes)
3. **Topocentric Corrections**: Observer's exact position on Earth
4. **Precise Solar Position**: Modern ephemeris data (vs. mean positions)
5. **Elevation**: Height above sea level (configurable)

### When to Use Each Method

**Traditional Surya Siddhanta:**
- For consistency with traditional panchanga calculations
- For religious/ritual timing based on traditional methods
- For educational/research purposes
- For astronomical calculations (tithi, nakshatra, yoga, karana)

**Drik Ephemeris:**
- For accurate civil sunrise/sunset times
- For user-facing time reporting
- For modern astronomical accuracy
- For integration with civil calendars

## Testing

Run the test script to compare both methods:

```bash
python test_drik.py
```

This will:
1. Compare sunrise/sunset for major Indian cities
2. Test the Drik API directly
3. Show differences between methods

## API Reference

### DrikEphemeris Class

```python
class DrikEphemeris:
    """Drik-based ephemeris calculations using Swiss Ephemeris."""
    
    def calculate_sunrise_sunset(
        self,
        date: datetime,
        latitude: float,
        longitude: float,
        elevation: float = 0.0,
        timezone_offset: float = 0.0
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Calculate sunrise and sunset times.
        
        Returns:
            ((sunrise_hour, sunrise_minute), (sunset_hour, sunset_minute))
        """
    
    def get_sun_longitude(
        self,
        jd: float,
        ayanamsa: str = 'lahiri'
    ) -> float:
        """Get sidereal solar longitude."""
    
    def get_moon_longitude(
        self,
        jd: float,
        ayanamsa: str = 'lahiri'
    ) -> float:
        """Get sidereal lunar longitude."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if Swiss Ephemeris is installed."""
```

### Supported Ayanamsa Systems

- `lahiri`: Lahiri (Chitrapaksha) - Default, widely used in India
- `raman`: B.V. Raman
- `krishnamurti`: Krishnamurti
- `fagan_bradley`: Fagan-Bradley (Western)
- `none`: Tropical (no ayanamsa)

## Future Enhancements

### Planned Features

1. **Tithi Calculation**: Use Drik for precise tithi start/end times
2. **Nakshatra Timing**: Accurate nakshatra transition times
3. **Eclipse Calculations**: Solar and lunar eclipse predictions
4. **Graha Yuddha**: Planetary conjunctions and wars
5. **Elevation Support**: Make elevation configurable in settings
6. **Timezone Auto-Detection**: Automatic timezone from coordinates

### Migration Path to Full Drik

If you want to migrate to full Drik calculations:

1. Enable Drik sunrise/sunset (current implementation) ✓
2. Use Drik for tithi start/end times (future)
3. Use Drik for nakshatra timing (future)
4. Use Drik for all astronomical elements (future)
5. Keep traditional calculations as an option

## Troubleshooting

### Swiss Ephemeris Not Available

**Error**: `ImportError: No module named 'swisseph'`

**Solution**: Install pyswisseph:
```bash
pip install pyswisseph
```

**Verify installation**:
```bash
python3 check_ephemeris.py
```

### Do I Need to Update Annually?

**No!** The ephemeris data bundled with `pyswisseph` covers thousands of years:
- Coverage: ~13000 BCE to ~17000 CE
- No annual updates needed for data
- Update only for bug fixes or new features

**Check your coverage**:
```bash
python3 check_ephemeris.py  # Tests dates from 1900 to 2500+
```

### Calculation Errors

If Drik calculations fail, the system automatically falls back to traditional methods. Check the console for warning messages.

### Timezone Issues

Make sure to provide the correct timezone offset:
- IST: 5.5 (UTC+5:30)
- SGT: 8.0 (UTC+8:00)
- PST: -8.0 (UTC-8:00)

### Network/Offline Usage

Swiss Ephemeris works **completely offline**:
- ✅ No internet required
- ✅ No data downloads
- ✅ No external API calls
- ✅ All data bundled with package

## References

- [Swiss Ephemeris Documentation](https://www.astro.com/swisseph/)
- [PySwisseph on PyPI](https://pypi.org/project/pyswisseph/)
- [JPL Ephemeris](https://ssd.jpl.nasa.gov/planets/eph_export.html)
- Surya Siddhanta (traditional text)

## License Note

Swiss Ephemeris is dual-licensed:
- **Free**: For free software (GPL)
- **Commercial**: Requires license for proprietary software

See [Swiss Ephemeris Licensing](https://www.astro.com/swisseph/swephinfo_e.htm#_Toc505244798) for details.
