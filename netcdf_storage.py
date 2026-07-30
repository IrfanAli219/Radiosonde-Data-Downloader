from datetime import datetime

import numpy as np
from netCDF4 import Dataset, date2num, num2date

from config import DATA_DIR


# ==========================================================
# Configuration
# ==========================================================

NETCDF_FOLDER = DATA_DIR / "netcdf"
NETCDF_FOLDER.mkdir(parents=True, exist_ok=True)

TIME_UNITS = "hours since 1970-01-01 00:00:00"
TIME_CALENDAR = "standard"

VARIABLES = (
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
)


# ==========================================================
# File Path
# ==========================================================

def get_netcdf_file(station_name):

    return NETCDF_FOLDER / f"{station_name}.nc"


# ==========================================================
# Pad One Profile To A Fixed Width (NaN-filled)
# ==========================================================

def _pad(values, width):

    values = np.asarray(values, dtype=np.float32)

    padded = np.full(width, np.nan, dtype=np.float32)

    padded[:len(values)] = values

    return padded


# ==========================================================
# Read Existing Launches (if file exists)
# ==========================================================

def read_existing_launches(station_name):

    path = get_netcdf_file(station_name)

    if not path.exists():
        return {}

    ds = Dataset(path, "r")

    time_var = ds.variables["time"]

    times = num2date(
        time_var[:],
        units=time_var.units,
        calendar=time_var.calendar
    )

    launches = {}

    for i, t in enumerate(times):

        launch_time = datetime(
            t.year, t.month, t.day,
            t.hour, t.minute, t.second
        )

        row = {"launch_time": launch_time}

        for var in VARIABLES:

            row[var] = np.array(
                ds.variables[var][i, :],
                dtype=np.float32
            )

        launches[launch_time] = row

    ds.close()

    return launches


# ==========================================================
# Load Only Existing Launch Times (cheap pre-check)
# ==========================================================

def load_existing_launch_times(station_name):

    path = get_netcdf_file(station_name)

    if not path.exists():
        return set()

    ds = Dataset(path, "r")

    time_var = ds.variables["time"]

    times = num2date(
        time_var[:],
        units=time_var.units,
        calendar=time_var.calendar
    )

    ds.close()

    return {
        datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
        for t in times
    }


# ==========================================================
# Write Station File (merge, sort, rewrite atomically)
# ==========================================================

def write_station_netcdf(station_name, new_launches):
    """
    new_launches: list of dicts, each with
        {"launch_time": datetime, "PRES": [...], "HGHT": [...], ...}

    Merges with any existing data for this station, de-duplicates
    by exact launch_time, sorts chronologically, and rewrites the
    whole file. Returns the number of launches actually added.
    """

    if not new_launches:
        return 0

    existing = read_existing_launches(station_name)

    added = 0

    for row in new_launches:

        launch_time = row["launch_time"]

        if launch_time in existing:
            continue

        existing[launch_time] = row
        added += 1

    if added == 0:
        return 0

    all_rows = sorted(
        existing.values(),
        key=lambda r: r["launch_time"]
    )

    max_width = max(
        len(np.asarray(r["PRES"]))
        for r in all_rows
    )

    path = get_netcdf_file(station_name)
    tmp_path = path.with_suffix(".nc.tmp")

    ds = Dataset(tmp_path, "w", format="NETCDF4")

    ds.createDimension("time", len(all_rows))
    ds.createDimension("level", max_width)

    time_var = ds.createVariable("time", "f8", ("time",))
    level_var = ds.createVariable("level", "i4", ("level",))

    time_var.units = TIME_UNITS
    time_var.calendar = TIME_CALENDAR

    level_var[:] = np.arange(max_width, dtype=np.int32)

    time_var[:] = date2num(
        [r["launch_time"] for r in all_rows],
        units=TIME_UNITS,
        calendar=TIME_CALENDAR
    )

    for var in VARIABLES:

        var_obj = ds.createVariable(
            var,
            "f4",
            ("time", "level"),
            zlib=True,
            complevel=4,
            fill_value=np.nan
        )

        for i, row in enumerate(all_rows):

            var_obj[i, :] = _pad(row[var], max_width)

    ds.station_name = station_name
    ds.created = datetime.utcnow().isoformat()

    ds.close()

    tmp_path.replace(path)

    return added