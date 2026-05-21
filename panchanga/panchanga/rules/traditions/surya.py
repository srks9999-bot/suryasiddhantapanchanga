"""
Surya Siddhanta tradition implementation.

The Surya Siddhanta is a classical Indian astronomical text (ca. AD 1000)
that provides the mathematical basis for traditional Hindu calendar calculations.
This tradition uses the constants and methods from that text.
"""

from typing import List, Dict, Any
from panchanga.rules.base import TithiRule
from panchanga.rules.traditions.base import BaseTradition


class SuryaTradition(BaseTradition):
    """
    Surya Siddhanta tradition for Panchanga calculations.
    
    This is the default and most widely used tradition for traditional
    Hindu calendar calculations. It uses:
    - Classical Yuga rotation constants from Surya Siddhanta
    - Traditional manda (equation of center) and sighra corrections
    - Sunrise-based tithi determination
    
    Key characteristics:
    - Based on mean motions over a Maha Yuga (4,320,000 solar years)
    - Uses traditional planetary apogee positions
    - Calculates true positions using two-step epicyclic corrections
    """
    
    name = "surya"
    display_name = "Surya Siddhanta"
    description = "Traditional Surya Siddhanta calculations (ca. AD 1000)"
    
    def __init__(self, **config):
        """
        Initialize Surya tradition.
        
        Config options:
            use_pancasiddhantika: Use older Pancasiddhantika constants (AD 505)
        """
        super().__init__(**config)
        self.use_pancasiddhantika = config.get('use_pancasiddhantika', False)
    
    def get_default_rules(self) -> List[TithiRule]:
        """
        Return default rules for Surya tradition.
        
        The Surya tradition uses:
        1. Sunrise-based rule as primary
        2. Ksaya handling with merge to previous
        3. Vriddhi handling with assignment to second day
        """
        from panchanga.rules.tithi_rules import (
            SunriseBasedRule, KsayaTithiRule, VriddhiTithiRule,
            PurnimaAmavasRule
        )
        
        return [
            # Special handling for Purnima/Amavasya first
            PurnimaAmavasRule(),
            # Primary rule: sunrise-based
            SunriseBasedRule(),
            # Ksaya handling: merge with previous tithi
            KsayaTithiRule(
                merge_with_previous=True,
                merge_with_next=False,
                report_as_ksaya=True
            ),
            # Vriddhi handling: assign to second day by default
            VriddhiTithiRule(
                assign_to_first_day=False,
                assign_to_both=False
            ),
        ]
    
    def get_planetary_constants(self) -> Dict[str, Any]:
        """
        Return Surya Siddhanta planetary constants.
        """
        from panchanga.data.planetary import (
            SURYA_SIDDHANTA_ROTATIONS,
            SURYA_SIDDHANTA_PLANETARY,
            PANCASIDDHANTIKA_ROTATIONS,
            PANCASIDDHANTIKA_PLANETARY,
            calculate_derived_constants
        )
        
        if self.use_pancasiddhantika:
            rotations = PANCASIDDHANTIKA_ROTATIONS
            planetary = PANCASIDDHANTIKA_PLANETARY
        else:
            rotations = SURYA_SIDDHANTA_ROTATIONS
            planetary = SURYA_SIDDHANTA_PLANETARY
        
        derived = calculate_derived_constants(rotations)
        
        return {
            'rotations': rotations.to_dict(),
            'planetary': {
                'sun_apogee': planetary.sun_apogee,
                'moon_circumm': planetary.moon_circumm,
                'sun_circumm': planetary.sun_circumm,
                'mercury_apogee': planetary.mercury_apogee,
                'mercury_circumm': planetary.mercury_circumm,
                'mercury_circums': planetary.mercury_circums,
                'venus_apogee': planetary.venus_apogee,
                'venus_circumm': planetary.venus_circumm,
                'venus_circums': planetary.venus_circums,
                'mars_apogee': planetary.mars_apogee,
                'mars_circumm': planetary.mars_circumm,
                'mars_circums': planetary.mars_circums,
                'jupiter_apogee': planetary.jupiter_apogee,
                'jupiter_circumm': planetary.jupiter_circumm,
                'jupiter_circums': planetary.jupiter_circums,
                'saturn_apogee': planetary.saturn_apogee,
                'saturn_circumm': planetary.saturn_circumm,
                'saturn_circums': planetary.saturn_circums,
            },
            'derived': derived
        }
    
    def get_ayanamsa(self, ahar: float) -> float:
        """
        Calculate ayanamsa using Surya Siddhanta method.
        
        The Surya Siddhanta uses a fixed rate of precession.
        
        Args:
            ahar: Ahargana value
            
        Returns:
            Ayanamsa in degrees
        """
        from panchanga.data.planetary import SURYA_SIDDHANTA_ROTATIONS
        
        # Surya Siddhanta ayanamsa calculation
        # Rate: 54" per year (slower than modern observed rate of ~50.3")
        # Reference point: ayanamsa was 0 at start of Kali Yuga (3102 BCE)
        
        yuga_civil_days = SURYA_SIDDHANTA_ROTATIONS.star - SURYA_SIDDHANTA_ROTATIONS.sun
        
        # Days per year
        days_per_year = yuga_civil_days / SURYA_SIDDHANTA_ROTATIONS.sun
        
        # Years since Kali epoch
        years = ahar / days_per_year
        
        # Ayanamsa: 54 arcseconds per year from Kali epoch
        # But traditionally, ayanamsa was considered 0 around 499 CE (Aryabhata)
        # We use the formula from Surya Siddhanta
        ayanamsa_reference_ahar = 1314930  # Approximately 499 CE
        years_from_reference = (ahar - ayanamsa_reference_ahar) / days_per_year
        
        return (54 / 3600) * years_from_reference  # degrees
    
    def get_system_name(self) -> str:
        """Get the astronomical system name."""
        if self.use_pancasiddhantika:
            return "InPancasiddhantika"
        return "SuryaSiddhanta"
