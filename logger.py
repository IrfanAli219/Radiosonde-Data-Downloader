from datetime import datetime
from pathlib import Path

from config import LOG_DIR

LOG_FILE = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"


def _write(level, message):

    text = f"[{level}] {message}"

    print(text)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")


def log_info(message):
    _write("INFO", message)


def log_success(message):
    _write("SUCCESS", message)


def log_warning(message):
    _write("WARNING", message)


def log_error(message):
    _write("ERROR", message)


# backward compatibility
def log(message):
    log_info(message)