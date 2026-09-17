import subprocess
import time


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


def track_activity():
    """Continuously track the active application."""

    print("Focus Tracker Started...")
    print("Press Ctrl+C to stop.\n")

    while True:
        active_app = get_active_app()

        current_time = time.strftime("%H:%M:%S")

        print(f"[{current_time}] Active App: {active_app}")

        time.sleep(2)


if __name__ == "__main__":
    track_activity()