# Two Calculation Methods - Implementation Summary

## What Was Built

Two new methods in `PanchangaCalculator` that explicitly separate:
1. **Astronomical/Epoch calculations** (midnight baseline)
2. **Civil day determinations** (sunrise baseline)

## New Methods

### 1. `calculate_astronomical(year, month, day)`

**Calculation Point:** MIDNIGHT

**Returns:**
- Yuga, Year, Era (Kali, Saka, Vikrama, Jovian)
- Solar month (Saura Masa) and day
- Weekday (Vara)
- Date conversions (Julian Day, Ahargana)
- Planetary positions (all 9 grahas) at midnight
- Sun & Moon longitudes at midnight
- Sunrise/sunset times (for display only)

**Use for:**
- Kali Yuga epoch verification
- Historical astronomical research
- Comparing with Surya Siddhanta reference values

### 2. `calculate_civil_day(year, month, day, include_timing=True)`

**Calculation Point:** SUNRISE

**Returns:**
- Lunar month (Masa) and Paksha
- Tithi with start/end times
- Nakshatra with start/end times
- Yoga with start/end times
- Karana with start/end times
- Sun & Moon longitudes at sunrise

**Use for:**
- Daily panchanga calendars
- Religious observance determination
- Traditional panchanga practice

## Console Debug Tool Updates

### New Command Line Option

```bash
# Compare both methods
python console_debug.py 2024 1 15 --compare

# With Drik ephemeris
python console_debug.py 2024 1 15 --compare --drik

# For Kali Yuga epoch
python console_debug.py -3100 1 23 --compare
```

### Interactive Mode

```bash
python console_debug.py --interactive

panchanga> compare 2024 1 15
panchanga> compare -3100 1 23
```

### New Function

`print_method_comparison(year, month, day, calculator)` - Shows side-by-side comparison of both methods

## Example Usage

### Astronomical Calculations (Midnight)

```python
from panchanga.core.calculator import PanchangaCalculator
from panchanga.models.settings import PanchangaSettings

settings = PanchangaSettings(loc_lat=23.2, loc_lon=75.8)
calc = PanchangaCalculator(settings)

# Verify Kali Yuga epoch
astro = calc.calculate_astronomical(-3100, 1, 23)
print(f"Year Kali: {astro['year_kali']}")
print(f"Saura Masa: {astro['saura_masa']}")
print(f"Planetary positions: {astro['planets']}")
```

### Civil Day Panchanga (Sunrise)

```python
# Daily panchanga
civil = calc.calculate_civil_day(2024, 1, 15)
print(f"Tithi: {civil['tithi_name']}")
print(f"Nakshatra: {civil['nakshatra']}")
print(f"Masa: {civil['masa']}")
```

### Combined Usage

```python
# Get complete panchanga data
astro = calc.calculate_astronomical(2024, 1, 15)
civil = calc.calculate_civil_day(2024, 1, 15)

# Astronomical framework
print(f"Year Kali: {astro['year_kali']}")
print(f"Saura Masa: {astro['saura_masa']}")

# Civil day elements
print(f"Tithi: {civil['tithi_name']}")
print(f"Nakshatra: {civil['nakshatra']}")

# Comparison
print(f"Sun moved: {civil['sun_longitude'] - astro['sun_longitude']:.4f}°")
```

## Testing

### Demo Script

```bash
cd packages/panchanga
python demo_two_methods.py
```

This demonstrates:
- Both methods for multiple dates
- Differences between midnight and sunrise calculations
- Appropriate use cases for each method

### Console Debug Comparisons

```bash
# Modern date
python console_debug.py 2024 1 15 --compare

# Historical date
python console_debug.py 1950 1 26 --compare

# Kali Yuga epoch
python console_debug.py -3100 1 23 --compare

# Different locations
python console_debug.py 2024 1 15 --compare --lat 28.6 --lon 77.2  # Delhi
python console_debug.py 2024 1 15 --compare --lat 8.08 --lon 77.54  # Kanyakumari
```

## Key Benefits

### 1. Explicit Separation
- No hidden configuration flags
- Clear method names indicate purpose
- No confusion about calculation point

### 2. Epoch Accuracy Preserved
- `calculate_astronomical()` uses midnight → Kali Yuga positions correct
- No risk of breaking epoch calculations

### 3. Traditional Practice Supported
- `calculate_civil_day()` uses sunrise → Matches printed panchangas
- Tithi, Nakshatra correctly determined at day start

### 4. Backward Compatibility
- Original `calculate()` method still works
- Existing code continues to function
- New code can use explicit methods

## Files Modified

1. **`panchanga/core/calculator.py`**
   - Added `calculate_astronomical()` method
   - Added `calculate_civil_day()` method

2. **`console_debug.py`**
   - Added `print_method_comparison()` function
   - Added `--compare` command line flag
   - Added `compare` command in interactive mode

## Files Created

1. **`MIDNIGHT_VS_SUNRISE_METHODS.md`** - Complete documentation
2. **`TWO_METHODS_SUMMARY.md`** - This file
3. **`demo_two_methods.py`** - Demonstration script

## Validation

To validate the implementation:

```bash
# Test modern date
python console_debug.py 2024 1 15 --compare

# Test Kali Yuga epoch (should show accurate year calculations)
python console_debug.py -3100 1 23 --compare

# Test summer vs winter (different sunrise times)
python console_debug.py 2024 1 15 --compare  # Winter
python console_debug.py 2024 6 21 --compare  # Summer

# Test different locations
python console_debug.py 2024 1 15 --compare --lat 8.08 --lon 77.54   # South
python console_debug.py 2024 1 15 --compare --lat 34.08 --lon 74.79  # North
```

## Design Rationale

The two-method approach recognizes that Indian astronomy has **two different baselines**:

1. **Midnight baseline** - For mathematical purity and epoch consistency (Surya Siddhanta mean longitudes)
2. **Sunrise baseline** - For observational practice and civil day determination (traditional panchanga)

These are **not contradictory** - they serve different purposes. Making them explicit methods eliminates confusion and makes the choice clear in the API.

## Next Steps

### For Users

1. Use `calculate_astronomical()` when verifying Kali Yuga epoch or doing historical research
2. Use `calculate_civil_day()` when creating daily panchangas
3. Use both together when you need complete panchanga data

### For Developers

Consider adding:
- More detailed planetary position analysis in astronomical method
- Ashtakavarga calculations (requires both methods)
- Dasha calculations (uses birth time, not just sunrise)
- Festival date calculations (may need both methods)

## Conclusion

This implementation provides a clean architectural separation that:
- ✅ Preserves Kali Yuga epoch accuracy
- ✅ Supports traditional panchanga practice
- ✅ Makes the choice explicit in the API
- ✅ Provides flexibility for different use cases
- ✅ Maintains backward compatibility

The distinction between astronomical (midnight) and civil day (sunrise) calculations is now **explicit, clear, and well-documented**.
