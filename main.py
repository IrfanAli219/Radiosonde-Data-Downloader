from statistics import Statistics

from progress import (
    clear_progress,
    delete_progress,
    has_progress,
    show_progress,
    load_progress
)

from validator import (
    get_main_menu_choice,
    get_single_day,
    get_date_range
)

from preview import (
    show_download_preview,
    confirm_download
)

from scheduler import (
    generate_schedule,
    count_launches
)

from historical_downloader import process_launch
from monitor import run_live_monitor

SEPARATOR = "=" * 50


# ======================================================
# Download Runner
# ======================================================

def run_download(
    start_date,
    end_date,
    resume_data=None
):

    stats = Statistics()
    stats.start_timer()

    schedule = list(
        generate_schedule(
            start_date,
            end_date
        )
    )

    total_launches = len(schedule)

    launch_number = 1

    if resume_data:

        try:

            launch_number = (
                schedule.index(
                    resume_data["launch"]
                ) + 1
            )

        except ValueError:

            launch_number = 1

    for launch in generate_schedule(
        start_date,
        end_date,
        resume_data
    ):

        stats.total_launches += 1

        print()
        print(SEPARATOR)
        print(
            f"Launch {launch_number} / {total_launches}"
        )
        print(
            launch.strftime(
                "%Y-%m-%d %H UTC"
            )
        )
        print(SEPARATOR)

        process_launch(
            start_date,
            end_date,
            launch,
            stats,
            resume_data
        )

        resume_data = None
        launch_number += 1

    stats.print_summary()

    delete_progress()

    print()
    print("Download Completed Successfully.")
    print()

    input(
        "Press Enter to return to Main Menu..."
    )

    print()


# ======================================================
# Main Program
# ======================================================

def main():

    print()
    print(SEPARATOR)
    print("RADIOSONDE HISTORICAL DOWNLOADER")
    print(SEPARATOR)

    while True:

        choice = get_main_menu_choice()

        # --------------------------------------
        # Exit
        # --------------------------------------

        if choice == "5":

            print()
            print("Program Closed.")
            break
        
                # --------------------------------------
        # Live Monitor
        # --------------------------------------

        if choice == "4":

            print()
            print(SEPARATOR)
            print("LIVE MONITORING MODE")
            print(SEPARATOR)
            print("Checking for new launches every 30 minutes.")
            print("Press Ctrl+C to stop and return to Main Menu.")
            print(SEPARATOR)
            print()

            try:

                run_live_monitor()

            except KeyboardInterrupt:

                print()
                print("Live Monitoring Stopped.")
                print()

            continue

        # --------------------------------------
        # Resume Download
        # --------------------------------------

        if choice == "3":

            if not has_progress():

                print()
                print("No previous download found.")
                print()

                input(
                    "Press Enter to return to Main Menu..."
                )

                continue

            progress = load_progress()

            show_progress()

            print()
            print("Resuming Previous Download...")
            print()

            run_download(
                progress["start_date"],
                progress["end_date"],
                progress
            )

            continue

        # --------------------------------------
        # Fresh Download
        # --------------------------------------

        clear_progress()

        if choice == "1":

            start_date, end_date = get_single_day()

        else:

            start_date, end_date = get_date_range()

        show_download_preview(
            start_date,
            end_date
        )

        if not confirm_download():

            print()
            print("Download Cancelled.")
            print()

            continue

        run_download(
            start_date,
            end_date
        )


if __name__ == "__main__":

    main()