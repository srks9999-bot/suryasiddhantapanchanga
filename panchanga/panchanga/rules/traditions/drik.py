"""
Drik Ganita (observational/modern) tradition implementation.

Drik Ganita uses modern astronomical calculations based on actual
observed planetary positions, typically using Swiss Ephemeris or
similar high-precision ephemeris data.
"""

from typing import List, Dict, Any
from panchanga.rules.base import TithiRule
from panchanga.rules.traditions.base import BaseTradition


class DrikTradition(BaseTradition):
    """
    Drik Ganita tradition for Panchanga calculations.
    
    This tradition uses modern astronomical calculations:
    - Actual observed planetary positions (ephemeris-based)
    - Modern ayanamsa calculations (Lahiri, Raman, etc.)
    - Precise sunrise/sunset calculations with atmospheric refraction
    
    Key characteristics:
    - More accurate planetary positions
    - Matches actual observed sky positions
    - Commonly used in modern computerized panchangas
    
    Note: Full implementation requires integration with an ephemeris
    library like Swiss Ephemeris (pyswisseph). This implementation
    provides the framework and falls back to Surya Siddhanta calculations
    when ephemeris data is not available.
    """
    
    name = "drik"
    display_name = "Drik Ganita"
    description = "Modern observational/ephemeris-based calculations"
    
    def __init__(self, **config):
        """
        Initialize Drik tradition.
        
        Config options:
            ayanamsa: Ayanamsa system ('lahiri', 'raman', 'krishnamurti')
            use_ephemeris: Whether to use ephemeris (requires pyswisseph)
        """
        super().__init__(**config)
        self.ayanamsa_system = config.get('ayanamsa', 'lahiri')
        self.use_ephemeris = config.get('use_ephemeris', False)
        self._ephemeris_available = self._check_ephemeris()
    
    def _check_ephemeris(self) -> bool:
        """Check if Swiss Ephemeris is available."""
        try:
            import swisseph
            return True
        except ImportError:
            return False
    
    def get_default_rules(self) -> List[TithiRule]:
        """
        Return default rules for Drik tradition.
        
        Drik tradition uses similar rules to Surya but may have
        slight variations in timing due to more precise calculations.
        """
        from panchanga.rules.tithi_rules import (
            SunriseBasedRule, KsayaTithiRule, VriddhiTithiRule,
            PurnimaAmavasRule, SpanBasedRule
        )
        
        return [
            # Special handling for Purnima/Amavasya
            PurnimaAmavasRule(),
            # Primary rule: sunrise-based
            SunriseBasedRule(),
            # Ksaya handling
            KsayaTithiRule(
                merge_with_previous=True,
                report_as_ksaya=True
            ),
            # Vriddhi handling
            VriddhiTithiRule(
                assign_to_first_day=False
            ),
            # Optional span-based as fallback
            SpanBasedRule(
                enabled=False,
                min_span_hours=3
            ),
        ]
    
    def get_planetary_constants(self) -> Dict[str, Any]:
        """
        Return planetary constants for Drik tradition.
        
        For true Drik calculations, these would come from ephemeris.
        Falls back to Surya Siddhanta constants when ephemeris unavailable.
        """
        if self._ephemeris_available and self.use_ephemeris:
            return self._get_ephemeris_constants()
        
        # Fallback to Surya Siddhanta constants
        return super().get_planetary_constants()
    
    def _get_ephemeris_constants(self) -> Dict[str, Any]:
        """
        Get constants from ephemeris.
        
        This would integrate with Swiss Ephemeris for actual positions.
        """
        # Placeholder - actual implementation would use swisseph
        return super().get_planetary_constants()
    
    def get_ayanamsa(self, ahar: float) -> float:
        """
        Calculate ayanamsa using modern values.
        
        Supports multiple ayanamsa systems commonly used in Drik calculations.
        
        Args:
            ahar: Ahargana value
            
        Returns:
            Ayanamsa in degrees
        """
        # Convert ahargana to Julian Day for standard calculations
        julian_day = ahar + 588465.50
        
        # Convert to year for ayanamsa calculation
        # J2000.0 = JD 2451545.0
        j2000 = 2451545.0
        days_from_j2000 = julian_day - j2000
        years_from_j2000 = days_from_j2000 / 365.25
        year = 2000 + years_from_j2000
        
        if self.ayanamsa_system == 'lahiri':
            return self._lahiri_ayanamsa(year)
        elif self.ayanamsa_system == 'raman':
            return self._raman_ayanamsa(year)
        elif self.ayanamsa_system == 'krishnamurti':
            return self._krishnamurti_ayanamsa(year)
        else:
            return self._lahiri_ayanamsa(year)
    
    def _lahiri_ayanamsa(self, year: float) -> float:
        """
        Calculate Lahiri (Chitrapaksha) ayanamsa.
        
        This is the official ayanamsa used by the Indian government.
        Reference: Spica (Chitra) at 180° sidereal longitude.
        """
        # Lahiri ayanamsa on Jan 1, 2000: approximately 23°51'
        # Rate: approximately 50.29" per year
        ayanamsa_2000 = 23.85  # degrees
        rate = 50.29 / 3600  # degrees per year
        return ayanamsa_2000 + (year - 2000) * rate
    
    def _raman_ayanamsa(self, year: float) -> float:
        """
        Calculate B.V. Raman ayanamsa.
        
        Slightly different from Lahiri, used by some astrologers.
        """
        # Raman ayanamsa on Jan 1, 2000: approximately 22°24'
        ayanamsa_2000 = 22.40
        rate = 50.29 / 3600
        return ayanamsa_2000 + (year - 2000) * rate
    
    def _krishnamurti_ayanamsa(self, year: float) -> float:
        """
        Calculate Krishnamurti ayanamsa.
        
        Used in KP (Krishnamurti Paddhati) astrology system.
        """
        # Krishnamurti ayanamsa on Jan 1, 2000: approximately 23°46'
        ayanamsa_2000 = 23.77
        rate = 50.29 / 3600
        return ayanamsa_2000 + (year - 2000) * rate
    
    def get_system_name(self) -> str:
        """Get the astronomical system name."""
        return "DrikGanita"
