"""
Planetary constants and Yuga rotations for different traditions.

This module contains astronomical constants used in Panchanga calculations,
including Yuga rotation counts and planetary parameters for different
calculation traditions (Surya Siddhanta, Drik Ganita, etc.).
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class YugaRotations:
    """
    Yuga rotation constants for a specific tradition.
    
    These represent the number of rotations each celestial body makes
    during a Maha Yuga (4,320,000 solar years).
    """
    star: int = 0
    sun: int = 0
    moon: int = 0
    mercury: int = 0
    venus: int = 0
    mars: int = 0
    jupiter: int = 0
    saturn: int = 0
    candrocca: int = 0  # Lunar apogee
    rahu: int = 0       # Lunar node (negative for retrograde)
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            'star': self.star,
            'sun': self.sun,
            'moon': self.moon,
            'mercury': self.mercury,
            'venus': self.venus,
            'mars': self.mars,
            'jupiter': self.jupiter,
            'saturn': self.saturn,
            'Candrocca': self.candrocca,
            'Rahu': self.rahu
        }


@dataclass
class PlanetaryConstants:
    """
    Planetary constants for a specific tradition.
    
    Contains apogee positions and circumference values used
    in manda (equation of center) and sighra (anomaly) corrections.
    """
    # Apogee positions (degrees)
    sun_apogee: float = 0.0
    moon_apogee: float = 0.0  # This is dynamic, calculated from Candrocca
    mercury_apogee: float = 0.0
    venus_apogee: float = 0.0
    mars_apogee: float = 0.0
    jupiter_apogee: float = 0.0
    saturn_apogee: float = 0.0
    
    # Manda circumference (epicycle size for equation of center)
    sun_circumm: float = 0.0
    moon_circumm: float = 0.0
    mercury_circumm: float = 0.0
    venus_circumm: float = 0.0
    mars_circumm: float = 0.0
    jupiter_circumm: float = 0.0
    saturn_circumm: float = 0.0
    
    # Sighra circumference (epicycle size for anomaly correction)
    mercury_circums: float = 0.0
    venus_circums: float = 0.0
    mars_circums: float = 0.0
    jupiter_circums: float = 0.0
    saturn_circums: float = 0.0


# Surya Siddhanta constants (ca. AD 1000)
SURYA_SIDDHANTA_ROTATIONS = YugaRotations(
    star=1582237828,
    sun=4320000,
    moon=57753336,
    mercury=17937060,
    venus=7022376,
    mars=2296832,
    jupiter=364220,
    saturn=146568,
    candrocca=488203,
    rahu=-232238  # Negative for retrograde motion
)

SURYA_SIDDHANTA_PLANETARY = PlanetaryConstants(
    # Apogees
    sun_apogee=77 + 17/60,
    mercury_apogee=220 + 27/60,
    venus_apogee=79 + 50/60,
    mars_apogee=130 + 2/60,
    jupiter_apogee=171 + 18/60,
    saturn_apogee=236 + 37/60,
    
    # Manda circumference
    sun_circumm=13 + 50/60,
    moon_circumm=31 + 50/60,
    mercury_circumm=29,
    venus_circumm=11.5,
    mars_circumm=73.5,
    jupiter_circumm=32.5,
    saturn_circumm=48.5,
    
    # Sighra circumference
    mercury_circums=131.5,
    venus_circums=261,
    mars_circums=233.5,
    jupiter_circums=71,
    saturn_circums=39.5
)


# Pancasiddhantika constants (AD 505) - older system
PANCASIDDHANTIKA_ROTATIONS = YugaRotations(
    star=1582237800,
    sun=4320000,
    moon=57753336,
    mercury=17937000,
    venus=7022388,
    mars=2296824,
    jupiter=364220,
    saturn=146564,
    candrocca=488219,
    rahu=-232226
)

# Pancasiddhantika uses same planetary constants as Surya Siddhanta
# (the main differences are in the Yuga rotation counts)
PANCASIDDHANTIKA_PLANETARY = SURYA_SIDDHANTA_PLANETARY


# Registry of tradition constants
TRADITION_ROTATIONS = {
    'surya': SURYA_SIDDHANTA_ROTATIONS,
    'pancasiddhantika': PANCASIDDHANTIKA_ROTATIONS,
    # 'drik' and 'lunar' will use different calculation methods
    # and may not use these fixed rotation constants
}

TRADITION_PLANETARY = {
    'surya': SURYA_SIDDHANTA_PLANETARY,
    'pancasiddhantika': PANCASIDDHANTIKA_PLANETARY,
}


def get_yuga_rotations(tradition: str = 'surya') -> YugaRotations:
    """
    Get Yuga rotation constants for a tradition.
    
    Args:
        tradition: Name of tradition ('surya', 'pancasiddhantika')
        
    Returns:
        YugaRotations instance for the tradition
    """
    return TRADITION_ROTATIONS.get(tradition, SURYA_SIDDHANTA_ROTATIONS)


def get_planetary_constants(tradition: str = 'surya') -> PlanetaryConstants:
    """
    Get planetary constants for a tradition.
    
    Args:
        tradition: Name of tradition ('surya', 'pancasiddhantika')
        
    Returns:
        PlanetaryConstants instance for the tradition
    """
    return TRADITION_PLANETARY.get(tradition, SURYA_SIDDHANTA_PLANETARY)


def calculate_derived_constants(rotations: YugaRotations) -> Dict[str, int]:
    """
    Calculate derived constants from Yuga rotations.
    
    Args:
        rotations: YugaRotations instance
        
    Returns:
        Dictionary with derived values:
        - YugaCivilDays: Civil days in a Yuga
        - YugaSynodicMonth: Synodic months in a Yuga
        - YugaAdhimasa: Adhimasas (intercalary months) in a Yuga
        - YugaTithi: Tithis in a Yuga
        - YugaKsayadina: Ksayadinas (lost days) in a Yuga
    """
    yuga_civil_days = rotations.star - rotations.sun
    yuga_synodic_month = rotations.moon - rotations.sun
    yuga_adhimasa = yuga_synodic_month - 12 * rotations.sun
    yuga_tithi = 30 * yuga_synodic_month
    yuga_ksayadina = yuga_tithi - yuga_civil_days
    
    return {
        'YugaCivilDays': yuga_civil_days,
        'YugaSynodicMonth': yuga_synodic_month,
        'YugaAdhimasa': yuga_adhimasa,
        'YugaTithi': yuga_tithi,
        'YugaKsayadina': yuga_ksayadina
    }
