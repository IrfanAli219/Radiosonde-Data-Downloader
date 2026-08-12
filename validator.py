from datetime import datetime


DATE_FORMAT = "%Y-%m-%d"

SEPARATOR = "=" * 50


# ======================================================
# Date Validation
# ======================================================

def get_valid_date(message):

    while True:

        user_input = input(message).strip()

        try:

            return datetime.strptime(
                user_input,
                DATE_FORMAT
            )

        except ValueError:

            print()
            print("Invalid date format.")
            print("Please use YYYY-MM-DD")
            print()


# ======================================================
# Main Menu
# ======================================================

def get_main_menu_choice():

    while True:

        print()
        print(SEPARATOR)
        print("MAIN MENU")
        print(SEPARATOR)

        print("1. Single Day Download")
        print("2. Date Range Download")
        print("3. Resume Previous Download")
        print("4. Live Monitor")
        print("5. Exit")

        print(SEPARATOR)
        print()

        choice = input(
            "Enter Choice (1-5): "
        ).strip()

        if choice in ("1", "2", "3", "4", "5"):
            return choice

        print()
        print("Invalid Choice.")
        print("Please enter a number between 1 and 5.")
        print()


# ======================================================
# Single Day
# ======================================================

def get_single_day():

    print()

    date = get_valid_date(
        "Enter Date (YYYY-MM-DD): "
    )

    return date, date


# ======================================================
# Date Range
# ======================================================

def get_date_range():

    while True:

        print()

        start_date = get_valid_date(
            "Enter Start Date (YYYY-MM-DD): "
        )

        end_date = get_valid_date(
            "Enter End Date (YYYY-MM-DD): "
        )

        if start_date > end_date:

            print()
            print(SEPARATOR)
            print("ERROR: Start Date cannot be after End Date.")
            print("Please enter the dates again.")
            print(SEPARATOR)
            print()

            continue

        return start_date, end_date