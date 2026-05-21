"""
Mathematical utility functions for Panchanga calculations.

This module provides mathematical helper functions used in astronomical
calculations, including trigonometric functions, rounding, and angle normalization.
"""

import math
from panchanga.core.constants import PI, EPS


class MathUtils:
    """Collection of mathematical utility functions for Panchanga calculations."""
    
    @staticmethod
    def trunc(x: float) -> int:
        """
        Truncate towards zero.
        
        Args:
            x: Number to truncate
            
        Returns:
            Integer part of x, truncated towards zero
        """
        return int(x)
    
    @staticmethod
    def floor(x: float) -> int:
        """
        Floor function - largest integer less than or equal to x.
        
        Args:
            x: Number to floor
            
        Returns:
            Largest integer <= x
        """
        y = int(x)
        return y - 1 if x < y else y
    
    @staticmethod
    def frac(x: float) -> float:
        """
        Get fractional part of a number.
        
        Args:
            x: Number to get fractional part of
            
        Returns:
            Fractional part (x - int(x))
        """
        return x - int(x)
    
    @staticmethod
    def round(x: float) -> int:
        """
        Round to nearest integer.
        
        Args:
            x: Number to round
            
        Returns:
            Nearest integer to x
        """
        return MathUtils.floor(x + 0.5)
    
    @staticmethod
    def sqr(x: float) -> float:
        """
        Square function.
        
        Args:
            x: Number to square
            
        Returns:
            x squared
        """
        return x * x
    
    @staticmethod
    def zero360(longitude: float) -> float:
        """
        Normalize angle to 0-360 degree range.
        
        Args:
            longitude: Angle in degrees
            
        Returns:
            Angle normalized to [0, 360) range
        """
        longitude = longitude - int(longitude / 360) * 360
        if longitude < 0:
            longitude += 360
        return longitude
    
    @staticmethod
    def tan(x: float) -> float:
        """
        Tangent function (x in radians).
        
        Args:
            x: Angle in radians
            
        Returns:
            Tangent of x
        """
        return math.sin(x) / math.cos(x)
    
    @staticmethod
    def arcsin(x: float) -> float:
        """
        Arcsine function with edge case handling.
        
        Handles edge cases where x is close to ±1 to avoid
        numerical issues.
        
        Args:
            x: Value to compute arcsine of (-1 to 1)
            
        Returns:
            Arcsine of x in radians
        """
        if EPS < abs(1 - MathUtils.sqr(x)):
            return math.atan2(x / math.sqrt(1 - MathUtils.sqr(x)), 1)
        elif x > 0:
            return PI / 2
        else:
            return 3 * PI / 2
    
    @staticmethod
    def three_relation(a: float, b: float, c: float) -> int:
        """
        Determine relationship between three values.
        
        Used in binary search algorithms to determine which direction
        to search.
        
        Args:
            a: First value
            b: Middle value
            c: Third value
            
        Returns:
            1 if a < b < c (ascending)
            -1 if c < b < a (descending)
            0 otherwise
        """
        if a < b < c:
            return 1
        elif c < b < a:
            return -1
        else:
            return 0
