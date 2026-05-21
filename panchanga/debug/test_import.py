#!/usr/bin/env python
"""Test basic import only"""

import sys
print("Starting test...", file=sys.stderr)

try:
    print("Importing calculator...", file=sys.stderr)
    from panchanga.core.calculator import PanchangaCalculator
    print("✅ Import successful", file=sys.stderr)
except Exception as e:
    print(f"❌ Import failed: {e}", file=sys.stderr)
    sys.exit(1)

print("Done", file=sys.stderr)
