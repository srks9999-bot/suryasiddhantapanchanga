import swisseph as swe
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------
IST_OFFSET = timedelta(hours=5, minutes=30)

# Swiss Ephemeris path (optional)
swe.set_ephe_path(".")

# ------------------------------------------------------------
# Moon Distance Function (km)
# ------------------------------------------------------------
def moon_distance_km(dt):
    """
    Returns geocentric Moon distance in km using Swiss Ephemeris
    """
    jd = swe.julday(dt.year, dt.month, dt.day,
                   dt.hour + dt.minute/60 + dt.second/3600)

    # Moon position (flags: Swiss Ephemeris)
    xx, _ = swe.calc_ut(jd, swe.MOON)

    # xx[2] = distance in AU
    dist_au = xx[2]

    # Convert AU → km
    return dist_au * 149597870.7


# ------------------------------------------------------------
# Quadratic Interpolation Peak Finder
# ------------------------------------------------------------
def quadratic_peak(t1, y1, t2, y2, t3, y3):
    """
    Fit parabola through 3 points and return peak time + value
    """

    x = np.array([-1, 0, 1])
    y = np.array([y1, y2, y3])

    a, b, c = np.polyfit(x, y, 2)

    xp = -b / (2 * a)
    yp = a*xp**2 + b*xp + c

    exact_time = t2 + timedelta(minutes=float(xp))

    return exact_time, yp


# ------------------------------------------------------------
# Find Perigees + Apogees for One Year
# ------------------------------------------------------------
def perigee_apogee_year(year):

    print("\n===========================================")
    print(f"🌙 Swiss Ephemeris Perigees & Apogees {year}")
    print("Console Only | IST Output")
    print("===========================================\n")

    start = datetime(year, 1, 1)
    end   = datetime(year + 1, 1, 1)

    step = timedelta(minutes=10)

    times = []
    dists = []

    # --- Scan Year ---
    t = start
    while t < end:
        times.append(t)
        dists.append(moon_distance_km(t))
        t += step

    # --- Find local extrema ---
    events = []

    for i in range(1, len(dists) - 1):

        if dists[i] < dists[i-1] and dists[i] < dists[i+1]:
            events.append((times[i], "Perigee"))

        if dists[i] > dists[i-1] and dists[i] > dists[i+1]:
            events.append((times[i], "Apogee"))

    # --- Refine each event ---
    for approx_time, mode in events:

        # Minute refinement ±2 hours
        window_start = approx_time - timedelta(hours=2)
        window_end   = approx_time + timedelta(hours=2)

        refine_times = []
        refine_dists = []

        tt = window_start
        while tt <= window_end:
            refine_times.append(tt)
            refine_dists.append(moon_distance_km(tt))
            tt += timedelta(minutes=1)

        # Find best index
        if mode == "Perigee":
            idx = np.argmin(refine_dists)
        else:
            idx = np.argmax(refine_dists)

        # Quadratic interpolation (3 points)
        if idx == 0 or idx == len(refine_dists) - 1:
            continue

        t1, y1 = refine_times[idx-1], refine_dists[idx-1]
        t2, y2 = refine_times[idx], refine_dists[idx]
        t3, y3 = refine_times[idx+1], refine_dists[idx+1]

        exact_time, exact_dist = quadratic_peak(t1, y1, t2, y2, t3, y3)

        # Convert to IST
        exact_time_ist = exact_time + IST_OFFSET

        print(f"{mode:8s} | {exact_time_ist:%Y-%b-%d %I:%M:%S %p} | {exact_dist:,.3f} km")


# ------------------------------------------------------------
# Run Automation 2026–2027
# ------------------------------------------------------------
if _name_ == "_main_":

    perigee_apogee_year(2026)
    perigee_apogee_year(2027)