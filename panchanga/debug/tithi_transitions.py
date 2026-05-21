#!/usr/bin/env python3
"""
Debug script to print tithi transitions for a given date without the API server.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# !/usr/bin/env python3
# !/usr/bin/env python3
"""
Deep Diagnostic for Tithi Ruling Logic.
Prints the exact comparisons made to determine the Ruling Tithi.
"""

import argparse
from datetime import date

from panchanga.core.calculator import PanchangaCalculator
from panchanga.core.date_utils import DateUtils
from panchanga.data.names import get_tithi_name
from panchanga.models.settings import PanchangaSettings


def format_ahar_as_dt(calculator, ahar: float) -> str:
    """Helper to convert Ahargana to a readable Date/Time string."""
    # Get the date components from the library
    dt = calculator._ahar_to_datetime(ahar)

    # 1. If it's a datetime object, it should already work
    if hasattr(dt, 'strftime'):
        return dt.strftime("%Y-%m-%d %H:%M")

    # 2. Extract date components
    y = dt.get('year') or dt.get('y')
    m = dt.get('month') or dt.get('m')
    d = dt.get('day') or dt.get('d')

    # 3. CALCULATE TIME FROM FRACTION
    # Ahargana 0.5 is Midnight. We need the fractional part of the day.
    # We add 0.5 because JD/Ahargana .0 is noon and .5 is midnight.
    fractional_day = (ahar) % 1

    total_minutes = int(fractional_day * 1440)  # 1440 mins in a day
    hh = (total_minutes // 60) % 24
    mm = total_minutes % 60

    return f"{y}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}"


def analyze_ruling_logic(
        calculator: PanchangaCalculator,
        year: int,
        month: int,
        day: int,
) -> None:
    language = calculator.settings.language or "english"

    print(f"\n{'=' * 120}")
    print(f"DIAGNOSTIC REPORT FOR: {year}-{month:02d}-{day:02d}")
    print(f"{'=' * 120}")

    # 1. Calculate Sunrise Baseline
    astro_midnight = calculator.calculate_astronomical(year, month, day, 6, 0)
    sriseh, srisem = astro_midnight["sunrise"]

    astro_sunrise = calculator.calculate_astronomical(year, month, day, sriseh, srisem)
    sunrise_ahar = astro_sunrise["ahar_at_time"]

    print(f"1. SUNRISE BASELINE")
    print(f"   Calculated Time: {sriseh:02d}:{srisem:02d}")
    print(f"   Ahargana Value:  {sunrise_ahar:.6f}")
    print(f"   Human Readable:  {format_ahar_as_dt(calculator, sunrise_ahar)}")

    # 2. Check Tithi Directly at Sunrise
    elements = calculator._get_elements_at_ahar(sunrise_ahar, language)
    ruling_name = get_tithi_name(elements["tithi_day"], elements["paksa"], language)

    print(f"\n2. TRUTH CHECK (Direct Query at {sriseh:02d}:{srisem:02d})")
    print(f"   Active Name:     {ruling_name} ({elements['paksa']})")

    # 3. Scan for Tithis and Log Logic with Readable Timestamps
    print(f"\n3. TRANSITION LOGIC CHECK")
    # Header updated to include Date/Time columns
    header = (f"   {'Tithi Name':<15} | {'Start (Ahar)':<14} | {'Start Date/Time':<18} | "
              f"{'End (Ahar)':<14} | {'End Date/Time':<18} | {'Result'}")
    print(header)
    print("-" * 120)

    scan_ahar = sunrise_ahar - 0.5
    stop_ahar = sunrise_ahar + 0.5
    epsilon = 0.00001

    while scan_ahar < stop_ahar:
        el = calculator._get_elements_at_ahar(scan_ahar, language)
        t_day, paksa = el["tithi_day"], el["paksa"]
        t_name = get_tithi_name(t_day, paksa, language)

        start_ahar = calculator._find_tithi_start_time(scan_ahar, t_day, paksa, language)
        end_ahar = calculator._find_tithi_end_time(scan_ahar, t_day, paksa, language)

        # Convert Ahargana to Strings
        start_dt_str = format_ahar_as_dt(calculator, start_ahar)
        end_dt_str = format_ahar_as_dt(calculator, end_ahar)

        # Logic Check
        cond_start = (start_ahar <= sunrise_ahar + epsilon)
        cond_end = (end_ahar >= sunrise_ahar - epsilon)
        res_str = "RULING" if (cond_start and cond_end) else "NO"

        print(f"   {t_name:<15} | {start_ahar:<14.4f} | {start_dt_str:<18} | "
              f"{end_ahar:<14.4f} | {end_dt_str:<18} | {res_str}")

        scan_ahar = end_ahar + 0.01
        if start_ahar > stop_ahar:
            break


def build_calculator(args):
    settings = PanchangaSettings()
    if args.lat: settings.loc_lat = args.lat
    if args.lon: settings.loc_lon = args.lon
    settings.language = args.lang or "english"
    if args.drik: settings.use_drik_sunrise_sunset = True
    return PanchangaCalculator(settings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("month", type=int)
    parser.add_argument("day", type=int)
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--lang", type=str)
    parser.add_argument("--drik", action="store_true")
    args = parser.parse_args()

    calc = build_calculator(args)
    analyze_ruling_logic(calc, args.year, args.month, args.day)


if __name__ == "__main__":
    main()