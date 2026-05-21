"""
Settings model for Panchanga calculations.

This module defines the configuration settings used by the Panchanga calculator,
including location, language, and calculation tradition preferences.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from panchanga.core.constants import (
    UJJAINI_LAT, UJJAINI_LON, DEFAULT_LANGUAGE, DEFAULT_TRADITION
)


@dataclass
class PanchangaSettings:
    """
    Settings for Panchanga calculations.
    
    Attributes:
        selected_system: Calculation system to use ('SuryaSiddhanta' or 'InPancasiddhantika')
        tradition: Calculation tradition ('surya', 'drik', 'lunar')
        loc_lat: Location latitude in degrees
        loc_lon: Location longitude in degrees
        language: Output language ('telugu', 'english')
        ayanamsa: Ayanamsa system to use ('lahiri', 'raman', 'krishnamurti', 'none')
        use_drik_sunrise_sunset: Use Drik ephemeris for sunrise/sunset reporting (default: False)
        use_sunrise_for_tithi: Calculate tithi at sunrise instead of midnight (default: False)
                              WARNING: Setting to True may affect epoch/historical calculations.
                              Keep False for Kali Yuga epoch consistency.
    """
    selected_system: str = 'SuryaSiddhanta'
    tradition: str = DEFAULT_TRADITION
    loc_lat: float = UJJAINI_LAT
    loc_lon: float = UJJAINI_LON
    language: str = DEFAULT_LANGUAGE
    ayanamsa: str = 'lahiri'
    use_drik_sunrise_sunset: bool = True
    use_sunrise_for_tithi: bool = False
    
    @property
    def desantara(self) -> float:
        """
        Calculate Desantara - time difference from IST standard meridian (82.5°E).
        
        This represents the local time offset in days from the IST reference.
        
        Returns:
            Time difference in days (positive = east of reference)
        """
        return (self.loc_lon - UJJAINI_LON) / 360
    
    def copy(self, **updates) -> 'PanchangaSettings':
        """
        Create a copy of settings with optional updates.
        
        Args:
            **updates: Keyword arguments for fields to update
            
        Returns:
            New PanchangaSettings instance with updates applied
        """
        return PanchangaSettings(
            selected_system=updates.get('selected_system', self.selected_system),
            tradition=updates.get('tradition', self.tradition),
            loc_lat=updates.get('loc_lat', self.loc_lat),
            loc_lon=updates.get('loc_lon', self.loc_lon),
            language=updates.get('language', self.language),
            ayanamsa=updates.get('ayanamsa', self.ayanamsa),
            use_drik_sunrise_sunset=updates.get('use_drik_sunrise_sunset', self.use_drik_sunrise_sunset),
            use_sunrise_for_tithi=updates.get('use_sunrise_for_tithi', self.use_sunrise_for_tithi)
        )
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            'selected_system': self.selected_system,
            'tradition': self.tradition,
            'latitude': self.loc_lat,
            'longitude': self.loc_lon,
            'language': self.language,
            'ayanamsa': self.ayanamsa,
            'use_drik_sunrise_sunset': self.use_drik_sunrise_sunset,
            'use_sunrise_for_tithi': self.use_sunrise_for_tithi
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PanchangaSettings':
        """Create settings from dictionary."""
        return cls(
            selected_system=data.get('selected_system', 'SuryaSiddhanta'),
            tradition=data.get('tradition', DEFAULT_TRADITION),
            loc_lat=data.get('latitude', data.get('loc_lat', UJJAINI_LAT)),
            loc_lon=data.get('longitude', data.get('loc_lon', UJJAINI_LON)),
            language=data.get('language', DEFAULT_LANGUAGE),
            ayanamsa=data.get('ayanamsa', 'lahiri'),
            use_drik_sunrise_sunset=data.get('use_drik_sunrise_sunset', False),
            use_sunrise_for_tithi=data.get('use_sunrise_for_tithi', False)
        )


# Preset locations
LOCATION_PRESETS = {
    'ujjain': PanchangaSettings(loc_lat=23.2, loc_lon=75.8),
    'delhi': PanchangaSettings(loc_lat=28.6, loc_lon=77.2),
    'mumbai': PanchangaSettings(loc_lat=19.1, loc_lon=72.9),
    'chennai': PanchangaSettings(loc_lat=13.1, loc_lon=80.3),
    'kolkata': PanchangaSettings(loc_lat=22.6, loc_lon=88.4),
    'bengaluru': PanchangaSettings(loc_lat=12.97, loc_lon=77.59),
    'hyderabad': PanchangaSettings(loc_lat=17.4, loc_lon=78.5),
    'varanasi': PanchangaSettings(loc_lat=25.3, loc_lon=83.0),
}
