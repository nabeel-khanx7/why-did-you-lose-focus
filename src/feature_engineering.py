import pandas as pd


INPUT_FILE = "data/activity_log.csv"
OUTPUT_FILE = "data/features.csv"


def create_features():
    df = pd.read_csv(INPUT_FILE)

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Time-based features
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute

    # App switching
    df["app_switch"] = (
        df["active_app"] != df["active_app"].shift(1)
    ).astype(int)

    # Rolling activity features
    df["idle_rolling_mean"] = (
        df["idle_seconds"]
        .rolling(window=5, min_periods=1)
        .mean()
    )

    df["switch_count"] = (
        df["app_switch"]
        .rolling(window=10, min_periods=1)
        .sum()
    )

    # Distraction indicator
    distraction_apps = [
        "Google Chrome",
        "WhatsApp",
        "Spotify"
    ]

    df["distraction"] = (
        df["active_app"]
        .isin(distraction_apps)
        .astype(int)
    )

    # Focus label
    # 1 = focused
    # 0 = distracted
    df["focus_label"] = (
        (df["idle_seconds"] < 5)
        & (df["distraction"] == 0)
        & (df["switch_count"] < 5)
    ).astype(int)

    # Save features
    df.to_csv(OUTPUT_FILE, index=False)

    print("=" * 50)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 50)

    print(f"Original records : {len(df)}")
    print(f"Features created : {len(df.columns)}")
    print(f"Focused records  : {df['focus_label'].sum()}")
    print(f"Distracted       : {(df['focus_label'] == 0).sum()}")

    print("\nFeature columns:")
    print(df.columns.tolist())

    print("\nSample:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    create_features()