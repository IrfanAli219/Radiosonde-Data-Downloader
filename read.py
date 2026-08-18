from pathlib import Path
from datetime import datetime

import xarray as xr
import pandas as pd


# ==========================
# NetCDF Folder
# ==========================

BASE_DIR = Path(__file__).resolve().parent

NETCDF_FOLDER = BASE_DIR / "data" / "netcdf"

# Display / input format
DATETIME_FORMAT = "%Y-%m-%d-%H"

VARIABLES = [
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


# ==========================
# Load Station File
# ==========================

def load_station_file(station):

    path = NETCDF_FOLDER / f"{station}.nc"

    if not path.exists():

        print("\nStation file not found!")

        print("\nAvailable stations:")

        for file in NETCDF_FOLDER.glob("*.nc"):

            print(
                "-",
                file.stem
            )

        return None

    return xr.open_dataset(path)


# ==========================
# Print Available Datetimes
# ==========================

def show_available_datetimes(ds):

    print("\n==============================")
    print("AVAILABLE DATETIMES")
    print("==============================")

    for t in ds.time.values:

        formatted = pd.to_datetime(t).strftime(DATETIME_FORMAT)

        print(formatted)


# ==========================
# Find Matching Time Index
# ==========================

def find_time_index(ds, user_datetime):

    times = pd.to_datetime(
        ds.time.values
    )

    try:

        target = datetime.strptime(
            user_datetime,
            DATETIME_FORMAT
        )

    except ValueError:

        print(
            f"\nInvalid format. Please use (YYYY-MM-DD-HH e.g. 2026-07-24-12)"
        )

        return None

    target = pd.Timestamp(target)

    indexes = [
        i for i, t in enumerate(times)
        if t == target
    ]

    if len(indexes) == 0:

        print("\nNo data found for that datetime!")

        return None

    if len(indexes) > 1:

        print("\nMultiple records found:")

        for count, idx in enumerate(indexes):

            print(count, "Index:", idx)

        choice = int(
            input("\nSelect record number: ")
        )

        return indexes[choice]

    return indexes[0]


# ==========================
# Option 1: Read Full Profile
# ==========================

def read_full_profile():

    station = input(
        "\nStation name: "
    )

    ds = load_station_file(station)

    if ds is None:
        return

    show_available_datetimes(ds)

    datetime_input = input(
        f"\nEnter datetime (YYYY-MM-DD-HH e.g. 2026-07-24-12): "
    )

    selected = find_time_index(ds, datetime_input)

    if selected is None:

        ds.close()
        return

    data = ds.isel(
        time=selected
    )

    print("\n==============================")
    print("RADIOSONDE PROFILE")
    print("==============================")

    print(data)

    df = data.to_dataframe()

    df = df.dropna(
        subset=VARIABLES,
        how="all"
    )

    print("\n==============================")
    print("DATA MATRIX")
    print("==============================")

    print(df)

    ds.close()


# ==========================
# Option 2: Read Exact Variable Value
# ==========================

def read_variable_value():

    station = input(
        "\nStation name: "
    )

    ds = load_station_file(station)

    if ds is None:
        return

    print("\n==============================")
    print("AVAILABLE VARIABLES")
    print("==============================")

    for index, var in enumerate(VARIABLES):
        print(f"{index}. {var}")

    var_input = input(
        "\nEnter variable name or number: "
    ).strip()

    if var_input.isdigit():

        var_index = int(var_input)

        if var_index < 0 or var_index >= len(VARIABLES):

            print("\nInvalid variable number.")
            ds.close()
            return

        variable = VARIABLES[var_index]

    else:

        variable = var_input.upper()

        if variable not in VARIABLES:

            print("\nInvalid variable name.")
            ds.close()
            return

    max_level = ds.dims["level"] - 1

    level_input = input(
        f"\nEnter level (0 to {max_level}): "
    ).strip()

    if not level_input.isdigit():

        print("\nLevel must be a whole number.")
        ds.close()
        return

    level = int(level_input)

    if level < 0 or level > max_level:

        print(f"\nLevel must be between 0 and {max_level}.")
        ds.close()
        return

    show_available_datetimes(ds)

    datetime_input = input(
        f"\nEnter datetime (YYYY-MM-DD-HH e.g. 2026-07-24-12): "
    ).strip()

    selected = find_time_index(ds, datetime_input)

    if selected is None:

        ds.close()
        return

    value = ds[variable].isel(
        time=selected,
        level=level
    ).values.item()

    print("\n==============================")
    print("VALUE")
    print("==============================")

    print(f"Station   : {station}")
    print(f"Variable  : {variable}")
    print(f"Level     : {level}")
    print(f"Datetime  : {datetime_input}")

    if pd.isna(value):

        print("Value     : No Data (NaN at this level)")

    else:

        print(f"Value     : {value}")

    ds.close()


# ==========================
# Main Loop
# ==========================

while True:

    print("\n\n")
    print("==============================")
    print("RADIOSONDE NETCDF READER")
    print("==============================")

    print("""
1. Read Full Profile
2. Read Exact Variable Value
3. Exit
""")

    option = input(
        "Enter option: "
    ).strip()

    if option == "3":

        print("\nProgram Closed")
        break

    elif option == "1":

        read_full_profile()

    elif option == "2":

        read_variable_value()

    else:

        print("\nInvalid option")