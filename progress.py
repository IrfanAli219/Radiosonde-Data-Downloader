import json
from datetime import datetime
from pathlib import Path

from config import PROGRESS_FILE
from stations import STATIONS


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

PROGRESS_PATH = Path(PROGRESS_FILE)

SEPARATOR = "=" * 50


# ======================================================
# Helpers
# ======================================================

def _write_json(data):

    PROGRESS_PATH.write_text(
        json.dumps(data, indent=4)
    )


def _read_json():

    try:

        return json.loads(
            PROGRESS_PATH.read_text()
        )

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return None


# ======================================================
# Save Progress
# ======================================================

def save_progress(
    start_date,
    end_date,
    launch,
    station_index
):

    _write_json({

        "start_date": start_date.strftime(DATE_FORMAT),

        "end_date": end_date.strftime(DATE_FORMAT),

        "current_launch": launch.strftime(DATE_FORMAT),

        "station_index": station_index

    })


# ======================================================
# Load Progress
# ======================================================

def load_progress():

    data = _read_json()

    if not data:

        return None

    try:

        return {

            "start_date": datetime.strptime(
                data["start_date"],
                DATE_FORMAT
            ),

            "end_date": datetime.strptime(
                data["end_date"],
                DATE_FORMAT
            ),

            "launch": datetime.strptime(
                data["current_launch"],
                DATE_FORMAT
            ),

            "station_index": int(
                data["station_index"]
            )

        }

    except (
        KeyError,
        ValueError
    ):

        return None


# ======================================================
# Clear Progress
# ======================================================

def clear_progress():

    _write_json({})


# ======================================================
# Delete Progress
# ======================================================

def delete_progress():

    PROGRESS_PATH.unlink(
        missing_ok=True
    )


# ======================================================
# Check Progress Exists
# ======================================================

def has_progress():

    return load_progress() is not None


# ======================================================
# Show Progress
# ======================================================

def show_progress():

    progress = load_progress()

    if progress is None:

        return

    station_names = list(
        STATIONS.keys()
    )

    index = progress["station_index"]

    if 0 <= index < len(station_names):

        station_name = station_names[index]

    else:

        station_name = "Unknown"

    print()
    print(SEPARATOR)
    print("PREVIOUS DOWNLOAD FOUND")
    print(SEPARATOR)

    print(
        f"Start Date : {progress['start_date']:%Y-%m-%d}"
    )

    print(
        f"End Date   : {progress['end_date']:%Y-%m-%d}"
    )

    print(
        f"Launch     : {progress['launch']:%Y-%m-%d %H UTC}"
    )

    print(
        f"Last Completed Station : {station_name}"
    )

    print(SEPARATOR)