import subprocess
import time
import csv
import os
from datetime import datetime


# ==============================
# File Paths
# ==============================

ACTIVITY_LOG = "data/activity_log.csv"
SESSION_LOG = "data/session_log.csv"


# ==============================
# Get Active Application
# ==============================

def get_active_app():
    """Returns the name of the currently active macOS application."""

    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    return frontApp
    '''

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


# ==============================
# Get Idle Time
# ==============================

def get_idle_seconds():
    """Returns how many seconds the user has been idle on macOS."""

    result = subprocess.run(
        ["ioreg", "-c", "IOHIDSystem"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():

        if "HIDIdleTime" in line:

            try:
                idle_nanoseconds = int(
                    line.split("=")[-1].strip()
                )

                idle_seconds = idle_nanoseconds / 1_000_000_000

                return idle_seconds

            except ValueError:
                return 0

    return 0


# ==============================
# Create Activity CSV
# ==============================

def initialize_activity_log():
    """Creates activity log file if it does not already exist."""

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(ACTIVITY_LOG):

        with open(
            ACTIVITY_LOG,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "active_app",
                "idle_seconds"
            ])


# ==============================
# Create Session CSV
# ==============================

def initialize_session_log():
    """Creates session log file if it does not already exist."""

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(SESSION_LOG):

        with open(
            SESSION_LOG,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "start_time",
                "end_time",
                "active_app",
                "duration_seconds"
            ])


# ==============================
# Save Activity
# ==============================

def save_activity(timestamp, active_app, idle_seconds):
    """Saves one activity record to activity_log.csv."""

    initialize_activity_log()

    with open(
        ACTIVITY_LOG,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            timestamp,
            active_app,
            round(idle_seconds, 2)
        ])


# ==============================
# Save Session
# ==============================

def save_session(
    start_time,
    end_time,
    active_app,
    duration_seconds
):
    """Saves one completed session."""

    initialize_session_log()

    with open(
        SESSION_LOG,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            start_time,
            end_time,
            active_app,
            round(duration_seconds, 2)
        ])


# ==============================
# Track Activity
# ==============================

def track_activity():
    """Continuously tracks active application and user idle time."""

    print("Focus Tracker Started...")
    print("Press Ctrl+C to stop.\n")

    current_session_app = None
    session_start_time = None

    try:

        while True:

            # Get current active application
            active_app = get_active_app()

            # Get current time
            current_time = datetime.now()

            # Get user idle time
            idle_seconds = get_idle_seconds()

            # Format timestamp
            timestamp = current_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # ==============================
            # Save Activity
            # ==============================

            save_activity(
                timestamp,
                active_app,
                idle_seconds
            )

            # ==============================
            # Session Detection
            # ==============================

            if current_session_app is None:

                # First session
                current_session_app = active_app
                session_start_time = current_time

            elif active_app != current_session_app:

                # Application changed
                session_end_time = current_time

                duration = (
                    session_end_time - session_start_time
                ).total_seconds()

                # Save previous session
                save_session(
                    session_start_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    session_end_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    current_session_app,
                    duration
                )

                # Start new session
                current_session_app = active_app
                session_start_time = current_time

            # ==============================
            # Console Output
            # ==============================

            print(
                f"[{timestamp}] "
                f"Active App: {active_app} | "
                f"Idle: {idle_seconds:.1f}s"
            )

            # Wait 2 seconds
            time.sleep(2)

    except KeyboardInterrupt:

        print("\nFocus Tracker Stopped.")

        # ==============================
        # Save Final Session
        # ==============================

        if (
            current_session_app is not None
            and session_start_time is not None
        ):

            session_end_time = datetime.now()

            duration = (
                session_end_time - session_start_time
            ).total_seconds()

            save_session(
                session_start_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                session_end_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                current_session_app,
                duration
            )

            print(
                f"Final session saved: "
                f"{current_session_app} "
                f"({duration:.1f} seconds)"
            )


# ==============================
# Program Entry Point
# ==============================

if __name__ == "__main__":
    track_activity()