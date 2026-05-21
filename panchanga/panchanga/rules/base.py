"""
Base classes and interfaces for the Panchanga rules engine.

This module defines the abstract base classes used by all tithi determination
rules and calculation traditions. The rules engine uses a strategy pattern
where rules can be composed, prioritized, and evaluated to make tithi decisions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum


class RuleCategory(Enum):
    """Categories of rules for organization and filtering."""
    TITHI = "tithi"
    MASA = "masa"
    NAKSHATRA = "nakshatra"
    FESTIVAL = "festival"
    CUSTOM = "custom"


@dataclass
class TithiContext:
    """
    All data needed for tithi determination.
    
    This context object is passed to rules for evaluation. It contains
    both the calculated astronomical data and metadata about the calculation.
    
    Attributes:
        date: Tuple of (year, month, day) for the date being evaluated
        sunrise_tithi: Tithi day (1-30) at sunrise
        sunrise_paksha: Paksha at sunrise ('Suklapaksa' or 'Krsnapaksa')
        tithi_start_ahar: Ahargana when current tithi started
        tithi_end_ahar: Ahargana when current tithi ends
        sunrise_ahar: Ahargana at sunrise
        next_sunrise_ahar: Ahargana at next day's sunrise
        tradition: Calculation tradition used
        previous_tithi: Previous tithi day (for ksaya detection)
        next_tithi: Next tithi day (for vriddhi detection)
        sun_longitude: True solar longitude at sunrise
        moon_longitude: True lunar longitude at sunrise
        masa_num: Current lunar month number
        language: Language for output names
    """
    date: tuple  # (year, month, day)
    sunrise_tithi: int
    sunrise_paksha: str
    tithi_start_ahar: float
    tithi_end_ahar: float
    sunrise_ahar: float
    next_sunrise_ahar: float
    tradition: str = "surya"
    previous_tithi: Optional[int] = None
    next_tithi: Optional[int] = None
    sun_longitude: Optional[float] = None
    moon_longitude: Optional[float] = None
    masa_num: Optional[int] = None
    language: str = "telugu"
    
    @property
    def tithi_duration_in_day(self) -> float:
        """
        Calculate what fraction of the day the tithi covers.
        
        Returns:
            Fraction of day (0-1) that tithi spans
        """
        day_start = self.sunrise_ahar
        day_end = self.next_sunrise_ahar
        day_length = day_end - day_start
        
        # Clamp tithi times to the day
        tithi_in_day_start = max(self.tithi_start_ahar, day_start)
        tithi_in_day_end = min(self.tithi_end_ahar, day_end)
        
        if tithi_in_day_end <= tithi_in_day_start:
            return 0.0
        
        return (tithi_in_day_end - tithi_in_day_start) / day_length
    
    @property
    def tithi_exists_at_sunrise(self) -> bool:
        """Check if the tithi exists at sunrise."""
        return self.tithi_start_ahar <= self.sunrise_ahar < self.tithi_end_ahar
    
    @property
    def tithi_spans_both_sunrises(self) -> bool:
        """Check if tithi spans both this and next sunrise (vriddhi)."""
        return (self.tithi_start_ahar < self.sunrise_ahar and 
                self.tithi_end_ahar > self.next_sunrise_ahar)
    
    @property
    def tithi_skipped(self) -> bool:
        """Check if tithi is skipped (ksaya) - starts after sunrise, ends before next sunrise."""
        return (self.tithi_start_ahar > self.sunrise_ahar and 
                self.tithi_end_ahar < self.next_sunrise_ahar)


@dataclass
class TithiDecisionData:
    """
    Result of rule evaluation.
    
    Contains the determined tithi along with metadata about
    which rule made the decision and confidence level.
    
    Attributes:
        tithi: Tithi day (1-15 within paksha)
        paksha: Paksha ('Suklapaksa' or 'Krsnapaksa')
        confidence: Confidence level (0-1)
        rule_name: Name of rule that made the decision
        tradition: Tradition used for calculation
        is_ksaya: Whether this is a ksaya (skipped) tithi
        is_vriddhi: Whether this is a vriddhi (extended) tithi
        notes: Additional notes about the decision
    """
    tithi: int
    paksha: str
    confidence: float = 1.0
    rule_name: str = ""
    tradition: str = "surya"
    is_ksaya: bool = False
    is_vriddhi: bool = False
    notes: List[str] = field(default_factory=list)
    
    def add_note(self, note: str) -> None:
        """Add a note to the decision."""
        self.notes.append(note)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tithi': self.tithi,
            'paksha': self.paksha,
            'confidence': self.confidence,
            'rule_name': self.rule_name,
            'tradition': self.tradition,
            'is_ksaya': self.is_ksaya,
            'is_vriddhi': self.is_vriddhi,
            'notes': self.notes
        }


class TithiRule(ABC):
    """
    Abstract base class for all tithi determination rules.
    
    Rules are evaluated in priority order. Each rule can either:
    - Return a TithiDecisionData if it makes a decision
    - Return None to defer to the next rule
    
    Subclasses must implement:
    - evaluate(): The main rule logic
    - name: A unique name for the rule
    - description: Human-readable description
    """
    
    name: str = "base_rule"
    description: str = "Base tithi rule"
    priority: int = 100  # Lower = higher priority
    category: RuleCategory = RuleCategory.TITHI
    
    def __init__(self, **params):
        """
        Initialize rule with optional parameters.
        
        Args:
            **params: Rule-specific parameters
        """
        self.params = params
        self.enabled = params.get('enabled', True)
    
    @abstractmethod
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate the rule and return decision or None.
        
        Args:
            context: TithiContext with all necessary data
            
        Returns:
            TithiDecisionData if rule makes a decision, None otherwise
        """
        pass
    
    def applies_to(self, context: TithiContext) -> bool:
        """
        Check if this rule applies to the given context.
        
        Override this method to add conditions for when the rule
        should be skipped entirely.
        
        Args:
            context: TithiContext to check
            
        Returns:
            True if rule should be evaluated, False to skip
        """
        return self.enabled
    
    def get_info(self) -> Dict[str, Any]:
        """Get rule information for API responses."""
        return {
            'name': self.name,
            'description': self.description,
            'priority': self.priority,
            'category': self.category.value,
            'enabled': self.enabled,
            'parameters': self.params
        }


class CompositeRule(TithiRule):
    """
    A rule that composes multiple sub-rules.
    
    Can be used to create complex rule combinations with
    AND/OR logic between sub-rules.
    """
    
    name = "composite_rule"
    description = "Composite rule combining multiple sub-rules"
    
    def __init__(self, rules: List[TithiRule], mode: str = "first_match", **params):
        """
        Initialize composite rule.
        
        Args:
            rules: List of sub-rules to compose
            mode: Combination mode:
                - "first_match": Return first non-None result
                - "all_agree": All rules must agree
                - "majority": Majority vote
            **params: Additional parameters
        """
        super().__init__(**params)
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.mode = mode
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """Evaluate composite rule based on mode."""
        if self.mode == "first_match":
            return self._first_match(context)
        elif self.mode == "all_agree":
            return self._all_agree(context)
        elif self.mode == "majority":
            return self._majority(context)
        return None
    
    def _first_match(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """Return first non-None result."""
        for rule in self.rules:
            if rule.applies_to(context):
                result = rule.evaluate(context)
                if result is not None:
                    return result
        return None
    
    def _all_agree(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """All rules must agree on the decision."""
        results = []
        for rule in self.rules:
            if rule.applies_to(context):
                result = rule.evaluate(context)
                if result is not None:
                    results.append(result)
        
        if not results:
            return None
        
        # Check if all agree
        first = results[0]
        if all(r.tithi == first.tithi and r.paksha == first.paksha for r in results):
            first.add_note(f"All {len(results)} rules agree")
            return first
        return None
    
    def _majority(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """Majority vote among rules."""
        results = []
        for rule in self.rules:
            if rule.applies_to(context):
                result = rule.evaluate(context)
                if result is not None:
                    results.append(result)
        
        if not results:
            return None
        
        # Count votes
        votes: Dict[tuple, List[TithiDecisionData]] = {}
        for r in results:
            key = (r.tithi, r.paksha)
            if key not in votes:
                votes[key] = []
            votes[key].append(r)
        
        # Find majority
        max_votes = 0
        winner = None
        for key, vote_list in votes.items():
            if len(vote_list) > max_votes:
                max_votes = len(vote_list)
                winner = vote_list[0]
        
        if winner:
            winner.add_note(f"Majority vote: {max_votes}/{len(results)}")
        return winner


class TraditionBase(ABC):
    """
    Abstract base class for calculation traditions.
    
    A tradition defines:
    - Which astronomical constants to use
    - Which rules are active by default
    - How to calculate specific elements
    
    Subclasses must implement:
    - name: Tradition identifier
    - display_name: Human-readable name
    - description: Description of the tradition
    - get_default_rules(): Returns list of default rules
    """
    
    name: str = "base"
    display_name: str = "Base Tradition"
    description: str = "Base tradition class"
    
    def __init__(self, **config):
        """
        Initialize tradition with optional configuration.
        
        Args:
            **config: Tradition-specific configuration
        """
        self.config = config
    
    @abstractmethod
    def get_default_rules(self) -> List[TithiRule]:
        """
        Return default rules for this tradition.
        
        Returns:
            List of TithiRule instances
        """
        pass
    
    @abstractmethod
    def get_planetary_constants(self) -> Dict[str, Any]:
        """
        Return planetary constants for this tradition.
        
        Returns:
            Dictionary with Yuga rotations and planetary parameters
        """
        pass
    
    def get_ayanamsa(self, ahar: float) -> float:
        """
        Calculate ayanamsa for this tradition.
        
        Default implementation uses Lahiri ayanamsa.
        Override for tradition-specific calculations.
        
        Args:
            ahar: Ahargana value
            
        Returns:
            Ayanamsa in degrees
        """
        # Default: Lahiri ayanamsa approximation
        # Reference: ayanamsa was 0 around 285 CE
        julian_year = ahar / 365.25 - 3101  # Approximate Julian year
        return (julian_year - 285) * (50.3 / 3600)  # ~50.3 arcseconds per year
    
    def get_info(self) -> Dict[str, Any]:
        """Get tradition information for API responses."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'default_rules': [r.name for r in self.get_default_rules()]
        }
