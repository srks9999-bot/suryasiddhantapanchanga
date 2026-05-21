"""
Calculation traditions for Panchanga.

Available traditions:
- Surya: Surya Siddhanta (ca. AD 1000) - Traditional Indian astronomical constants
- Drik: Drik Ganita - Modern ephemeris-based calculations
- Lunar: Lunar calendar conventions (Amanta/Purnimanta)
"""

from panchanga.rules.traditions.base import TraditionBase
from panchanga.rules.traditions.surya import SuryaTradition
from panchanga.rules.traditions.drik import DrikTradition
from panchanga.rules.traditions.lunar import LunarTradition

# Registry of available traditions
TRADITIONS = {
    "surya": SuryaTradition,
    "drik": DrikTradition,
    "lunar": LunarTradition,
}

DEFAULT_TRADITION = "surya"

__all__ = [
    "TraditionBase", "SuryaTradition", "DrikTradition", "LunarTradition",
    "TRADITIONS", "DEFAULT_TRADITION"
]
