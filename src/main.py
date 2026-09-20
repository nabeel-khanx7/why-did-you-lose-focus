import subprocess
import sys
import time
from pathlib import Path


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

ACTIVITY_TRACKER = BASE_DIR / "src" / "activity_tracker.py"
DASHBOARD = BASE_DIR / "src" / "dashboard.py"


# ==========================================
# START ACTIVITY TRACKER
# ==========================================

def start_activity_tracker():

    print("=" * 60)
    print("STARTING ACTIVITY TRACKER")
    print("=" * 60)

    process = subprocess.Popen(
        [
            sys.executable,
            str(ACTIVITY_TRACKER)
        ],
        cwd=BASE_DIR
    )

    return process


# ==========================================
# START STREAMLIT DASHBOARD
# ==========================================

def start_dashboard():

    print("=" * 60)
    print("STARTING STREAMLIT DASHBOARD")
    print("=" * 60)

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(DASHBOARD)
        ],
        cwd=BASE_DIR
    )

    return process


# ==========================================
# MAIN CONTROLLER
# ==========================================

def main():

    print("\n" + "=" * 60)
    print("       WHY DID YOU LOSE FOCUS?")
    print("       AI FOCUS & PRODUCTIVITY SYSTEM")
    print("=" * 60)

    print("\nStarting project components...\n")

    tracker_process = None
    dashboard_process = None

    try:

        # Start activity tracking
        tracker_process = start_activity_tracker()

        # Give tracker a moment to initialize
        time.sleep(2)

        # Start dashboard
        dashboard_process = start_dashboard()

        print("\n" + "=" * 60)
        print("PROJECT RUNNING")
        print("=" * 60)

        print("\nActivity Tracker : RUNNING")
        print("Dashboard        : RUNNING")

        print("\nOpen the Streamlit URL shown above.")
        print("Press Ctrl+C to stop the project.")

        # Keep main process alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("\n\nStopping project...")

    finally:

        if tracker_process is not None:
            tracker_process.terminate()

        if dashboard_process is not None:
            dashboard_process.terminate()

        print("Activity Tracker stopped.")
        print("Dashboard stopped.")
        print("\nProject closed.")


# ==========================================
# PROGRAM ENTRY
# ==========================================

if __name__ == "__main__":
    main()