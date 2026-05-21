"""
Date conversion utilities for Panchanga calculations.

This module provides functions for converting between various calendar systems:
- Gregorian/Julian calendar
- Julian Day number
- Ahargana (days from epoch)
- Kali Yuga era
- Saka era
"""

from typing import Tuple
from panchanga.core.math_utils import MathUtils


class DateUtils:
    """Collection of date conversion utilities for Panchanga calculations."""
    
    # Julian Day of Kali epoch (February 18, 3102 BCE at noon)
    # Note: In Julian Day convention, .0 = noon, .5 = midnight
    KALI_EPOCH_JD = 588465.5
    
    # Gregorian calendar reform date (Julian Day)
    GREGORIAN_REFORM_JD = 2299160
    
    @staticmethod
    def modern_date_to_julian_day(year: int, month: int, day: int) -> float:
        """
        Convert modern (Gregorian/Julian) date to Julian Day number.
        
        Handles both Julian calendar (before 1582-10-15) and 
        Gregorian calendar (after 1582-10-15).
        
        Args:
            year: Year (negative for BCE)
            month: Month (1-12)
            day: Day of month
            
        Returns:
            Julian Day number at noon
        """
        if month < 3:
            year -= 1
            month += 12
        
        julian_day = int(365.25 * year) + int(30.59 * (month - 2)) + day + 1721086.5
        
        if year < 0:
            julian_day -= 1
            if (year % 4) == 0 and month >= 3:
                julian_day += 1
        
        if julian_day > DateUtils.GREGORIAN_REFORM_JD:
            julian_day = julian_day + int(year / 400) - int(year / 100) + 2
        
        return julian_day
    
    @staticmethod
    def julian_day_to_julian_date(julian_day: float) -> Tuple[int, int, int]:
        """
        Convert Julian Day to Julian calendar date.
        
        Args:
            julian_day: Julian Day number
            
        Returns:
            Tuple of (year, month, day) in Julian calendar
        """
        j = int(julian_day) + 1402
        k = int((j - 1) / 1461)
        l = j - 1461 * k
        n = int((l - 1) / 365) - int(l / 1461)
        i = l - 365 * n + 30
        J = int(80 * i / 2447)
        day = i - int(2447 * J / 80)
        I = int(J / 11)
        month = J + 2 - 12 * I
        year = 4 * k + n + I - 4716
        return (year, month, day)

    @staticmethod
    def julian_day_to_gregorian_date_time(julian_day: float, include_time: bool = False) -> Tuple[int, ...]:
        """
        Convert Julian Day to Gregorian calendar date (and optionally time).

        Args:
            julian_day: Julian Day number
            include_time: If True, also return hours, minutes, seconds

        Returns:
            Tuple of (year, month, day) or (year, month, day, hour, minute, second)
        """
        # Extract fractional day for time calculation
        # JD .0 = noon, .5 = midnight, so adjust by 0.5
        fractional_day = (julian_day + 0.5) % 1.0

        # Use integer JD for date calculation
        jd_int = int(julian_day + 0.5)

        a = jd_int + 68569
        b = int(a / 36524.25)
        c = a - int(36524.25 * b + 0.75)
        e = int((c + 1) / 365.2425)

        f = c - int(365.25 * e) + 31
        g = int(f / 30.59)
        h = int(g / 11)

        day = int(f - int(30.59 * g))
        month = int(g - 12 * h + 2)
        year = int(100 * (b - 49) + e + h)

        if not include_time:
            return (year, month, day)

        # Convert fractional day to hours, minutes, seconds
        total_seconds = fractional_day * 86400  # 24 * 60 * 60
        hour = int(total_seconds // 3600)
        minute = int((total_seconds % 3600) // 60)
        second = int(total_seconds % 60)

        return (year, month, day, hour, minute, second)

    @staticmethod
    def julian_day_to_gregorian_date(julian_day: float) -> Tuple[int, int, int]:
        """
        Convert Julian Day to Gregorian calendar date.
        
        Args:
            julian_day: Julian Day number
            
        Returns:
            Tuple of (year, month, day) in Gregorian calendar
        """
        a = julian_day + 68569
        b = int(a / 36524.25)
        c = a - int(36524.25 * b + 0.75)
        e = int((c + 1) / 365.2425)
        
        f = c - int(365.25 * e) + 31
        g = int(f / 30.59)
        h = int(g / 11)
        
        day = MathUtils.trunc(f - int(30.59 * g) + (julian_day - int(julian_day)))
        month = MathUtils.trunc(g - 12 * h + 2)
        year = MathUtils.trunc(100 * (b - 49) + e + h)
        
        return (year, month, day)
    
    @staticmethod
    def julian_day_to_modern_date(julian_day: float) -> Tuple[int, int, int]:
        """
        Convert Julian Day to modern (Gregorian/Julian) date.
        
        Automatically chooses Julian or Gregorian calendar based on the date.
        
        Args:
            julian_day: Julian Day number
            
        Returns:
            Tuple of (year, month, day)
        """
        # Julian calendar was used before October 15, 1582 (JD 2299239)
        if julian_day < 2299239:
            return DateUtils.julian_day_to_julian_date(julian_day)
        else:
            return DateUtils.julian_day_to_gregorian_date(julian_day)
    
    @staticmethod
    def julian_day_to_ahargana(julian_day: float) -> float:
        """
        Convert Julian Day to Ahargana (days from Kali epoch).
        
        The Kali epoch is February 18, 3102 BCE.
        
        Args:
            julian_day: Julian Day number
            
        Returns:
            Ahargana (days since Kali epoch)
        """
        return julian_day - DateUtils.KALI_EPOCH_JD
    
    @staticmethod
    def ahargana_to_julian_day(ahar: float) -> float:
        """
        Convert Ahargana to Julian Day.
        
        Args:
            ahar: Ahargana (days since Kali epoch)
            
        Returns:
            Julian Day number
        """
        return DateUtils.KALI_EPOCH_JD + ahar
    
    @staticmethod
    def kali_to_saka(year_kali: int) -> int:
        """
        Convert Kali year to Saka year.
        
        The Saka era began in 78 CE (Kali year 3179).
        
        Args:
            year_kali: Year in Kali era
            
        Returns:
            Year in Saka era
        """
        return year_kali - 3179
    
    @staticmethod
    def saka_to_kali(year_saka: int) -> int:
        """
        Convert Saka year to Kali year.
        
        Args:
            year_saka: Year in Saka era
            
        Returns:
            Year in Kali era
        """
        return year_saka + 3179
    
    @staticmethod
    def next_date(year: int, month: int, day: int) -> Tuple[int, int, int]:
        """
        Get the next calendar date.
        
        Handles month/year boundaries correctly.
        
        Args:
            year: Current year
            month: Current month (1-12)
            day: Current day
            
        Returns:
            Tuple of (year, month, day) for next date
        """
        day += 1
        
        # Days in each month (non-leap year)
        if month == 2:
            if day > 29:
                day = 1
                month += 1
        elif month in (4, 6, 9, 11):
            if day > 30:
                day = 1
                month += 1
        else:
            if day > 31:
                day = 1
                month += 1
        
        if month > 12:
            month = 1
            year += 1
        
        # Verify date by comparing Julian days
        if DateUtils.modern_date_to_julian_day(year, month, day) == \
           DateUtils.modern_date_to_julian_day(year, month + 1, 1):
            return (year, month + 1, 1)
        else:
            return (year, month, day)
