from datetime import datetime
import math


PROFILE_COLUMNS = [
    "PRES",
    "HGHT",
    "TEMP",
    "DWPT",
    "RELH",
    "MIXR",
    "DRCT",
    "SPED",
    "THTA",
    "THTE",
    "THTV"
]


MIN_LEVELS = 3


def validate_data(data):

    # -------------------------------
    # Required Keys
    # -------------------------------

    required = [
        "station_name",
        "station_number",
        "launch_time",
        *PROFILE_COLUMNS
    ]

    for key in required:

        if key not in data:
            return False, f"Missing Key : {key}"

    # -------------------------------
    # Launch Time
    # -------------------------------

    if not isinstance(data["launch_time"], datetime):
        return False, "Invalid Launch Time"

    # -------------------------------
    # Empty Profile
    # -------------------------------

    n = len(data["PRES"])

    if n < MIN_LEVELS:
        return False, "Too Few Levels"

    # -------------------------------
    # Equal Length
    # -------------------------------

    for column in PROFILE_COLUMNS:

        if len(data[column]) != n:
            return False, f"Length Mismatch : {column}"

    # -------------------------------
    # Numeric Check
    # -------------------------------

    for column in PROFILE_COLUMNS:

        for value in data[column]:

            if not isinstance(value, (int, float)):
                return False, f"Non Numeric : {column}"

            # NaN is ALLOWED
            if math.isinf(value):
                return False, f"Infinite Value : {column}"

    # -------------------------------
    # Pressure
    # -------------------------------

    pressure = [
        p for p in data["PRES"]
        if not math.isnan(p)
    ]

    for p in pressure:

        if p <= 0:
            return False, "Invalid Pressure"

    # -------------------------------
    # Height
    # -------------------------------

    for h in data["HGHT"]:

        if math.isnan(h):
            continue

        if h < 0:
            return False, "Negative Height"

    # -------------------------------
    # Relative Humidity
    # -------------------------------

    for rh in data["RELH"]:

        if math.isnan(rh):
            continue

        if rh < 0 or rh > 100:
            return False, "Invalid Relative Humidity"

    # -------------------------------
    # Wind Direction
    # -------------------------------

    for wd in data["DRCT"]:

        if math.isnan(wd):
            continue

        if wd < 0 or wd > 360:
            return False, "Invalid Wind Direction"

    # -------------------------------
    # Wind Speed
    # -------------------------------

    for ws in data["SPED"]:

        if math.isnan(ws):
            continue

        if ws < 0:
            return False, "Negative Wind Speed"

    return True, None