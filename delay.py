import random
import time

from config import (
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX
)


# ======================================================
# Random Delay Between Requests
# ======================================================

def wait_before_request():

    delay = random.uniform(
        REQUEST_DELAY_MIN,
        REQUEST_DELAY_MAX
    )

    print(f"Waiting {delay:.1f} seconds...")

    time.sleep(delay)