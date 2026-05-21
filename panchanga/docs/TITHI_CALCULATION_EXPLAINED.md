# Tithi Calculation Explained

## What is Tithi?

**Tithi** is a lunar day in the Hindu calendar system. Unlike solar days (which are based on Earth's rotation), tithis are based on the angular relationship between the Sun and Moon.

### Core Formula

```
Tithi = (Moon Longitude - Sun Longitude) / 12°
```

- There are **30 tithis** in a lunar month
- Each tithi spans **12°** of elongation (360° ÷ 30 = 12°)
- Tithis are numbered 1-15 for each paksha (fortnight)

### Paksha (Fortnight)

- **Shukla Paksha** (Bright Fortnight): Tithis 1-15 during waxing moon
- **Krishna Paksha** (Dark Fortnight): Tithis 1-15 during waning moon

## How Traditional Panchanga Calculates Tithi

### Step-by-Step Process

1. **Convert Date to Ahargana** (days since Kali Yuga epoch)
   ```
   Julian Day → Ahargana
   ```

2. **Apply Desantara Correction** (longitude-based time offset)
   ```
   Ahargana_corrected = Ahargana - (Longitude / 360)
   ```

3. **Find Sunrise Moment**
   - Option A: Use Drik Ephemeris (Swiss Ephemeris - very accurate)
   - Option B: Use Traditional Surya Siddhanta method
   
   ```
   # Sunrise time is CALCULATED (not hardcoded)
   # Example for 6:47 AM:
   Sunrise_fraction = (6 + 47/60) / 24 = 0.2826388...
   Ahargana_sunrise = Ahargana_midnight + Sunrise_fraction
   
   # This varies by location, date, and season!
   ```

4. **Calculate True Longitudes at Sunrise**
   
   **Sun's True Longitude:**
   ```
   Mean_Sun = 360 × frac(Sun_rotations × Ahargana / Yuga_days)
   Manda_correction = arcsin(circumference/360 × sin(Mean_Sun - Apogee))
   True_Sun = Mean_Sun - Manda_correction
   ```
   
   **Moon's True Longitude:**
   ```
   Mean_Moon = 360 × frac(Moon_rotations × Ahargana / Yuga_days)
   Moon_Apogee = Mean_Candrocca + 90°
   Manda_correction = arcsin(circumference/360 × sin(Mean_Moon - Moon_Apogee))
   True_Moon = Mean_Moon - Manda_correction
   ```

5. **Calculate Tithi**
   ```
   Elongation = (True_Moon - True_Sun) mod 360°
   Tithi_float = Elongation / 12°
   Tithi_day = floor(Tithi_float) + 1
   Tithi_fraction = Tithi_float - floor(Tithi_float)
   ```

6. **Determine Paksha**
   ```
   If Tithi_day > 15:
       Tithi_day = Tithi_day - 15
       Paksha = Krishna Paksha
   Else:
       Paksha = Shukla Paksha
   ```

## Why Sunrise is Important

In traditional Hindu astronomy, **the "ruling tithi" for a civil day is determined at sunrise**. This is because:

1. **Vedic Day Definition**: A civil day begins at sunrise (not midnight)
2. **Observational Tradition**: Ancient astronomers made observations at sunrise
3. **Religious Practice**: Most Hindu rituals are timed relative to sunrise

## Critical Distinction: Epoch vs Civil Day

### The Problem with Sunrise Correction

There's a **fundamental tension** between two requirements:

1. **Epoch Consistency**: Mean longitude calculations must use midnight ahargana for Kali Yuga epoch accuracy
2. **Civil Day Determination**: The "ruling tithi" should be determined at sunrise

### Why Midnight Baseline Matters

The Surya Siddhanta calculations use a **midnight baseline** for mean positions:

```python
Mean_Longitude = 360 × frac(rotations × ahargana / yuga_days)
```

If we add sunrise correction to `ahargana` here, we **break epoch calculations**:
- Kali Yuga start positions become incorrect
- Historical date calculations are affected
- The entire astronomical framework shifts

### The Solution: Configurable Behavior

The implementation now provides **both options** via a setting:

```python
# DEFAULT: Midnight calculation (preserves epoch)
use_sunrise_for_tithi = False  # ← Keeps Kali Yuga accuracy

# OPTIONAL: Sunrise calculation (civil day ruling tithi)
use_sunrise_for_tithi = True   # ← Traditional panchanga practice
```

### Implementation Details

```python
# Step 1: Calculate midnight ahargana (epoch baseline)
ahar_midnight = ahar - desantara

# Step 2: Calculate sunrise time
sunrise_fraction = (sunrise_hour + sunrise_minute/60) / 24.0

# Step 3: Choose calculation point based on setting
if use_sunrise_for_tithi:
    ahar_for_calc = ahar_midnight + sunrise_fraction  # Sunrise
else:
    ahar_for_calc = ahar_midnight  # Midnight (default)

# Step 4: Calculate longitudes at chosen moment
tslong = get_true_solar_longitude(ahar_for_calc)
tllong = get_true_lunar_longitude(ahar_for_calc)
tithi = get_tithi(tllong, tslong)
```

### Which Should You Use?

**Use midnight (default)** when:
- ✅ Verifying Kali Yuga epoch positions
- ✅ Historical astronomical research
- ✅ Comparing with classical Surya Siddhanta values
- ✅ Need epoch consistency

**Use sunrise** when:
- ✅ Creating civil day panchangas for religious observance
- ✅ Determining which tithi "rules" a specific day
- ✅ Following traditional panchanga practice
- ✅ Matching printed panchangas (which show sunrise tithi)

## Using Ephemeris for Sunrise

### Drik Ephemeris (Swiss Ephemeris)

When `use_drik_sunrise_sunset = True` in settings:

1. **High Accuracy**: Uses JPL ephemeris data
2. **Topocentric Correction**: Accounts for observer's location on Earth
3. **Atmospheric Refraction**: Corrects for light bending in atmosphere
4. **True Solar Disc**: Calculates when upper limb of sun crosses horizon

```python
drik = DrikEphemeris()
sunrise, sunset = drik.calculate_sunrise_sunset(
    date=date,
    latitude=latitude,
    longitude=longitude,
    elevation=elevation,
    timezone_offset=5.5  # IST
)
# Returns: ((hour, minute), (hour, minute))
```

### Traditional Method (Surya Siddhanta)

When Drik is not available or disabled:

```python
eqtime = 0.5 × arcsin(tan(latitude) × tan(declination)) / π
sunrise_hour = floor((0.25 - eqtime) × 24)
sunrise_minute = floor(60 × frac((0.25 - eqtime) × 24))
```

## Impact on Tithi Determination

### Timing Difference

- **Midnight vs Sunrise**: Typically 5-7 hours difference
- **Moon's motion**: ~0.5° per hour (~6° difference)
- **Tithi impact**: Can change which tithi is "at sunrise"

### Example Scenario

```
Date: 2024-01-15
Location: Hyderabad (17.4°N, 78.5°E)
Ephemeris Sunrise: 06:47 AM (sunrise_fraction = 0.2826)

At Midnight (00:00):
  Sun: 270.5°, Moon: 282.3°
  Elongation: 11.8°
  Tithi: 0.98 → Pratipada (1st)

At Sunrise (06:47):
  Ahargana offset: +0.2826 days (from ephemeris calculation)
  Sun: 270.7°, Moon: 285.6°
  Elongation: 14.9°
  Tithi: 1.24 → Dwitiya (2nd)

Result: Tithi changes from 1st to 2nd due to sunrise timing!

Note: Sunrise time varies by:
  - Latitude (northern locations have later sunrise in winter)
  - Longitude (eastern locations sunrise earlier)
  - Season (winter vs summer solstice ~±30 minutes)
  - Method (Drik vs Traditional ~±2-5 minutes typically)
```

## Changes Made to Code

### Summary of Updates

1. **Added configurable calculation point**:
   - New setting: `use_sunrise_for_tithi` (default: `False`)
   - `False` = midnight calculation (epoch consistent)
   - `True` = sunrise calculation (civil day ruling tithi)

2. **Separated ahargana values**:
   - `ahar_midnight`: Midnight baseline (epoch consistent)
   - `ahar_for_calc`: Either midnight or sunrise based on setting

3. **Sunrise fraction calculation**:
   ```python
   sunrise_fraction = (sriseh + srisem / 60.0) / 24.0
   if use_sunrise_for_tithi:
       ahar_for_calc = ahar_midnight + sunrise_fraction
   else:
       ahar_for_calc = ahar_midnight  # Default
   ```

4. **Updated all astronomical calculations** to use `ahar_for_calc`:
   - True solar longitude
   - True lunar longitude
   - Tithi calculation
   - Nakshatra, Yoga, Karana
   - Masa calculations
   - Timing calculations

5. **Preserved epoch accuracy**:
   - Default behavior keeps midnight calculation
   - Kali Yuga epoch positions remain accurate
   - Historical calculations unaffected

## Trade-offs and Considerations

### Midnight Calculation (Default)

**Pros:**
- ✅ Epoch consistent (Kali Yuga accuracy)
- ✅ Matches Surya Siddhanta framework
- ✅ Suitable for historical research
- ✅ Mean longitude calculations remain pure

**Cons:**
- ❌ May not match printed panchangas exactly
- ❌ Doesn't reflect "ruling tithi" concept
- ❌ Civil day boundary at midnight (not sunrise)

### Sunrise Calculation (Optional)

**Pros:**
- ✅ Matches traditional panchanga practice
- ✅ Shows "ruling tithi" at sunrise
- ✅ Civil day aligned with sunrise
- ✅ Closer to observational astronomy

**Cons:**
- ❌ Breaks epoch consistency
- ❌ Historical dates may be inaccurate
- ❌ Kali Yuga positions will be off
- ❌ Adds ~0.25 day to all calculations

### The Recommended Approach

For most use cases, **keep the default (midnight)**:
```python
use_sunrise_for_tithi = False  # Default, epoch consistent
```

Only enable sunrise for **specific panchanga printing** where you need the ruling tithi:
```python
use_sunrise_for_tithi = True   # Civil day panchangas only
```

## Configuration

### Default Configuration (Epoch Consistent)

```python
from panchanga.models.settings import PanchangaSettings

settings = PanchangaSettings(
    loc_lat=17.385,                    # Latitude
    loc_lon=78.4867,                   # Longitude
    use_drik_sunrise_sunset=True,      # Use ephemeris for sunrise/sunset display
    use_sunrise_for_tithi=False,       # Calculate at midnight (DEFAULT)
    language='telugu'
)

calculator = PanchangaCalculator(settings)
result = calculator.calculate(2024, 1, 15)
```

### Civil Day Panchanga Configuration

```python
settings = PanchangaSettings(
    loc_lat=17.385,
    loc_lon=78.4867,
    use_drik_sunrise_sunset=True,      # Use ephemeris for sunrise/sunset
    use_sunrise_for_tithi=True,        # Calculate at SUNRISE (civil day)
    language='telugu'
)

calculator = PanchangaCalculator(settings)
result = calculator.calculate(2024, 1, 15)
```

### ⚠️ IMPORTANT WARNING

**Setting `use_sunrise_for_tithi=True` will affect:**
- Historical date calculations
- Kali Yuga epoch verification
- Comparison with Surya Siddhanta reference values

**For epoch accuracy, always use `use_sunrise_for_tithi=False` (default)**

## Verification

To verify the changes are working:

```python
# Get detailed ahar breakdown
ahar_data = calculator.get_ahar_at_sunrise(2024, 1, 15)
print(f"Ahar raw: {ahar_data['ahar_raw']}")
print(f"Desantara: {ahar_data['desantara']}")
print(f"Eqtime: {ahar_data['eqtime']}")
print(f"Ahar final: {ahar_data['ahar_final']}")

# Calculate panchanga
result = calculator.calculate(2024, 1, 15)
print(f"Sunrise: {result['sunrise']}")
print(f"Tithi: {result['tithi_name']}")
print(f"Sun longitude: {result['sun_longitude']}")
print(f"Moon longitude: {result['moon_longitude']}")
```

## References

- **Surya Siddhanta**: Classical Indian astronomical treatise
- **Swiss Ephemeris**: Modern high-precision ephemeris
- **Drik Ganita**: Observational astronomy method
- **Vakya System**: Tabular method (not implemented here)

## Future Enhancements

1. **Multiple Calculation Points**:
   - At sunrise (current)
   - At noon
   - At sunset
   
2. **Comparative Analysis**:
   - Compare Drik vs Traditional sunrise times
   - Compare midnight vs sunrise tithi determination
   
3. **Historical Accuracy**:
   - Use epoch-appropriate precession values
   - Account for historical location changes

## Conclusion

The updated implementation now provides **configurable behavior** that balances two critical requirements:

### Default Behavior (use_sunrise_for_tithi = False)
- ✅ Calculates at midnight (epoch baseline)
- ✅ Preserves Kali Yuga epoch accuracy
- ✅ Maintains Surya Siddhanta framework integrity
- ✅ Suitable for historical and astronomical research
- ✅ Uses ephemeris for accurate sunrise/sunset reporting

### Optional Behavior (use_sunrise_for_tithi = True)
- ✅ Calculates at actual sunrise moment
- ✅ Determines "ruling tithi" for the civil day
- ✅ Matches traditional panchanga practice
- ✅ Shows which tithi is present at sunrise
- ⚠️ May affect epoch and historical calculations

### Key Insight

There is a **fundamental difference** between:
1. **Astronomical calculations** (midnight baseline for epoch consistency)
2. **Civil day determination** (sunrise for traditional panchanga)

The implementation now allows you to choose based on your use case, with the default preserving the critical epoch accuracy that you worked hard to achieve.

### Recommendation

**For your use case (verifying Kali Yuga positions):**
```python
use_sunrise_for_tithi = False  # Keep this setting!
```

This preserves the framework that gives correct Kali Yuga start planetary calculations.
