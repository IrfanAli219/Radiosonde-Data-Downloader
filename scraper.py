import time
import requests
from requests.adapters import HTTPAdapter

from config import (
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY
)


# ==========================================================
# URL
# ==========================================================

URL = "https://weather.uwyo.edu/wsgi/sounding"

SESSION = requests.Session()

# Increase connection pool size so multiple threads can reuse
# this single Session without exhausting/recreating connections.
_ADAPTER = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=20
)

SESSION.mount("https://", _ADAPTER)
SESSION.mount("http://", _ADAPTER)


# ==========================================================
# Download HTML
# ==========================================================

def fetch_html(station_id, launch_time):

    params = {

        "datetime": launch_time.strftime("%Y-%m-%d %H:00:00"),

        "id": station_id,

        "src": "FM35",

        "type": "TEXT:LIST"

    }

    retries = 0

    for attempt in range(MAX_RETRIES):

        try:

            response = SESSION.get(

                URL,

                params=params,

                timeout=REQUEST_TIMEOUT

            )

            # ------------------------------------------
            # No data available
            # ------------------------------------------

            if response.status_code == 404:

                return {

                    "status": "no_data",

                    "html": None,

                    "retries": retries

                }

            response.raise_for_status()

            # ------------------------------------------
            # Success
            # ------------------------------------------

            return {

                "status": "success",

                "html": response.text,

                "retries": retries

            }

        except (

            requests.ConnectionError,

            requests.Timeout

        ):

            retries += 1

            if retries >= MAX_RETRIES:

                return {

                    "status": "network_error",

                    "html": None,

                    "retries": retries

                }

            time.sleep(RETRY_DELAY)

        except requests.HTTPError:

            return {

                "status": "http_error",

                "html": None,

                "retries": retries

            }

        except requests.RequestException:

            return {

                "status": "request_error",

                "html": None,

                "retries": retries

            }