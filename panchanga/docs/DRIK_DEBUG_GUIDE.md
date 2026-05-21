# Drik Debug Tool - Usage Guide

## Overview

`console_drik_debug.py` is a standalone tool for exploring planetary positions on any date (including historical BCE dates) using Swiss Ephemeris. It's completely separate from the main framework and perfect for research and comparison.

## Quick Start

### Default: Kali Yuga Epoch (3101 BC - Jan 23)

```bash
python3 console_drik_debug.py
```

This will show:
- All planetary positions (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu)
- Tropical and sidereal longitudes
- Zodiac signs and nakshatras
- Sunrise/sunset times
- Tithi calculation

### Specific Historical Date

```bash
# 3101 BC Jan 23 (Kali Yuga epoch)
python3 console_drik_debug.py -3100 1 23

# 1000 BC
python3 console_drik_debug.py -999 6 15

# 500 AD
python3 console_drik_debug.py 500 3 21
```

**CRITICAL - BCE Date Conversion**:

Historical calendars skip from 1 BC directly to 1 AD (no year 0), but astronomical numbering includes year 0. This creates an **off-by-one** difference:

| Want This | Type This | Calculation |
|-----------|-----------|-------------|
| 3101 BC (Kali Yuga) | `-3100` | -(3101 - 1) = -3100 |
| 563 BC (Buddha) | `-562` | -(563 - 1) = -562 |
| 2 BC | `-1` | -(2 - 1) = -1 |
| 1 BC | `0` | -(1 - 1) = 0 |
| 1 AD | `1` | No conversion |

**Formula**: For N BC, use `-(N - 1)`

See `BCE_DATE_REFERENCE.md` for complete conversion table and explanation.

### Modern Date

```bash
# Today's equivalent
python3 console_drik_debug.py 2026 1 15
```

## Features

### 1. Different Ayanamsa Systems

```bash
# Lahiri (default - most common in India)
python3 console_drik_debug.py -3100 1 23 --ayanamsa lahiri

# B.V. Raman
python3 console_drik_debug.py -3100 1 23 --ayanamsa raman

# Krishnamurti
python3 console_drik_debug.py -3100 1 23 --ayanamsa krishnamurti

# Tropical (no ayanamsa)
python3 console_drik_debug.py -3100 1 23 --ayanamsa none
```

### 2. Different Locations

```bash
# Delhi
python3 console_drik_debug.py -3100 1 23 --lat 28.6 --lon 77.2

# Varanasi
python3 console_drik_debug.py -3100 1 23 --lat 25.3 --lon 83.0

# Chennai
python3 console_drik_debug.py -3100 1 23 --lat 13.1 --lon 80.3
```

### 3. Compare with Traditional Surya Siddhanta

```bash
# For modern dates only (traditional panchanga doesn't support BCE)
python3 console_drik_debug.py 2026 1 15 --compare
```

This will show side-by-side comparison of:
- Drik (Swiss Ephemeris) positions
- Traditional Surya Siddhanta positions
- Differences between them

### 4. Timezone Adjustment

```bash
# IST (default)
python3 console_drik_debug.py -3100 1 23 --tz 5.5

# UTC
python3 console_drik_debug.py -3100 1 23 --tz 0

# EST
python3 console_drik_debug.py -3100 1 23 --tz -5
```

## Output Explanation

### Planetary Positions

For each planet, you'll see:

```
┌─ Sun ─────────────────────────────────────────────────────────────────────┐
  Tropical Longitude: 297.8234° = Cap  27.82°
  Sidereal Longitude: 274.1234° = Cap   4.12°
  Zodiac Position:    Capricorn  4° 07' 24"
  Latitude:           0.0000°
  Speed:              0.9856°/day
```

- **Tropical**: Position in tropical zodiac (fixed to seasons)
- **Sidereal**: Position in sidereal zodiac (fixed to stars, with ayanamsa correction)
- **Zodiac Position**: Detailed position in sign
- **Latitude**: North/South from ecliptic
- **Speed**: Daily motion (negative = retrograde)

### Sunrise/Sunset

Shows accurate civil sunrise/sunset times accounting for:
- Atmospheric refraction
- Solar semidiameter
- Geographic location
- Elevation (currently 0m, can be modified in code)

### Tithi Calculation

Calculates tithi from Drik lunar and solar positions:
- Elongation = (Moon - Sun) % 360
- Tithi = Elongation / 12
- Shows tithi day, name, and paksha

## Understanding the Kali Yuga Epoch Date

### What is 3101 BC Jan 23?

This is the **traditional start of Kali Yuga** according to Hindu astronomy. It's significant because:

1. **Astronomical Alignment**: Traditional texts describe specific planetary positions on this date
2. **Calendar Zero Point**: Many Indian calendar calculations use this as a reference
3. **Historical Significance**: Marks the end of Mahabharata war era in tradition

### Checking Planetary Positions

```bash
python3 console_drik_debug.py -3100 1 23
```

This will show you the **actual astronomical positions** on that date according to modern ephemeris calculations (Drik), which you can compare with traditional texts.

### Expected Findings

According to traditional texts, on Kali Yuga epoch:
- All planets were supposedly near 0° Aries (a grand conjunction)
- This is more of a computational convenience than actual astronomy
- Drik will show you the **real** positions

## Examples

### Example 1: Kali Yuga Epoch with Different Ayanamsas

```bash
# See how different ayanamsa systems affect the positions
python3 console_drik_debug.py -3100 1 23 --ayanamsa lahiri
python3 console_drik_debug.py -3100 1 23 --ayanamsa raman
python3 console_drik_debug.py -3100 1 23 --ayanamsa none
```

### Example 2: Historical Event Dates

```bash
# Approximate date of Buddha's birth (563 BC)
python3 console_drik_debug.py -562 4 8

# Approximate Mahabharata war date (various theories)
python3 console_drik_debug.py -3067 10 1
```

### Example 3: Solar Eclipse Research

```bash
# Check planetary positions during historical eclipses
# Example: A known eclipse date
python3 console_drik_debug.py -1100 5 3
```

## Advanced Usage

### Custom Calculations

The script is standalone - you can modify it to add:

1. **More planets**: Uranus, Neptune, Pluto
2. **House calculations**: Add ascendant/house cusps
3. **Aspects**: Calculate planetary aspects
4. **Yogas**: Check for specific yogas
5. **Dasha periods**: Calculate planetary periods

Simply edit the functions in `console_drik_debug.py`.

### Batch Processing

```bash
# Check multiple dates
for year in -3100 -3000 -2900; do
    python3 console_drik_debug.py $year 1 23
done
```

### Output to File

```bash
# Save output for analysis
python3 console_drik_debug.py -3100 1 23 > kali_epoch.txt

# Without colors (better for files)
python3 console_drik_debug.py -3100 1 23 --no-color > kali_epoch.txt
```

## Technical Notes

### Date Range

Swiss Ephemeris supports: **~13000 BCE to ~17000 CE**

All dates in this range are valid!

### Accuracy

- **High precision**: Based on JPL ephemeris
- **Actual astronomical positions**: Not simplified models
- **Refraction included**: For sunrise/sunset
- **Topocentric**: Corrected for observer location

### Limitations

1. **Traditional Comparison**: Only works for modern dates (>1 AD)
2. **Elevation**: Currently fixed at 0m (can be modified)
3. **No Eclipse Detection**: Doesn't automatically detect eclipses (but shows positions)

## Comparison with Traditional

For modern dates, compare Drik vs Traditional:

```bash
python3 console_drik_debug.py 2026 1 15 --compare
```

This will show:
- **Drik**: High-precision ephemeris positions
- **Traditional**: Surya Siddhanta calculations
- **Differences**: Usually ±0.5° to ±2°

The differences arise because:
- Traditional uses mean positions and simplified corrections
- Drik uses precise ephemeris with all perturbations

## Troubleshooting

### Swiss Ephemeris Not Installed

```
✗ Swiss Ephemeris not installed!
```

**Solution**:
```bash
pip install pyswisseph
```

### Invalid Date

```
Error calculating Drik positions: ...
```

Check that:
- Month is 1-12
- Day is valid for that month
- Year is within range (~13000 BCE to ~17000 CE)

### Traditional Comparison Unavailable

For BCE dates, traditional comparison won't work (this is expected):
```
Traditional calculations not available for this date.
(BCE dates or panchanga modules not installed)
```

## Research Ideas

### 1. Verify Traditional Texts

Check if planetary positions in ancient texts match actual astronomy:
```bash
python3 console_drik_debug.py -3100 1 23  # Kali Yuga
```

### 2. Historical Astrology

Research historical events:
```bash
python3 console_drik_debug.py -560 4 8   # Buddha's birth
python3 console_drik_debug.py -3000 1 1  # Ancient epoch
```

### 3. Ayanamsa Research

Compare different ayanamsa systems:
```bash
for ayan in lahiri raman krishnamurti; do
    echo "=== $ayan ===" 
    python3 console_drik_debug.py 2026 1 15 --ayanamsa $ayan
done
```

### 4. Sunrise Evolution

See how sunrise times changed over millennia:
```bash
for year in -3100 -2000 -1000 0 1000 2000; do
    python3 console_drik_debug.py $year 1 23 | grep "Sunrise:"
done
```

## See Also

- `DRIK_INTEGRATION.md` - Main Drik integration documentation
- `check_ephemeris.py` - Check Swiss Ephemeris installation
- `test_drik.py` - Test suite for Drik calculations
- `console_debug.py` - Main panchanga debug tool
