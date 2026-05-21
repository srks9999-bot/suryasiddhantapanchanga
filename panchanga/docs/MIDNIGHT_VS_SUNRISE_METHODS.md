# Midnight vs Sunrise Calculation Methods

## Overview

The panchanga calculator now provides **two separate methods** that explicitly separate astronomical/epoch calculations from civil day determinations:

1. **`calculate_astronomical()`** - Midnight-based (epoch consistent)
2. **`calculate_civil_day()`** - Sunrise-based (traditional panchanga)

This architectural separation makes it clear **which calculations should use which baseline**.

## Method 1: `calculate_astronomical(year, month, day)`

### Purpose
Calculate astronomical elements at **MIDNIGHT** for Kali Yuga epoch consistency.

### When to Use
- ✅ Verifying Kali Yuga epoch planetary positions
- ✅ Historical astronomical research
- ✅ Comparing with classical Surya Siddhanta reference values
- ✅ Mean longitude calculations
- ✅ Era/Year calculations

### What It Calculates (at Midnight)
- **Yuga, Year, Era calculations** (Kali, Saka, Vikrama, Jovian)
- **Solar month** (Saura Masa) and day
- **Weekday** (Vara)
- **Date conversions** (Julian Day, Ahargana)
- **Planetary positions** (all 9 grahas)
- **Sun & Moon longitudes** (at midnight)
- **Ayanamsa**
- **Sunrise/Sunset times** (for display, not used in calculations)

### Example Usage

```python
from panchanga.models.settings import PanchangaSettings
from panchanga.core.calculator import PanchangaCalculator

settings = PanchangaSettings(
    loc_lat=23.2,      # Ujjain
    loc_lon=75.8,
    language='english'
)

calc = PanchangaCalculator(settings)

# Calculate for Kali Yuga epoch
astronomical = calc.calculate_astronomical(-3100, 1, 23)

print(f"Year Kali: {astronomical['year_kali']}")
print(f"Sun longitude (midnight): {astronomical['sun_longitude']:.4f}°")
print(f"Moon longitude (midnight): {astronomical['moon_longitude']:.4f}°")
print(f"Saura Masa: {astronomical['saura_masa']}")
print(f"All planets: {astronomical['planets']}")
```

### Return Structure

```python
{
    'calculation_point': 'midnight',
    'gregorian_date': (year, month, day),
    'weekday': str,                      # Day of week
    'julian_day': int,
    'ahargana': int,
    'ahar_midnight': float,              # Ahargana at midnight
    'desantara': float,
    'ayanamsa': (degrees, minutes),
    'sunrise': (hour, minute),           # For display only
    'sunset': (hour, minute),
    'eqtime': float,
    'year_saka': int,
    'year_vikrama': int,
    'year_kali': int,                    # Epoch consistent!
    'jovian_year_north': str,
    'jovian_year_south': str,
    'saura_masa_num': int,               # Solar month number
    'saura_masa': str,                   # Solar month name
    'saura_masa_day': int,
    'sun_longitude': float,              # At midnight
    'moon_longitude': float,             # At midnight
    'planets': {                         # All at midnight
        'sun': float,
        'moon': float,
        'mars': float,
        'mercury': float,
        'jupiter': float,
        'venus': float,
        'saturn': float,
        'rahu': float,
        'ketu': float
    },
    'settings': {...}
}
```

## Method 2: `calculate_civil_day(year, month, day, include_timing=True)`

### Purpose
Calculate civil day elements at **SUNRISE** for traditional panchanga determination.

### When to Use
- ✅ Creating daily panchangas for religious observance
- ✅ Determining which tithi "rules" a specific day
- ✅ Lunar calendar elements (Masa, Tithi, Nakshatra)
- ✅ Matching printed panchanga behavior
- ✅ Observational astronomy practice

### What It Calculates (at Sunrise)
- **Lunar month** (Masa) and Paksha
- **Tithi** with start/end times
- **Nakshatra** with start/end times
- **Yoga** with start/end times
- **Karana** with start/end times
- **Sun & Moon longitudes** (at sunrise)
- **Sunrise fraction** (for debugging)

### Example Usage

```python
from panchanga.models.settings import PanchangaSettings
from panchanga.core.calculator import PanchangaCalculator

settings = PanchangaSettings(
    loc_lat=17.4,      # Hyderabad
    loc_lon=78.5,
    use_drik_sunrise_sunset=True,  # Use ephemeris for sunrise
    language='english'
)

calc = PanchangaCalculator(settings)

# Calculate civil day panchanga
civil_day = calc.calculate_civil_day(2024, 1, 15)

print(f"Masa: {civil_day['adhimasa']}{civil_day['masa']}")
print(f"Tithi: {civil_day['tithi_name']} ({civil_day['tithi_day']})")
print(f"Paksha: {civil_day['paksha_name']}")
print(f"Nakshatra: {civil_day['nakshatra']}")
print(f"Yoga: {civil_day['yoga']}")
print(f"Karana: {civil_day['karana']}")
print(f"Sun at sunrise: {civil_day['sun_longitude']:.4f}°")
print(f"Moon at sunrise: {civil_day['moon_longitude']:.4f}°")
```

### Return Structure

```python
{
    'calculation_point': 'sunrise',
    'gregorian_date': (year, month, day),
    'ahar_sunrise': float,               # Ahargana at sunrise
    'sunrise_fraction': float,           # Days after midnight
    'sunrise': (hour, minute),
    'sunset': (hour, minute),
    'masa_num': int,                     # Lunar month number
    'masa': str,                         # Lunar month name
    'adhimasa': str,                     # Intercalary prefix if any
    'paksa': str,                        # 'Suklapaksa' or 'Krsnapaksa'
    'paksha_name': str,                  # Localized name
    'sukla_krsna': str,
    'tithi_day': int,                    # 1-15 in each paksha
    'tithi_name': str,                   # Localized tithi name
    'tithi_fraction': float,             # Completion fraction
    'nakshatra': str,                    # Nakshatra name
    'karana': str,                       # Karana name
    'yoga': str,                         # Yoga name
    'tithi_start_time': (hour, minute),
    'tithi_end_time': (hour, minute),
    'tithi_start_datetime': {...},
    'tithi_end_datetime': {...},
    'nakshatra_start_time': (hour, minute),
    'nakshatra_end_time': (hour, minute),
    'nakshatra_start_datetime': {...},
    'nakshatra_end_datetime': {...},
    'yoga_start_time': (hour, minute),
    'yoga_end_time': (hour, minute),
    'yoga_start_datetime': {...},
    'yoga_end_datetime': {...},
    'karana_start_time': (hour, minute),
    'karana_end_time': (hour, minute),
    'karana_start_datetime': {...},
    'karana_end_datetime': {...},
    'sun_longitude': float,              # At sunrise
    'moon_longitude': float,             # At sunrise
    'settings': {...}
}
```

## Comparison Example

```python
from panchanga.core.calculator import PanchangaCalculator
from panchanga.models.settings import PanchangaSettings

settings = PanchangaSettings(loc_lat=17.4, loc_lon=78.5)
calc = PanchangaCalculator(settings)

year, month, day = 2024, 1, 15

# Method 1: Astronomical (midnight)
astro = calc.calculate_astronomical(year, month, day)
print(f"At MIDNIGHT:")
print(f"  Year Kali: {astro['year_kali']}")
print(f"  Saura Masa: {astro['saura_masa']}")
print(f"  Sun: {astro['sun_longitude']:.4f}°")
print(f"  Moon: {astro['moon_longitude']:.4f}°")

# Method 2: Civil Day (sunrise)
civil = calc.calculate_civil_day(year, month, day)
print(f"\nAt SUNRISE (6:47 AM):")
print(f"  Masa: {civil['masa']}")
print(f"  Tithi: {civil['tithi_name']}")
print(f"  Nakshatra: {civil['nakshatra']}")
print(f"  Sun: {civil['sun_longitude']:.4f}°")
print(f"  Moon: {civil['moon_longitude']:.4f}°")

print(f"\nDifference:")
print(f"  Sun moved: {civil['sun_longitude'] - astro['sun_longitude']:.4f}°")
print(f"  Moon moved: {civil['moon_longitude'] - astro['moon_longitude']:.4f}°")
```

## Testing with console_debug.py

### Compare Methods

```bash
cd packages/panchanga

# Compare midnight vs sunrise for today
python console_debug.py --compare

# Compare for specific date
python console_debug.py 2024 1 15 --compare

# Compare with Drik ephemeris
python console_debug.py 2024 1 15 --compare --drik

# Compare for Kali Yuga epoch
python console_debug.py -3100 1 23 --compare
```

### Interactive Mode

```bash
python console_debug.py --interactive

# Then use:
panchanga> compare 2024 1 15
panchanga> compare -3100 1 23    # Kali Yuga epoch
```

## Key Differences

| Aspect | Midnight Method | Sunrise Method |
|--------|----------------|----------------|
| **Calculation Point** | Midnight (00:00) | Sunrise (e.g., 6:47 AM) |
| **Ahargana** | Integer + desantara correction | Midnight + sunrise fraction |
| **Epoch Consistency** | ✅ Yes (Kali Yuga accurate) | ❌ No (shifted by ~0.25 days) |
| **Use Case** | Astronomical research | Daily panchanga |
| **Years/Eras** | ✅ Calculated | ❌ Not included |
| **Solar Month** | ✅ Calculated | ❌ Not included |
| **Lunar Month** | ❌ Not included | ✅ Calculated |
| **Tithi** | ❌ Not included | ✅ Calculated with timing |
| **Nakshatra** | ❌ Not included | ✅ Calculated with timing |
| **Planetary Positions** | ✅ All 9 grahas | ❌ Not included |
| **Matches Printed Panchanga** | ❌ No | ✅ Yes |

## Design Rationale

### Why Two Methods?

The fundamental issue is that there are **two different questions**:

1. **"What is the astronomical state at this date?"**
   - Answer requires midnight baseline for epoch consistency
   - Used for: Year calculations, era calculations, historical research
   - Method: `calculate_astronomical()`

2. **"Which tithi rules this civil day?"**
   - Answer requires sunrise observation point
   - Used for: Daily panchangas, religious observance, traditional practice
   - Method: `calculate_civil_day()`

### Historical Context

Traditional Indian astronomy uses:
- **Midnight baseline** for mean longitude calculations (Surya Siddhanta)
- **Sunrise observation** for civil day determination (traditional panchanga practice)

These are **not contradictory** - they serve different purposes. The two-method approach makes this distinction explicit in the API.

## Best Practices

### For Kali Yuga Epoch Verification

```python
# ALWAYS use midnight method
astronomical = calc.calculate_astronomical(-3100, 1, 23)
verify_planetary_positions(astronomical['planets'])
```

### For Daily Panchanga Printing

```python
# Use sunrise method for lunar elements
civil = calc.calculate_civil_day(2024, 1, 15)
print_panchanga_calendar(civil)

# But also get astronomical data for completeness
astro = calc.calculate_astronomical(2024, 1, 15)
add_year_info(astro['year_kali'], astro['year_saka'])
```

### For Complete Analysis

```python
# Use both methods together
astro = calc.calculate_astronomical(year, month, day)
civil = calc.calculate_civil_day(year, month, day)

# Combine data
complete_panchanga = {
    **astro,  # Years, eras, solar month, planetary positions
    **civil,  # Tithi, nakshatra, lunar month
    'sun_longitude_midnight': astro['sun_longitude'],
    'sun_longitude_sunrise': civil['sun_longitude'],
    'longitude_change': civil['sun_longitude'] - astro['sun_longitude']
}
```

## Migration from Old `calculate()` Method

The original `calculate()` method still exists for backward compatibility but now uses the configurable `use_sunrise_for_tithi` setting:

```python
# Old way (still works)
result = calc.calculate(year, month, day)
# Uses midnight by default (use_sunrise_for_tithi=False)

# New explicit way (recommended)
astro = calc.calculate_astronomical(year, month, day)
civil = calc.calculate_civil_day(year, month, day)
```

## Summary

The two-method approach provides:
- ✅ **Explicit separation** of concerns
- ✅ **Epoch accuracy** preserved (midnight method)
- ✅ **Traditional practice** supported (sunrise method)
- ✅ **Clear API** - no hidden configuration flags
- ✅ **Flexibility** - use either or both as needed

Use `calculate_astronomical()` for **scientific/historical work**.  
Use `calculate_civil_day()` for **panchanga calendars**.  
Use **both together** for complete panchanga data.
