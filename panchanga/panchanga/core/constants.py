"""
Mathematical and astronomical constants for Panchanga calculations.

This module contains fundamental constants used throughout the Panchanga calculator,
including mathematical constants, precision parameters, and default location settings.
"""

import math

# Mathematical constants
PI = math.pi
PI2 = PI * 2
RAD = 180 / PI  # Radians to degrees conversion factor

# Precision constants
EPS = 1e-6      # For arcsin calculations
EPSILON = 1e-8  # For calculation cutoff in iterative methods

# Configuration limits
YEAR_MAX = 3000

# Default location settings (Ujjain - traditional reference point)
UJJAINI_LAT = 23.2              # Default latitude (Ujjain)
IST_STANDARD_LON = 82.5         # IST standard meridian (82.5°E)
UJJAINI_LON = IST_STANDARD_LON  # Use IST meridian as reference
#UJJAINI_LON = 75.8

# Supported languages
SUPPORTED_LANGUAGES = ["telugu", "english", "sanskrit"]
DEFAULT_LANGUAGE = "telugu"

# Supported traditions
SUPPORTED_TRADITIONS = ["surya", "drik", "lunar"]
DEFAULT_TRADITION = "surya"
