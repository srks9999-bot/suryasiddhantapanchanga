"""
Tithi determination rules for Panchanga calculations.

This module implements the core rules used to determine which tithi
applies to a given day. Rules can be combined and configured to
support different regional traditions and preferences.
"""

from typing import Optional, List
from panchanga.rules.base import (
    TithiRule, TithiContext, TithiDecisionData, RuleCategory
)


class SunriseBasedRule(TithiRule):
    """
    Sunrise-based tithi determination rule.
    
    This is the most common rule: the tithi that exists at sunrise
    is considered the tithi for the entire day.
    
    This rule is used by most Hindu calendar systems and is the
    default rule for the Surya tradition.
    """
    
    name = "sunrise_based"
    description = "Tithi present at sunrise determines the day's tithi"
    priority = 10  # High priority - usually the primary rule
    category = RuleCategory.TITHI
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate sunrise-based rule.
        
        Returns the tithi that exists at sunrise as the day's tithi.
        """
        if context.tithi_exists_at_sunrise:
            return TithiDecisionData(
                tithi=context.sunrise_tithi,
                paksha=context.sunrise_paksha,
                confidence=1.0,
                rule_name=self.name,
                tradition=context.tradition,
                notes=["Tithi exists at sunrise"]
            )
        return None


class SpanBasedRule(TithiRule):
    """
    Span-based tithi determination rule.
    
    This rule requires the tithi to span a minimum portion of the day
    (from sunrise) to be considered the day's tithi.
    
    Parameters:
        min_span_hours: Minimum hours the tithi must span (default: 0)
        min_span_fraction: Minimum fraction of day (0-1) the tithi must span
    """
    
    name = "span_based"
    description = "Tithi must span a minimum portion of the day"
    priority = 20
    category = RuleCategory.TITHI
    
    def __init__(self, **params):
        super().__init__(**params)
        self.min_span_hours = params.get('min_span_hours', 0)
        self.min_span_fraction = params.get('min_span_fraction', 0)
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate span-based rule.
        
        Returns the tithi only if it spans the minimum required duration.
        """
        span_fraction = context.tithi_duration_in_day
        span_hours = span_fraction * 24  # Approximate
        
        meets_hours = span_hours >= self.min_span_hours
        meets_fraction = span_fraction >= self.min_span_fraction
        
        if meets_hours and meets_fraction:
            return TithiDecisionData(
                tithi=context.sunrise_tithi,
                paksha=context.sunrise_paksha,
                confidence=min(1.0, span_fraction * 2),  # Higher confidence for longer spans
                rule_name=self.name,
                tradition=context.tradition,
                notes=[f"Tithi spans {span_hours:.1f} hours ({span_fraction:.1%} of day)"]
            )
        return None


class KsayaTithiRule(TithiRule):
    """
    Ksaya (skipped) tithi handling rule.
    
    A ksaya tithi is one that starts after sunrise and ends before
    the next sunrise, thus "skipping" a day. This rule determines
    how to handle such cases.
    
    Parameters:
        merge_with_previous: If True, merge ksaya tithi with previous tithi
        merge_with_next: If True, merge ksaya tithi with next tithi
        report_as_ksaya: If True, report the day as having ksaya tithi
    """
    
    name = "ksaya_handling"
    description = "Handle ksaya (skipped) tithi - starts after sunrise, ends before next sunrise"
    priority = 15  # Between sunrise and span rules
    category = RuleCategory.TITHI
    
    def __init__(self, **params):
        super().__init__(**params)
        self.merge_with_previous = params.get('merge_with_previous', True)
        self.merge_with_next = params.get('merge_with_next', False)
        self.report_as_ksaya = params.get('report_as_ksaya', True)
    
    def applies_to(self, context: TithiContext) -> bool:
        """Only apply when a ksaya tithi is detected."""
        return self.enabled and context.tithi_skipped
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate ksaya tithi handling rule.
        
        Determines how to handle a skipped tithi based on configuration.
        """
        if not context.tithi_skipped:
            return None
        
        # The tithi at sunrise is the "previous" tithi relative to the ksaya
        notes = [f"Ksaya tithi detected: tithi {context.sunrise_tithi} is skipped"]
        
        if self.merge_with_previous:
            # Use the tithi that exists at sunrise (previous to ksaya)
            return TithiDecisionData(
                tithi=context.sunrise_tithi,
                paksha=context.sunrise_paksha,
                confidence=0.9,
                rule_name=self.name,
                tradition=context.tradition,
                is_ksaya=self.report_as_ksaya,
                notes=notes + ["Merged with previous tithi (at sunrise)"]
            )
        elif self.merge_with_next and context.next_tithi is not None:
            # Use the next tithi
            # Calculate next paksha if tithi wraps
            next_paksha = context.sunrise_paksha
            if context.sunrise_tithi == 15:
                next_paksha = 'Krsnapaksa' if context.sunrise_paksha == 'Suklapaksa' else 'Suklapaksa'
            
            return TithiDecisionData(
                tithi=context.next_tithi if context.next_tithi <= 15 else context.next_tithi - 15,
                paksha=next_paksha,
                confidence=0.9,
                rule_name=self.name,
                tradition=context.tradition,
                is_ksaya=self.report_as_ksaya,
                notes=notes + ["Merged with next tithi"]
            )
        
        # Default: use sunrise tithi but mark as ksaya
        return TithiDecisionData(
            tithi=context.sunrise_tithi,
            paksha=context.sunrise_paksha,
            confidence=0.8,
            rule_name=self.name,
            tradition=context.tradition,
            is_ksaya=True,
            notes=notes
        )


class VriddhiTithiRule(TithiRule):
    """
    Vriddhi (extended) tithi handling rule.
    
    A vriddhi tithi is one that spans two consecutive sunrises,
    appearing on two days. This rule determines which day gets
    the tithi designation.
    
    Parameters:
        assign_to_first_day: If True, assign tithi to first day
        assign_to_both: If True, both days get the tithi
        prefer_auspicious: If True, prefer assigning to more auspicious day
    """
    
    name = "vriddhi_handling"
    description = "Handle vriddhi (extended) tithi - spans two sunrises"
    priority = 16
    category = RuleCategory.TITHI
    
    def __init__(self, **params):
        super().__init__(**params)
        self.assign_to_first_day = params.get('assign_to_first_day', False)
        self.assign_to_both = params.get('assign_to_both', False)
        self.prefer_auspicious = params.get('prefer_auspicious', False)
    
    def applies_to(self, context: TithiContext) -> bool:
        """Only apply when a vriddhi tithi is detected."""
        return self.enabled and context.tithi_spans_both_sunrises
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate vriddhi tithi handling rule.
        
        Determines how to handle an extended tithi based on configuration.
        """
        if not context.tithi_spans_both_sunrises:
            return None
        
        notes = [f"Vriddhi tithi detected: tithi {context.sunrise_tithi} spans two days"]
        
        # For now, use the tithi at sunrise (this is the "first day" scenario)
        # The second day's context would have a different sunrise_tithi
        
        if self.assign_to_first_day or self.assign_to_both:
            return TithiDecisionData(
                tithi=context.sunrise_tithi,
                paksha=context.sunrise_paksha,
                confidence=1.0,
                rule_name=self.name,
                tradition=context.tradition,
                is_vriddhi=True,
                notes=notes + ["Assigned to this day (vriddhi)"]
            )
        else:
            # Default behavior: assign to second day (next day gets the tithi)
            # This context is for the first day, so we use previous tithi if available
            if context.previous_tithi is not None:
                prev_tithi = context.previous_tithi
                prev_paksha = context.sunrise_paksha
                # Adjust paksha if needed
                if prev_tithi == 15 and context.sunrise_tithi == 1:
                    prev_paksha = 'Suklapaksa' if context.sunrise_paksha == 'Krsnapaksa' else 'Krsnapaksa'
                
                return TithiDecisionData(
                    tithi=prev_tithi if prev_tithi <= 15 else prev_tithi - 15,
                    paksha=prev_paksha,
                    confidence=0.9,
                    rule_name=self.name,
                    tradition=context.tradition,
                    is_vriddhi=True,
                    notes=notes + ["Current tithi assigned to next day; using previous tithi"]
                )
        
        # Fallback: use sunrise tithi
        return TithiDecisionData(
            tithi=context.sunrise_tithi,
            paksha=context.sunrise_paksha,
            confidence=0.8,
            rule_name=self.name,
            tradition=context.tradition,
            is_vriddhi=True,
            notes=notes
        )


class MuhurtaBasedRule(TithiRule):
    """
    Muhurta-based tithi determination rule.
    
    This rule considers specific muhurtas (time periods) for determining
    the tithi, particularly useful for festival and ritual timings.
    
    Parameters:
        muhurta_start_hour: Hour when muhurta period starts
        muhurta_end_hour: Hour when muhurta period ends
    """
    
    name = "muhurta_based"
    description = "Tithi determination based on specific muhurta periods"
    priority = 25
    category = RuleCategory.TITHI
    
    def __init__(self, **params):
        super().__init__(**params)
        self.muhurta_start_hour = params.get('muhurta_start_hour', 6)  # Sunrise
        self.muhurta_end_hour = params.get('muhurta_end_hour', 12)  # Noon
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate muhurta-based rule.
        
        Checks if tithi exists during the specified muhurta period.
        """
        # Calculate muhurta period in ahargana
        day_length = context.next_sunrise_ahar - context.sunrise_ahar
        muhurta_start = context.sunrise_ahar + (self.muhurta_start_hour - 6) / 24 * day_length
        muhurta_end = context.sunrise_ahar + (self.muhurta_end_hour - 6) / 24 * day_length
        
        # Check if tithi exists during muhurta
        tithi_in_muhurta = (
            context.tithi_start_ahar < muhurta_end and
            context.tithi_end_ahar > muhurta_start
        )
        
        if tithi_in_muhurta:
            return TithiDecisionData(
                tithi=context.sunrise_tithi,
                paksha=context.sunrise_paksha,
                confidence=0.95,
                rule_name=self.name,
                tradition=context.tradition,
                notes=[f"Tithi exists during muhurta ({self.muhurta_start_hour}:00-{self.muhurta_end_hour}:00)"]
            )
        return None


class PurnimaAmavasRule(TithiRule):
    """
    Special handling for Purnima (full moon) and Amavasya (new moon).
    
    These special tithis may have different rules for determination,
    particularly for festivals and observances.
    
    Parameters:
        strict_purnima: Require moon to be truly full for Purnima
        strict_amavasya: Require moon to be truly new for Amavasya
    """
    
    name = "purnima_amavasya"
    description = "Special handling for Purnima and Amavasya tithis"
    priority = 5  # Very high priority for these special tithis
    category = RuleCategory.TITHI
    
    def __init__(self, **params):
        super().__init__(**params)
        self.strict_purnima = params.get('strict_purnima', False)
        self.strict_amavasya = params.get('strict_amavasya', False)
    
    def applies_to(self, context: TithiContext) -> bool:
        """Only apply for tithi 15 (Purnima/Amavasya)."""
        return self.enabled and context.sunrise_tithi == 15
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate Purnima/Amavasya handling rule.
        """
        if context.sunrise_tithi != 15:
            return None
        
        is_purnima = context.sunrise_paksha == 'Suklapaksa'
        special_name = "Purnima" if is_purnima else "Amavasya"
        
        # For strict mode, we would need to check actual moon phase
        # For now, use standard sunrise-based logic
        if context.tithi_exists_at_sunrise:
            return TithiDecisionData(
                tithi=15,
                paksha=context.sunrise_paksha,
                confidence=1.0,
                rule_name=self.name,
                tradition=context.tradition,
                notes=[f"{special_name} exists at sunrise"]
            )
        
        return None


# Registry of available rules
AVAILABLE_RULES = {
    'sunrise_based': SunriseBasedRule,
    'span_based': SpanBasedRule,
    'ksaya_handling': KsayaTithiRule,
    'vriddhi_handling': VriddhiTithiRule,
    'muhurta_based': MuhurtaBasedRule,
    'purnima_amavasya': PurnimaAmavasRule,
}


def get_rule(name: str, **params) -> Optional[TithiRule]:
    """
    Get a rule instance by name.
    
    Args:
        name: Rule name
        **params: Rule parameters
        
    Returns:
        TithiRule instance or None if not found
    """
    rule_class = AVAILABLE_RULES.get(name)
    if rule_class:
        return rule_class(**params)
    return None


def get_all_rules() -> List[TithiRule]:
    """
    Get instances of all available rules with default parameters.
    
    Returns:
        List of all rule instances
    """
    return [rule_class() for rule_class in AVAILABLE_RULES.values()]
