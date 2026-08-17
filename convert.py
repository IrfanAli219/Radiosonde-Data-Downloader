from pathlib import Path

from parser import parse_text
from data_validator import validate_data

from netcdf_storage import (
    load_existing_launch_times,
    write_station_netcdf
)


# ==========================================================
# Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

TEXT_FOLDER = BASE_DIR / "data" / "text"

SEPARATOR = "=" * 70


# ==========================================================
# Read TXT File
# ==========================================================

def read_text_file(path):

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


# ==========================================================
# Split TXT into Launch Blocks
# ==========================================================

def split_launches(text):

    launches = []
    current = None

    for line in text.splitlines():

        if line.startswith("Station:"):

            if current is not None:

                block = "\n".join(current).strip()

                if block:
                    launches.append(block)

            current = [line]

        else:

            if current is not None:
                current.append(line)

    if current is not None:

        block = "\n".join(current).strip()

        if block:
            launches.append(block)

    return launches


# ==========================================================
# Convert One Station
# ==========================================================

def convert_station(text_file):

    print()
    print(SEPARATOR)
    print(f"Converting : {text_file.name}")
    print(SEPARATOR)

    station_name = text_file.stem

    text = read_text_file(text_file)

    launches = split_launches(text)

    total = len(launches)

    existing_times = load_existing_launch_times(station_name)

    to_save = []

    duplicates = 0
    failed = 0

    for index, block in enumerate(launches, start=1):

        print(f"[{index}/{total}] ", end="")

        try:

            data = parse_text(block)

            if data is None:

                failed += 1
                print("Parser Failed")
                continue

            valid, reason = validate_data(data)

            if not valid:

                failed += 1
                print(reason)
                continue

            if data["launch_time"] in existing_times:

                duplicates += 1
                print("Duplicate")
                continue

            to_save.append(data)
            print("Parsed OK (pending save)")

        except Exception as error:

            failed += 1
            print(error)

    # ------------------------------------------------------
    # One combined write for the whole station
    # ------------------------------------------------------

    converted = 0

    if to_save:

        try:

            converted = write_station_netcdf(
                station_name,
                to_save
            )

        except Exception as error:

            print(f"\nFailed to write NetCDF for {station_name}: {error}")
            failed += len(to_save)
            converted = 0

    print()
    print(SEPARATOR)

    print(f"Station     : {station_name}")
    print(f"Launches    : {total}")
    print(f"Converted   : {converted}")
    print(f"Duplicates  : {duplicates}")
    print(f"Failed      : {failed}")

    print(SEPARATOR)

    return converted, duplicates, failed


# ==========================================================
# Main
# ==========================================================

def main():

    print()
    print(SEPARATOR)
    print("TXT TO NETCDF CONVERTER")
    print(SEPARATOR)

    text_files = sorted(TEXT_FOLDER.glob("*.txt"))

    if not text_files:

        print("\nNo TXT files found.")
        return

    total_converted = 0
    total_duplicates = 0
    total_failed = 0

    for text_file in text_files:

        converted, duplicates, failed = convert_station(text_file)

        total_converted += converted
        total_duplicates += duplicates
        total_failed += failed

    print()
    print(SEPARATOR)
    print("OVERALL SUMMARY")
    print(SEPARATOR)

    print(f"Converted  : {total_converted}")
    print(f"Duplicates : {total_duplicates}")
    print(f"Failed     : {total_failed}")

    print(SEPARATOR)

    input("\nPress Enter to Exit...")


if __name__ == "__main__":
    main()