# console_drik_debug.py - Quick Start

## What Is This?

A **standalone research tool** for exploring planetary positions on any date (including historical BCE dates like Kali Yuga epoch) using Swiss Ephemeris (Drik method).

### Key Features

✅ **Historical dates** - Works for BCE dates (back to ~13000 BCE)  
✅ **Completely standalone** - No changes to your framework  
✅ **All planets** - Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu  
✅ **Multiple ayanamsas** - Lahiri, Raman, Krishnamurti, Fagan-Bradley, Tropical  
✅ **Sunrise/sunset** - Accurate times for any location  
✅ **Tithi calculation** - From Drik positions  
✅ **Comparison mode** - Compare Drik vs Traditional Surya Siddhanta  

## Installation

```bash
# Make sure Swiss Ephemeris is installed
pip install pyswisseph

# Make executable (optional)
chmod +x console_drik_debug.py
```

## Usage

### Default: Kali Yuga Epoch (3101 BC - Jan 23)

```bash
python3 console_drik_debug.py
```

### Any Historical Date

```bash
# Format: python3 console_drik_debug.py <year> <month> <day>

# Kali Yuga epoch (3101 BC)
python3 console_drik_debug.py -3100 1 23

# 1000 BC
python3 console_drik_debug.py -999 6 15

# Buddha's birth (563 BC, approx)
python3 console_drik_debug.py -562 4 8

# Modern date
python3 console_drik_debug.py 2026 1 15
```

**IMPORTANT - BCE Date Format**: Use **astronomical year numbering** (not historical year!)

| Historical Year | What to Type | Why |
|----------------|--------------|-----|
| 3101 BC | `-3100` | 3101 - 1 = 3100 (then negate) |
| 563 BC | `-562` | 563 - 1 = 562 (then negate) |
| 2 BC | `-1` | 2 - 1 = 1 (then negate) |
| 1 BC | `0` | 1 - 1 = 0 |
| 1 AD | `1` | No conversion |

**Why?** Historical calendars have no year 0 (goes 1 BC → 1 AD), but astronomical numbering includes year 0. This creates an off-by-one difference for BCE dates.

**Formula**: `astronomical_year = -(historical_bc_year - 1)`

📖 See `BCE_DATE_REFERENCE.md` for detailed explanation and conversion table.

## Common Options

### Different Location

```bash
# Delhi
python3 console_drik_debug.py -3100 1 23 --lat 28.6 --lon 77.2

# Varanasi
python3 console_drik_debug.py -3100 1 23 --lat 25.3 --lon 83.0
```

### Different Ayanamsa

```bash
# Lahiri (default)
python3 console_drik_debug.py -3100 1 23 --ayanamsa lahiri

# B.V. Raman
python3 console_drik_debug.py -3100 1 23 --ayanamsa raman

# Tropical (no ayanamsa)
python3 console_drik_debug.py -3100 1 23 --ayanamsa none
```

### Compare with Traditional

```bash
# Only works for modern dates (>1 AD)
python3 console_drik_debug.py 2026 1 15 --compare
```

### All Options

```bash
python3 console_drik_debug.py -3100 1 23 \
    --lat 23.2 \
    --lon 75.8 \
    --tz 5.5 \
    --ayanamsa lahiri \
    --compare
```

## What You'll See

### 1. Date Information
- Gregorian date in BC/AD format
- Astronomical year
- Special date notifications (e.g., Kali Yuga epoch)

### 2. Planetary Positions (for each planet)
- Tropical longitude
- Sidereal longitude  
- Zodiac sign and degrees
- Nakshatra (for Moon)
- Latitude
- Speed (with retrograde indicator)

### 3. Sunrise & Sunset
- Times in local timezone
- Day length

### 4. Tithi Calculation
- Sun and Moon longitudes
- Elongation
- Tithi day and name
- Paksha

### 5. Comparison (if --compare used)
- Side-by-side Drik vs Traditional
- Differences in degrees

## Example Output

```
════════════════════════════════════════════════════════════════════════════════
  DATE INFORMATION
════════════════════════════════════════════════════════════════════════════════

Gregorian Date: 3101 BC, 01-23
Astronomical Year: -3100

⭐ SPECIAL DATE: Kali Yuga Epoch (Traditional Start)

════════════════════════════════════════════════════════════════════════════════
  DRIK EPHEMERIS PLANETARY POSITIONS (LAHIRI)
════════════════════════════════════════════════════════════════════════════════

Julian Day: 588465.750000
Ayanamsa Value: -43.xxxx°

┌─ Sun ─────────────────────────────────────────────────────────────────────────┐
Tropical Longitude: 297.xxxx° = Cap 27.xx°
Sidereal Longitude: 341.xxxx° = Pis 11.xx°
Zodiac Position: Pisces 11° 23' 45"
...
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `python3 console_drik_debug.py` | Kali Yuga epoch (default) |
| `python3 console_drik_debug.py -3100 1 23` | Specific historical date |
| `python3 console_drik_debug.py 2026 1 15` | Modern date |
| `--lat XX --lon YY` | Different location |
| `--ayanamsa lahiri` | Ayanamsa system |
| `--compare` | Compare with traditional |
| `--no-color` | Disable colors (for file output) |
| `--help` | Show all options |

## Save Output to File

```bash
# With colors (for viewing)
python3 console_drik_debug.py -3100 1 23 > kali_epoch.txt

# Without colors (for processing)
python3 console_drik_debug.py -3100 1 23 --no-color > kali_epoch.txt
```

## Batch Processing

```bash
# Check multiple dates
for year in -3100 -3000 -2900 -2800; do
    echo "=== Year $year ==="
    python3 console_drik_debug.py $year 1 23 | grep "Sun Longitude"
done
```

## Important Notes

### ✅ What This Tool Does

- Shows **actual astronomical positions** from Swiss Ephemeris
- Works for **any date** (~13000 BCE to ~17000 CE)
- **Completely standalone** - no framework changes
- **Research and education** focused

### ❌ What This Tool Doesn't Do

- **Not integrated** with your panchanga service
- **Not for production** - this is a debug/research tool
- **No API** - command-line only
- **Traditional comparison** only works for modern dates

### Framework Integration

Your main framework (`console_debug.py`) remains unchanged. This is a **separate research tool** for exploring:
- Historical dates
- Kali Yuga epoch verification
- Ayanamsa comparisons
- Traditional vs Drik differences

## Use Cases

### 1. Verify Kali Yuga Epoch
```bash
python3 console_drik_debug.py -3100 1 23
```
Check if planets were really at 0° Aries as traditionally stated.

### 2. Research Historical Dates
```bash
python3 console_drik_debug.py -562 4 8  # Buddha's birth
```

### 3. Compare Ayanamsa Systems
```bash
for ayan in lahiri raman krishnamurti; do
    python3 console_drik_debug.py 2026 1 15 --ayanamsa $ayan
done
```

### 4. Verify Traditional Calculations
```bash
python3 console_drik_debug.py 2026 1 15 --compare
```

## Troubleshooting

### Swiss Ephemeris Not Installed
```
✗ Swiss Ephemeris not installed!
```
**Solution**: `pip install pyswisseph`

### Invalid Date
Check that:
- Month is 1-12
- Day is valid for that month
- Year is in range (~-13000 to ~17000)

### Traditional Comparison Not Working
For BCE dates, this is expected - traditional panchanga doesn't support BCE.

## Documentation Files

- `DRIK_DEBUG_GUIDE.md` - Comprehensive usage guide
- `KALI_EPOCH_EXAMPLE.md` - Expected output and insights
- `DRIK_INTEGRATION.md` - Main Drik integration docs
- `console_drik_debug.py` - The tool itself (with inline docs)

## Quick Test

```bash
# Test installation
python3 console_drik_debug.py -3100 1 23

# Should show:
# ✓ Planetary positions for all planets
# ✓ Sunrise/sunset times
# ✓ Tithi calculation
# ✓ Special date notification for Kali Yuga epoch
```

---

**Happy exploring! 🌟**

For questions or to add features, simply edit `console_drik_debug.py` - it's completely standalone with all functions included.
