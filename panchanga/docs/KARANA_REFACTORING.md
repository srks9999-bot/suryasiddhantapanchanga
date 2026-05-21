# Karana Function Refactoring - Summary

## Date: January 26, 2026

## What Was Changed

### Refactored `get_karana_name()` to use `_get_karana_name_math()`

**File**: `panchanga/data/names.py`
**Line**: 563-575

## Previous Implementation

The `get_karana_name()` function had its own logic using `MathUtils.trunc()`:

```python
def get_karana_name(tithi: float, language: str = 'telugu') -> str:
    """Get karana name from tithi value."""
    from panchanga.core.math_utils import MathUtils
    
    karana = MathUtils.trunc(2 * tithi)
    karana_names = KARANA_NAMES.get(language, KARANA_NAMES['english'])
    
    # ... complex if-elif logic for mapping karana index to name
```

## New Implementation

Now `get_karana_name()` uses `_get_karana_name_math()` internally:

```python
def get_karana_name(tithi: float, language: str = 'telugu') -> str:
    """
    Get karana name from tithi value.
    
    This function now uses _get_karana_name_math internally for better consistency.
    The fractional part of the tithi determines which half we're in.
    """
    # Determine which half of the tithi we're in
    fractional_part = tithi % 1.0
    is_second_half = fractional_part >= 0.5
    
    # Use the math-based function
    return _get_karana_name_math(tithi, is_second_half, language)
```

## Benefits

1. **Single Source of Truth**: All karana calculations now use the same underlying logic (`_get_karana_name_math`)
2. **Consistency**: Ensures consistent results across all parts of the codebase
3. **Maintainability**: Changes to karana calculation logic only need to be made in one place
4. **Clarity**: The logic for determining which half of the tithi we're in is explicit

## How It Works

The function determines which half of the tithi we're in based on the fractional part:
- **Fractional part < 0.5**: First half of the tithi (`is_second_half=False`)
- **Fractional part >= 0.5**: Second half of the tithi (`is_second_half=True`)

Examples:
- `tithi = 1.2` → fractional = 0.2 → 1st half of Pratipada
- `tithi = 1.7` → fractional = 0.7 → 2nd half of Pratipada
- `tithi = 15.4` → fractional = 0.4 → 1st half of Purnima
- `tithi = 15.8` → fractional = 0.8 → 2nd half of Purnima

## Impact

### All existing calls to `get_karana_name()` now benefit from the refactoring:

1. **calculator.py, line 337**: `karana = get_karana_name(tithi, language)`
2. **calculator.py, line 938**: `karana = get_karana_name(tithi, language)`
3. **calculator.py, line 1322**: `karana = get_karana_name(ruling_tithi['tithi'], language)`

### No changes needed to calling code

The function signature remains the same, so all existing code continues to work without modification.

## Testing

A test file has been created at `test_karana_refactor.py` to verify the refactoring produces consistent results.

## Backward Compatibility

✅ **Fully backward compatible** - The function signature and behavior remain the same from the caller's perspective.

## Related Files

- `panchanga/data/names.py` - Contains both `_get_karana_name_math()` and `get_karana_name()`
- `panchanga/core/calculator.py` - Uses `get_karana_name()` in multiple places
- `test_karana_refactor.py` - Test file to verify consistency
