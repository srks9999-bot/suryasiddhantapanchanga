"""
Rule engine for Panchanga tithi determination.

The rule engine orchestrates the evaluation of multiple rules to determine
the tithi for a given day. It supports:
- Priority-based rule evaluation
- Tradition-specific rule sets
- Configuration-driven rule activation
- Evaluation tracing for debugging
"""

from typing import Optional, List, Dict, Any
from panchanga.rules.base import (
    TithiRule, TithiContext, TithiDecisionData, TraditionBase
)
from panchanga.rules.tithi_rules import AVAILABLE_RULES, get_rule


class RuleEngine:
    """
    Engine for evaluating tithi determination rules.
    
    The engine maintains a list of active rules and evaluates them
    in priority order until a decision is made.
    
    Attributes:
        tradition: The calculation tradition being used
        rules: List of active rules
        trace_enabled: Whether to record evaluation trace
    """
    
    def __init__(
        self,
        tradition: Optional[TraditionBase] = None,
        rules: Optional[List[TithiRule]] = None,
        trace_enabled: bool = False
    ):
        """
        Initialize the rule engine.
        
        Args:
            tradition: Tradition to use (determines default rules)
            rules: Custom list of rules (overrides tradition defaults)
            trace_enabled: Enable evaluation tracing
        """
        self.tradition = tradition
        self.trace_enabled = trace_enabled
        self._trace: List[Dict[str, Any]] = []
        
        if rules is not None:
            self.rules = sorted(rules, key=lambda r: r.priority)
        elif tradition is not None:
            self.rules = sorted(tradition.get_default_rules(), key=lambda r: r.priority)
        else:
            # Default rules if no tradition specified
            self.rules = self._get_default_rules()
    
    def _get_default_rules(self) -> List[TithiRule]:
        """Get default rule set."""
        from panchanga.rules.tithi_rules import (
            SunriseBasedRule, KsayaTithiRule, VriddhiTithiRule
        )
        return sorted([
            SunriseBasedRule(),
            KsayaTithiRule(),
            VriddhiTithiRule(),
        ], key=lambda r: r.priority)
    
    def add_rule(self, rule: TithiRule) -> None:
        """
        Add a rule to the engine.
        
        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a rule by name.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was found and removed
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """
        Enable a rule by name.
        
        Args:
            rule_name: Name of rule to enable
            
        Returns:
            True if rule was found
        """
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """
        Disable a rule by name.
        
        Args:
            rule_name: Name of rule to disable
            
        Returns:
            True if rule was found
        """
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False
    
    def evaluate(self, context: TithiContext) -> Optional[TithiDecisionData]:
        """
        Evaluate all rules and return the tithi decision.
        
        Rules are evaluated in priority order. The first rule that
        returns a non-None decision wins.
        
        Args:
            context: TithiContext with calculation data
            
        Returns:
            TithiDecisionData if any rule makes a decision, None otherwise
        """
        self._trace = []
        
        for rule in self.rules:
            # Check if rule applies
            if not rule.applies_to(context):
                self._add_trace(rule.name, "skipped", "Rule does not apply to context")
                continue
            
            # Evaluate rule
            try:
                result = rule.evaluate(context)
                
                if result is not None:
                    self._add_trace(
                        rule.name, 
                        "decided",
                        f"Tithi {result.tithi} {result.paksha}",
                        result.to_dict()
                    )
                    return result
                else:
                    self._add_trace(rule.name, "deferred", "Rule returned None")
                    
            except Exception as e:
                self._add_trace(rule.name, "error", str(e))
                continue
        
        # No rule made a decision - use fallback
        self._add_trace("fallback", "used", "No rule made a decision, using sunrise tithi")
        return TithiDecisionData(
            tithi=context.sunrise_tithi,
            paksha=context.sunrise_paksha,
            confidence=0.5,
            rule_name="fallback",
            tradition=context.tradition,
            notes=["No rule made a decision; using sunrise tithi as fallback"]
        )
    
    def _add_trace(
        self,
        rule_name: str,
        action: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add entry to evaluation trace if tracing is enabled."""
        if self.trace_enabled:
            entry = {
                'rule': rule_name,
                'action': action,
                'message': message
            }
            if data:
                entry['data'] = data
            self._trace.append(entry)
    
    def get_trace(self) -> List[Dict[str, Any]]:
        """
        Get the evaluation trace.
        
        Returns:
            List of trace entries from last evaluation
        """
        return self._trace.copy()
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """
        Get information about active rules.
        
        Returns:
            List of rule information dictionaries
        """
        return [rule.get_info() for rule in self.rules if rule.enabled]
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """
        Get information about all rules (including disabled).
        
        Returns:
            List of rule information dictionaries
        """
        return [rule.get_info() for rule in self.rules]
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'RuleEngine':
        """
        Create a rule engine from configuration dictionary.
        
        Args:
            config: Configuration with 'tradition' and 'rules' keys
            
        Returns:
            Configured RuleEngine instance
        """
        from panchanga.rules.traditions import TRADITIONS, DEFAULT_TRADITION
        
        # Get tradition
        tradition_name = config.get('tradition', DEFAULT_TRADITION)
        tradition_class = TRADITIONS.get(tradition_name)
        tradition = tradition_class() if tradition_class else None
        
        # Build rules from config
        rules_config = config.get('rules', [])
        rules = []
        
        for rule_cfg in rules_config:
            if isinstance(rule_cfg, str):
                # Simple rule name
                rule = get_rule(rule_cfg)
            elif isinstance(rule_cfg, dict):
                # Rule with parameters
                rule_name = rule_cfg.get('name')
                params = rule_cfg.get('params', {})
                params['enabled'] = rule_cfg.get('enabled', True)
                rule = get_rule(rule_name, **params)
            else:
                continue
            
            if rule:
                rules.append(rule)
        
        # If no rules specified, use tradition defaults
        if not rules and tradition:
            rules = tradition.get_default_rules()
        
        return cls(
            tradition=tradition,
            rules=rules if rules else None,
            trace_enabled=config.get('trace_enabled', False)
        )


# Singleton default engine
_default_engine: Optional[RuleEngine] = None


def get_default_engine() -> RuleEngine:
    """
    Get the default rule engine instance.
    
    Returns:
        Default RuleEngine instance
    """
    global _default_engine
    if _default_engine is None:
        _default_engine = RuleEngine()
    return _default_engine


def set_default_engine(engine: RuleEngine) -> None:
    """
    Set the default rule engine instance.
    
    Args:
        engine: RuleEngine to use as default
    """
    global _default_engine
    _default_engine = engine


def evaluate_tithi(context: TithiContext, engine: Optional[RuleEngine] = None) -> TithiDecisionData:
    """
    Convenience function to evaluate tithi using the default or provided engine.
    
    Args:
        context: TithiContext with calculation data
        engine: Optional engine to use (uses default if None)
        
    Returns:
        TithiDecisionData with the decision
    """
    if engine is None:
        engine = get_default_engine()
    
    result = engine.evaluate(context)
    if result is None:
        # Should not happen due to fallback, but handle gracefully
        result = TithiDecisionData(
            tithi=context.sunrise_tithi,
            paksha=context.sunrise_paksha,
            confidence=0.5,
            rule_name="emergency_fallback",
            tradition=context.tradition,
            notes=["Emergency fallback - no decision made"]
        )
    return result
