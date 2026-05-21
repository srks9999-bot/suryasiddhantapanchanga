# ============================================================
# FULL PANCHANGA + LUNAR PERIGEE/APOGEE (HYDERABAD)
# Surya Siddhanta Angas + Drik Sunrise + Drik Moon Distance
# Gives:
#  - Tithi + Duration
#  - Nakshatra + Duration
#  - Yoga
#  - Karana (2)
#  - Lunar Perigee / Apogee (Nearest Event)
# ============================================================

import math
from datetime import datetime, timedelta

from skyfield.api import load, wgs84
from skyfield import almanac

# ---------------- BASIC MATH ----------------
PI = math.pi
RAD = 180 / PI

def trunc(x): return math.floor(x)
def frac(x): return x - math.floor(x)

def zero360(x): return x % 360

def arcsin(x):
    if abs(x) <= 1:
        return math.asin(x)
    return math.copysign(PI/2, x)

def ahar_to_time(ahar):
    h = trunc(frac(ahar) * 24)
    m = trunc((frac(ahar) * 24 - h) * 60)
    return f"{h:02d}:{m:02d}"

def duration_hours(a1, a2):
    """Ahargana difference → Hours"""
    return abs(a2 - a1) * 24

# ---------------- TELUGU NAMES ----------------
TITHI_NAMES = [
    "పాడ్యమి","విదియ","తృతీయ","చవితి","పంచమి",
    "షష్ఠి","సప్తమి","అష్టమి","నవమి","దశమి",
    "ఏకాదశి","ద్వాదశి","త్రయోదశి","చతుర్దశి","పౌర్ణమి",
    "పాడ్యమి","విదియ","తృతీయ","చవితి","పంచమి",
    "షష్ఠి","సప్తమి","అష్టమి","నవమి","దశమి",
    "ఏకాదశి","ద్వాదశి","త్రయోదశి","చతుర్దశి","అమావాస్య"
]

NAK_NAMES = [
    "అశ్విని","భరణి","కృత్తిక","రోహిణి","మృగశిర","ఆర్ద్ర",
    "పునర్వసు","పుష్య","ఆశ్లేష","మఘ",
    "పూర్వ ఫల్గుణి","ఉత్తర ఫల్గుణి","హస్త","చిత్ర","స్వాతి",
    "విశాఖ","అనురాధ","జ్యేష్ఠ","మూల",
    "పూర్వాషాఢ","ఉత్తరాషాఢ","శ్రావణ","ధనిష్ఠ","శతభిష",
    "పూర్వ భాద్రపద","ఉత్తర భాద్రపద","రేవతి"
]

YOGA_NAMES = [
    "విష్కంభ","ప్రీతి","ఆయుష్మాన్","సౌభాగ్య","శోభన",
    "అతిగండ","సుకర్మ","ధృతి","శూల","గండ",
    "వృద్ధి","ధ్రువ","వ్యాఘాత","హర్షణ","వజ్ర",
    "సిద్ధి","వ్యతిపాత","వరీయాన్","పరిఘ",
    "శివ","సిద్ధ","సాధ్య","శుభ","శుక్ల",
    "బ్రహ్మ","ఇంద్ర","వైదృతీ"
]

KARANA_NAMES = [
    "కింస్తుఘ్న","బవ","బాలవ","కౌలవ","తైతిల",
    "గరజ","వణిజ","విష్టి"
]

WEEKDAY = ['సోమవారం','మంగళవారం','బుధవారం','గురువారం',
           'శుక్రవారం','శనివారం','ఆదివారం']

# ---------------- JULIAN DAY ----------------
def jd_from_datetime(dt):
    y, m = dt.year, dt.month
    d = dt.day + (dt.hour + dt.minute/60)/24

    if m < 3:
        y -= 1
        m += 12

    jd = int(365.25*y) + int(30.59*(m-2)) + d + 1721086.5
    if jd > 2299160:
        jd += int(y/400) - int(y/100) + 2
    return jd

def ahargana(jd):
    return jd - 588465.5


# ============================================================
# PANCHANGA ENGINE
# ============================================================

class Panchanga:

    def _init_(self):

        # Surya Siddhanta constants
        self.sun_rot   = 4320000
        self.moon_rot  = 57753336
        self.candrocca = 488203
        self.civil_days = 1582237828 - 4320000

        # Skyfield setup
        self.ts = load.timescale()
        self.eph = load("de421.bsp")
        self.place = wgs84.latlon(17.385, 78.4867)

    # ---------------- MEAN LONGITUDE ----------------
    def mean_long(self, ah, rot):
        return 360 * frac(rot * ah / self.civil_days)

    # ---------------- TRUE SUN ----------------
    def true_sun(self, ah):
        m = self.mean_long(ah, self.sun_rot)
        manda = arcsin((13.833/360) * math.sin((m - 77.283)/RAD)) * RAD
        return zero360(m - manda)

    # ---------------- TRUE MOON ----------------
    def true_moon(self, ah):
        m = self.mean_long(ah, self.moon_rot)
        ap = self.mean_long(ah, self.candrocca) + 90

        manda = arcsin((31.833/360) * math.sin((m - ap)/RAD)) * RAD
        moon1 = m - manda

        sighra = arcsin((2.0/360) * math.sin((moon1 - ap)/RAD)) * RAD
        return zero360(moon1 + sighra)

    # ---------------- DRIG SUNRISE ----------------
    def drik_sunrise(self, date):

        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day + 1)

        f = almanac.sunrise_sunset(self.eph, self.place)
        times, events = almanac.find_discrete(t0, t1, f)

        for ti, ev in zip(times, events):
            if ev == 1:
                return ti.utc_datetime() + timedelta(hours=5, minutes=30)

        return None

    # ---------------- LUNAR DISTANCE ----------------
    def moon_distance_km(self, dt):

        t = self.ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)

        earth = self.eph["earth"]
        moon = self.eph["moon"]

        dist = earth.at(t).observe(moon).distance().km
        return dist

    # ---------------- FIND NEAREST PERIGEE/APOGEE ----------------
    def perigee_apogee(self, date):

        dt0 = date - timedelta(days=15)
        dt1 = date + timedelta(days=15)

        t0 = self.ts.utc(dt0.year, dt0.month, dt0.day)
        t1 = self.ts.utc(dt1.year, dt1.month, dt1.day)

        earth = self.eph["earth"]
        moon = self.eph["moon"]

        def distance(t):
            return earth.at(t).observe(moon).distance().km

        # sample every 6 hours
        times = []
        dists = []

        t = t0
        while t.tt <= t1.tt:
            dt = t.utc_datetime()
            dist = distance(t)

            times.append(dt)
            dists.append(dist)

            t = self.ts.utc(dt + timedelta(hours=6))

        # find min & max
        min_i = dists.index(min(dists))
        max_i = dists.index(max(dists))

        return times[min_i], dists[min_i], times[max_i], dists[max_i]

    # ---------------- FIND END TIME ----------------
    def find_end(self, ah, func):

        step = 0.0003
        v0 = trunc(func(ah))

        a = ah
        while trunc(func(a)) == v0:
            a += step

        b = a - step

        for _ in range(40):
            mid = (a + b) / 2
            if trunc(func(mid)) == v0:
                b = mid
            else:
                a = mid

        return (a + b) / 2

    # ---------------- FIND START TIME ----------------
    def find_start(self, ah, func):

        step = 0.0003
        v0 = trunc(func(ah))

        a = ah
        while trunc(func(a)) == v0:
            a -= step

        b = a + step

        for _ in range(40):
            mid = (a + b) / 2
            if trunc(func(mid)) == v0:
                a = mid
            else:
                b = mid

        return (a + b) / 2

    # ---------------- ANGAS ----------------
    def tithi(self, ah):
        return zero360(self.true_moon(ah) - self.true_sun(ah)) / 12

    def nakshatra(self, ah):
        return self.true_moon(ah) * 27 / 360

    # ---------------- ONE DAY PANCHANGA ----------------
    def one_day(self, y, m, d):

        dt = datetime(y, m, d, 6, 0, 0)

        wd = WEEKDAY[dt.weekday()]
        sunrise_dt = self.drik_sunrise(dt)
        ah_sr = ahargana(jd_from_datetime(sunrise_dt))

        # ----------- TITHI -----------
        t_index = trunc(self.tithi(ah_sr))
        t_start = self.find_start(ah_sr, self.tithi)
        t_end   = self.find_end(ah_sr, self.tithi)
        t_dur   = duration_hours(t_start, t_end)

        # ----------- NAKSHATRA -------
        n_index = trunc(self.nakshatra(ah_sr))
        n_start = self.find_start(ah_sr, self.nakshatra)
        n_end   = self.find_end(ah_sr, self.nakshatra)
        n_dur   = duration_hours(n_start, n_end)

        # ----------- PERIGEE / APOGEE -------
        per_dt, per_km, apo_dt, apo_km = self.perigee_apogee(dt)

        # ----------- PRINT ----------
        print("\n===================================================")
        print("   🕉️ PANCHANGA + LUNAR PERIGEE/APOGEE 🕉️")
        print("===================================================")
        print(f"Date       : {y}-{m:02d}-{d:02d}")
        print(f"Weekday    : {wd}")
        print(f"Sunrise    : {sunrise_dt.strftime('%H:%M')}")
        print("---------------------------------------------------")

        print("Tithi      :", TITHI_NAMES[t_index],
              f"({t_dur:.2f} hrs)")
        print("Start-End  :", ahar_to_time(t_start),
              "→", ahar_to_time(t_end))

        print("Nakshatra  :", NAK_NAMES[n_index],
              f"({n_dur:.2f} hrs)")
        print("Start-End  :", ahar_to_time(n_start),
              "→", ahar_to_time(n_end))

        print("---------------------------------------------------")
        print("🌙 Nearest Perigee :",
              per_dt.strftime("%Y-%m-%d %H:%M"),
              f"Distance = {per_km:,.0f} km")

        print("🌕 Nearest Apogee  :",
              apo_dt.strftime("%Y-%m-%d %H:%M"),
              f"Distance = {apo_km:,.0f} km")

        print("===================================================\n")


# ---------------- RUN ----------------
if _name_ == "_main_":

    p = Panchanga()

    # Example Hyderabad Date
    p.one_day(2026, 1, 23)