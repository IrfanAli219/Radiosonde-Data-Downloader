from datetime import datetime
import re

from config import DATA_DIR


# ==========================================================
# TXT Folder
# ==========================================================

TEXT_FOLDER = DATA_DIR / "text"

TEXT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# TXT Path
# ==========================================================

def get_text_file(station_name):
    return TEXT_FOLDER / f"{station_name}.txt"


# ==========================================================
# Duplicate Check
# ==========================================================

def launch_exists(path, launch_time):

    if not path.exists():
        return False

    launch_string = f"Launch: {launch_time:%Y-%m-%d %H:%M:%S}"

    with open(path, "r", encoding="utf-8") as file:
        return launch_string in file.read()


# ==========================================================
# Helpers
# ==========================================================

def _is_separator(line):
    stripped = line.strip()
    return bool(stripped) and set(stripped) == {"="}


def clean_table_lines(table_text):

    cleaned = []

    for line in table_text.splitlines():

        line = line.rstrip()

        if not line:
            continue

        if _is_separator(line):
            continue

        cleaned.append(line)

    return cleaned


# ==========================================================
# Parse Existing File Into Structured Records
# (separators are always treated as pure boundaries and discarded)
# ==========================================================

def parse_existing_launches(text):

    records = []
    current = None

    for raw_line in text.splitlines():

        line = raw_line.rstrip()

        if _is_separator(line):
            continue

        if line.startswith("Station:"):

            if current is not None:
                records.append(current)

            current = {
                "station_name": line.split(":", 1)[1].strip(),
                "station_number": None,
                "launch_time": None,
                "table_lines": []
            }
            continue

        if current is None:
            # stray line outside any block, ignore
            continue

        if line.startswith("Station Number:"):
            match = re.search(r"Station Number:\s*(\d+)", line)
            if match:
                current["station_number"] = int(match.group(1))
            continue

        if line.startswith("Launch:"):
            match = re.search(r"Launch:\s*([0-9\-]+\s+[0-9:]+)", line)
            if match:
                current["launch_time"] = datetime.strptime(
                    match.group(1), "%Y-%m-%d %H:%M:%S"
                )
            continue

        if line.strip():
            current["table_lines"].append(line)

    if current is not None:
        records.append(current)

    return [
        r for r in records
        if r["station_number"] is not None
        and r["launch_time"] is not None
        and r["table_lines"]
    ]


# ==========================================================
# Format One Block (always fresh, never copied from old text)
# ==========================================================

def format_block(station_name, station_number, launch_time, table_lines):

    lines = [
        "=" * 80,
        f"Station: {station_name}",
        f"Station Number: {station_number}",
        f"Launch: {launch_time:%Y-%m-%d %H:%M:%S}",
        "=" * 80,
    ]

    lines.extend(table_lines)

    return "\n".join(lines)


# ==========================================================
# Append One Launch (Sorted)
# ==========================================================

def append_launch(station_name, station_number, launch_time, table_text):

    path = get_text_file(station_name)

    if launch_exists(path, launch_time):
        return False

    table_lines = clean_table_lines(table_text)

    records = []

    if path.exists():
        with open(path, "r", encoding="utf-8") as file:
            records = parse_existing_launches(file.read())

    records.append({
        "station_name": station_name,
        "station_number": station_number,
        "launch_time": launch_time,
        "table_lines": table_lines
    })

    records.sort(key=lambda r: r["launch_time"])

    with open(path, "w", encoding="utf-8") as file:

        for i, r in enumerate(records):

            file.write(format_block(
                r["station_name"],
                r["station_number"],
                r["launch_time"],
                r["table_lines"]
            ))

            file.write("\n\n" if i < len(records) - 1 else "\n")

    return True