import pandas as pd


ACTIVITY_LOG = "data/activity_log.csv"
SESSION_LOG = "data/session_log.csv"


def analyze_activity():
    """Analyze tracked computer activity."""

    print("\n===== Activity Analysis =====\n")

    # Load activity data
    df = pd.read_csv(ACTIVITY_LOG)

    # Check if data exists
    if df.empty:
        print("No activity data found.")
        return

    # Convert idle time to numeric
    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    )

    # Remove invalid idle values
    df["idle_seconds"] = df["idle_seconds"].fillna(0)

    # ==============================
    # Total Tracked Time
    # ==============================

    total_tracked_time = df["idle_seconds"].count()

    print(
        f"Total activity records: "
        f"{len(df)}"
    )

    # ==============================
    # Time Per Application
    # ==============================

    time_per_app = (
        df.groupby("active_app")["idle_seconds"]
        .count()
        * 2
    )

    print("\nTime spent per application:")

    print(
        time_per_app.sort_values(
            ascending=False
        )
    )

    # ==============================
    # Application Switches
    # ==============================

    app_switches = (
        df["active_app"]
        .ne(df["active_app"].shift())
        .sum()
        - 1
    )

    print(
        f"\nApplication switches: "
        f"{max(app_switches, 0)}"
    )

    # ==============================
    # Average Idle Time
    # ==============================

    average_idle = df["idle_seconds"].mean()

    print(
        f"\nAverage idle time: "
        f"{average_idle:.2f} seconds"
    )

    # ==============================
    # Maximum Idle Time
    # ==============================

    max_idle = df["idle_seconds"].max()

    print(
        f"Maximum idle time: "
        f"{max_idle:.2f} seconds"
    )

    # ==============================
    # High Idle Records
    # ==============================

    high_idle_records = df[
        df["idle_seconds"] >= 5
    ]

    print(
        f"\nHigh-idle records "
        f"(>= 5 seconds): "
        f"{len(high_idle_records)}"
    )

    # ==============================
    # Session Analysis
    # ==============================

    try:

        sessions = pd.read_csv(SESSION_LOG)

        if not sessions.empty:

            session_count = len(sessions)

            print(
                f"\nTotal sessions: "
                f"{session_count}"
            )

            # Application with longest session
            longest_session = sessions.loc[
                sessions["duration_seconds"].idxmax()
            ]

            print("\nLongest session:")

            print(
                f"Application: "
                f"{longest_session['active_app']}"
            )

            print(
                f"Duration: "
                f"{longest_session['duration_seconds']} "
                f"seconds"
            )

    except FileNotFoundError:

        print("\nNo session data found.")


if __name__ == "__main__":
    analyze_activity()