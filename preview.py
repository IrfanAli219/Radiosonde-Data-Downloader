from scheduler import count_launches
from stations import STATIONS


SEPARATOR = "=" * 50


def show_download_preview(start_date, end_date):

    total_launches = count_launches(
        start_date,
        end_date
    )

    total_stations = len(STATIONS)

    total_requests = total_launches * total_stations

    mode = (
        "Single Day Download"
        if start_date == end_date
        else "Date Range Download"
    )

    print()
    print(SEPARATOR)
    print("DOWNLOAD PREVIEW")
    print(SEPARATOR)
    print()

    print(f"Mode               : {mode}")
    print(f"Start Date         : {start_date:%Y-%m-%d}")
    print(f"End Date           : {end_date:%Y-%m-%d}")

    print()

    print(f"Total Launches     : {total_launches}")
    print(f"Stations           : {total_stations}")
    print(f"Estimated Requests : {total_requests}")
    print(f"Historical Records : {total_requests}")

    print()

    print("Storage Format     : One historical file per station")

    print()
    print(SEPARATOR)


def confirm_download():

    while True:

        choice = input(
            "\nProceed with download? (Y/N): "
        ).strip().upper()

        if choice in ("Y", "N"):
            return choice == "Y"

        print()
        print("Invalid Choice.")
        print("Please enter Y or N.")