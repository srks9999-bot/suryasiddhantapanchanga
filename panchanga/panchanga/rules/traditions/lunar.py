"""
Lunar tradition implementation.

The Lunar tradition focuses on lunar calendar conventions, particularly
the differences between Amanta (new moon ending) and Purnimanta
(full moon ending) month systems used in different regions of India.
"""

from typing import List, Dict, Any
from panchanga.rules.base import TithiRule
from panchanga.rules.traditions.base import BaseTradition


class LunarTradition(BaseTradition):
    """
    Lunar tradition for Panchanga calculations.
    
    This tradition emphasizes lunar calendar conventions:
    - Amanta (Amavasyant): Month ends on Amavasya (new moon)
      Used in: Maharashtra, Gujarat, Andhra Pradesh, Karnataka, etc.
    - Purnimanta (Purnimant): Month ends on Purnima (full moon)
      Used in: North India (UP, Bihar, MP, Rajasthan, etc.)
    
    Key characteristics:
    - Same astronomical calculations as Surya, but different month naming
    - In Purnimanta, Krishna paksha comes before Shukla paksha
    - Adhika masa (intercalary month) handling may differ
    
    The underlying planetary calculations use Surya Siddhanta constants,
    but the month determination and naming follows lunar conventions.
    """
    
    name = "lunar"
    display_name = "Lunar Convention"
    description = "Lunar calendar conventions (Amanta/Purnimanta)"
    
    def __init__(self, **config):
        """
        Initialize Lunar tradition.
        
        Config options:
            month_ending: 'amanta' (new moon) or 'purnimanta' (full moon)
            adhika_masa_rule: How to handle intercalary months
        """
        super().__init__(**config)
        self.month_ending = config.get('month_ending', 'amanta')
        self.adhika_masa_rule = config.get('adhika_masa_rule', 'solar_month')
    
    @property
    def is_purnimanta(self) -> bool:
        """Check if using Purnimanta convention."""
        return self.month_ending == 'purnimanta'
    
    @property
    def is_amanta(self) -> bool:
        """Check if using Amanta convention."""
        return self.month_ending == 'amanta'
    
    def get_default_rules(self) -> List[TithiRule]:
        """
        Return default rules for Lunar tradition.
        
        Uses standard tithi rules but may apply special handling
        for month boundaries based on convention.
        """
        from panchanga.rules.tithi_rules import (
            SunriseBasedRule, KsayaTithiRule, VriddhiTithiRule,
            PurnimaAmavasRule
        )
        
        rules = [
            # Special handling for Purnima/Amavasya (important for month boundaries)
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
        ]
        
        return rules
    
    def get_planetary_constants(self) -> Dict[str, Any]:
        """
        Return planetary constants for Lunar tradition.
        
        Uses Surya Siddhanta constants for astronomical calculations.
        """
        return super().get_planetary_constants()
    
    def adjust_masa_for_convention(self, masa_num: int, paksha: str) -> int:
        """
        Adjust masa number based on month ending convention.
        
        In Purnimanta system:
        - Krishna paksha belongs to the NEXT month
        - So Chaitra Krishna paksha is called Vaishakha Krishna in Purnimanta
        
        Args:
            masa_num: Masa number in Amanta system (0=Chaitra)
            paksha: Current paksha ('Suklapaksa' or 'Krsnapaksa')
            
        Returns:
            Adjusted masa number for the tradition's convention
        """
        if self.is_purnimanta and paksha == 'Krsnapaksa':
            # In Purnimanta, Krishna paksha is part of the next month
            return (masa_num + 1) % 12
        return masa_num
    
    def get_paksha_order(self) -> List[str]:
        """
        Get the order of pakshas within a month.
        
        Returns:
            List of paksha names in order
        """
        if self.is_purnimanta:
            # Purnimanta: Krishna comes first, then Shukla
            return ['Krsnapaksa', 'Suklapaksa']
        else:
            # Amanta: Shukla comes first, then Krishna
            return ['Suklapaksa', 'Krsnapaksa']
    
    def is_month_start(self, tithi_day: int, paksha: str) -> bool:
        """
        Check if the current tithi is the start of a new month.
        
        Args:
            tithi_day: Tithi day (1-15)
            paksha: Current paksha
            
        Returns:
            True if this is the first day of the month
        """
        if self.is_purnimanta:
            # Purnimanta: Month starts on Krishna Pratipada
            return tithi_day == 1 and paksha == 'Krsnapaksa'
        else:
            # Amanta: Month starts on Shukla Pratipada
            return tithi_day == 1 and paksha == 'Suklapaksa'
    
    def is_month_end(self, tithi_day: int, paksha: str) -> bool:
        """
        Check if the current tithi is the end of the month.
        
        Args:
            tithi_day: Tithi day (1-15)
            paksha: Current paksha
            
        Returns:
            True if this is the last day of the month
        """
        if self.is_purnimanta:
            # Purnimanta: Month ends on Purnima (Shukla 15)
            return tithi_day == 15 and paksha == 'Suklapaksa'
        else:
            # Amanta: Month ends on Amavasya (Krishna 15)
            return tithi_day == 15 and paksha == 'Krsnapaksa'
    
    def get_info(self) -> Dict[str, Any]:
        """Get tradition information."""
        info = super().get_info()
        info.update({
            'month_ending': self.month_ending,
            'adhika_masa_rule': self.adhika_masa_rule,
            'paksha_order': self.get_paksha_order()
        })
        return info
    
    def get_system_name(self) -> str:
        """Get the astronomical system name."""
        return "SuryaSiddhanta"  # Uses same astronomical base


class AmantaTradition(LunarTradition):
    """
    Amanta (Amavasyant) tradition.
    
    Month ends on Amavasya (new moon).
    Used in South and West India.
    """
    
    name = "amanta"
    display_name = "Amanta (South Indian)"
    description = "Amanta lunar convention - month ends on Amavasya"
    
    def __init__(self, **config):
        config['month_ending'] = 'amanta'
        super().__init__(**config)


class PurnimantaTradition(LunarTradition):
    """
    Purnimanta (Purnimant) tradition.
    
    Month ends on Purnima (full moon).
    Used in North India.
    """
    
    name = "purnimanta"
    display_name = "Purnimanta (North Indian)"
    description = "Purnimanta lunar convention - month ends on Purnima"
    
    def __init__(self, **config):
        config['month_ending'] = 'purnimanta'
        super().__init__(**config)
