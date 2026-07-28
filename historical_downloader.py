import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import fetch_html
from parser import parse_html

from delay import wait_before_request

from logger import (
    log_info,
    log_success,
    log_warning,
    log_error
)

from text_storage import (
    append_launch,
    get_text_file,
    launch_exists
)

from progress import save_progress
from stations import STATIONS


# How many stations to download in parallel per launch.
# Raise/lower this based on how your network and the
# server respond -- 8 is a reasonable, polite default.
MAX_WORKERS = 8


# ==========================================================
# Process One Station (runs inside a worker thread)
# ==========================================================

def _process_station(station_name, station_number, launch, stats, stats_lock):

    path = get_text_file(station_name)

    # --------------------------------------------------
    # Skip instantly if already downloaded (no network call)
    # --------------------------------------------------

    if launch_exists(path, launch):

        return f"{station_name}: Already Downloaded"

    wait_before_request()

    with stats_lock:
        stats.total_stations += 1
        stats.total_requests += 1

    # --------------------------------------------------
    # Download HTML
    # --------------------------------------------------

    try:

        result = fetch_html(
            station_number,
            launch
        )

    except Exception as error:

        with stats_lock:
            stats.network_failed += 1

        return f"{station_name}: Request Failed - {error}"

    with stats_lock:
        stats.retry_attempts += result.get("retries", 0)

    status = result["status"]

    # --------------------------------------------------
    # No Data
    # --------------------------------------------------

    if status == "no_data":

        with stats_lock:
            stats.no_data += 1

        return f"{station_name}: No Data"

    # --------------------------------------------------
    # Network Error
    # --------------------------------------------------

    if status in (
        "network_error",
        "http_error",
        "request_error"
    ):

        with stats_lock:
            stats.network_failed += 1

        return f"{station_name}: Network Failed"

    # --------------------------------------------------
    # Parse HTML
    # --------------------------------------------------

    try:

        data = parse_html(result["html"])

    except Exception as error:

        with stats_lock:
            stats.parser_failed += 1

        return f"{station_name}: Parser Exception - {error}"

    if data is None:

        with stats_lock:
            stats.parser_failed += 1

        return f"{station_name}: Parser returned None"

    # --------------------------------------------------
    # Save TXT
    # --------------------------------------------------

    try:

        append_launch(
            station_name=data["station_name"],
            station_number=data["station_number"],
            launch_time=data["launch_time"],
            table_text=data["table_text"]
        )

    except Exception as error:

        with stats_lock:
            stats.validation_failed += 1

        return f"{station_name}: Save Failed - {error}"

    with stats_lock:
        stats.saved_records += 1
        stats.successful_downloads += 1

    return f"{station_name}: Saved -> {path}"


# ==========================================================
# Process One Launch (all stations in parallel)
# ==========================================================

def process_launch(
    start_date,
    end_date,
    launch,
    stats,
    resume_data=None
):

    log_info(f"Launch: {launch}")

    stats_lock = threading.Lock()

    station_items = list(STATIONS.items())

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(
                _process_station,
                station_name,
                station_number,
                launch,
                stats,
                stats_lock
            ): station_name
            for station_name, station_number in station_items
        }

        for future in as_completed(futures):

            message = future.result()

            if "Saved" in message:
                log_success(message)
            elif "Already Downloaded" in message:
                log_info(message)
            elif "No Data" in message:
                log_warning(message)
            else:
                log_error(message)

    # --------------------------------------------------
    # Save Resume Progress (whole launch is now complete)
    # --------------------------------------------------

    save_progress(
        start_date,
        end_date,
        launch,
        len(station_items) - 1
    )