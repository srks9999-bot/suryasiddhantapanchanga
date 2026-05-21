#!/usr/bin/env python3
"""
Test to verify that the new get_karana_name implementation using _get_karana_name_math
produces consistent results with the old implementation.
"""

from panchanga.data.names import get_karana_name, _get_karana_name_math, KARANA_NAMES
from panchanga.core.math_utils import MathUtils

def get_karana_name_old(tithi: float, language: str = 'telugu') -> str:
    """Old implementation of get_karana_name for comparison."""
    karana = MathUtils.trunc(2 * tithi)
    karana_names = KARANA_NAMES.get(language, KARANA_NAMES['english'])

    if karana == 0:
        return karana_names.get(0, '')
    elif karana < 57:
        karana = karana % 7
        if karana == 0:
            return karana_names.get(7, '')
        else:
            return karana_names.get(karana, '')
    elif karana == 57:
        return karana_names.get(8, '')
    elif karana == 58:
        return karana_names.get(9, '')
    elif karana == 59:
        return karana_names.get(10, '')
    return ''

def test_karana_consistency():
    """Test that new and old implementations match."""
    test_cases = [
        0.0, 0.2, 0.4, 0.5, 0.7, 0.9,  # Tithi 0 (Amavasya)
        1.0, 1.2, 1.4, 1.5, 1.7, 1.9,  # Tithi 1 (Pratipada)
        7.0, 7.3, 7.5, 7.8,             # Tithi 7 (Saptami)
        14.0, 14.4, 14.5, 14.9,         # Tithi 14 (Chaturdashi)
        15.0, 15.2, 15.5, 15.8,         # Tithi 15 (Purnima/Amavasya)
        28.0, 28.3, 28.5, 28.8,         # Tithi 28
        29.0, 29.2, 29.5, 29.8,         # Tithi 29
        29.9, 29.99                      # Near end of month
    ]

    languages = ['english', 'telugu']
    errors = []

    for tithi in test_cases:
        for lang in languages:
            old_result = get_karana_name_old(tithi, lang)
            new_result = get_karana_name(tithi, lang)

            if old_result != new_result:
                errors.append(f"Tithi {tithi} ({lang}): OLD='{old_result}' vs NEW='{new_result}'")
            else:
                print(f"✓ Tithi {tithi:5.2f} ({lang:7s}): {new_result}")

    print("\n" + "="*70)
    if errors:
        print("❌ ERRORS FOUND:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ ALL TESTS PASSED!")
        print("The new get_karana_name implementation is consistent with the old one.")
        return True

def test_manual_examples():
    """Test some manual examples to verify correctness."""
    print("\n" + "="*70)
    print("Manual Test Examples:")
    print("="*70)

    examples = [
        (0.3, "english"),   # First karana of Amavasya
        (0.7, "english"),   # Second karana of Amavasya
        (1.2, "english"),   # First karana of Pratipada
        (1.6, "english"),   # Second karana of Pratipada
        (15.1, "english"),  # First karana of Purnima
        (15.8, "english"),  # Second karana of Purnima
    ]

    for tithi, lang in examples:
        karana = get_karana_name(tithi, lang)
        is_second = (tithi % 1.0) >= 0.5
        half = "2nd half" if is_second else "1st half"
        print(f"Tithi {tithi:5.2f} ({half}): {karana}")

if __name__ == "__main__":
    print("Testing Karana Name Consistency")
    print("="*70)

    success = test_karana_consistency()
    test_manual_examples()

    if success:
        print("\n" + "="*70)
        print("✅ Refactoring validated successfully!")
        print("="*70)
        exit(0)
    else:
        exit(1)
