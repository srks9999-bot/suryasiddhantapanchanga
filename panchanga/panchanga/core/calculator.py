"""
Main Panchanga Calculator.

This module provides the main PanchangaCalculator class that orchestrates
all Panchanga calculations using the modular components.
"""

import math
from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime

from panchanga.core.constants import EPSILON
from panchanga.core.math_utils import MathUtils
from panchanga.core.date_utils import DateUtils
from panchanga.core.astronomical import AstronomicalCalculator
from panchanga.models.settings import PanchangaSettings
from panchanga.data.names import (
    get_weekday_name, get_masa_name, get_saura_masa_name,
    get_tithi_name, get_paksha_name, get_karana_name,
    get_yoga_name, get_nakshatra_name, get_jovian_year_name,
    get_jovian_year_name_south, get_adhimasa_prefix, _get_karana_name_math
)
from panchanga.data.planetary import (
    get_yuga_rotations, get_planetary_constants, calculate_derived_constants
)

# Optional: Drik ephemeris for accurate sunrise/sunset
try:
    from panchanga.core.drik_ephemeris import DrikEphemeris
    DRIK_AVAILABLE = True
except ImportError:
    DRIK_AVAILABLE = False
    DrikEphemeris = None


class PanchangaCalculator:
    """
    Main Panchanga Calculator class.
    
    This class provides complete Panchanga calculations for any given date,
    including all five elements (Tithi, Nakshatra, Yoga, Karana, Vara)
    and additional calendar information.
    """
    
    def __init__(self, settings: Optional[PanchangaSettings] = None):
        """
        Initialize Panchanga Calculator.
        
        Args:
            settings: Calculation settings (uses defaults if not provided)
        """
        self.settings = settings or PanchangaSettings()
        self._init_calculator()
        self._init_cache()
    
    def _init_calculator(self):
        """Initialize the astronomical calculator with current settings."""
        # Get rotation and planetary constants based on tradition/system
        tradition = self.settings.tradition
        system = self.settings.selected_system
        
        # For now, use the system setting to choose constants
        if system == 'InPancasiddhantika':
            from panchanga.data.planetary import (
                PANCASIDDHANTIKA_ROTATIONS, PANCASIDDHANTIKA_PLANETARY
            )
            rotations = PANCASIDDHANTIKA_ROTATIONS
            planetary = PANCASIDDHANTIKA_PLANETARY
        else:
            from panchanga.data.planetary import (
                SURYA_SIDDHANTA_ROTATIONS, SURYA_SIDDHANTA_PLANETARY
            )
            rotations = SURYA_SIDDHANTA_ROTATIONS
            planetary = SURYA_SIDDHANTA_PLANETARY
        
        self.astro = AstronomicalCalculator(rotations, planetary)
        self._derived = calculate_derived_constants(rotations)
        
        # Store rotation dict for compatibility
        self.YugaRotation = rotations.to_dict()
        self.YugaCivilDays = self._derived['YugaCivilDays']
    
    def _init_cache(self):
        """Initialize cache for expensive calculations."""
        self._back_clong_ahar = -1
        self._back_nclong_ahar = -1
        self._back_clong = -1
        self._back_nclong = -1
    
    def _clear_cache(self):
        """Clear calculation cache."""
        self._init_cache()
        self.astro.clear_cache()
    
    def _calculate_drik_sunrise_sunset(
        self,
        year: int,
        month: int,
        day: int
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Calculate sunrise/sunset using Drik ephemeris (Skyfield).
        
        This method provides high-accuracy sunrise/sunset times based on
        modern ephemeris calculations using Skyfield library, accounting for 
        atmospheric refraction and topocentric corrections.
        
        Note: Only works for years 1-9999 (CE dates) due to Python datetime limitations.
        For BCE dates, automatically falls back to traditional method.
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            
        Returns:
            Tuple of ((sunrise_hour, sunrise_minute), (sunset_hour, sunset_minute))
            or None if Drik calculation fails
        """
        if not DRIK_AVAILABLE:
            return None
        
        # Check if year is within datetime module's valid range
        if year < 1 or year > 9999:
            # BCE dates or far future dates - cannot use datetime, fall back to traditional
            return None
        
        try:
            drik = DrikEphemeris()
            date = datetime(year, month, day)
            
            # Calculate timezone offset for India (IST = UTC+5:30)
            # You can make this configurable in the future
            timezone_offset = 5.5
            
            sunrise, sunset = drik.calculate_sunrise_sunset(
                date,
                self.settings.loc_lat,
                self.settings.loc_lon,
                0.0,  # elevation - can be made configurable
                timezone_offset
            )
            
            return sunrise, sunset
            
        except Exception as e:
            # Log error but don't crash - fallback to traditional method
            # Only print warning for unexpected errors (not datetime range errors)
            if "year must be in" not in str(e):
                print(f"Warning: Drik ephemeris calculation failed: {e}")
            return None
    
    # =========================================================================
    # Tithi and Paksha Calculations
    # =========================================================================
    
    def get_tithi_set(self, tithi: float) -> Tuple[int, float]:
        """
        Get tithi day and fraction.
        
        Args:
            tithi: Tithi as float (0-30)
            
        Returns:
            Tuple of (tithi_day, fraction)
        """
        tithi_day = MathUtils.trunc(tithi) + 1
        ftithi = MathUtils.frac(tithi)
        return (tithi_day, ftithi)
    
    def set_sukla_krsna(self, tithi_day: int) -> Tuple[int, str, str]:
        """
        Determine paksha from tithi day.
        
        Args:
            tithi_day: Tithi day (1-30)
            
        Returns:
            Tuple of (adjusted_tithi_day, sukla_krsna, paksa)
        """
        if tithi_day > 15:
            tithi_day = tithi_day - 15
            paksa = 'Krsnapaksa'
        else:
            paksa = 'Suklapaksa'
        sukla_krsna = paksa
        return (tithi_day, sukla_krsna, paksa)
    
    # =========================================================================
    # Conjunction and Masa Calculations
    # =========================================================================
    
    def get_clong(self, ahar: float, tithi: float) -> float:
        """
        Get longitude at last conjunction.
        
        Args:
            ahar: Ahargana
            tithi: Current tithi
            
        Returns:
            Solar longitude at last conjunction
        """
        new_new = self.YugaCivilDays / (self.YugaRotation['moon'] - self.YugaRotation['sun'])
        search_ahar = ahar - tithi * (new_new / 30)
        
        if abs(search_ahar - self._back_clong_ahar) < 1:
            return self._back_clong
        elif abs(search_ahar - self._back_nclong_ahar) < 1:
            self._back_clong_ahar = self._back_nclong_ahar
            self._back_clong = self._back_nclong
            return self._back_nclong
        else:
            self._back_clong_ahar = search_ahar
            self._back_clong = self.astro.get_conjunction(search_ahar)
            return self._back_clong
    
    def get_nclong(self, ahar: float, tithi: float) -> float:
        """
        Get longitude at next conjunction.
        
        Args:
            ahar: Ahargana
            tithi: Current tithi
            
        Returns:
            Solar longitude at next conjunction
        """
        new_new = self.YugaCivilDays / (self.YugaRotation['moon'] - self.YugaRotation['sun'])
        search_ahar = ahar + (30 - tithi) * (new_new / 30)
        
        if abs(search_ahar - self._back_nclong_ahar) < 1:
            return self._back_nclong
        else:
            self._back_nclong_ahar = search_ahar
            self._back_nclong = self.astro.get_conjunction(search_ahar)
            return self._back_nclong
    
    def adhimasa_p(self, clong: float, nclong: float) -> bool:
        """Check if current month is adhimasa (intercalary)."""
        return MathUtils.trunc(clong / 30) == MathUtils.trunc(nclong / 30)
    
    def get_adhimasa(self, clong: float, nclong: float, language: str = 'telugu') -> str:
        """Get adhimasa prefix if applicable."""
        if self.adhimasa_p(clong, nclong):
            return get_adhimasa_prefix(language)
        return ""
    
    def get_masa_num(self, tslong: float, clong: float) -> int:
        """
        Get lunar month number.
        
        Args:
            tslong: True solar longitude
            clong: Longitude at last conjunction
            
        Returns:
            Masa number (0-11, 0=Chaitra)
        """
        masa_num = MathUtils.trunc(tslong / 30) % 12
        if (MathUtils.trunc(clong / 30) % 12) == masa_num:
            masa_num += 1
        masa_num = (masa_num + 12) % 12
        return masa_num
    
    # =========================================================================
    # Solar Month Calculations
    # =========================================================================
    
    def today_saura_masa_first_p(self, ahar: float) -> Tuple[bool, Optional[float]]:
        """Check if today is first day of solar month."""
        desantara = self.settings.desantara
        tslong_today = self.astro.get_true_solar_longitude(ahar - desantara)
        tslong_tomorrow = self.astro.get_true_solar_longitude(ahar - desantara + 1)
        
        tslong_today = tslong_today - int(tslong_today / 30) * 30
        tslong_tomorrow = tslong_tomorrow - int(tslong_tomorrow / 30) * 30
        
        if tslong_today > 25 and tslong_tomorrow < 5:
            samkranti = self.astro.find_samkranti(ahar, ahar + 1) + desantara
            return (True, samkranti)
        return (False, None)
    
    def get_saura_masa_day(self, ahar: float) -> Tuple[int, int, Optional[float]]:
        """
        Get solar month and day.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Tuple of (month_num, day, samkranti_ahar or None)
        """
        ahar = MathUtils.trunc(ahar)
        is_first, samkranti = self.today_saura_masa_first_p(ahar)
        
        if is_first:
            day = 1
            desantara = self.settings.desantara
            tslong_tomorrow = self.astro.get_true_solar_longitude(ahar + 1)
            month = MathUtils.trunc(tslong_tomorrow / 30) % 12
            month = (month + 12) % 12
            return (month, day, samkranti)
        else:
            month, day, samkranti = self.get_saura_masa_day(ahar - 1)
            day = day + 1
            return (month, day, samkranti)
    
    def get_saura_masa_day_simple(self, ahar: float) -> Tuple[int, int]:
        """
        Get solar month and day without samkranti computation.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Tuple of (month_num, day)
        """
        month, day, _ = self.get_saura_masa_day(ahar)
        return (month, day)
    
    # =========================================================================
    # Element Timing Calculations
    # =========================================================================
    
    def _get_elements_at_ahar(self, ahar: float, language: str) -> dict:
        """Get panchanga elements at a given ahargana."""
        tslong = self.astro.get_true_solar_longitude(ahar)
        tllong = self.astro.get_true_lunar_longitude(ahar)
        
        tithi = self.astro.get_tithi(tllong, tslong)
        tithi_day, ftithi = self.get_tithi_set(tithi)
        tithi_day, sukla_krsna, paksa = self.set_sukla_krsna(tithi_day)
        
        nakshatra = get_nakshatra_name(tllong, language)
        karana = get_karana_name(tithi, language)
        yoga = get_yoga_name(tslong, tllong, language)
        
        return {
            'tithi_day': tithi_day,
            'tithi': tithi,
            'sukla_krsna': sukla_krsna,
            'paksa': paksa,
            'nakshatra': nakshatra,
            'karana': karana,
            'yoga': yoga
        }
    
    def _get_element_avg_duration(self, element_name: str) -> float:
        """
        Get average duration of an element in days.
        
        - Nakshatra: 360°/27 ≈ 13.33° span, Moon moves ~13.2°/day → ~1.01 days
        - Yoga: 360°/27 ≈ 13.33° span, Sun+Moon ~14.2°/day → ~0.94 days
        - Karana: Half a tithi → ~0.49 days
        - Tithi: 12° span, elongation ~12.2°/day → ~0.98 days
        """
        durations = {
            'nakshatra': 1.01,
            'yoga': 0.94,
            'karana': 0.49,
            'tithi': 0.98
        }
        return durations.get(element_name, 1.0)
    
    def _find_element_start_time(
        self,
        ahar: float,
        element_name: str,
        current_value: Any,
        language: str
    ) -> float:
        """
        Find start time of current element using pure binary search.
        
        Halves the search window each iteration - O(log n) complexity.
        """
        # We know: at 'ahar' the element IS the current_value
        # We need to find where it started (transition from NOT current_value to current_value)
        
        # Set initial bounds
        right = ahar  # Element IS current_value here
        left = ahar - 1.5  # Max 1.5 days back - element should NOT be current_value here
        
        # Verify left bound is actually different
        left_elements = self._get_elements_at_ahar(left, language)
        if left_elements[element_name] == current_value:
            # Element spans more than 1.5 days - unusual, return start of day
            return int(ahar)
        
        # Pure binary search - halve the window each time
        tolerance = 0.00001  # ~0.86 seconds
        
        while right - left > tolerance:
            mid = (left + right) / 2
            elements = self._get_elements_at_ahar(mid, language)
            
            if elements[element_name] == current_value:
                # Transition is before mid (or at mid)
                right = mid
            else:
                # Transition is after mid
                left = mid
        
        return (left + right) / 2
    
    def _find_element_end_time(
        self,
        ahar: float,
        element_name: str,
        current_value: Any,
        language: str
    ) -> float:
        """
        Find end time of current element using pure binary search.
        
        Halves the search window each iteration - O(log n) complexity.
        """
        # We know: at 'ahar' the element IS the current_value
        # We need to find where it ends (transition from current_value to NOT current_value)
        
        # Set initial bounds
        left = ahar  # Element IS current_value here
        right = ahar + 1.5  # Max 1.5 days ahead - element should NOT be current_value here
        
        # Verify right bound is actually different
        right_elements = self._get_elements_at_ahar(right, language)
        if right_elements[element_name] == current_value:
            # Element spans more than 1.5 days - unusual, return end of day
            return math.ceil(ahar)
        
        # Pure binary search - halve the window each time
        tolerance = 0.00001  # ~0.86 seconds
        
        while right - left > tolerance:
            mid = (left + right) / 2
            elements = self._get_elements_at_ahar(mid, language)
            
            if elements[element_name] == current_value:
                # Transition is after mid
                left = mid
            else:
                # Transition is before mid (or at mid)
                right = mid
        
        return (left + right) / 2
    
    def _find_tithi_start_time(
        self,
        ahar: float,
        current_tithi_day: int,
        current_paksa: str,
        language: str,
        tithi_fraction: float = None
    ) -> float:
        """
        Find start time of current tithi using pure binary search.
        
        Halves the search window each iteration - O(log n) complexity.
        """
        # We know: at 'ahar' the tithi IS the target
        # We need to find where it started (transition from NOT target to target)
        
        # Set initial bounds
        right = ahar  # Tithi IS target here
        left = ahar - 1.5  # Max 1.5 days back - tithi should NOT be target here
        
        # Verify left bound is actually different tithi
        left_elements = self._get_elements_at_ahar(left, language)
        left_is_same = (left_elements['tithi_day'] == current_tithi_day and 
                        left_elements['paksa'] == current_paksa)
        
        if left_is_same:
            # Tithi spans more than 1.5 days - unusual, return start of day
            return int(ahar)
        
        # Pure binary search - halve the window each time
        tolerance = 0.00001  # ~0.86 seconds
        
        while right - left > tolerance:
            mid = (left + right) / 2
            elements = self._get_elements_at_ahar(mid, language)
            is_target = (elements['tithi_day'] == current_tithi_day and 
                         elements['paksa'] == current_paksa)
            
            if is_target:
                # Transition is before mid (or at mid)
                right = mid
            else:
                # Transition is after mid
                left = mid
        
        return (left + right) / 2
    
    def _find_tithi_end_time(
        self,
        ahar: float,
        current_tithi_day: int,
        current_paksa: str,
        language: str,
        tithi_fraction: float = None
    ) -> float:
        """
        Find end time of current tithi using pure binary search.
        
        Halves the search window each iteration - O(log n) complexity.
        """
        # We know: at 'ahar' the tithi IS the target
        # We need to find where it ends (transition from target to NOT target)
        
        # Set initial bounds
        left = ahar  # Tithi IS target here
        right = ahar + 1.5  # Max 1.5 days ahead - tithi should NOT be target here
        
        # Verify right bound is actually different tithi
        right_elements = self._get_elements_at_ahar(right, language)
        right_is_same = (right_elements['tithi_day'] == current_tithi_day and 
                         right_elements['paksa'] == current_paksa)
        
        if right_is_same:
            # Tithi spans more than 1.5 days - unusual, return end of day
            return math.ceil(ahar)
        
        # Pure binary search - halve the window each time
        tolerance = 0.00001  # ~0.86 seconds
        
        while right - left > tolerance:
            mid = (left + right) / 2
            elements = self._get_elements_at_ahar(mid, language)
            is_target = (elements['tithi_day'] == current_tithi_day and 
                         elements['paksa'] == current_paksa)
            
            if is_target:
                # Transition is after mid
                left = mid
            else:
                # Transition is before mid (or at mid)
                right = mid
        
        return (left + right) / 2
    
    # =========================================================================
    # Linear Search Methods (Old approach - for comparison)
    # =========================================================================
    
    def _find_tithi_start_time_linear(
        self,
        ahar: float,
        current_tithi_day: int,
        current_paksa: str,
        language: str,
        max_search_days: int = 2
    ) -> float:
        """
        Find start time of current tithi using LINEAR search (old approach).
        
        This is O(n) complexity - kept for comparison with optimized version.
        """
        step = 0.00025  # ~21.6 seconds
        search_ahar = ahar
        start_ahar = ahar - max_search_days
        
        while search_ahar >= start_ahar:
            elements = self._get_elements_at_ahar(search_ahar, language)
            if elements['tithi_day'] != current_tithi_day or elements['paksa'] != current_paksa:
                return self._refine_transition_time_linear(
                    search_ahar, search_ahar + step,
                    lambda a: (
                        self._get_elements_at_ahar(a, language)['tithi_day'] == current_tithi_day and
                        self._get_elements_at_ahar(a, language)['paksa'] == current_paksa
                    )
                )
            search_ahar -= step
        
        return int(ahar)
    
    def _find_tithi_end_time_linear(
        self,
        ahar: float,
        current_tithi_day: int,
        current_paksa: str,
        language: str,
        max_search_days: int = 2
    ) -> float:
        """
        Find end time of current tithi using LINEAR search (old approach).
        
        This is O(n) complexity - kept for comparison with optimized version.
        """
        step = 0.00025
        search_ahar = ahar
        end_ahar = ahar + max_search_days
        
        while search_ahar <= end_ahar:
            elements = self._get_elements_at_ahar(search_ahar, language)
            if elements['tithi_day'] != current_tithi_day or elements['paksa'] != current_paksa:
                return self._refine_transition_time_linear(
                    search_ahar - step, search_ahar,
                    lambda a: (
                        self._get_elements_at_ahar(a, language)['tithi_day'] == current_tithi_day and
                        self._get_elements_at_ahar(a, language)['paksa'] == current_paksa
                    ),
                    find_start=False  # Finding end (TRUE→FALSE transition)
                )
            search_ahar += step
        
        return math.ceil(ahar)
    
    def _find_element_start_time_linear(
        self,
        ahar: float,
        element_name: str,
        current_value: Any,
        language: str,
        max_search_days: int = 2
    ) -> float:
        """
        Find start time of current element using LINEAR search (old approach).
        
        This is O(n) complexity - kept for comparison with optimized version.
        """
        step = 0.00025  # ~21.6 seconds
        search_ahar = ahar
        start_ahar = ahar - max_search_days
        
        while search_ahar >= start_ahar:
            elements = self._get_elements_at_ahar(search_ahar, language)
            if elements[element_name] != current_value:
                return self._refine_transition_time_linear(
                    search_ahar, search_ahar + step,
                    lambda a: self._get_elements_at_ahar(a, language)[element_name] == current_value
                )
            search_ahar -= step
        
        return int(ahar)
    
    def _find_element_end_time_linear(
        self,
        ahar: float,
        element_name: str,
        current_value: Any,
        language: str,
        max_search_days: int = 2
    ) -> float:
        """
        Find end time of current element using LINEAR search (old approach).
        
        This is O(n) complexity - kept for comparison with optimized version.
        """
        step = 0.00025
        search_ahar = ahar
        end_ahar = ahar + max_search_days
        
        while search_ahar <= end_ahar:
            elements = self._get_elements_at_ahar(search_ahar, language)
            if elements[element_name] != current_value:
                return self._refine_transition_time_linear(
                    search_ahar - step, search_ahar,
                    lambda a: self._get_elements_at_ahar(a, language)[element_name] == current_value,
                    find_start=False  # Finding end (TRUE→FALSE transition)
                )
            search_ahar += step
        
        return math.ceil(ahar)
    
    def _refine_transition_time_linear(
        self,
        left_ahar: float,
        right_ahar: float,
        is_current_element,
        find_start: bool = True
    ) -> float:
        """
        Refine transition time using binary search (used by linear search methods).
        
        Args:
            find_start: True if finding start (FALSE→TRUE transition), 
                       False if finding end (TRUE→FALSE transition)
        """
        tolerance = 0.00001  # ~0.86 seconds
        left = left_ahar
        right = right_ahar
        
        if is_current_element(left) == is_current_element(right):
            return left
        
        while right - left > tolerance:
            mid = (left + right) / 2
            if find_start:
                # Finding start: left=FALSE, right=TRUE, looking for FALSE→TRUE
                if is_current_element(mid):
                    right = mid  # Transition is before mid
                else:
                    left = mid   # Transition is after mid
            else:
                # Finding end: left=TRUE, right=FALSE, looking for TRUE→FALSE
                if is_current_element(mid):
                    left = mid   # Transition is after mid
                else:
                    right = mid  # Transition is before mid
        
        return (left + right) / 2
    
    # =========================================================================
    # Comparison Method
    # =========================================================================
    
    def compare_timing_methods(
        self,
        ahar: float,
        tithi_day: int,
        paksa: str,
        language: str,
        tithi_fraction: float = None
    ) -> dict:
        """
        Compare results from optimized vs linear timing search methods.
        
        Returns a dict with both results and timing differences.
        Useful for validating the optimized approach.
        """
        import time
        
        results = {}
        
        # Optimized tithi timing
        start_time = time.perf_counter()
        opt_tithi_start = self._find_tithi_start_time(ahar, tithi_day, paksa, language, tithi_fraction)
        opt_tithi_end = self._find_tithi_end_time(ahar, tithi_day, paksa, language, tithi_fraction)
        opt_duration = time.perf_counter() - start_time
        
        # Linear tithi timing
        start_time = time.perf_counter()
        lin_tithi_start = self._find_tithi_start_time_linear(ahar, tithi_day, paksa, language)
        lin_tithi_end = self._find_tithi_end_time_linear(ahar, tithi_day, paksa, language)
        lin_duration = time.perf_counter() - start_time
        
        results['tithi'] = {
            'optimized': {
                'start_ahar': opt_tithi_start,
                'end_ahar': opt_tithi_end,
                'start_time': self._ahar_to_time(opt_tithi_start),
                'end_time': self._ahar_to_time(opt_tithi_end),
                'duration_ms': opt_duration * 1000
            },
            'linear': {
                'start_ahar': lin_tithi_start,
                'end_ahar': lin_tithi_end,
                'start_time': self._ahar_to_time(lin_tithi_start),
                'end_time': self._ahar_to_time(lin_tithi_end),
                'duration_ms': lin_duration * 1000
            },
            'difference': {
                'start_ahar_diff': abs(opt_tithi_start - lin_tithi_start),
                'end_ahar_diff': abs(opt_tithi_end - lin_tithi_end),
                'start_seconds_diff': abs(opt_tithi_start - lin_tithi_start) * 86400,
                'end_seconds_diff': abs(opt_tithi_end - lin_tithi_end) * 86400,
                'speedup': lin_duration / opt_duration if opt_duration > 0 else 0
            }
        }
        
        return results
    
    def get_ahar_at_sunrise(self, year: int, month: int, day: int) -> dict:
        """
        Calculate ahargana with all intermediate values for a given date.
        
        This method exposes the step-by-step calculation for debugging.
        MATCHES EXACTLY what calculate() uses for longitude calculations.
        
        NOTE: Despite the name, this returns MIDNIGHT ahargana (ahar_final),
        which is the value used for all planetary longitude calculations
        to maintain Kali Yuga epoch consistency.
        
        The eqtime (daylight equation) is returned but is ONLY used for
        sunrise/sunset DISPLAY, not for longitude calculations.
        
        Key values returned:
        - ahar_raw: Days since Kali epoch at noon
        - desantara: Longitude correction from IST meridian
        - ahar_final: MIDNIGHT ahargana = ahar_raw - desantara (USED FOR ALL CALCS)
        - eqtime: Daylight equation (FOR DISPLAY ONLY)
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            
        Returns:
            Dictionary with all intermediate calculation values
        """
        julian_day = DateUtils.modern_date_to_julian_day(year, month, day)
        ahar_raw = DateUtils.julian_day_to_ahargana(julian_day)
        
        # Desantara correction (calculations at midnight)
        desantara = self.settings.desantara
        ahar_final = ahar_raw - desantara  # This is what's used for longitude calculations
        
        # Time of sunrise at local latitude (for sunrise/sunset DISPLAY only)
        eqtime = self.astro.get_daylight_equation(year, self.settings.loc_lat, ahar_final)
        
        return {
            'julian_day': julian_day,
            'kali_epoch_jd': DateUtils.KALI_EPOCH_JD,
            'ahar_raw': ahar_raw,
            'desantara': desantara,
            'eqtime': eqtime,  # For sunrise/sunset display only
            'ahar_final': ahar_final,  # FRACTIONAL - used for longitude calculations (at midnight)
        }
    
    def _ahar_to_time(self, ahar: float) -> Tuple[int, int]:
        """Convert ahargana to time of day."""
        desantara = self.settings.desantara
        adjusted_ahar = ahar + desantara
        hours = MathUtils.trunc(MathUtils.frac(adjusted_ahar) * 24)
        minutes = MathUtils.trunc(60 * MathUtils.frac(MathUtils.frac(adjusted_ahar) * 24))
        return (hours, minutes)
    
    def _ahar_to_datetime(self, ahar: float) -> dict:
        """Convert ahargana to date and time dict."""
        desantara = self.settings.desantara
        julian_day = DateUtils.ahargana_to_julian_day(ahar)
        year, month, day = DateUtils.julian_day_to_modern_date(julian_day)
        adjusted_ahar = ahar + desantara
        hours = MathUtils.trunc(MathUtils.frac(adjusted_ahar) * 24)
        minutes = MathUtils.trunc(60 * MathUtils.frac(MathUtils.frac(adjusted_ahar) * 24))
        return {'year': year, 'month': month, 'day': day, 'hours': hours, 'minutes': minutes}
    
    # =========================================================================
    # Main Calculation Method
    # =========================================================================
    
    def calculate(
        self,
        year: int,
        month: int,
        day: int,
        include_timing: bool = True
    ) -> dict:
        """
        Main calculation for a given date.
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            include_timing: Whether to calculate element start/end times (expensive operation)
            
        Returns:
            Dictionary with all Panchanga data
        """
        self._init_calculator()
        
        srushtiAdiAhargana = 714402296627
        julian_day = DateUtils.modern_date_to_julian_day(year, month, day)
        ahar = DateUtils.julian_day_to_ahargana(julian_day) 
        julian_day_int = int(julian_day + 0.5)
        #ahar = ahar + srushtiAdiAhargana
        ahargana = int(ahar + 0.5)
        
        language = self.settings.language or 'telugu'
        weekday_name = get_weekday_name(MathUtils.trunc(julian_day_int + 0.5) % 7, language)
        # Ayanamsa calculation (using original ahar before corrections)
        ayanadeg, ayanamin = self.astro.get_ayanamsa(ahar)
        
        # Desantara correction (calculations at midnight - Surya Siddhanta epoch baseline)
        desantara = self.settings.desantara
        ahar_midnight = ahar - desantara
        
        # Time of sunrise at local latitude (for sunrise/sunset display and civil day determination)
        eqtime = self.astro.get_daylight_equation(year, self.settings.loc_lat, ahar_midnight)
        
        # Calculate sunrise/sunset using Drik or traditional method
        sunrise_fraction = 0  # Fraction of day to add for sunrise
        if self.settings.use_drik_sunrise_sunset and DRIK_AVAILABLE:
            # Use Drik ephemeris for accurate sunrise/sunset
            drik_times = self._calculate_drik_sunrise_sunset(year, month, day)
            if drik_times:
                sriseh, srisem = drik_times[0]
                sseth, ssetm = drik_times[1]
                # Convert sunrise time to fraction of day
                sunrise_fraction = (sriseh + srisem / 60.0) / 24.0
            else:
                # Fallback to traditional if Drik fails
                sriseh, srisem = self.astro.get_sunrise_time(eqtime)
                sseth, ssetm = self.astro.get_sunset_time(eqtime)
                sunrise_fraction = (sriseh + srisem / 60.0) / 24.0
        else:
            # Use traditional Surya Siddhanta method
            sriseh, srisem = self.astro.get_sunrise_time(eqtime)
            sseth, ssetm = self.astro.get_sunset_time(eqtime)
            sunrise_fraction = (sriseh + srisem / 60.0) / 24.0
        
        # IMPORTANT: For epoch consistency and mean longitude calculations,
        # we use MIDNIGHT ahargana. This preserves Kali Yuga epoch accuracy.
        # The sunrise correction should ONLY be applied for determining the
        # "ruling tithi" of the civil day, not for the underlying calculations.
        
        # Option 1: Calculate at midnight (preserves epoch, traditional for mean longitudes)
        # Option 2: Calculate at sunrise (for civil day determination)
        # We use a setting to control this behavior
        use_sunrise_for_tithi = getattr(self.settings, 'use_sunrise_for_tithi', False)
        
        if use_sunrise_for_tithi:
            # Calculate at actual sunrise moment (for civil day determination)
            ahar_for_calc = ahar_midnight + sunrise_fraction
        else:
            # Calculate at midnight (preserves epoch, traditional Surya Siddhanta)
            ahar_for_calc = ahar_midnight
        
        # True sun and moon longitudes
        # CRITICAL: This uses ahar_for_calc which is either midnight or sunrise
        # Midnight = epoch consistent, Sunrise = civil day ruling tithi
        tslong = self.astro.get_true_solar_longitude(ahar_for_calc)
        tllong = self.astro.get_true_lunar_longitude(ahar_for_calc)
        
        # Tithi calculation
        tithi = self.astro.get_tithi(tllong, tslong)
        tithi_day, ftithi = self.get_tithi_set(tithi)
        tithi_day, sukla_krsna, paksa = self.set_sukla_krsna(tithi_day)
        
        # Conjunction longitudes
        clong = self.get_clong(ahar_for_calc, tithi)
        nclong = self.get_nclong(ahar_for_calc, tithi)
        
        # Masa
        adhimasa = self.get_adhimasa(clong, nclong, language)
        masa_num = self.get_masa_num(tslong, clong)
        masa = get_masa_name(masa_num, language)
        
        # Solar month
        saura_masa_num, saura_masa_day = self.get_saura_masa_day_simple(ahar_for_calc)
        saura_masa = get_saura_masa_name(saura_masa_num, language)
        
        # Nakshatra, Karana, Yoga
        nakshatra = get_nakshatra_name(tllong, language)
        karana = get_karana_name(tithi, language)
        yoga = get_yoga_name(tslong, tllong, language)
        
        # Timing calculations (expensive - can be skipped for faster computation)
        if include_timing:
            tithi_start_ahar = self._find_tithi_start_time(ahar_for_calc, tithi_day, paksa, language, ftithi)
            tithi_end_ahar = self._find_tithi_end_time(ahar_for_calc, tithi_day, paksa, language, ftithi)
            
            nakshatra_start_ahar = self._find_element_start_time(ahar_for_calc, 'nakshatra', nakshatra, language)
            nakshatra_end_ahar = self._find_element_end_time(ahar_for_calc, 'nakshatra', nakshatra, language)
            
            yoga_start_ahar = self._find_element_start_time(ahar_for_calc, 'yoga', yoga, language)
            yoga_end_ahar = self._find_element_end_time(ahar_for_calc, 'yoga', yoga, language)
            
            karana_start_ahar = self._find_element_start_time(ahar_for_calc, 'karana', karana, language)
            karana_end_ahar = self._find_element_end_time(ahar_for_calc, 'karana', karana, language)
            
            # Convert to time
            tithi_start_time = self._ahar_to_time(tithi_start_ahar)
            tithi_end_time = self._ahar_to_time(tithi_end_ahar)
            nakshatra_start_time = self._ahar_to_time(nakshatra_start_ahar)
            nakshatra_end_time = self._ahar_to_time(nakshatra_end_ahar)
            yoga_start_time = self._ahar_to_time(yoga_start_ahar)
            yoga_end_time = self._ahar_to_time(yoga_end_ahar)
            karana_start_time = self._ahar_to_time(karana_start_ahar)
            karana_end_time = self._ahar_to_time(karana_end_ahar)
            
            # Convert to datetime
            tithi_start_ahar_raw = tithi_start_ahar + eqtime + desantara
            tithi_end_ahar_raw = tithi_end_ahar + eqtime + desantara
            tithi_start_datetime = self._ahar_to_datetime(tithi_start_ahar_raw)
            tithi_end_datetime = self._ahar_to_datetime(tithi_end_ahar_raw)
            
            nakshatra_start_datetime = self._ahar_to_datetime(nakshatra_start_ahar + eqtime + desantara)
            nakshatra_end_datetime = self._ahar_to_datetime(nakshatra_end_ahar + eqtime + desantara)
            yoga_start_datetime = self._ahar_to_datetime(yoga_start_ahar + eqtime + desantara)
            yoga_end_datetime = self._ahar_to_datetime(yoga_end_ahar + eqtime + desantara)
            karana_start_datetime = self._ahar_to_datetime(karana_start_ahar + eqtime + desantara)
            karana_end_datetime = self._ahar_to_datetime(karana_end_ahar + eqtime + desantara)
        else:
            tithi_start_ahar = self._find_tithi_start_time(ahar_for_calc, tithi_day, paksa, language, ftithi)
            tithi_end_ahar = self._find_tithi_end_time(ahar_for_calc, tithi_day, paksa, language, ftithi)

            tithi_start_time = self._ahar_to_time(tithi_start_ahar)
            tithi_end_time = self._ahar_to_time(tithi_end_ahar)

            # Convert to datetime
            tithi_start_ahar_raw = tithi_start_ahar + eqtime + desantara
            tithi_end_ahar_raw = tithi_end_ahar + eqtime + desantara
            tithi_start_datetime = self._ahar_to_datetime(tithi_start_ahar_raw)
            tithi_end_datetime = self._ahar_to_datetime(tithi_end_ahar_raw)

            # Default values when timing is skipped
            #tithi_start_time = tithi_end_time = (0, 0)
            nakshatra_start_time = nakshatra_end_time = (0, 0)
            yoga_start_time = yoga_end_time = (0, 0)
            karana_start_time = karana_end_time = (0, 0)
            #tithi_start_datetime = tithi_end_datetime = None
            nakshatra_start_datetime = nakshatra_end_datetime = None
            yoga_start_datetime = yoga_end_datetime = None
            karana_start_datetime = karana_end_datetime = None
        
        # Placeholder for masa timing (simplified)
        masa_start_time = (0, 0)
        masa_end_time = (0, 0)
        masa_start_datetime = None
        masa_end_datetime = None
        
        # Era calculations
        year_kali = self.astro.ahargana_to_kali(ahar_for_calc + (4 - masa_num) * 30)
        year_saka = DateUtils.kali_to_saka(year_kali)
        year_vikrama = year_saka + 135
        
        jovian_year_north = get_jovian_year_name(year_kali, language)
        jovian_year_south = get_jovian_year_name_south(year_kali, language)
        
        # Names
        tithi_name = get_tithi_name(tithi_day, paksa, language)
        paksha_name = get_paksha_name(paksa, language)
        
        return {
            'gregorian_date': (year, month, day),
            'weekday': weekday_name,
            'julian_day': julian_day_int,
            'ahargana': ahargana,
            'ayanamsa': (ayanadeg, ayanamin),
            'sunrise': (sriseh, srisem),
            'sunset': (sseth, ssetm),
            'year_saka': year_saka,
            'year_vikrama': year_vikrama,
            'year_kali': year_kali,
            'jovian_year_north': jovian_year_north,
            'jovian_year_south': jovian_year_south,
            'masa_num': masa_num,
            'masa': masa,
            'adhimasa': adhimasa,
            'paksa': paksa,
            'paksha_name': paksha_name,
            'sukla_krsna': sukla_krsna,
            'tithi_day': tithi_day,
            'tithi_name': tithi_name,
            'tithi_fraction': ftithi,
            'saura_masa_num': saura_masa_num,
            'saura_masa': saura_masa,
            'saura_masa_day': saura_masa_day,
            'nakshatra': nakshatra,
            'karana': karana,
            'yoga': yoga,
            'tithi_start_time': tithi_start_time,
            'tithi_end_time': tithi_end_time,
            'tithi_start_datetime': tithi_start_datetime,
            'tithi_end_datetime': tithi_end_datetime,
            'nakshatra_start_time': nakshatra_start_time,
            'nakshatra_end_time': nakshatra_end_time,
            'nakshatra_start_datetime': nakshatra_start_datetime,
            'nakshatra_end_datetime': nakshatra_end_datetime,
            'yoga_start_time': yoga_start_time,
            'yoga_end_time': yoga_end_time,
            'yoga_start_datetime': yoga_start_datetime,
            'yoga_end_datetime': yoga_end_datetime,
            'karana_start_time': karana_start_time,
            'karana_end_time': karana_end_time,
            'karana_start_datetime': karana_start_datetime,
            'karana_end_datetime': karana_end_datetime,
            'masa_start_time': masa_start_time,
            'masa_end_time': masa_end_time,
            'masa_start_datetime': masa_start_datetime,
            'masa_end_datetime': masa_end_datetime,
            'sun_longitude': tslong,
            'moon_longitude': tllong,
            'next_year_birthday': None,
            'next_years_birthdays': [],
            'next_ugadi_dates': [],
            'settings': {
                'system': self.settings.selected_system,
                'tradition': self.settings.tradition,
                'latitude': self.settings.loc_lat,
                'longitude': self.settings.loc_lon,
                'language': language
            }
        }
    
    def calculate_astronomical(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0
    ) -> dict:
        """
        Calculate astronomical elements at specified time (default: MIDNIGHT for epoch consistency).
        
        This method calculates elements that should use midnight baseline
        for Kali Yuga epoch consistency:
        - Yuga, Year, Era calculations
        - Solar month (Saura Masa)
        - Weekday (Vara)
        - Date conversions
        - Planetary positions
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            hour: Hour of day (0-23, default: 0 for midnight)
            minute: Minute (0-59, default: 0)
            
        Returns:
            Dictionary with astronomical/epoch-consistent calculations
        """
        self._init_calculator()
        
        # Date conversions with time support
        # modern_date_to_julian_day returns JD at noon, adjust for specified time
        julian_day_noon = DateUtils.modern_date_to_julian_day(year, month, day)

        # Convert time to fraction of day (noon = 0.5)
        time_fraction = (hour + minute / 60.0) / 24.0
        # Adjust from noon to specified time
        julian_day = julian_day_noon + time_fraction
        ahar_raw = DateUtils.julian_day_to_ahargana(julian_day)
        julian_day_int = int(julian_day_noon + 0.5)  # Keep integer JD at noon for weekday
        language = self.settings.language or 'english'
        weekday_name = get_weekday_name(MathUtils.trunc(julian_day_int + 0.5) % 7, language)
        
        # Desantara correction (calculations at specified time)
        desantara = self.settings.desantara
        ahar_at_time = ahar_raw - desantara
        
        # Ayanamsa (using original ahar before corrections)
        ayanadeg, ayanamin = self.astro.get_ayanamsa(ahar_raw)
        
        # Calculate sunrise for display (but not used in calculations)
        eqtime = self.astro.get_daylight_equation(year, self.settings.loc_lat, ahar_at_time)
        
        if self.settings.use_drik_sunrise_sunset and DRIK_AVAILABLE:
            drik_times = self._calculate_drik_sunrise_sunset(year, month, day)
            if drik_times:
                sriseh, srisem = drik_times[0]
                sseth, ssetm = drik_times[1]
            else:
                sriseh, srisem = self.astro.get_sunrise_time(eqtime)
                sseth, ssetm = self.astro.get_sunset_time(eqtime)
        else:
            sriseh, srisem = self.astro.get_sunrise_time(eqtime)
            sseth, ssetm = self.astro.get_sunset_time(eqtime)
        
        # ALL CALCULATIONS AT SPECIFIED TIME
        #tslong = self.astro.get_true_solar_longitude(ahar_at_time)
        #tllong = self.astro.get_true_lunar_longitude(ahar_at_time)
        
        tslong = self.astro.get_true_planet_longitude(ahar_raw,'sun',(self.settings.loc_lat, self.settings.loc_lon))
        tllong = self.astro.get_true_planet_longitude(ahar_raw,'moon',(self.settings.loc_lat, self.settings.loc_lon))
        
        # Solar month (at specified time)
        saura_masa_num, saura_masa_day = self.get_saura_masa_day_simple(ahar_at_time)
        saura_masa = get_saura_masa_name(saura_masa_num, language)
        
        # Era calculations (at specified time for epoch consistency)
        # Temporary tithi calculation for masa determination
        temp_tithi = self.astro.get_tithi(tllong, tslong)
        temp_clong = self.get_clong(ahar_at_time, temp_tithi)
        temp_nclong = self.get_nclong(ahar_at_time, temp_tithi)
        temp_masa_num = self.get_masa_num(tslong, temp_clong)
        
        year_kali = self.astro.ahargana_to_kali(ahar_at_time + (4 - temp_masa_num) * 30)
        year_saka = DateUtils.kali_to_saka(year_kali)
        year_vikrama = year_saka + 135
        
        jovian_year_north = get_jovian_year_name(year_kali, language)
        jovian_year_south = get_jovian_year_name_south(year_kali, language)
        
        # All planet positions (at specified time) - both simple and detailed
        all_planets = self.astro.get_all_planet_positions(ahar_at_time)
        all_planets_detailed = self.astro.get_all_planet_positions_detailed(ahar_at_time)
        
        # Determine calculation point description
        if hour == 0 and minute == 0:
            calc_point = 'midnight'
        else:
            calc_point = f'{hour:02d}:{minute:02d}'
        
        return {
            'calculation_point': calc_point,
            'calculation_time': (hour, minute),
            'gregorian_date': (year, month, day),
            'weekday': weekday_name,
            'julian_day': julian_day_int,
            'julian_day_at_time': julian_day,
            #'ahargana': ahargana,
            'ahar_at_time': ahar_at_time,
            'ahar_midnight': ahar_at_time if (hour == 0 and minute == 0) else None,  # For backward compat
            'time_fraction': time_fraction,
            'desantara': desantara,
            'ayanamsa': (ayanadeg, ayanamin),
            'sunrise': (sriseh, srisem),
            'sunset': (sseth, ssetm),
            'eqtime': eqtime,
            'year_saka': year_saka,
            'year_vikrama': year_vikrama,
            'year_kali': year_kali,
            'jovian_year_north': jovian_year_north,
            'jovian_year_south': jovian_year_south,
            'saura_masa_num': saura_masa_num,
            'saura_masa': saura_masa,
            'saura_masa_day': saura_masa_day,
            'sun_longitude': tslong,
            'moon_longitude': tllong,
            'planets': all_planets,
            'planets_detailed': all_planets_detailed,
            'settings': {
                'system': self.settings.selected_system,
                'tradition': self.settings.tradition,
                'latitude': self.settings.loc_lat,
                'longitude': self.settings.loc_lon,
                'language': language
            }
        }
    
    def calculate_civil_day(
        self,
        year: int,
        month: int,
        day: int,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        include_timing: bool = True,
        tslong: Optional[float] = None,
        tllong: Optional[float] = None,
        ahar_at_time: Optional[float] = None,
        sunrise_hour: int = None,
        sunrise_minute: int = None,
        sunset_hour: int = None,
        sunset_minute: int = None
    ) -> dict:
        """
        Calculate civil day elements at specified time or SUNRISE (day start).
        
        This method calculates elements that should use sunrise (day start)
        for traditional panchanga civil day determination:
        - Lunar month (Masa)
        - Tithi
        - Nakshatra
        - Yoga
        - Karana
        - Paksha
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            hour: Hour of day (0-23). If None, uses actual sunrise time.
            minute: Minute (0-59). If None, uses actual sunrise time.
            include_timing: Whether to calculate element start/end times
            tslong: pre-calculated true solar longitude.
            tllong: pre-calculated true lunar longitude.
            
        Returns:
            Dictionary with civil day / sunrise-based calculations
        """
        self._init_calculator()

        # Use passed values or calculate if not provided
        if sunrise_hour is not None and sunrise_minute is not None:
            sriseh, srisem = sunrise_hour, sunrise_minute
            sseth, ssetm = sunset_hour, sunset_minute
            sunrise_ahar = ahar_at_time
        else:
            astro_midnight = self.calculate_astronomical(year, month, day, 6, 0)
            sriseh, srisem = astro_midnight["sunrise"]
            sseth, ssetm = astro_midnight["sunset"]
            astro_sunrise = self.calculate_astronomical(year, month, day, sriseh, srisem)
            sunrise_ahar = astro_sunrise["ahar_at_time"]


        ## we expect these values to be passed for successful calculation
        if (tslong is None or
            tllong is None or
            ahar_at_time is None):
            return {}

        language = self.settings.language or 'english'

        # Get all tithis around sunrise - let observers decide ruling tithi based on tradition
        tithis_data = self.get_tithis_for_civil_day(
            year, month, day,
            sunrise_ahar=sunrise_ahar,
            sriseh=sriseh,
            srisem=srisem,
            sseth=sseth,
            ssetm=ssetm,
        )

        # The ruling tithi is the one that spans sunrise
        ruling_tithi = next((t for t in tithis_data["tithis"] if t["tithi_for_day"]), None)

        if ruling_tithi:
            ruling_tithi_day = ruling_tithi["day"]
            ruling_paksa = ruling_tithi["paksa"]
            tithi_start = ruling_tithi["start_ahar"]
            tithi_end = ruling_tithi["end_ahar"]
            sukla_krsna = ruling_tithi["sukla_krsna"]
        else:
            ruling_tithi = next((t for t in tithis_data["tithis"] if t["spans_sunrise"]), None)
            ruling_tithi_day = ruling_tithi["day"]
            ruling_paksa = ruling_tithi["paksa"]
            tithi_start = ruling_tithi["start_ahar"]
            tithi_end = ruling_tithi["end_ahar"]
            sukla_krsna = ruling_tithi["sukla_krsna"]



        # Conjunction longitudes (at specified time)
        clong = self.get_clong(ahar_at_time, ruling_tithi['tithi'])
        nclong = self.get_nclong(ahar_at_time, ruling_tithi['tithi'])
        
        # Masa (at specified time)
        adhimasa = self.get_adhimasa(clong, nclong, language)
        masa_num = self.get_masa_num(tslong, clong)
        masa = get_masa_name(masa_num, language)
        
        # Nakshatra, Karana, Yoga (at specified time)
        nakshatra = get_nakshatra_name(tllong, language)
        karana = get_karana_name(ruling_tithi['tithi'], language)

        yoga = get_yoga_name(tslong, tllong, language)
        
        # Get karanas list for the tithi (always, not just when include_timing)
        karanas_list = self._get_karanas_for_tithi(
            ruling_tithi['tithi'],
            tithi_start,
            tithi_end,
            language
        )

        kshaya_tithi = next((t for t in tithis_data["tithis"] if t["is_kshaya"]), None)
        if (kshaya_tithi is not None):
            kshaya_karanas_list = self._get_karanas_for_tithi(
                kshaya_tithi["tithi"],
                kshaya_tithi["start_ahar"],
                kshaya_tithi["end_ahar"],
                language
            )
            karanas_list.extend(kshaya_karanas_list)


        # Timing calculations
        if include_timing:
            nakshatra_start_ahar = self._find_element_start_time(ahar_at_time, 'nakshatra', nakshatra, language)
            nakshatra_end_ahar = self._find_element_end_time(ahar_at_time, 'nakshatra', nakshatra, language)
            
            yoga_start_ahar = self._find_element_start_time(ahar_at_time, 'yoga', yoga, language)
            yoga_end_ahar = self._find_element_end_time(ahar_at_time, 'yoga', yoga, language)
            
            karana_start_ahar = self._find_element_start_time(ahar_at_time, 'karana', karana, language)
            karana_end_ahar = self._find_element_end_time(ahar_at_time, 'karana', karana, language)
            # Convert to time
            tithi_start_time = self._ahar_to_time(tithi_start)
            tithi_end_time = self._ahar_to_time(tithi_end)
            nakshatra_start_time = self._ahar_to_time(nakshatra_start_ahar)
            nakshatra_end_time = self._ahar_to_time(nakshatra_end_ahar)
            yoga_start_time = self._ahar_to_time(yoga_start_ahar)
            yoga_end_time = self._ahar_to_time(yoga_end_ahar)
            karana_start_time = self._ahar_to_time(karana_start_ahar)
            karana_end_time = self._ahar_to_time(karana_end_ahar)
        else:
            tithi_start_time = tithi_end_time = (0, 0)
            nakshatra_start_time = nakshatra_end_time = (0, 0)
            yoga_start_time = yoga_end_time = (0, 0)
            karana_start_time = karana_end_time = (0, 0)

        # Names
        tithi_name = ruling_tithi['name']
        paksha_name = ruling_paksa
        
        # Sunrise fraction for backward compatibility
        sunrise_fraction = (sriseh + srisem / 60.0) / 24.0
        
        return {
            'calculation_point': 'sunrise',
            'gregorian_date': (year, month, day),
            'ahar_at_time': ahar_at_time,
            'sunrise_fraction': sunrise_fraction,
            'sunrise': (sriseh, srisem),
            'sunset': (sseth, ssetm),
            'masa_num': masa_num,
            'masa': masa,
            'adhimasa': adhimasa,
            'paksa': ruling_paksa,
            'paksha_name': paksha_name,
            'sukla_krsna': sukla_krsna,
            'tithi_day': ruling_tithi_day,
            'tithi_name': tithi_name,
            'tithis': tithis_data["tithis"],  # All tithis around sunrise for tradition-based selection
            'nakshatra': nakshatra,
            'karana': karana,
            'karanas': karanas_list,
            'yoga': yoga,
            'tithi_start_time': tithi_start_time,
            'tithi_end_time': tithi_end_time,
            'nakshatra_start_time': nakshatra_start_time,
            'nakshatra_end_time': nakshatra_end_time,
            'yoga_start_time': yoga_start_time,
            'yoga_end_time': yoga_end_time,
            'karana_start_time': karana_start_time,
            'karana_end_time': karana_end_time,
            'sun_longitude': tslong,
            'moon_longitude': tllong,
            'settings': {
                'system': self.settings.selected_system,
                'tradition': self.settings.tradition,
                'latitude': self.settings.loc_lat,
                'longitude': self.settings.loc_lon,
                'language': language
            }
        }

    def _get_karanas_for_tithi(
            self,
            tithi_index: float,  # Added this argument
            tithi_start_ahar: float,
            tithi_end_ahar: float,
            language: str
    ) -> List[dict]:
        """
        Get all karanas for a specific tithi.

        OPTIMIZATION:
        1. Reuse tithi_start (K1 Start) and tithi_end (K2 End).
        2. Use tithi_index to derive names mathematically (No planetary lookups).
        3. Only calculate the Midpoint (where K1 ends and K2 starts).
        """
        karanas = []

        # 1. Determine Karana 1 Name (Math only)
        # We are in the 1st half of this Tithi
        karana1_name = _get_karana_name_math(tithi_index, is_second_half=False, language=language)

        # 2. Find the Midpoint (The only astronomical calc required)
        # We search for when Karana 1 ends.
        tithi_midpoint_ahar = self._find_element_end_time(
            tithi_start_ahar, 'karana', karana1_name, language
        )

        # 3. Construct Karana 1
        karanas.append({
            'karana_name': karana1_name,
            'start_ahar': tithi_start_ahar,  # REUSE
            'end_ahar': tithi_midpoint_ahar,  # CALCULATED
            'start_time': self._ahar_to_time(tithi_start_ahar),
            'end_time': self._ahar_to_time(tithi_midpoint_ahar)
        })

        # 4. Determine Karana 2 Name (Math only)
        # We are in the 2nd half of this Tithi
        karana2_name = _get_karana_name_math(tithi_index, is_second_half=True, language=language)

        # 5. Construct Karana 2
        karanas.append({
            'karana_name': karana2_name,
            'start_ahar': tithi_midpoint_ahar,  # REUSE
            'end_ahar': tithi_end_ahar,  # REUSE
            'start_time': self._ahar_to_time(tithi_midpoint_ahar),
            'end_time': self._ahar_to_time(tithi_end_ahar)
        })

        return karanas

    def get_tithis_for_civil_day(
        self,
        year: int,
        month: int,
        day: int,
        sunrise_ahar: Optional[float] = None,
        sriseh: Optional[int] = None,
        srisem: Optional[int] = None,
        sseth: Optional[int] = None,
        ssetm: Optional[int] = None,
        scan_window: float = 0.5
    ) -> dict:
        """
        Get all tithis around sunrise for a civil day.

        This method scans for all tithis in a window around sunrise (default ±12 hours)
        and returns them with timing information. Each tithi includes a flag indicating
        whether it spans sunrise, allowing observers to decide the ruling tithi based
        on their tradition.

        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            sunrise_ahar: Pre-calculated Ahargana at sunrise (optional)
            sunrise_hour: Pre-calculated sunrise hour (optional)
            sunrise_minute: Pre-calculated sunrise minute (optional)
            scan_window: Days before and after sunrise to scan (default 0.5 = ±12 hours)

        Returns:
            Dictionary with:
            - date: Gregorian date string
            - sunrise: Tuple of (hour, minute)
            - sunrise_ahar: Ahargana at sunrise
            - tithis: List of tithi dictionaries, each containing:
                - name: Tithi name
                - day: Tithi day number (1-15)
                - paksa: 'sukla' or 'krsna'
                - start_ahar: Start Ahargana
                - end_ahar: End Ahargana
                - start_time: Start time as (hour, minute)
                - end_time: End time as (hour, minute)
                - spans_sunrise: Boolean indicating if tithi is active at sunrise
                - starts_on_date: Boolean indicating if tithi is active on given gregorian date
        """
        language = self.settings.language or "english"

        # Calculate date boundaries for starts_on_date check
        # Midnight (00:00) of the given date
        midnight_ahar = sunrise_ahar - ((sriseh + srisem / 60.0) / 24.0)

        # Sunset of the given date (calculate if not available)
        sunset_ahar = midnight_ahar + ((sseth + ssetm / 60.0) / 24.0)

        tithis = []

        def _check_starts_on_date(start_ahar: float) -> bool:
            """Check if tithi starts on the given date (between midnight and sunset)."""
            return midnight_ahar <= start_ahar < sunset_ahar

        # Calculate next day's sunrise for Vriddhi detection
        # Next sunrise is approximately 1 day after current sunrise
        next_sunrise_ahar = sunrise_ahar + 1.0

        def _is_vriddhi(start_ahar: float, end_ahar: float) -> bool:
            """
            Check if tithi is Vriddhi (extended) - spans two consecutive sunrises.
            A tithi is Vriddhi if it starts before today's sunrise and ends after tomorrow's sunrise.
            """
            return start_ahar < sunrise_ahar and end_ahar > next_sunrise_ahar

        def _is_kshaya(start_ahar: float, end_ahar: float) -> bool:
            """
            Check if tithi is Kshaya (skipped) - never sees a sunrise.
            A tithi is Kshaya if it starts after today's sunrise and ends before tomorrow's sunrise.
            """
            return start_ahar > sunrise_ahar and end_ahar < next_sunrise_ahar

        # Step 1: Get the tithi at sunrise (this is the ruling tithi)
        el = self._get_elements_at_ahar(sunrise_ahar, language)
        t_day, paksa = el["tithi_day"], el["paksa"]
        t_name = get_tithi_name(t_day, paksa, language)

        start_ahar = self._find_tithi_start_time(sunrise_ahar, t_day, paksa, language)
        end_ahar = self._find_tithi_end_time(sunrise_ahar, t_day, paksa, language)

        # The tithi at sunrise is the ruling tithi (Udaya Tithi)
        # tithi_for_day = True because it spans sunrise
        is_vriddhi_main = _is_vriddhi(start_ahar, end_ahar)

        tithis.append({
            'tithi': el["tithi"],
            "name": t_name,
            "day": t_day,
            "paksa": paksa,
            'sukla_krsna': el["sukla_krsna"],
            "start_ahar": start_ahar,
            "end_ahar": end_ahar,
            "start_time": self._ahar_to_time(start_ahar),
            "end_time": self._ahar_to_time(end_ahar),
            "spans_sunrise": True,
            "starts_on_date": _check_starts_on_date(start_ahar),
            "tithi_for_day": True,  # Udaya Tithi - active at sunrise
            "is_vriddhi": is_vriddhi_main,  # Extended - same tithi for two days
            "is_kshaya": False  # Cannot be Kshaya if it spans sunrise
        })

        # Step 2: Get the previous tithi (if it falls within scan window)
        prev_scan_ahar = start_ahar - 0.01
        if prev_scan_ahar >= (sunrise_ahar - scan_window):
            el_prev = self._get_elements_at_ahar(prev_scan_ahar, language)
            t_day_prev, paksa_prev = el_prev["tithi_day"], el_prev["paksa"]
            t_name_prev = get_tithi_name(t_day_prev, paksa_prev, language)

            start_ahar_prev = self._find_tithi_start_time(prev_scan_ahar, t_day_prev, paksa_prev, language)
            end_ahar_prev = self._find_tithi_end_time(prev_scan_ahar, t_day_prev, paksa_prev, language)

            tithis.insert(0, {
                'tithi': el_prev["tithi"],
                "name": t_name_prev,
                "day": t_day_prev,
                "paksa": paksa_prev,
                'sukla_krsna': el_prev["sukla_krsna"],
                "start_ahar": start_ahar_prev,
                "end_ahar": end_ahar_prev,
                "start_time": self._ahar_to_time(start_ahar_prev),
                "end_time": self._ahar_to_time(end_ahar_prev),
                "spans_sunrise": False,  # Ended before sunrise
                "starts_on_date": _check_starts_on_date(start_ahar_prev),
                "tithi_for_day": False,  # Not active at sunrise
                "is_vriddhi": False,  # Previous tithi ended, not extended
                "is_kshaya": _is_kshaya(start_ahar_prev, end_ahar_prev)
            })

        # Step 3: Get the next tithi (if it falls within scan window)
        next_scan_ahar = end_ahar + 0.01
        if next_scan_ahar <= (sunrise_ahar + scan_window):
            el_next = self._get_elements_at_ahar(next_scan_ahar, language)
            t_day_next, paksa_next = el_next["tithi_day"], el_next["paksa"]
            t_name_next = get_tithi_name(t_day_next, paksa_next, language)

            start_ahar_next = self._find_tithi_start_time(next_scan_ahar, t_day_next, paksa_next, language)
            end_ahar_next = self._find_tithi_end_time(next_scan_ahar, t_day_next, paksa_next, language)

            tithis.append({
                'tithi': el_next["tithi"],
                "name": t_name_next,
                "day": t_day_next,
                "paksa": paksa_next,
                'sukla_krsna': el_next["sukla_krsna"],
                "start_ahar": start_ahar_next,
                "end_ahar": end_ahar_next,
                "start_time": self._ahar_to_time(start_ahar_next),
                "end_time": self._ahar_to_time(end_ahar_next),
                "spans_sunrise": False,  # Starts after sunrise
                "starts_on_date": _check_starts_on_date(start_ahar_next),
                "tithi_for_day": False,  # Not active at this day's sunrise
                "is_vriddhi": _is_vriddhi(start_ahar_next, end_ahar_next),  # May span to next sunrise
                "is_kshaya": _is_kshaya(start_ahar_next, end_ahar_next)  # May be skipped
            })

        return {
            "date": f"{year}-{month:02d}-{day:02d}",
            "tithis": tithis
        }
