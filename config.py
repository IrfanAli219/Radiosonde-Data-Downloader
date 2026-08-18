from pathlib import Path

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

PROGRESS_FILE = BASE_DIR / "progress.json"

# Automatically create required folders
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ==========================================================
# HTTP Request Settings
# ==========================================================

REQUEST_TIMEOUT = 30

MAX_RETRIES = 3
RETRY_DELAY = 5

REQUEST_DELAY_MIN = 0
REQUEST_DELAY_MAX = 0

# ==========================================================
# Radiosonde Launch Hours (UTC)
# ==========================================================

LAUNCH_HOURS = (
    0,
    12
)