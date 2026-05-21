"""
Drik Ephemeris Calculations using Skyfield.

This module provides high-accuracy sunrise/sunset calculations using
the Skyfield library. These calculations account for:
- Atmospheric refraction (handled by Skyfield)
- Topocentric corrections
- Precise planetary positions using JPL ephemeris (de421.bsp)
- Elevation above sea level

NOTE: Library changed from pyswisseph to skyfield for drik-based sunrise/sunset calculations.
The interface remains the same to maintain compatibility with existing code.

Used for reporting accurate sunrise/sunset times separately from
traditional Surya Siddhanta astronomical calculations.
"""

import math
from typing import Tuple, Optional
from datetime import datetime, timedelta
import os

try:
    from skyfield.api import load, wgs84
    from skyfield import almanac
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False
    load = None
    wgs84 = None
    almanac = None


class DrikEphemeris:
    """
    Drik-based ephemeris calculations using Skyfield.
    
    This class provides accurate sunrise/sunset calculations that can be
    used for reporting purposes while keeping astronomical calculations
    separate from the traditional Surya Siddhanta methods.
    
    NOTE: Changed from pyswisseph to skyfield library. The interface remains
    the same for compatibility.
    """
    
    def __init__(self):
        """Initialize Drik Ephemeris calculator."""
        if not SKYFIELD_AVAILABLE:
            raise ImportError(
                "Skyfield is not installed. "
                "Install it with: pip install skyfield"
            )
        
        # Load Skyfield timescale and ephemeris
        # Look for de421.bsp file in the panchanga package root
        # Go up two levels: core/ -> panchanga/ -> packages/panchanga/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_root = os.path.dirname(os.path.dirname(current_dir))
        bsp_path = os.path.join(package_root, 'de421.bsp')
        
        self.ts = load.timescale()
        
        # Try to load de421.bsp from package root, otherwise let skyfield download it
        if os.path.exists(bsp_path):
            self.eph = load(bsp_path)
        else:
            # Skyfield will download de421.bsp automatically if not found
            self.eph = load('de421.bsp')
    
    def calculate_sunrise_sunset(
        self,
        date: datetime,
        latitude: float,
        longitude: float,
        elevation: float = 0.0,
        timezone_offset: float = 0.0
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Calculate accurate sunrise and sunset times using Skyfield.
        
        Args:
            date: Date for calculation (time component is ignored)
            latitude: Geographic latitude in degrees (positive = North)
            longitude: Geographic longitude in degrees (positive = East)
            elevation: Elevation above sea level in meters (default: 0)
            timezone_offset: Timezone offset in hours from UTC (default: 0)
            
        Returns:
            Tuple of ((sunrise_hour, sunrise_minute), (sunset_hour, sunset_minute))
            Times are in local time based on the timezone_offset
            
        Example:
            >>> drik = DrikEphemeris()
            >>> sunrise, sunset = drik.calculate_sunrise_sunset(
            ...     datetime(2024, 1, 15),
            ...     latitude=17.4,
            ...     longitude=78.5,
            ...     timezone_offset=5.5
            ... )
            >>> print(f"Sunrise: {sunrise[0]:02d}:{sunrise[1]:02d}")
            >>> print(f"Sunset: {sunset[0]:02d}:{sunset[1]:02d}")
        """
        # Create location using wgs84 (handles elevation)
        place = wgs84.latlon(latitude, longitude, elevation_m=elevation)
        
        # Create time range for the day (UTC)
        year, month, day = date.year, date.month, date.day
        t0 = self.ts.utc(year, month, day)
        t1 = self.ts.utc(year, month, day + 1)
        
        # Find sunrise and sunset events
        f = almanac.sunrise_sunset(self.eph, place)
        times, events = almanac.find_discrete(t0, t1, f)
        
        # Extract sunrise (event == 1) and sunset (event == 0)
        sunrise_dt = None
        sunset_dt = None
        
        for ti, ev in zip(times, events):
            if ev == 1:  # Sunrise
                sunrise_dt = ti.utc_datetime()
            elif ev == 0:  # Sunset
                sunset_dt = ti.utc_datetime()
        
        # Convert to local time and return as (hour, minute) tuples
        if sunrise_dt is None or sunset_dt is None:
            raise RuntimeError("Could not find sunrise or sunset for the given date")
        
        sunrise_time = self._datetime_to_time(sunrise_dt, timezone_offset)
        sunset_time = self._datetime_to_time(sunset_dt, timezone_offset)
        
        return sunrise_time, sunset_time
    
    def _datetime_to_time(self, dt: datetime, timezone_offset: float) -> Tuple[int, int]:
        """
        Convert datetime to local time (hours, minutes).
        
        Args:
            dt: UTC datetime
            timezone_offset: Timezone offset in hours from UTC
            
        Returns:
            Tuple of (hours, minutes)
        """
        # Apply timezone offset
        local_dt = dt + timedelta(hours=timezone_offset)
        
        return (local_dt.hour, local_dt.minute)
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Skyfield is available.
        
        Returns:
            True if skyfield is installed and available
        """
        return SKYFIELD_AVAILABLE


def calculate_drik_sunrise_sunset(
    date: datetime,
    latitude: float,
    longitude: float,
    elevation: float = 0.0,
    timezone_offset: float = 5.5
) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Convenience function to calculate sunrise/sunset using Drik method.
    
    NOTE: Now uses Skyfield library instead of pyswisseph.
    
    Args:
        date: Date for calculation
        latitude: Geographic latitude in degrees
        longitude: Geographic longitude in degrees
        elevation: Elevation above sea level in meters
        timezone_offset: Timezone offset in hours from UTC (default: 5.5 for IST)
        
    Returns:
        Tuple of ((sunrise_hour, sunrise_minute), (sunset_hour, sunset_minute))
        or None if Skyfield is not available
    """
    if not DrikEphemeris.is_available():
        return None
    
    try:
        drik = DrikEphemeris()
        return drik.calculate_sunrise_sunset(
            date, latitude, longitude, elevation, timezone_offset
        )
    except Exception:
        return None
