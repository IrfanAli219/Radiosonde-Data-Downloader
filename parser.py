import re
from datetime import datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup


# ==========================================================
# Variables
# ==========================================================

VARIABLE_NAMES = (
    "PRES",
    "HGHT",
    "TEMP",
    "DWPT",
    "RELH",
    "MIXR",
    "DRCT",
    "SPED",
    "THTA",
    "THTE",
    "THTV"
)


COLUMN_WIDTH = 7


# ==========================================================
# HTML Metadata
# ==========================================================

def extract_metadata(soup):

    observation = soup.find("h1")
    station = soup.find("h3")

    if observation is None or station is None:
        return None

    return {
        "observation": observation.get_text(" ", strip=True),
        "station": station.get_text(" ", strip=True)
    }


# ==========================================================
# HTML PRE Block
# ==========================================================

def extract_html_pre(html):

    soup = BeautifulSoup(html, "html.parser")

    pre = soup.find("pre")

    if pre is None:
        return None

    return pre.get_text()


# ==========================================================
# HTML Station Name
# ==========================================================

def extract_html_station_name(text):

    return (
        text.split(",")[0]
        .strip()
        .title()
        .replace("/", "_")
        .replace("\\", "_")
    )


# ==========================================================
# HTML Station Number
# ==========================================================

def extract_html_station_number(text):

    match = re.search(r"Station\s+(\d+)", text)

    if match:
        return int(match.group(1))

    return None


# ==========================================================
# HTML Launch Time
# ==========================================================

def extract_html_launch_time(text):

    match = re.search(
        r"at\s+(\d{2})\s+UTC\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})",
        text
    )

    if match is None:
        return None

    return datetime.strptime(
        f"{match.group(2)} {match.group(3)} {match.group(4)} {match.group(1)}",
        "%d %b %Y %H"
    )


# ==========================================================
# TXT Station Name
# ==========================================================

def extract_text_station_name(text):

    match = re.search(r"Station:\s*(.+)", text)

    if match:
        return match.group(1).strip()

    return None


# ==========================================================
# TXT Station Number
# ==========================================================

def extract_text_station_number(text):

    match = re.search(r"Station Number:\s*(\d+)", text)

    if match:
        return int(match.group(1))

    return None


# ==========================================================
# TXT Launch Time
# ==========================================================

def extract_text_launch_time(text):

    match = re.search(
        r"Launch:\s*([0-9\-]+\s+[0-9:]+)",
        text
    )

    if match is None:
        return None

    return datetime.strptime(
        match.group(1),
        "%Y-%m-%d %H:%M:%S"
    )


# ==========================================================
# HTML Table Extraction
# ==========================================================

def extract_html_data_block(text):

    lines = text.splitlines()

    rows = []

    start = False

    for line in lines:

        if (
            "PRES" in line
            and "HGHT" in line
            and "TEMP" in line
            and "DWPT" in line
        ):
            start = True
            continue

        if not start:
            continue

        # separator line
        if line.startswith("---"):
            continue

        # stop if another section starts
        if line.startswith("Station"):
            break

        if line.strip():
            rows.append(line.rstrip())

    if not rows:
        return None

    return "\n".join(rows)


# ==========================================================
# TXT Table Extraction
# ==========================================================

def extract_text_data_block(text):

    lines = text.splitlines()

    rows = []

    start = False

    for line in lines:

        if set(line.strip()) == {"="}:
            start = True
            continue

        if not start:
            continue

        if (
            line.startswith("Station:")
            or line.startswith("Station Number:")
            or line.startswith("Launch:")
        ):
            continue

        if line.strip():
            rows.append(line.rstrip())

    if not rows:
        return None

    return "\n".join(rows)

def parse_table(table_text):

    colspecs = [
        (index * COLUMN_WIDTH, (index + 1) * COLUMN_WIDTH)
        for index in range(len(VARIABLE_NAMES))
    ]

    df = pd.read_fwf(
        StringIO(table_text),
        colspecs=colspecs,
        names=VARIABLE_NAMES,
        header=None
    )

    df = df.apply(
        pd.to_numeric,
        errors="coerce"
    )

    df = df.dropna(subset=["PRES"])

    if df.empty:
        return None

    return {
        column: df[column].astype(float).tolist()
        for column in VARIABLE_NAMES
    }


# ==========================================================
# HTML Parser
# ==========================================================

def parse_html(html):

    soup = BeautifulSoup(html, "html.parser")

    metadata = extract_metadata(soup)

    if metadata is None:
        return None

    pre_text = extract_html_pre(html)

    if pre_text is None:
        return None

    launch_time = extract_html_launch_time(
        metadata["observation"]
    )

    if launch_time is None:
        return None

    table_text = extract_html_data_block(pre_text)

    if table_text is None:
        return None

    variables = parse_table(table_text)

    if variables is None:
        return None

    return {

        "station_name": extract_html_station_name(
            metadata["station"]
        ),

        "station_number": extract_html_station_number(
            metadata["observation"]
        ),

        "launch_time": launch_time,

        "table_text": table_text,

        **variables

    }


# ==========================================================
# TXT Parser
# ==========================================================

def parse_text(text):

    station_name = extract_text_station_name(text)

    station_number = extract_text_station_number(text)

    launch_time = extract_text_launch_time(text)

    if (
        station_name is None
        or station_number is None
        or launch_time is None
    ):
        return None

    table_text = extract_text_data_block(text)

    if table_text is None:
        return None

    variables = parse_table(table_text)

    if variables is None:
        return None

    return {

        "station_name": station_name,

        "station_number": station_number,

        "launch_time": launch_time,

        "table_text": table_text,

        **variables

    }