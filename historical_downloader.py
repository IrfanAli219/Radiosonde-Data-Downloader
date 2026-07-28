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
    get_text_file
)

from progress import save_progress
from stations import STATIONS


# ==========================================================
# Process One Launch
# ==========================================================

def process_launch(
    start_date,
    end_date,
    launch,
    stats,
    resume_data=None
):

    log_info(f"Launch: {launch}")

    start_index = 0

    if (
        resume_data is not None
        and launch == resume_data["launch"]
    ):
        start_index = resume_data["station_index"] + 1

    station_items = list(STATIONS.items())

    for station_index, (station_name, station_number) in enumerate(station_items):

        if station_index < start_index:
            continue

        stats.total_stations += 1

        log_info(
            f"Downloading {station_name}"
        )

        wait_before_request()

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

            log_error(
                f"{station_name}: Request Failed - {error}"
            )

            stats.network_failed += 1
            continue

        stats.retry_attempts += result.get(
            "retries",
            0
        )

        status = result["status"]

        # --------------------------------------------------
        # No Data
        # --------------------------------------------------

        if status == "no_data":

            log_warning(
                f"{station_name}: No Data"
            )

            stats.no_data += 1
            continue

        # --------------------------------------------------
        # Network Error
        # --------------------------------------------------

        if status in (
            "network_error",
            "http_error",
            "request_error"
        ):

            log_error(
                f"{station_name}: Network Failed"
            )

            stats.network_failed += 1
            continue

        # --------------------------------------------------
        # Parse HTML
        # --------------------------------------------------

        try:

            data = parse_html(
                result["html"]
            )

        except Exception as error:

            log_error(
                f"{station_name}: Parser Exception - {error}"
            )

            stats.parser_failed += 1
            continue

        if data is None:

            log_error(
                f"{station_name}: Parser returned None"
            )

            # Save failed HTML for debugging
            try:

                with open(
                    "parser_failed.html",
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(result["html"])

                log_warning(
                    "Failed HTML saved as parser_failed.html"
                )

            except Exception:
                pass

            stats.parser_failed += 1
            continue

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

            log_error(
                f"{station_name}: Save Failed - {error}"
            )

            stats.validation_failed += 1
            continue

        stats.saved_records += 1
        stats.successful_downloads += 1

        path = get_text_file(
            station_name
        )

        log_success(
            f"Saved: {path}"
        )

        # --------------------------------------------------
        # Save Resume Progress
        # --------------------------------------------------

        save_progress(
            start_date,
            end_date,
            launch,
            station_index
        )