import time
import os
import pandas as pd
import joblib


MODEL_FILE = "models/focus_model.pkl"
ACTIVITY_FILE = "data/activity_log.csv"


# Apps that are generally considered distracting
DISTRACTION_APPS = {
    "Google Chrome",
    "WhatsApp",
    "Spotify",
    "Safari"
}


def create_live_features(df):
    """
    Convert activity log into the same type of features
    used by the trained ML model.
    """

    df = df.copy()

    # Make sure timestamp is datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Sort by time
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute

    # Detect application switches
    df["app_switch"] = (
        df["active_app"] != df["active_app"].shift(1)
    ).astype(int)

    # First record should not count as a switch
    if len(df) > 0:
        df.loc[0, "app_switch"] = 0

    # Rolling idle time
    df["idle_rolling_mean"] = (
        df["idle_seconds"]
        .rolling(window=5, min_periods=1)
        .mean()
    )

    # Total application switches
    df["switch_count"] = df["app_switch"].cumsum()

    # Distraction indicator
    df["distraction"] = (
        df["active_app"]
        .isin(DISTRACTION_APPS)
        .astype(int)
    )

    return df


def get_latest_features():
    """Read the latest activity data and create live features."""

    if not os.path.exists(ACTIVITY_FILE):
        return None

    try:
        df = pd.read_csv(ACTIVITY_FILE)
    except Exception as e:
        print(f"Could not read activity log: {e}")
        return None

    if df.empty:
        return None

    required_columns = {
        "timestamp",
        "active_app",
        "idle_seconds"
    }

    if not required_columns.issubset(df.columns):
        print("Activity log is missing required columns.")
        return None

    features_df = create_live_features(df)

    return features_df.iloc[-1]


def predict_live_focus():

    if not os.path.exists(MODEL_FILE):
        print("Model file not found.")
        return

    # Load model
    model = joblib.load(MODEL_FILE)

    latest = get_latest_features()

    if latest is None:
        print("No activity data available.")
        return

    # Features expected by trained model
    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    else:
        feature_names = [
            "idle_seconds",
            "hour",
            "minute",
            "app_switch",
            "idle_rolling_mean",
            "switch_count",
            "distraction"
        ]

    # Create prediction row
    X = pd.DataFrame(
        [[latest.get(feature, 0) for feature in feature_names]],
        columns=feature_names
    )

    # Prediction
    prediction = model.predict(X)[0]

    # Probability/confidence
    confidence = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[0]
        confidence = max(probabilities) * 100

    # Convert label
    if int(prediction) == 1:
        status = "FOCUSED"
    else:
        status = "DISTRACTED"

    print("\n" + "=" * 55)
    print("REAL-TIME FOCUS MONITOR")
    print("=" * 55)

    print(f"Focus Status : {status}")

    if confidence is not None:
        print(f"Confidence   : {confidence:.2f}%")

    print("\nCurrent Activity:")
    print(f"Application        : {latest['active_app']}")
    print(f"Idle seconds       : {latest['idle_seconds']:.2f}")
    print(f"Hour               : {latest['hour']}")
    print(f"Minute             : {latest['minute']}")
    print(f"App switch         : {latest['app_switch']}")
    print(f"Idle rolling mean  : {latest['idle_rolling_mean']:.2f}")
    print(f"Switch count       : {latest['switch_count']}")
    print(f"Distraction        : {latest['distraction']}")

    print("=" * 55)


def run_monitor():

    print("\nStarting REAL-TIME FOCUS MONITOR...")
    print("Monitoring activity_log.csv")
    print("Press Ctrl+C to stop.\n")

    try:

        while True:

            predict_live_focus()

            print("\nNext prediction in 5 seconds...")

            time.sleep(5)

    except KeyboardInterrupt:

        print("\nReal-Time Focus Monitor stopped.")


if __name__ == "__main__":
    run_monitor()