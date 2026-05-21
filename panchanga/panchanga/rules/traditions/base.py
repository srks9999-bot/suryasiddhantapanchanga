"""
Base class for calculation traditions.

This module provides the abstract base class that all calculation
traditions must implement. A tradition defines:
- Which astronomical constants to use
- Which rules are active by default
- How to calculate ayanamsa and other tradition-specific values
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from panchanga.rules.base import TithiRule, TraditionBase


class BaseTradition(TraditionBase):
    """
    Base implementation of TraditionBase with common functionality.
    
    Provides default implementations for common methods that can be
    overridden by specific traditions.
    """
    
    name = "base"
    display_name = "Base Tradition"
    description = "Abstract base tradition"
    
    def __init__(self, **config):
        """
        Initialize tradition with configuration.
        
        Args:
            **config: Tradition-specific configuration options
        """
        super().__init__(**config)
        self._rules_cache = None
    
    def get_default_rules(self) -> List[TithiRule]:
        """
        Return default rules for this tradition.
        
        Override in subclasses to customize default rules.
        """
        from panchanga.rules.tithi_rules import (
            SunriseBasedRule, KsayaTithiRule, VriddhiTithiRule
        )
        return [
            SunriseBasedRule(),
            KsayaTithiRule(merge_with_previous=True),
            VriddhiTithiRule(assign_to_first_day=False),
        ]
    
    def get_planetary_constants(self) -> Dict[str, Any]:
        """
        Return planetary constants for this tradition.
        
        Override in subclasses to provide tradition-specific constants.
        """
        from panchanga.data.planetary import (
            SURYA_SIDDHANTA_ROTATIONS,
            SURYA_SIDDHANTA_PLANETARY,
            calculate_derived_constants
        )
        
        rotations = SURYA_SIDDHANTA_ROTATIONS
        derived = calculate_derived_constants(rotations)
        
        return {
            'rotations': rotations.to_dict(),
            'planetary': {
                'sun_apogee': SURYA_SIDDHANTA_PLANETARY.sun_apogee,
                'moon_apogee': SURYA_SIDDHANTA_PLANETARY.moon_apogee,
                'mercury_apogee': SURYA_SIDDHANTA_PLANETARY.mercury_apogee,
                'venus_apogee': SURYA_SIDDHANTA_PLANETARY.venus_apogee,
                'mars_apogee': SURYA_SIDDHANTA_PLANETARY.mars_apogee,
                'jupiter_apogee': SURYA_SIDDHANTA_PLANETARY.jupiter_apogee,
                'saturn_apogee': SURYA_SIDDHANTA_PLANETARY.saturn_apogee,
            },
            'derived': derived
        }
    
    def get_ayanamsa(self, ahar: float) -> float:
        """
        Calculate ayanamsa for this tradition.
        
        Default implementation uses Lahiri ayanamsa.
        
        Args:
            ahar: Ahargana value
            
        Returns:
            Ayanamsa in degrees
        """
        # Lahiri ayanamsa
        # Reference: ayanamsa was approximately 23°15' on Jan 1, 2000
        # Rate: approximately 50.29" per year
        
        # Ahargana for Jan 1, 2000 (approximately)
        ahar_2000 = 1861018  # Approximate
        years_from_2000 = (ahar - ahar_2000) / 365.25
        
        # Ayanamsa on Jan 1, 2000 was about 23.85 degrees
        ayanamsa_2000 = 23.85
        rate_per_year = 50.29 / 3600  # degrees per year
        
        return ayanamsa_2000 + (years_from_2000 * rate_per_year)
    
    def get_system_name(self) -> str:
        """Get the astronomical system name used by this tradition."""
        return "SuryaSiddhanta"
