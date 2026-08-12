from datetime import timedelta

from config import LAUNCH_HOURS


# ======================================================
# Generate Launch Schedule
# ======================================================

def generate_schedule(
    start_date,
    end_date,
    resume_data=None
):

    resume_launch = (
        resume_data["launch"]
        if resume_data
        else None
    )

    current_date = start_date

    while current_date <= end_date:

        for hour in map(int, LAUNCH_HOURS):

            launch = current_date.replace(
                hour=hour,
                minute=0,
                second=0,
                microsecond=0
            )

            if resume_launch and launch < resume_launch:
                continue

            yield launch

        current_date += timedelta(days=1)


# ======================================================
# Count Total Launches
# ======================================================

def count_launches(
    start_date,
    end_date
):

    total_days = (
        end_date.date() - start_date.date()
    ).days + 1

    return total_days * len(LAUNCH_HOURS)