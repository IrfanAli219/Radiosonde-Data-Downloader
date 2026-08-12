from datetime import datetime


class Statistics:

    def __init__(self):

        # ============================
        # Download Statistics
        # ============================

        self.total_launches = 0
        self.total_stations = 0
        self.total_requests = 0

        # ============================
        # Results
        # ============================

        self.successful_downloads = 0
        self.saved_records = 0
        self.already_downloaded = 0

        self.no_data = 0
        self.parser_failed = 0
        self.validation_failed = 0
        self.network_failed = 0

        # ============================
        # Retry Statistics
        # ============================

        self.retry_attempts = 0

        # ============================
        # Runtime
        # ============================

        self.start_time = datetime.now()
        self.end_time = None

    # =====================================================
    # Timer
    # =====================================================

    def start_timer(self):

        self.start_time = datetime.now()

    def stop_timer(self):

        self.end_time = datetime.now()

    def runtime(self):

        end = self.end_time or datetime.now()

        return str(end - self.start_time).split(".")[0]

    # =====================================================
    # Summary
    # =====================================================

    def print_summary(self):

        self.stop_timer()

        print()
        print("=" * 50)
        print("DOWNLOAD SUMMARY")
        print("=" * 50)
        print()

        print(f"Total Launches       : {self.total_launches}")
        print(f"Stations Checked     : {self.total_stations}")
        print(f"Total Requests       : {self.total_requests}")

        print()

        print(f"Successful Downloads : {self.successful_downloads}")
        print(f"Saved Records        : {self.saved_records}")
        print(f"Already Exists       : {self.already_downloaded}")

        print()

        print(f"No Data              : {self.no_data}")
        print(f"Parser Failed        : {self.parser_failed}")
        print(f"Invalid Dataset      : {self.validation_failed}")
        print(f"Network Failed       : {self.network_failed}")

        print()

        print(f"Retry Attempts       : {self.retry_attempts}")
        print(f"Total Runtime        : {self.runtime()}")

        print()
        print("=" * 50)