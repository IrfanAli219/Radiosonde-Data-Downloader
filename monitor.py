import time
from datetime import datetime, timedelta, timezone

from config import LAUNCH_HOURS
from stations import STATIONS
from scraper import fetch_html
from parser import parse_html
from text_storage import append_launch, get_text_file, launch_exists

from logger import (
    log_info,
    log_success,
    log_warning,
    log_error
)


CHECK_INTERVAL_SECONDS = 30 * 60


# ======================================================
# Find Most Recent Expected Launch
# ======================================================

def get_latest_expected_launch(now=None):

    now = (now or datetime.now(timezone.utc)).replace(tzinfo=None)

    launch_hours = sorted(int(h) for h in LAUNCH_HOURS)

    candidate = None

    for hour in launch_hours:

        candidate_time = now.replace(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0
        )

        if candidate_time <= now:
            candidate = candidate_time

    if candidate is None:

        yesterday = now - timedelta(days=1)

        candidate = yesterday.replace(
            hour=launch_hours[-1],
            minute=0,
            second=0,
            microsecond=0
        )

    return candidate


# ======================================================
# Check + Download One Launch, All Stations
# ======================================================

def check_and_download(launch_time):

    new_downloads = 0

    for station_name, station_number in STATIONS.items():

        path = get_text_file(station_name)

        if launch_exists(path, launch_time):
            continue

        log_info(
            f"Checking {station_name} for {launch_time:%Y-%m-%d %H:%M} UTC"
        )

        try:

            result = fetch_html(
                station_number,
                launch_time
            )

        except Exception as error:

            log_error(f"{station_name}: Request Failed - {error}")
            continue

        if result["status"] == "no_data":

            log_warning(f"{station_name}: Not Available Yet")
            continue

        if result["status"] != "success":

            log_error(f"{station_name}: Network Failed")
            continue

        try:

            data = parse_html(result["html"])

        except Exception as error:

            log_error(f"{station_name}: Parser Exception - {error}")
            continue

        if data is None:

            log_error(f"{station_name}: Parser returned None")
            continue

        try:

            saved = append_launch(
                station_name=data["station_name"],
                station_number=data["station_number"],
                launch_time=data["launch_time"],
                table_text=data["table_text"]
            )

        except Exception as error:

            log_error(f"{station_name}: Save Failed - {error}")
            continue

        if saved:

            new_downloads += 1

            log_success(
                f"{station_name}: Saved {launch_time:%Y-%m-%d %H:%M} UTC"
            )

    return new_downloads


# ======================================================
# Live Monitor Loop
# ======================================================

def run_live_monitor():

    log_info("Live monitoring started (checking every 30 minutes).")

    while True:

        launch_time = get_latest_expected_launch()

        log_info(
            f"Target launch: {launch_time:%Y-%m-%d %H:%M} UTC"
        )

        new_downloads = check_and_download(launch_time)

        if new_downloads:

            log_success(
                f"{new_downloads} new launch(es) downloaded this cycle."
            )

        else:

            log_info("No new data this cycle.")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":

    run_live_monitor()