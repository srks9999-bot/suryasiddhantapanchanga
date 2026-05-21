import math

def calculate_desantara_all(observer_lat, observer_long):
    """
    Calculates Desantara Phala for all 9 planets (Navagraha).
    """
    
    # --- 1. Constants & Location Setup ---
    EARTH_DIAMETER = 1600.0
    PRIME_MERIDIAN = 75.7667  # Ujjain/Lanka
    
    # Bhu Paridhi & Sphuta Paridhi
    bhu_paridhi = EARTH_DIAMETER * math.sqrt(10)
    co_latitude_rad = math.radians(90 - observer_lat)
    sphuta_paridhi = bhu_paridhi * math.sin(co_latitude_rad)
    
    # Time Difference Calculation
    long_diff = observer_long - PRIME_MERIDIAN
    time_diff_ghatis = long_diff / 6.0
    desantara_yojanas = (sphuta_paridhi * time_diff_ghatis) / 60.0

    # --- 2. Define Planetary Motions (Degrees per Day) ---
    # Based on Surya Siddhanta approximations
    planets = {
        "Sun":        0.9856,
        "Moon":       13.1764,
        "Mars":       0.5240,
        "Mercury (Sheeghra)": 4.0923, # Motion of its Fast Apogee
        "Jupiter":    0.0831,
        "Venus (Sheeghra)":   1.6021, # Motion of its Fast Apogee
        "Saturn":     0.0335,
        "Rahu":      -0.0530, # Retrograde (Negative motion)
        "Ketu":      -0.0530  # Retrograde (Same as Rahu)
    }

    # --- 3. Output Header ---
    print(f"--- Desantara Corrections ---")
    print(f"Location: {observer_lat}°N, {observer_long}°E")
    print(f"Dist from Prime Meridian: {desantara_yojanas:.2f} Yojanas")
    print(f"{'Planet':<20} | {'Daily Motion':<12} | {'Correction (Deg)':<18} | {'Correction (Min/Kala)'}")
    print("-" * 85)

    # --- 4. Loop Through Planets ---
    results = {}
    
    for name, motion in planets.items():
        # The Core Formula: (Motion * Desantara Yojanas) / Sphuta Paridhi
        correction_deg = (motion * desantara_yojanas) / sphuta_paridhi
        
        # Convert to Minutes (Kalas) for easier reading
        correction_min = correction_deg * 60
        
        results[name] = correction_deg
        
        # Formatting for the table
        print(f"{name:<20} | {motion:<12.4f} | {correction_deg:<18.6f} | {correction_min:.4f}")

    return results

# --- Example Usage ---
# Hyderabad Coordinates
lat = 17.3850
long = 78.4867

corrections = calculate_desantara_all(lat, long)

print("-" * 85)
print("NOTE: ")
print("1. If the correction is POSITIVE (+), ADD it to the Mean Longitude.")
print("2. If the correction is NEGATIVE (-), SUBTRACT it from the Mean Longitude.")
print("3. For Rahu/Ketu, the sign is automatically flipped because their motion is negative.")