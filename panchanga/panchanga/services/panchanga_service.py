"""
Panchanga Service - High-level service layer.

This service provides a clean interface for Panchanga calculations,
integrating the calculator with the rules engine and traditions.
It's designed to be used by the REST API and can also be wrapped
as a Temporal activity in the future.
"""

from typing import Optional, List, Dict, Any
from datetime import date
import calendar

from panchanga.models.settings import PanchangaSettings
from panchanga.core.calculator import PanchangaCalculator
from panchanga.rules.engine import RuleEngine
from panchanga.rules.base import TithiContext, TithiDecisionData
from panchanga.rules.traditions import TRADITIONS, DEFAULT_TRADITION


class PanchangaService:
    """
    High-level service for Panchanga calculations.
    
    This service provides a clean API for:
    - Single date calculations
    - Monthly calendars
    - Birthday searches
    - Ugadi date finding
    - Rule evaluation
    
    It integrates the PanchangaCalculator with the rules engine
    for extensible tithi determination.
    """
    
    def __init__(
        self,
        settings: Optional[PanchangaSettings] = None,
        tradition: Optional[str] = None,
        rule_engine: Optional[RuleEngine] = None
    ):
        """
        Initialize Panchanga Service.
        
        Args:
            settings: Calculation settings
            tradition: Tradition name (overrides settings if provided)
            rule_engine: Custom rule engine (uses tradition defaults if not provided)
        """
        self.settings = settings or PanchangaSettings()
        
        # Set tradition
        if tradition:
            self.settings.tradition = tradition
        
        # Initialize calculator
        self.calculator = PanchangaCalculator(self.settings)
        
        # Initialize rule engine
        if rule_engine:
            self.rule_engine = rule_engine
        else:
            tradition_name = self.settings.tradition
            tradition_class = TRADITIONS.get(tradition_name)
            if tradition_class:
                tradition_instance = tradition_class()
                self.rule_engine = RuleEngine(tradition=tradition_instance)
            else:
                self.rule_engine = RuleEngine()
    
    def calculate(
        self,
        year: int,
        month: int,
        day: int,
        include_timing: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate Panchanga for a specific date.
        
        Args:
            year: Year
            month: Month (1-12)
            day: Day of month
            include_timing: Whether to calculate element start/end times (expensive operation)
            
        Returns:
            Dictionary with all Panchanga data
        """
        result = self.calculator.calculate(year, month, day, include_timing=include_timing)
        
        # Optionally apply rules engine for tithi decision
        if self.rule_engine:
            context = self._create_tithi_context(result)
            decision = self.rule_engine.evaluate(context)
            if decision:
                result['tithi_decision'] = decision.to_dict()
        
        return result
    
    def calculate_month(self, year: int, month: int) -> Dict[str, Any]:
        """
        Calculate Panchanga for an entire month.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Dictionary with month data and list of daily panchangas
        """
        num_days = calendar.monthrange(year, month)[1]
        month_name = calendar.month_name[month]
        
        days = []
        for day in range(1, num_days + 1):
            data = self.calculator.calculate(year, month, day)
            
            days.append({
                'date': f"{year}-{month:02d}-{day:02d}",
                'weekday': data['weekday'],
                'year_saka': data['year_saka'],
                'masa': f"{data['adhimasa']}{data['masa']}",
                'paksha': 'Sukla' if data['paksa'] == 'Suklapaksa' else 'Krsna',
                'tithi_day': data['tithi_day'],
                'tithi_name': data.get('tithi_name', ''),
                'nakshatra': data['nakshatra'],
                'yoga': data['yoga'],
                'karana': data['karana'],
            })
        
        return {
            'year': year,
            'month': month,
            'month_name': month_name,
            'days': days,
            'settings': {
                'system': self.settings.selected_system,
                'tradition': self.settings.tradition,
                'latitude': self.settings.loc_lat,
                'longitude': self.settings.loc_lon,
                'language': self.settings.language
            }
        }
    
    def find_birthdays(
        self,
        year: int,
        month: int,
        day: int,
        masa_num: Optional[int] = None,
        paksha: Optional[str] = None,
        tithi_day: Optional[int] = None,
        number_of_years: int = 5
    ) -> Dict[str, Any]:
        """
        Find future birthdays based on tithi, masa, and paksha.
        
        Args:
            year: Reference year
            month: Reference month
            day: Reference day
            masa_num: Lunar month (if None, uses reference date's masa)
            paksha: Paksha (if None, uses reference date's paksha)
            tithi_day: Tithi day (if None, uses reference date's tithi)
            number_of_years: Number of years to search
            
        Returns:
            Dictionary with birthday information
        """
        # First calculate reference date to get tithi/masa/paksha if not provided
        ref_data = self.calculate(year, month, day)
        
        target_masa = masa_num if masa_num is not None else ref_data['masa_num']
        target_paksha = paksha if paksha else ref_data['paksa']
        target_tithi = tithi_day if tithi_day is not None else ref_data['tithi_day']
        
        # Search for birthdays
        from panchanga.core.date_utils import DateUtils
        
        birthdays = []
        search_year, search_month, search_day = DateUtils.next_date(year, month, day)
        start_julian = DateUtils.modern_date_to_julian_day(year, month, day)
        max_search_days = number_of_years * 400
        days_searched = 0
        last_found_year = year - 1
        
        while days_searched < max_search_days and len(birthdays) < number_of_years:
            try:
                data = self.calculator.calculate(
                    search_year, search_month, search_day,
                    skip_next_year_search=True
                )
                
                if (data['masa_num'] == target_masa and
                    data['paksa'] == target_paksha and
                    data['tithi_day'] == target_tithi and
                    search_year > last_found_year):
                    
                    julian = DateUtils.modern_date_to_julian_day(search_year, search_month, search_day)
                    birthdays.append({
                        'year': search_year,
                        'month': search_month,
                        'day': search_day,
                        'days_ahead': int(julian - start_julian),
                        'year_number': len(birthdays) + 1,
                        'is_ksaya_tithi': False,
                        'is_ksaya_masa': False
                    })
                    last_found_year = search_year
            except Exception:
                pass
            
            search_year, search_month, search_day = DateUtils.next_date(
                search_year, search_month, search_day
            )
            days_searched += 1
        
        return {
            'reference_date': (year, month, day),
            'masa_num': target_masa,
            'masa_name': ref_data['masa'] if target_masa == ref_data['masa_num'] else '',
            'paksha': target_paksha,
            'tithi_day': target_tithi,
            'tithi_name': ref_data.get('tithi_name', ''),
            'birthdays': birthdays,
            'settings': {
                'system': self.settings.selected_system,
                'tradition': self.settings.tradition,
                'latitude': self.settings.loc_lat,
                'longitude': self.settings.loc_lon,
                'language': self.settings.language
            }
        }
    
    def find_ugadi_dates(
        self,
        year: int,
        month: int,
        day: int,
        number_of_years: int = 5
    ) -> Dict[str, Any]:
        """
        Find upcoming Ugadi (Telugu New Year) dates.
        
        Ugadi falls on Chaitra Shukla Pratipada.
        
        Args:
            year: Starting year
            month: Starting month
            day: Starting day
            number_of_years: Number of Ugadi dates to find
            
        Returns:
            Dictionary with Ugadi date information
        """
        from panchanga.core.date_utils import DateUtils
        
        ugadi_dates = []
        search_year, search_month, search_day = DateUtils.next_date(year, month, day)
        start_julian = DateUtils.modern_date_to_julian_day(year, month, day)
        max_search_days = number_of_years * 400
        days_searched = 0
        last_found_julian = 0
        min_days_between = 340  # Minimum days between Ugadis
        
        while days_searched < max_search_days and len(ugadi_dates) < number_of_years:
            try:
                data = self.calculator.calculate(
                    search_year, search_month, search_day,
                    skip_next_year_search=True
                )
                
                # Check for Chaitra Shukla Pratipada
                if (data['masa_num'] == 0 and
                    data['paksa'] == 'Suklapaksa' and
                    data['tithi_day'] == 1):
                    
                    julian = DateUtils.modern_date_to_julian_day(search_year, search_month, search_day)
                    
                    # Ensure minimum gap between Ugadis
                    if last_found_julian == 0 or (julian - last_found_julian) >= min_days_between:
                        ugadi_dates.append({
                            'year': search_year,
                            'month': search_month,
                            'day': search_day,
                            'days_ahead': int(julian - start_julian),
                            'tithi': 1,
                            'tithi_name': 'Pratipada',
                            'pratipada_starts_at': None,
                            'exists_at_sunrise': True
                        })
                        last_found_julian = julian
            except Exception:
                pass
            
            search_year, search_month, search_day = DateUtils.next_date(
                search_year, search_month, search_day
            )
            days_searched += 1
        
        return {
            'reference_date': (year, month, day),
            'ugadi_dates': ugadi_dates,
            'settings': {
                'system': self.settings.selected_system,
                'tradition': self.settings.tradition,
                'latitude': self.settings.loc_lat,
                'longitude': self.settings.loc_lon,
                'language': self.settings.language
            }
        }
    
    def evaluate_rules(
        self,
        year: int,
        month: int,
        day: int
    ) -> Dict[str, Any]:
        """
        Evaluate tithi rules for debugging.
        
        Args:
            year: Year
            month: Month
            day: Day
            
        Returns:
            Dictionary with rule evaluation details
        """
        # Enable tracing
        self.rule_engine.trace_enabled = True
        
        # Calculate base data
        data = self.calculate(year, month, day)
        
        # Create context and evaluate
        context = self._create_tithi_context(data)
        decision = self.rule_engine.evaluate(context)
        trace = self.rule_engine.get_trace()
        
        # Disable tracing
        self.rule_engine.trace_enabled = False
        
        return {
            'date': (year, month, day),
            'tradition': self.settings.tradition,
            'rules_evaluated': [r['name'] for r in self.rule_engine.get_all_rules()],
            'decision': decision.to_dict() if decision else None,
            'evaluation_trace': trace
        }
    
    def _create_tithi_context(self, data: Dict[str, Any]) -> TithiContext:
        """Create TithiContext from calculation data."""
        # Get timing data for context
        tithi_start = data.get('tithi_start_datetime', {})
        tithi_end = data.get('tithi_end_datetime', {})
        
        return TithiContext(
            date=data['gregorian_date'],
            sunrise_tithi=data['tithi_day'],
            sunrise_paksha=data['paksa'],
            tithi_start_ahar=0,  # Would need to compute from datetime
            tithi_end_ahar=0,
            sunrise_ahar=0,
            next_sunrise_ahar=0,
            tradition=self.settings.tradition,
            sun_longitude=data.get('sun_longitude'),
            moon_longitude=data.get('moon_longitude'),
            masa_num=data.get('masa_num'),
            language=self.settings.language
        )
    
    def get_available_traditions(self) -> List[Dict[str, Any]]:
        """Get list of available traditions."""
        traditions = []
        for name, tradition_class in TRADITIONS.items():
            tradition = tradition_class()
            traditions.append(tradition.get_info())
        return traditions
    
    def get_available_rules(self) -> List[Dict[str, Any]]:
        """Get list of available rules."""
        from panchanga.rules.tithi_rules import get_all_rules
        return [rule.get_info() for rule in get_all_rules()]


# Convenience function for creating service with settings from dict
def create_service(
    settings_dict: Optional[Dict[str, Any]] = None,
    tradition: Optional[str] = None
) -> PanchangaService:
    """
    Create a PanchangaService from a settings dictionary.
    
    Args:
        settings_dict: Dictionary with settings values
        tradition: Tradition override
        
    Returns:
        Configured PanchangaService instance
    """
    if settings_dict:
        settings = PanchangaSettings.from_dict(settings_dict)
    else:
        settings = PanchangaSettings()
    
    return PanchangaService(settings=settings, tradition=tradition)
