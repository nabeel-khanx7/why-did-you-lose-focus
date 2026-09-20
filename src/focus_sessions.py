import pandas as pd

def get_focus_session_stats(df):

    if df.empty:
        return {
            "sessions": 0,
            "total_minutes": 0,
            "longest_minutes": 0
        }

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    ).fillna(0)

    df = df.dropna(subset=["timestamp"])

    df = df.sort_values("timestamp").reset_index(drop=True)

    df["time_gap"] = (
        df["timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    df["focused"] = (
        (df["idle_seconds"] < 5) &
        (df["time_gap"] <= 10) &
        (
            df["active_app"]
            == df["active_app"].shift()
        )
    )

    sessions = []

    session_start = None

    for i, row in df.iterrows():

        if row["focused"]:

            if session_start is None:
                session_start = row["timestamp"]

        else:

            if session_start is not None:

                session_end = df.loc[
                    i - 1,
                    "timestamp"
                ]

                duration = (
                    session_end - session_start
                ).total_seconds()

                if duration >= 60:
                    sessions.append(duration)

                session_start = None

    # Final session
    if session_start is not None:

        session_end = df.iloc[-1]["timestamp"]

        duration = (
            session_end - session_start
        ).total_seconds()

        if duration >= 60:
            sessions.append(duration)

    if not sessions:
        return {
            "sessions": 0,
            "total_minutes": 0,
            "longest_minutes": 0
        }

    return {
        "sessions": len(sessions),
        "total_minutes": sum(sessions) / 60,
        "longest_minutes": max(sessions) / 60
    }

def detect_focus_sessions():

    try:
        df = pd.read_csv("data/activity_log.csv")

        if df.empty:
            print("No activity data found.")
            return

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df["idle_seconds"] = pd.to_numeric(
            df["idle_seconds"],
            errors="coerce"
        ).fillna(0)

        df = df.dropna(subset=["timestamp"])

        # Sort activity chronologically
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Calculate time between activity records
        df["time_gap"] = (
            df["timestamp"]
            .diff()
            .dt.total_seconds()
            .fillna(0)
        )

        # Focus conditions
        # Low idle + same application = focused activity
        df["focused"] = (
            (df["idle_seconds"] < 5) &
            (df["time_gap"] <= 10) &
            (
                df["active_app"]
                == df["active_app"].shift()
            )
        )

        sessions = []

        session_start = None
        session_records = 0

        for i, row in df.iterrows():

            if row["focused"]:

                if session_start is None:
                    session_start = row["timestamp"]
                    session_records = 1
                else:
                    session_records += 1

            else:

                if session_start is not None:

                    session_end = df.loc[
                        i - 1, "timestamp"
                    ]

                    duration = (
                        session_end - session_start
                    ).total_seconds()

                    if duration >= 60:

                        sessions.append({
                            "start": session_start,
                            "end": session_end,
                            "duration_seconds": duration,
                            "records": session_records
                        })

                    session_start = None
                    session_records = 0

        # Handle final session
        if session_start is not None:

            session_end = df.iloc[-1]["timestamp"]

            duration = (
                session_end - session_start
            ).total_seconds()

            if duration >= 60:

                sessions.append({
                    "start": session_start,
                    "end": session_end,
                    "duration_seconds": duration,
                    "records": session_records
                })

        print("\n" + "=" * 55)
        print("             FOCUS SESSION ANALYSIS")
        print("=" * 55)

        if not sessions:

            print("\nNo focused sessions detected.")

            print(
                "\nTip: Stay in one application "
                "with low idle time for at least 1 minute."
            )

            return

        total_focus = sum(
            session["duration_seconds"]
            for session in sessions
        )

        longest_session = max(
            sessions,
            key=lambda x: x["duration_seconds"]
        )

        print(
            f"\nFocused Sessions : {len(sessions)}"
        )

        print(
            f"Total Focus Time : "
            f"{total_focus / 60:.2f} minutes"
        )

        print(
            f"Longest Session  : "
            f"{longest_session['duration_seconds'] / 60:.2f} minutes"
        )

        print("\nSessions:")

        for i, session in enumerate(
            sessions,
            1
        ):

            print(
                f"{i}. "
                f"{session['start'].strftime('%H:%M:%S')} → "
                f"{session['end'].strftime('%H:%M:%S')} | "
                f"{session['duration_seconds'] / 60:.2f} min"
            )

        print("\n" + "=" * 55)

    except FileNotFoundError:

        print(
            "Activity log file not found."
        )

    except Exception as e:

        print("Error:", e)


if __name__ == "__main__":
    detect_focus_sessions()