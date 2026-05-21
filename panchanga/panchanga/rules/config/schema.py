"""
Rule configuration schema and loading utilities.

This module provides Pydantic models for validating rule configurations
and utilities for loading configurations from YAML files.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class RuleParams(BaseModel):
    """Parameters for a single rule."""
    enabled: bool = True
    priority: Optional[int] = None
    # Rule-specific parameters (validated per-rule)
    extra: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = 'allow'


class RuleConfigItem(BaseModel):
    """Configuration for a single rule."""
    name: str
    enabled: bool = True
    priority: Optional[int] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class LunarOptions(BaseModel):
    """Lunar tradition specific options."""
    month_ending: str = Field(default="amanta", pattern="^(amanta|purnimanta)$")
    adhika_masa_rule: str = Field(default="solar_month")


class RuleConfig(BaseModel):
    """
    Complete rule configuration schema.
    
    This model validates the structure of rule configuration files
    and provides defaults for missing values.
    """
    tradition: str = Field(
        default="surya",
        description="Calculation tradition (surya, drik, lunar)"
    )
    ayanamsa: str = Field(
        default="lahiri",
        description="Ayanamsa system (lahiri, raman, krishnamurti, none)"
    )
    rules: List[Union[str, RuleConfigItem]] = Field(
        default_factory=list,
        description="List of rules to apply"
    )
    lunar_options: Optional[LunarOptions] = Field(
        default=None,
        description="Options for lunar tradition"
    )
    custom_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Custom rule definitions"
    )
    trace_enabled: bool = Field(
        default=False,
        description="Enable rule evaluation tracing"
    )
    
    @field_validator('tradition')
    @classmethod
    def validate_tradition(cls, v):
        valid = ['surya', 'drik', 'lunar', 'amanta', 'purnimanta']
        if v not in valid:
            raise ValueError(f"tradition must be one of {valid}")
        return v
    
    @field_validator('ayanamsa')
    @classmethod
    def validate_ayanamsa(cls, v):
        valid = ['lahiri', 'raman', 'krishnamurti', 'none']
        if v not in valid:
            raise ValueError(f"ayanamsa must be one of {valid}")
        return v
    
    def get_rules_list(self) -> List[RuleConfigItem]:
        """
        Convert rules to list of RuleConfigItem.
        
        Handles both string rule names and full config objects.
        """
        result = []
        for rule in self.rules:
            if isinstance(rule, str):
                result.append(RuleConfigItem(name=rule))
            elif isinstance(rule, RuleConfigItem):
                result.append(rule)
            elif isinstance(rule, dict):
                result.append(RuleConfigItem(**rule))
        return result


def load_config(path: Union[str, Path]) -> RuleConfig:
    """
    Load rule configuration from a YAML file.
    
    Args:
        path: Path to YAML configuration file
        
    Returns:
        Validated RuleConfig instance
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for config loading. Install with: pip install pyyaml")
    
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if data is None:
        data = {}
    
    return RuleConfig(**data)


def load_config_from_string(yaml_string: str) -> RuleConfig:
    """
    Load rule configuration from a YAML string.
    
    Args:
        yaml_string: YAML configuration as string
        
    Returns:
        Validated RuleConfig instance
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for config loading. Install with: pip install pyyaml")
    
    data = yaml.safe_load(yaml_string)
    if data is None:
        data = {}
    
    return RuleConfig(**data)


def get_default_config() -> RuleConfig:
    """
    Get default rule configuration.
    
    Returns:
        Default RuleConfig instance
    """
    return RuleConfig(
        tradition="surya",
        ayanamsa="lahiri",
        rules=[
            RuleConfigItem(name="purnima_amavasya", priority=5),
            RuleConfigItem(name="sunrise_based", priority=10),
            RuleConfigItem(name="ksaya_handling", priority=15, params={"merge_with_previous": True}),
            RuleConfigItem(name="vriddhi_handling", priority=16, params={"assign_to_first_day": False}),
        ]
    )


def save_config(config: RuleConfig, path: Union[str, Path]) -> None:
    """
    Save rule configuration to a YAML file.
    
    Args:
        config: RuleConfig to save
        path: Path to save to
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for config saving. Install with: pip install pyyaml")
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict, handling Pydantic models
    data = config.model_dump(exclude_none=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# Default configuration directory
DEFAULT_CONFIG_DIR = Path(__file__).parent


def get_config_path(name: str = "default") -> Path:
    """
    Get path to a named configuration file.
    
    Args:
        name: Configuration name (without .yaml extension)
        
    Returns:
        Path to configuration file
    """
    return DEFAULT_CONFIG_DIR / f"{name}.yaml"
