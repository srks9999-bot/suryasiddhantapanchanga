"""
Astronomical calculations for Panchanga.

This module provides the core astronomical calculations used in Panchanga,
including planetary position calculations, sunrise/sunset times, and
various astronomical corrections.
"""

import math
from typing import Dict, Tuple, Optional
from panchanga.core.constants import PI, RAD, EPSILON
from panchanga.core.math_utils import MathUtils
from panchanga.core.debug_context import debug_trace, debug_log, debug_value
from panchanga.data.planetary import (
    YugaRotations, PlanetaryConstants,
    SURYA_SIDDHANTA_ROTATIONS, SURYA_SIDDHANTA_PLANETARY,
    calculate_derived_constants
)


class AstronomicalCalculator:
    """
    Core astronomical calculations for Panchanga.
    
    This class handles all planetary position calculations based on
    classical Indian astronomical methods (Surya Siddhanta).
    """
    
    def __init__(
        self,
        rotations: Optional[YugaRotations] = None,
        planetary: Optional[PlanetaryConstants] = None
    ):
        """
        Initialize astronomical calculator.
        
        Args:
            rotations: Yuga rotation constants
            planetary: Planetary constants
        """
        self.rotations = rotations or SURYA_SIDDHANTA_ROTATIONS
        self.planetary = planetary or SURYA_SIDDHANTA_PLANETARY
        self._derived = calculate_derived_constants(self.rotations)
        
        # Cache for expensive calculations
        self._cache: Dict[str, any] = {}
    
    @property
    def yuga_civil_days(self) -> int:
        """Get number of civil days in a Yuga."""
        return self._derived['YugaCivilDays']
    
    @property
    def yuga_synodic_month(self) -> int:
        """Get number of synodic months in a Yuga."""
        return self._derived['YugaSynodicMonth']
    
    @property
    def yuga_adhimasa(self) -> int:
        """Get number of adhimasas in a Yuga."""
        return self._derived['YugaAdhimasa']
    
    @property
    def yuga_tithi(self) -> int:
        """Get number of tithis in a Yuga."""
        return self._derived['YugaTithi']
    
    @property
    def yuga_ksayadina(self) -> int:
        """Get number of ksayadinas in a Yuga."""
        return self._derived['YugaKsayadina']
    
    def _get_daily_motion(self, planet: str) -> float:
        """
        Calculate mean daily motion in degrees.
        Formula: (Rotations * 360) / YugaCivilDays
        """
        rotations = self._get_planet_rotation(planet)
        
        # Handle Retrograde nodes (Rahu/Ketu)
        if planet in ['rahu', 'ketu']:
            # In your class, get_rahu_longitude treats rotation as positive
            # but we need negative motion for Desantara logic
            return -1 * (rotations * 360) / self.yuga_civil_days
            
        return (rotations * 360) / self.yuga_civil_days

    @debug_trace
    def get_desantara(self, planet: str, obs_lat: float, obs_long: float) -> float:
        """
        Calculate the Desantara (longitudinal) correction for a specific planet.
        
        This method automatically selects the correct daily motion:
        - Mercury/Venus: Uses Sighra (Fast) motion (approx 4°/day for Merc).
        - Mars/Jup/Sat: Uses Mean motion.
        - Rahu/Ketu: Uses Retrograde motion.
        
        Args:
            planet: Planet name (sun, moon, mercury, venus, mars, jupiter, saturn, rahu, ketu)
            obs_lat: Observer's Latitude
            obs_long: Observer's Longitude
            
        Returns:
            Correction in degrees. 
            (Subtract this from the Mean Longitude if Observer is East of Ujjain).
        """
        # --- 1. Constants & Geometry ---
        # Ujjain/Lanka Meridian (Classical Reference)
        SS_PRIME_MERIDIAN = 75.7667 
        EARTH_DIAMETER = 1600.0
        
        # Bhu Paridhi (Earth Circumference)
        bhu_paridhi = EARTH_DIAMETER * math.sqrt(10)
        
        # Sphuta Paridhi (Rectified Circumference at Latitude)
        co_lat_rad = (90 - obs_lat) / RAD
        sphuta_paridhi = bhu_paridhi * math.sin(co_lat_rad)
        
        # --- 2. Time Difference (Desantara) ---
        # Distance from Ujjain to Observer
        long_diff = obs_long - SS_PRIME_MERIDIAN
        
        # Convert to Time Difference in Ghatis (1 deg = 1/6 ghati)
        time_diff_ghatis = long_diff / 6.0
        
        # Convert to Desantara Yojanas
        desantara_yojanas = (sphuta_paridhi * time_diff_ghatis) / 60.0
        
        # --- 3. Determine Correct Motion Speed ---
        # Calculate rotations per Yuga based on planet type
        rotations = 0
        
        if planet in ('mercury', 'venus'):
            # IMPORTANT: For Mercury/Venus, the Mean Longitude follows the Sun,
            # but their physical position is determined by their Sighra (Fast) motion.
            # We use Sighra speed for the most accurate Desantara correction.
            rotations = self.rotations.mercury if planet == 'mercury' else self.rotations.venus
        elif planet in ('rahu', 'ketu'):
            # Retrograde motion (negative speed)
            # Use Rahu's rotation count (negative direction)
            rotations = -1 * self.rotations.rahu
        else:
            # Standard Planets (Sun, Moon, Mars, Jup, Sat) use Mean rotations
            rotations = self._get_planet_rotation(planet)

        # Calculate Daily Motion (Degrees/Day)
        daily_motion = (rotations * 360) / self.yuga_civil_days
        
        # --- 4. Final Calculation ---
        # Formula: (DailyMotion * DesantaraYojanas) / SphutaParidhi
        correction = (daily_motion * desantara_yojanas) / sphuta_paridhi
        
        debug_log("Desantara Single", 
                  planet=planet, 
                  motion_type="Sighra" if planet in ('mercury', 'venus') else "Mean",
                  daily_motion=daily_motion,
                  correction=correction)
                  
        return correction

    def get_precise_elongation(self, ahar: float) -> float:
        """
        Get the precise elongation (Moon - Sun) normalized to 0-360.
        This is the raw fuel for Tithi calculations.
        """
        tslong = self.get_true_solar_longitude(ahar)
        tllong = self.get_true_lunar_longitude(ahar)
        return MathUtils.zero360(tllong - tslong)
        
    def get_true_planet_longitude(self, ahar: float, planet: str, 
                                  location: Optional[Tuple[float, float]] = None) -> float:
        """
        Calculate true longitude (Updated to support Desantara).
        
        Args:
            ahar: Ahargana
            planet: Planet name
            location: Optional tuple (latitude, longitude) for Desantara correction
        """
        # 1. Get Base Mean Longitude (at Ujjain)
        mean_sun = self.get_mean_longitude(ahar, self.rotations.sun)
        
        if planet in ('mercury', 'venus'):
            planet_mean = mean_sun
        else:
            planet_mean = self.get_mean_longitude(ahar, self._get_planet_rotation(planet))
            
        # --- DESANTARA INTEGRATION START ---
        if location:
            lat, long = location
            
            # Apply correction to Planet Mean
            # Note: We subtract the correction. 
            # If East (long > 75), correction is (+), so we subtract.
            # If West (long < 75), correction is (-), subtracting a negative adds it.
            p_corr = self.get_desantara(planet, lat, long)
            planet_mean = planet_mean - p_corr
            
            # Apply correction to Sun Mean (needed for anomalies)
            s_corr = self.get_desantara('sun', lat, long)
            mean_sun = mean_sun - s_corr
            
            # Note: Sighra Mean usually needs correction too if it's derived from Sun
        # --- DESANTARA INTEGRATION END ---

        # Get sighra mean longitude
        sighra_mean = self.get_mean_longitude(ahar, self._get_planet_sighra(planet))
        # Get apogee
        apogee = self._get_apogee(planet)
        
        # ===== STEP 1: First Sighra Half-Correction =====
        if planet in ('mercury', 'venus'):
            # For inferior planets: sighra anomaly = sighra - mean Sun
            anomaly1 = sighra_mean - mean_sun
        else:
            # For superior planets: sighra anomaly = sighra (Sun) - planet mean
            anomaly1 = sighra_mean - planet_mean
        
        equ1 = self.get_sighra_equation(anomaly1, planet)
        
        # ===== STEP 2: First Manda Half-Correction =====
        mean_long1 = planet_mean + equ1 / 2
        argument1 = mean_long1 - apogee
        equ2 = self.get_manda_equation(argument1, planet)
        
        # ===== STEP 3: Second Manda Correction =====
        mean_long2 = mean_long1 - equ2 / 2
        argument2 = mean_long2 - apogee
        equ3 = self.get_manda_equation(argument2, planet)
        
        # ===== STEP 4: Second Sighra Correction =====
        mean_long3 = planet_mean - equ3
        anomaly2 = sighra_mean - mean_long3
        equ4 = self.get_sighra_equation(anomaly2, planet)
        
        # Final true longitude
        true_longitude = MathUtils.zero360(mean_long3 + equ4)
        
        return true_longitude
        
    @debug_trace
    def get_mean_sun_longitude(self, ahar: float, rotation: int) -> float:
        """
        Calculate mean longitude of a celestial body.
        
        Formula: MeanLong = 360 * frac(rotation * ahar / YugaCivilDays)
        
        Args:
            ahar: Ahargana (days from epoch)
            rotation: Number of rotations in a Yuga
            
        Returns:
            Mean longitude in degrees (0-360)
        """
        srushtiAdiAhargana = 714402296627
        ratio = rotation * (ahar + srushtiAdiAhargana) / self.yuga_civil_days
        frac_part = MathUtils.frac(ratio)
        result = 360 * frac_part
        
        debug_log("Mean longitude calculation (with Srishti Adi)", 
                  ratio=ratio, frac=frac_part, result=result,
                  formula="360 * frac(rotation * (ahar + srushtiAdiAhargana) / YugaCivilDays)")
        return result

    @debug_trace
    def get_mean_longitude(self, ahar: float, rotation: int) -> float:
        """
        Calculate mean longitude of a celestial body.
        
        Formula: MeanLong = 360 * frac(rotation * ahar / YugaCivilDays)
        
        Args:
            ahar: Ahargana (days from epoch)
            rotation: Number of rotations in a Yuga
            
        Returns:
            Mean longitude in degrees (0-360)
        """
        srushtiAdiAhargana = 714402296627
        ratio = rotation * (ahar) / self.yuga_civil_days
        frac_part = MathUtils.frac(ratio)
        result = 360 * frac_part
        
        debug_log("Mean longitude calculation", 
                  ratio=ratio, frac=frac_part, result=result,
                  formula="vikas 360 * frac(rotation *  (ahar + srushtiAdiAhargana) / YugaCivilDays) ")
        return result
    
    @debug_trace
    def get_manda_equation(self, argument: float, planet: str) -> float:
        """
        Calculate manda (equation of center) correction.
        
        Formula: MandaCorr = arcsin(circumm/360 * sin(argument)) * RAD
        
        The manda correction accounts for the eccentricity of the orbit.
        
        Args:
            argument: Manda argument in degrees
            planet: Planet name
            
        Returns:
            Manda correction in degrees
        """
        circumm = self._get_circumm(planet)
        arg_rad = argument / RAD
        sin_arg = math.sin(arg_rad)
        ratio = circumm / 360
        sine_corr = ratio * sin_arg
        result = MathUtils.arcsin(sine_corr) * RAD
        debug_log("Manda equation calculation",
                  planet=planet, circumm=circumm, argument=argument,
                  sin_arg=sin_arg, ratio=ratio, sine_corr=sine_corr,
                  result=result,
                  formula="arcsin(circumm/360 * sin(argument)) * (180/π)")
        return result
    
    def get_sighra_equation(self, anomaly: float, planet: str) -> float:
        """
        Calculate sighra (anomaly) correction.
        
        The sighra correction accounts for the planet's position on its
        epicycle as seen from Earth.
        
        Args:
            anomaly: Sighra anomaly in degrees
            planet: Planet name
            
        Returns:
            Sighra correction in degrees
        """
        circums = self._get_circums(planet)
        bhuja = circums / 360 * math.sin(anomaly / RAD) * RAD
        koti = circums / 360 * math.cos(anomaly / RAD) * RAD
        karna = math.sqrt(MathUtils.sqr(RAD + koti) + MathUtils.sqr(bhuja))
        return MathUtils.arcsin(bhuja / karna) * RAD
    
    def _get_circumm(self, planet: str) -> float:
        """Get manda circumference for a planet."""
        mapping = {
            'sun': self.planetary.sun_circumm,
            'moon': self.planetary.moon_circumm,
            'mercury': self.planetary.mercury_circumm,
            'venus': self.planetary.venus_circumm,
            'mars': self.planetary.mars_circumm,
            'jupiter': self.planetary.jupiter_circumm,
            'saturn': self.planetary.saturn_circumm,
        }
        return mapping.get(planet, 0)
    
    def _get_circums(self, planet: str) -> float:
        """Get sighra circumference for a planet."""
        mapping = {
            'mercury': self.planetary.mercury_circums,
            'venus': self.planetary.venus_circums,
            'mars': self.planetary.mars_circums,
            'jupiter': self.planetary.jupiter_circums,
            'saturn': self.planetary.saturn_circums,
        }
        return mapping.get(planet, 0)
    
    def _get_apogee(self, planet: str) -> float:
        """Get apogee position for a planet."""
        mapping = {
            'sun': self.planetary.sun_apogee,
            'mercury': self.planetary.mercury_apogee,
            'venus': self.planetary.venus_apogee,
            'mars': self.planetary.mars_apogee,
            'jupiter': self.planetary.jupiter_apogee,
            'saturn': self.planetary.saturn_apogee,
        }
        return mapping.get(planet, 0)
    
    @debug_trace
    def get_true_solar_longitude(self, ahar: float) -> float:
        """
        Calculate true solar longitude.
        
        Formula: TrueSun = zero360(MeanSun - MandaCorrection)
        where MandaArg = MeanSun - SunApogee
        
        Args:
            ahar: Ahargana
            
        Returns:
            True solar longitude in degrees (0-360)
        """
        mslong = self.get_mean_longitude(ahar, self.rotations.sun)
        debug_log("Step 1: Got mean Sun longitude", mean_sun=mslong)
        
        sun_apogee = self.planetary.sun_apogee
        manda_arg = mslong - sun_apogee
        debug_log("Step 2: Computed manda argument", 
                  sun_apogee=sun_apogee, manda_arg=manda_arg,
                  formula="MandaArg = MeanSun - SunApogee")
        
        manda_correction = self.get_manda_equation(manda_arg, 'sun')
        debug_log("Step 3: Got manda correction", manda_correction=manda_correction)
        
        result = MathUtils.zero360(mslong - manda_correction)
        debug_log("Step 4: Computed true Sun", 
                  true_sun=result,
                  formula="TrueSun = zero360(MeanSun - MandaCorr)")
        return result
    
    @debug_trace
    def get_true_lunar_longitude(self, ahar: float) -> float:
        """
        Calculate true lunar longitude.
        
        Formula: TrueMoon = zero360(MeanMoon - MandaCorrection)
        where MoonApogee = MeanCandrocca + 90°
        
        Args:
            ahar: Ahargana
            
        Returns:
            True lunar longitude in degrees (0-360)
        """
        mllong = self.get_mean_longitude(ahar, self.rotations.moon)
        debug_log("Step 1: Got mean Moon longitude", mean_moon=mllong)
        
        # Moon's apogee (Candrocca) position + 90°
        mean_candrocca = self.get_mean_longitude(ahar, self.rotations.candrocca)
        moon_apogee = mean_candrocca + 90
        debug_log("Step 2: Computed Moon apogee",
                  mean_candrocca=mean_candrocca, moon_apogee=moon_apogee,
                  formula="MoonApogee = MeanCandrocca + 90°")
        
        manda_arg = mllong - moon_apogee
        debug_log("Step 3: Computed manda argument", manda_arg=manda_arg)
        
        manda_correction = self.get_manda_equation(manda_arg, 'moon')
        debug_log("Step 4: Got manda correction", manda_correction=manda_correction)
        
        result = MathUtils.zero360(mllong - manda_correction)
        debug_log("Step 5: Computed true Moon",
                  true_moon=result,
                  formula="TrueMoon = zero360(MeanMoon - MandaCorr)")
        return result
    
    def get_elongation(self, ahar: float) -> float:
        """
        Calculate elongation between Sun and Moon.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Elongation in degrees (0-180)
        """
        elong = abs(self.get_true_lunar_longitude(ahar) - self.get_true_solar_longitude(ahar))
        if elong > 180:
            elong = 360 - elong
        return elong
    
    @debug_trace
    def get_tithi(self, tllong: float, tslong: float) -> float:
        """
        Calculate tithi from lunar and solar longitudes.
        
        Formula: Tithi = zero360(Moon - Sun) / 12
        Each tithi spans 12° of elongation (360° / 30 tithis)
        
        Args:
            tllong: True lunar longitude
            tslong: True solar longitude
            
        Returns:
            Tithi as a float (0-30)
        """
        raw_diff = tllong - tslong
        elong = MathUtils.zero360(raw_diff)
        tithi = elong / 12
        debug_log("Tithi calculation",
                  moon_longitude=tllong, sun_longitude=tslong,
                  raw_difference=raw_diff, elongation_normalized=elong,
                  tithi_float=tithi, tithi_day=int(tithi) + 1,
                  formula="Tithi = zero360(Moon - Sun) / 12°")
        return tithi
    
    def get_declination(self, longitude: float) -> float:
        """
        Calculate declination from longitude.
        
        Args:
            longitude: Celestial longitude in degrees
            
        Returns:
            Declination in degrees
        """
        return MathUtils.arcsin(
            math.sin(longitude / RAD) * math.sin(24 / RAD)
        ) * RAD
    
    @debug_trace
    def get_daylight_equation(self, year: int, lat: float, ahar: float) -> float:
        """
        Calculate equation of daylight.
        
        Formula: EqTime = 0.5 * arcsin(tan(lat) * tan(decl)) / π
        
        Args:
            year: Year
            lat: Latitude in degrees
            ahar: Ahargana
            
        Returns:
            Daylight equation as fraction of day
        """
        mslong = self.get_mean_longitude(ahar, self.rotations.sun)
        debug_log("Step 1: Got mean Sun for daylight", mean_sun=mslong)
        
        # Adjust for precession
        precession_corr = (54 / 3600) * (year - 499)
        samslong = mslong + precession_corr
        debug_log("Step 2: Applied precession", 
                  precession_corr=precession_corr, 
                  precession_adjusted_sun=samslong,
                  formula="Samslong = MeanSun + (54/3600)*(year-499)")
        
        sdecl = self.get_declination(samslong)
        debug_log("Step 3: Got solar declination", declination=sdecl)
        
        tan_lat = MathUtils.tan(lat / RAD)
        tan_decl = MathUtils.tan(sdecl / RAD)
        x = tan_lat * tan_decl
        result = 0.5 * MathUtils.arcsin(x) / PI
        
        debug_log("Step 4: Computed daylight equation",
                  tan_lat=tan_lat, tan_decl=tan_decl, x=x,
                  daylight_eq=result,
                  formula="0.5 * arcsin(tan(lat)*tan(decl)) / π")
        return result
    
    def get_sunrise_time(self, eqtime: float) -> Tuple[int, int]:
        """
        Calculate sunrise time from daylight equation.
        
        Args:
            eqtime: Daylight equation
            
        Returns:
            Tuple of (hours, minutes)
        """
        hours = MathUtils.trunc((0.25 - eqtime) * 24)
        minutes = MathUtils.trunc(60 * MathUtils.frac((0.25 - eqtime) * 24))
        return (hours, minutes)
    
    def get_sunset_time(self, eqtime: float) -> Tuple[int, int]:
        """
        Calculate sunset time from daylight equation.
        
        Args:
            eqtime: Daylight equation
            
        Returns:
            Tuple of (hours, minutes)
        """
        hours = MathUtils.trunc((0.75 + eqtime) * 24)
        minutes = MathUtils.trunc(60 * MathUtils.frac((0.75 + eqtime) * 24))
        return (hours, minutes)
    
    def get_ayanamsa(self, ahar: float) -> Tuple[int, int]:
        """
        Calculate ayanamsa.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Tuple of (degrees, minutes)
        """
        value = (54 * self.rotations.sun / self.yuga_civil_days / 3600) * (ahar - 1314930)
        degrees = MathUtils.trunc(value)
        minutes = MathUtils.trunc(60 * MathUtils.frac(value))
        return (degrees, minutes)
    
    def find_conjunction(
        self,
        leftx: float,
        lefty: float,
        rightx: float,
        righty: float
    ) -> float:
        """
        Find conjunction (new moon) using binary search.
        
        Args:
            leftx: Left bound ahargana
            lefty: Elongation at left bound
            rightx: Right bound ahargana
            righty: Elongation at right bound
            
        Returns:
            True solar longitude at conjunction
        """
        width = (rightx - leftx) / 2
        centrex = (rightx + leftx) / 2
        
        if width < EPSILON:
            return self.get_true_solar_longitude(centrex)
        
        centrey = self.get_elongation(centrex)
        relation = MathUtils.three_relation(lefty, centrey, righty)
        
        if relation < 0:
            rightx = rightx + width
            righty = self.get_elongation(rightx)
            return self.find_conjunction(centrex, centrey, rightx, righty)
        elif relation > 0:
            leftx = leftx - width
            lefty = self.get_elongation(leftx)
            return self.find_conjunction(leftx, lefty, centrex, centrey)
        else:
            leftx = leftx + width / 2
            lefty = self.get_elongation(leftx)
            rightx = rightx - width / 2
            righty = self.get_elongation(rightx)
            return self.find_conjunction(leftx, lefty, rightx, righty)
    
    def get_conjunction(self, ahar: float) -> float:
        """
        Get longitude at conjunction near given ahargana.
        
        Args:
            ahar: Ahargana
            
        Returns:
            True solar longitude at conjunction
        """
        return self.find_conjunction(
            ahar - 2, self.get_elongation(ahar - 2),
            ahar + 2, self.get_elongation(ahar + 2)
        )
    
    def ahargana_to_kali(self, ahar: float) -> int:
        """
        Convert Ahargana to Kali year.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Kali year
        """
        return MathUtils.trunc(ahar * self.rotations.sun / self.yuga_civil_days)
    
    def kali_to_ahargana(self, year_kali: int, masa_num: int, tithi_day: int) -> float:
        """
        Convert Kali date to Ahargana.
        
        Args:
            year_kali: Kali year
            masa_num: Masa number (0-11)
            tithi_day: Tithi day (1-30)
            
        Returns:
            Ahargana
        """
        sm = year_kali * 12 + masa_num  # expired saura masas
        adhim = int(sm * self.yuga_adhimasa / (12 * self.rotations.sun))  # expired adhimasas
        cm = sm + adhim  # expired candra masas
        tithi = 30 * cm + tithi_day - 1  # expired tithis
        avama = int(tithi * self.yuga_ksayadina / self.yuga_tithi)  # expired avamas
        return tithi - avama
    
    def find_samkranti(self, o_ahar: float, n_ahar: float) -> float:
        """
        Find samkranti (solar ingress) time.
        
        Args:
            o_ahar: Old ahargana bound
            n_ahar: New ahargana bound
            
        Returns:
            Ahargana at samkranti
        """
        o_tslong = self.get_true_solar_longitude(o_ahar)
        n_tslong = self.get_true_solar_longitude(n_ahar)
        
        o_tslong = o_tslong - int(o_tslong / 30) * 30
        n_tslong = n_tslong - int(n_tslong / 30) * 30
        
        width = (n_ahar - o_ahar) / 2
        c_ahar = (n_ahar + o_ahar) / 2
        
        if width < EPSILON:
            return c_ahar
        
        c_tslong = self.get_true_solar_longitude(c_ahar)
        c_tslong = c_tslong - int(c_tslong / 30) * 30
        
        if c_tslong < 5:
            return self.find_samkranti(o_ahar, c_ahar)
        else:
            return self.find_samkranti(c_ahar, n_ahar)
    
    def clear_cache(self):
        """Clear calculation cache."""
        self._cache.clear()
    
    # =========================================================================
    # Planetary Longitude Calculations (All Planets)
    # =========================================================================
    
    def _get_planet_rotation(self, planet: str) -> int:
        """Get yuga rotation count for a planet."""
        mapping = {
            'sun': self.rotations.sun,
            'moon': self.rotations.moon,
            'mercury': self.rotations.mercury,
            'venus': self.rotations.venus,
            'mars': self.rotations.mars,
            'jupiter': self.rotations.jupiter,
            'saturn': self.rotations.saturn,
            'candrocca': self.rotations.candrocca,
            'rahu': self.rotations.rahu,
        }
        return mapping.get(planet, 0)
    
    def _get_planet_sighra(self, planet: str) -> int:
        """
        Get sighra rotation count for a planet.
        
        For inferior planets (Mercury, Venus): their own rotation (faster than Sun)
        For superior planets (Mars, Jupiter, Saturn): Sun's rotation
        """
        mapping = {
            'mercury': self.rotations.mercury,
            'venus': self.rotations.venus,
            'mars': self.rotations.sun,
            'jupiter': self.rotations.sun,
            'saturn': self.rotations.sun,
        }
        return mapping.get(planet, self.rotations.sun)
    
    def get_planet_longitude(self, ahar: float, planet: str) -> float:
        """
        Calculate true longitude of a planet using 4-step Surya Siddhanta method.
        
        This implements the full iterative correction algorithm:
        1. First sighra half-correction
        2. First manda half-correction  
        3. Second manda full correction
        4. Second sighra full correction
        
        For inferior planets (Mercury, Venus):
            Mean longitude follows the Sun
            Sighra rotation is the planet's own orbital speed
            
        For superior planets (Mars, Jupiter, Saturn):
            Mean longitude is the planet's own
            Sighra rotation is the Sun's (used for geocentric correction)
        
        Args:
            ahar: Ahargana (days from Kali epoch)
            planet: Planet name ('mercury', 'venus', 'mars', 'jupiter', 'saturn')
            
        Returns:
            True longitude in degrees (0-360)
            
        Reference: SuryaSiddhantham.java lines 565-596
        """
        # Get mean Sun longitude (needed for both inferior and superior planets)
        mean_sun = self.get_mean_longitude(ahar, self.rotations.sun)
        
        # Determine mean position based on planet type
        if planet in ('mercury', 'venus'):
            # Inferior planets: mean longitude follows the Sun
            planet_mean = mean_sun
        else:
            # Superior planets: their own mean longitude
            planet_mean = self.get_mean_longitude(ahar, self._get_planet_rotation(planet))
        
        # Get sighra mean longitude
        sighra_mean = self.get_mean_longitude(ahar, self._get_planet_sighra(planet))
        
        # Get apogee
        apogee = self._get_apogee(planet)
        
        # ===== STEP 1: First Sighra Half-Correction =====
        if planet in ('mercury', 'venus'):
            # For inferior planets: sighra anomaly = sighra - mean Sun
            anomaly1 = sighra_mean - mean_sun
        else:
            # For superior planets: sighra anomaly = sighra (Sun) - planet mean
            anomaly1 = sighra_mean - planet_mean
        
        equ1 = self.get_sighra_equation(anomaly1, planet)
        
        # ===== STEP 2: First Manda Half-Correction =====
        mean_long1 = planet_mean + equ1 / 2
        argument1 = mean_long1 - apogee
        equ2 = self.get_manda_equation(argument1, planet)
        
        # ===== STEP 3: Second Manda Correction =====
        mean_long2 = mean_long1 - equ2 / 2
        argument2 = mean_long2 - apogee
        equ3 = self.get_manda_equation(argument2, planet)
        
        # ===== STEP 4: Second Sighra Correction =====
        mean_long3 = planet_mean - equ3
        anomaly2 = sighra_mean - mean_long3
        equ4 = self.get_sighra_equation(anomaly2, planet)
        
        # Final true longitude
        true_longitude = MathUtils.zero360(mean_long3 + equ4)
        
        return true_longitude
    
    def get_true_planet_longitude_detailed(self, ahar: float, planet: str) -> Dict[str, float]:
        """
        Calculate true longitude with all intermediate values for debugging.
        
        Args:
            ahar: Ahargana
            planet: Planet name
            
        Returns:
            Dictionary with all intermediate calculation values
        """
        mean_sun = self.get_mean_longitude(ahar, self.rotations.sun)
        
        if planet in ('mercury', 'venus'):
            planet_mean = mean_sun
        else:
            planet_mean = self.get_mean_longitude(ahar, self._get_planet_rotation(planet))
        
        sighra_mean = self.get_mean_longitude(ahar, self._get_planet_sighra(planet))
        apogee = self._get_apogee(planet)
        
        # Step 1
        if planet in ('mercury', 'venus'):
            anomaly1 = sighra_mean - mean_sun
        else:
            anomaly1 = sighra_mean - planet_mean
        equ1 = self.get_sighra_equation(anomaly1, planet)
        
        # Step 2
        mean_long1 = planet_mean + equ1 / 2
        argument1 = mean_long1 - apogee
        equ2 = self.get_manda_equation(argument1, planet)
        
        # Step 3
        mean_long2 = mean_long1 - equ2 / 2
        argument2 = mean_long2 - apogee
        equ3 = self.get_manda_equation(argument2, planet)
        
        # Step 4
        mean_long3 = planet_mean - equ3
        anomaly2 = sighra_mean - mean_long3
        equ4 = self.get_sighra_equation(anomaly2, planet)
        
        true_longitude = MathUtils.zero360(mean_long3 + equ4)
        
        return {
            'planet': planet,
            'mean_sun': mean_sun,
            'planet_mean': planet_mean,
            'sighra_mean': sighra_mean,
            'apogee': apogee,
            # Step 1
            'anomaly1': anomaly1,
            'equ1_sighra_half': equ1,
            # Step 2
            'mean_long1': mean_long1,
            'argument1': argument1,
            'equ2_manda_half': equ2,
            # Step 3
            'mean_long2': mean_long2,
            'argument2': argument2,
            'equ3_manda': equ3,
            # Step 4
            'mean_long3': mean_long3,
            'anomaly2': anomaly2,
            'equ4_sighra': equ4,
            # Result
            'true_longitude': true_longitude
        }
    
    def get_rahu_longitude(self, ahar: float) -> float:
        """
        Calculate Rahu (North Lunar Node) longitude.
        
        Rahu moves retrograde (negative rotation in yuga counts).
        
        Args:
            ahar: Ahargana
            
        Returns:
            Rahu longitude in degrees (0-360)
        """
        # Rahu has no manda or sighra corrections, just mean longitude
        return MathUtils.zero360(self.get_mean_longitude(ahar, self.rotations.rahu))
    
    def get_ketu_longitude(self, ahar: float) -> float:
        """
        Calculate Ketu (South Lunar Node) longitude.
        
        Ketu is always 180° opposite to Rahu.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Ketu longitude in degrees (0-360)
        """
        return MathUtils.zero360(self.get_rahu_longitude(ahar) + 180)
    
    def get_all_planet_positions(self, ahar: float) -> Dict[str, float]:
        """
        Calculate true longitudes for all celestial bodies.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Dictionary with all planet longitudes
        """
        return {
            'sun': self.get_true_solar_longitude(ahar),
            'moon': self.get_true_lunar_longitude(ahar),
            'mercury': self.get_true_planet_longitude(ahar, 'mercury'),
            'venus': self.get_true_planet_longitude(ahar, 'venus'),
            'mars': self.get_true_planet_longitude(ahar, 'mars'),
            'jupiter': self.get_true_planet_longitude(ahar, 'jupiter'),
            'saturn': self.get_true_planet_longitude(ahar, 'saturn'),
            'rahu': self.get_rahu_longitude(ahar),
            'ketu': self.get_ketu_longitude(ahar),
        }
    
    def get_all_planet_positions_detailed(self, ahar: float) -> Dict[str, Dict[str, float]]:
        """
        Calculate detailed positions for all celestial bodies with intermediate values.
        
        Args:
            ahar: Ahargana
            
        Returns:
            Dictionary with detailed calculation info for each planet
        """
        result = {}
        
        # Sun
        mslong = self.get_mean_longitude(ahar, self.rotations.sun)
        tslong = self.get_true_solar_longitude(ahar)
        result['sun'] = {
            'mean_longitude': mslong,
            'apogee': self.planetary.sun_apogee,
            'manda_arg': mslong - self.planetary.sun_apogee,
            'manda_corr': self.get_manda_equation(mslong - self.planetary.sun_apogee, 'sun'),
            'true_longitude': tslong
        }
        
        # Moon
        mllong = self.get_mean_longitude(ahar, self.rotations.moon)
        mean_candrocca = self.get_mean_longitude(ahar, self.rotations.candrocca)
        moon_apogee = mean_candrocca + 90
        tllong = self.get_true_lunar_longitude(ahar)
        result['moon'] = {
            'mean_longitude': mllong,
            'mean_candrocca': mean_candrocca,
            'apogee': moon_apogee,
            'manda_arg': mllong - moon_apogee,
            'manda_corr': self.get_manda_equation(mllong - moon_apogee, 'moon'),
            'true_longitude': tllong
        }
        
        # Five planets
        for planet in ['mercury', 'venus', 'mars', 'jupiter', 'saturn']:
            result[planet] = self.get_true_planet_longitude_detailed(ahar, planet)
        
        # Nodes
        rahu_long = self.get_ketu_longitude(ahar)
        result['rahu'] = {
            'mean_longitude': rahu_long,
            'true_longitude': rahu_long,
            'note': 'retrograde motion'
        }
        result['ketu'] = {
            'mean_longitude': MathUtils.zero360(rahu_long + 180),
            'true_longitude': MathUtils.zero360(rahu_long + 180),
            'note': '180° from Rahu'
        }
        
        return result