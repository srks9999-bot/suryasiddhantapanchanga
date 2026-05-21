# BCE Date Reference for Swiss Ephemeris

## The Year Numbering Problem

Historical calendars (Gregorian/Julian) **do not have a year 0**:
```
... → 3 BC → 2 BC → 1 BC → 1 AD → 2 AD → ...
                          ↑
                    No year 0!
```

Astronomical year numbering **includes year 0**:
```
... → -2 → -1 → 0 → 1 → 2 → 3 → ...
              ↑
        Year 0 = 1 BC
```

This creates an **off-by-one difference** for BCE dates!

## Conversion Table

### Quick Reference: Common Historical Dates

| Historical Date | Astronomical Year | For pyswisseph |
|-----------------|-------------------|----------------|
| **Kali Yuga Epoch** | 3101 BC Jan 23 | **-3100** |
| Buddha's Birth (approx) | 563 BC Apr 8 | **-562** |
| Mahabharata War (theory) | 3067 BC | **-3066** |
| 1000 BC | 1000 BC | **-999** |
| 500 BC | 500 BC | **-499** |
| 100 BC | 100 BC | **-99** |
| 10 BC | 10 BC | **-9** |
| 2 BC | 2 BC | **-1** |
| 1 BC | 1 BC | **0** |
| 1 AD | 1 AD | **1** |
| 2 AD | 2 AD | **2** |

## The Formula

```python
# Historical BC to Astronomical Year
astronomical_year = -(historical_bc_year - 1)

# Examples:
3101 BC → -(3101 - 1) = -3100
563 BC  → -(563 - 1)  = -562
2 BC    → -(2 - 1)    = -1
1 BC    → -(1 - 1)    = 0
```

## Why This Matters

### For pyswisseph (Swiss Ephemeris)

```python
import swisseph as swe

# For 3101 BC Jan 23 (Kali Yuga epoch)
jd = swe.julday(-3100, 1, 23, 0.0)  # Note: -3100, not -3101!
```

### For console_drik_debug.py

```bash
# Kali Yuga epoch (3101 BC)
python3 console_drik_debug.py -3100 1 23

# Buddha's birth (563 BC)
python3 console_drik_debug.py -562 4 8

# 1 BC
python3 console_drik_debug.py 0 1 1
```

## Common Mistakes

### ❌ WRONG
```bash
# DO NOT USE the historical year directly for BCE!
python3 console_drik_debug.py -3101 1 23  # Wrong! This is 3102 BC
```

### ✅ CORRECT
```bash
# Use astronomical year numbering
python3 console_drik_debug.py -3100 1 23  # Correct! This is 3101 BC
```

## Understanding the Off-By-One

Think of it this way:

```
Historical:  ... 3 BC, 2 BC, 1 BC, 1 AD, 2 AD ...
                                    ↑
                              Jumps from 1 BC to 1 AD

Astronomical: ... -2,  -1,   0,   1,   2  ...
                              ↑
                        Continuous sequence
```

To align them:
- **1 BC** must equal **0** (astronomical)
- Therefore **2 BC** = **-1**
- Therefore **3 BC** = **-2**
- Therefore **N BC** = **-(N-1)**

## Examples with Explanations

### Example 1: Kali Yuga Epoch

**Historical**: February 18, 3102 BC (or January 23, 3101 BC depending on tradition)

**For Swiss Ephemeris**:
```bash
# Using Jan 23, 3101 BC
python3 console_drik_debug.py -3100 1 23

# The tool will display:
# "Gregorian Date: 3101 BC, 01-23"
# "Astronomical Year: -3100"
```

### Example 2: Buddha's Birth

**Historical**: April 8, 563 BC (one theory)

**For Swiss Ephemeris**:
```bash
python3 console_drik_debug.py -562 4 8

# Displays:
# "Gregorian Date: 563 BC, 04-08"
# "Astronomical Year: -562"
```

### Example 3: The Transition Year

**Historical**: December 31, 1 BC → January 1, 1 AD

**For Swiss Ephemeris**:
```bash
# Last day of 1 BC
python3 console_drik_debug.py 0 12 31

# First day of 1 AD
python3 console_drik_debug.py 1 1 1
```

## Why Astronomers Do This

1. **Mathematical Continuity**: Makes calculations easier
2. **No Discontinuity**: Avoids the jump from -1 to +1
3. **Consistent Formulas**: Year arithmetic works correctly
4. **International Standard**: ISO 8601 uses astronomical year numbering

## ISO 8601 Standard

The international standard ISO 8601 explicitly uses astronomical year numbering:
- **Year 0** = 1 BC
- **Year -1** = 2 BC
- **Year -100** = 101 BC

This is what pyswisseph follows!

## Validation

You can verify the conversion is working correctly:

```bash
# Check that the tool displays the right historical date
python3 console_drik_debug.py -3100 1 23 | grep "Gregorian Date"

# Should show:
# "Gregorian Date: 3101 BC, 01-23"
```

## Quick Conversion Tool

For quick conversions, use this Python snippet:

```python
def bc_to_astronomical(bc_year):
    """Convert historical BC year to astronomical year."""
    return -(bc_year - 1)

def astronomical_to_bc(astro_year):
    """Convert astronomical year to historical BC year."""
    if astro_year <= 0:
        return -(astro_year - 1)  # BC year
    else:
        return astro_year  # AD year

# Examples:
print(bc_to_astronomical(3101))  # -3100
print(bc_to_astronomical(563))   # -562
print(bc_to_astronomical(1))     # 0

print(astronomical_to_bc(-3100))  # 3101 BC
print(astronomical_to_bc(-562))   # 563 BC
print(astronomical_to_bc(0))      # 1 BC
print(astronomical_to_bc(1))      # 1 AD
```

## In the Code

Here's how `console_drik_debug.py` handles this:

```python
def display_date_info(year: int, month: int, day: int):
    """Display date information."""
    
    # Handle BCE dates
    if year < 0:
        year_display = f"{abs(year) + 1} BC"  # Convert back to historical
        year_astro = year
    else:
        year_display = f"{year} AD"
        year_astro = year
    
    print(f"Gregorian Date: {year_display}, {month:02d}-{day:02d}")
    print(f"Astronomical Year: {year_astro}")
```

So when you input `-3100`, it correctly displays as `3101 BC`.

## Summary

| What You Want | What You Type | Why |
|--------------|---------------|-----|
| 3101 BC | `-3100` | 3101 - 1 = 3100 (then negate) |
| 563 BC | `-562` | 563 - 1 = 562 (then negate) |
| 1 BC | `0` | 1 - 1 = 0 |
| 1 AD | `1` | No conversion needed |

**Remember**: For BCE dates, subtract 1 from the historical year, then negate!

## Further Reading

- [Wikipedia: Astronomical year numbering](https://en.wikipedia.org/wiki/Astronomical_year_numbering)
- [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601)
- Swiss Ephemeris documentation on date handling

---

**TL;DR**: Use `-3100` for 3101 BC because astronomical year numbering includes year 0 (= 1 BC), creating an off-by-one difference for all BCE dates.
