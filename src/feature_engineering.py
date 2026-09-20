import pandas as pd


INPUT_FILE = "data/activity_log.csv"
OUTPUT_FILE = "data/features.csv"

# Number of records used to define future behavior.
# Activity tracker roughly every 2 seconds par record banata hai,
# so 15 records ≈ 30 seconds.
FUTURE_WINDOW = 15


def create_features():

    # ============================================================
    # LOAD DATA
    # ============================================================

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        print("No activity data found.")
        return

    # ============================================================
    # CLEAN DATA
    # ============================================================

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    ).fillna(0)

    df["active_app"] = (
        df["active_app"]
        .fillna("Unknown")
        .astype(str)
    )

    df = df.dropna(subset=["timestamp"])

    # Sort chronologically
    df = df.sort_values("timestamp").reset_index(drop=True)

    # ============================================================
    # TIME FEATURES
    # ============================================================

    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute

    # ============================================================
    # APPLICATION SWITCHING
    # ============================================================

    df["app_switch"] = (
        df["active_app"] != df["active_app"].shift(1)
    ).astype(int)

    # First record cannot really be a switch
    df.loc[0, "app_switch"] = 0

    # ============================================================
    # ROLLING FEATURES
    # ============================================================

    df["idle_rolling_mean"] = (
        df["idle_seconds"]
        .rolling(
            window=5,
            min_periods=1
        )
        .mean()
    )

    df["switch_count"] = (
        df["app_switch"]
        .rolling(
            window=10,
            min_periods=1
        )
        .sum()
    )

    # ============================================================
    # DISTRACTION DETECTION
    # ============================================================

    distraction_apps = [
        "Google Chrome",
        "WhatsApp",
        "Spotify",
        "YouTube",
        "Instagram",
        "Facebook",
        "Telegram",
        "Netflix",
        "Reddit",
        "Twitter",
        "X"
    ]

    df["distraction"] = (
        df["active_app"]
        .str.lower()
        .apply(
            lambda app: int(
                any(
                    keyword.lower() in app
                    for keyword in distraction_apps
                )
            )
        )
    )

    # ============================================================
    # FUTURE FOCUS LABEL
    # ============================================================
    #
    # IMPORTANT:
    # The label is based on FUTURE activity.
    #
    # The ML model will use CURRENT activity
    # to predict FUTURE focus.
    #
    # 1 = likely to remain focused
    # 0 = likely to become distracted
    #
    # ============================================================

    future_idle = (
        df["idle_seconds"]
        .shift(-1)
        .rolling(
            window=FUTURE_WINDOW,
            min_periods=FUTURE_WINDOW
        )
        .mean()
        .shift(-(FUTURE_WINDOW - 1))
    )

    future_distraction = (
        df["distraction"]
        .shift(-1)
        .rolling(
            window=FUTURE_WINDOW,
            min_periods=FUTURE_WINDOW
        )
        .mean()
        .shift(-(FUTURE_WINDOW - 1))
    )

    future_switches = (
        df["app_switch"]
        .shift(-1)
        .rolling(
            window=FUTURE_WINDOW,
            min_periods=FUTURE_WINDOW
        )
        .sum()
        .shift(-(FUTURE_WINDOW - 1))
    )

    # Future-focused definition
    df["focus_label"] = (
        (future_idle < 8)
        & (future_distraction < 0.35)
        & (future_switches < 7)
    ).astype(int)

    # Last FUTURE_WINDOW rows don't have enough future data
    df = df.iloc[:-FUTURE_WINDOW].copy()

    # ============================================================
    # SAVE DATASET
    # ============================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ============================================================
    # REPORT
    # ============================================================

    print("=" * 60)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 60)

    print(f"Original records : {len(df) + FUTURE_WINDOW}")
    print(f"Usable records   : {len(df)}")

    print(
        f"Focused records  : "
        f"{int(df['focus_label'].sum())}"
    )

    print(
        f"Distracted       : "
        f"{int((df['focus_label'] == 0).sum())}"
    )

    print("\nFeature columns:")

    print(df.columns.tolist())

    print("\nSample:")

    print(
        df[
            [
                "timestamp",
                "active_app",
                "idle_seconds",
                "app_switch",
                "idle_rolling_mean",
                "switch_count",
                "distraction",
                "focus_label"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print("=" * 60)


if __name__ == "__main__":
    create_features()