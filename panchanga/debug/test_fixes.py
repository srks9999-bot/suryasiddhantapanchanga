#!/usr/bin/env python3
"""
Test script to verify the fixes for the internal server error.
"""

try:
    print("1. Testing import of _get_karana_name_math...")
    from panchanga.data.names import _get_karana_name_math
    print("   ✓ Import successful")

    print("\n2. Testing _get_karana_name_math function call...")
    result = _get_karana_name_math(1.0, False, 'english')
    print(f"   ✓ Function call successful, result: {result}")

    print("\n3. Testing PanchangaCalculator import...")
    from panchanga.core.calculator import PanchangaCalculator
    print("   ✓ PanchangaCalculator import successful")

    print("\n4. Testing API main import...")
    from api.main import app
    print("   ✓ API main import successful")

    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print("\nThe internal server error should be resolved.")
    print("You can now start the server with:")
    print("  uvicorn api.main:app --reload --port 8000")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
