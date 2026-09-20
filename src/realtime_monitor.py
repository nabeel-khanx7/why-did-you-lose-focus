import time
import os
import io
import contextlib

import pandas as pd
import joblib

from focus_reason import detect_focus_reasons


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_FILE = "models/focus_model.pkl"
ACTIVITY_FILE = "data/activity_log.csv"

FEATURE_COLUMNS = [
    "idle_seconds",
    "hour",
    "minute",
    "app_switch",
    "idle_rolling_mean",
    "switch_count",
    "distraction"
]


# ==========================================
# DISTRACTION APPS
# Must match feature_engineering.py
# ==========================================

DISTRACTION_APPS = {
    "Google Chrome",
    "WhatsApp",
    "Spotify"
}


# ==========================================
# CREATE LIVE FEATURES
# ==========================================

def create_live_features(df):

    df = df.copy()

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Remove invalid timestamps
    df = df.dropna(
        subset=["timestamp"]
    )

    # Sort by time
    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    # Make sure idle_seconds is numeric
    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    ).fillna(0)

    # ======================================
    # Time features
    # ======================================

    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute

    # ======================================
    # Application switching
    # ======================================

    df["app_switch"] = (
        df["active_app"] != df["active_app"].shift(1)
    ).astype(int)

    # First record is not a switch
    if len(df) > 0:
        df.loc[0, "app_switch"] = 0

    # ======================================
    # Rolling idle time
    # Same as training
    # ======================================

    df["idle_rolling_mean"] = (
        df["idle_seconds"]
        .rolling(
            window=5,
            min_periods=1
        )
        .mean()
    )

    # ======================================
    # Switch count
    # Same as training
    # ======================================

    df["switch_count"] = (
        df["app_switch"]
        .rolling(
            window=10,
            min_periods=1
        )
        .sum()
    )

    # ======================================
    # Distraction
    # ======================================

    df["distraction"] = (
        df["active_app"]
        .isin(DISTRACTION_APPS)
        .astype(int)
    )

    return df


# ==========================================
# GET LATEST FEATURES
# ==========================================

def get_latest_features():

    if not os.path.exists(ACTIVITY_FILE):
        return None

    try:

        df = pd.read_csv(
            ACTIVITY_FILE
        )

    except Exception as error:

        print(
            f"Could not read activity log: {error}"
        )

        return None

    if df.empty:
        return None

    required_columns = {
        "timestamp",
        "active_app",
        "idle_seconds"
    }

    if not required_columns.issubset(
        df.columns
    ):

        print(
            "Activity log is missing required columns."
        )

        return None

    features_df = create_live_features(df)

    if features_df.empty:
        return None

    return features_df.iloc[-1]


# ==========================================
# LOAD MODEL
# ==========================================

def load_model():

    if not os.path.exists(MODEL_FILE):

        print(
            "Model file not found."
        )

        return None

    try:

        model = joblib.load(
            MODEL_FILE
        )

        return model

    except Exception as error:

        print(
            f"Could not load model: {error}"
        )

        return None


# ==========================================
# GET AI FOCUS REASONS
# ==========================================

def get_focus_reasons():

    try:

        # focus_reason.py already prints its own
        # analysis. We temporarily hide that output
        # because realtime_monitor will display
        # the useful information itself.

        with contextlib.redirect_stdout(
            io.StringIO()
        ):

            reason_data = detect_focus_reasons()

        if not isinstance(
            reason_data,
            dict
        ):
            return {
                "main_reason": "Unable to determine reason",
                "reasons": []
            }

        return reason_data

    except Exception as error:

        print(
            f"Reason analysis error: {error}"
        )

        return {
            "main_reason": "Reason analysis unavailable",
            "reasons": []
        }


# ==========================================
# PREDICT LIVE FOCUS
# ==========================================

def predict_live_focus(model):

    latest = get_latest_features()

    if latest is None:

        print(
            "No activity data available."
        )

        return None

    # ======================================
    # Create model input
    # ======================================

    X = pd.DataFrame(
        [[
            latest[column]
            for column in FEATURE_COLUMNS
        ]],
        columns=FEATURE_COLUMNS
    )

    # ======================================
    # Prediction
    # ======================================

    prediction = model.predict(X)[0]

    # ======================================
    # Confidence
    # ======================================

    confidence = None

    if hasattr(
        model,
        "predict_proba"
    ):

        probabilities = model.predict_proba(X)[0]

        confidence = (
            max(probabilities) * 100
        )

    # ======================================
    # Status
    # ======================================

    if int(prediction) == 1:

        status = "FOCUSED"

    else:

        status = "DISTRACTED"

    # ======================================
    # AI REASON DETECTION
    # ======================================

    reason_data = get_focus_reasons()

    main_reason = reason_data.get(
        "main_reason",
        "Unknown"
    )

    reasons = reason_data.get(
        "reasons",
        []
    )

    # ======================================
    # DISPLAY
    # ======================================

    print("\n" + "=" * 60)

    print(
        "REAL-TIME AI FOCUS MONITOR"
    )

    print("=" * 60)

    print(
        f"Focus Status : {status}"
    )

    if confidence is not None:

        print(
            f"Confidence   : {confidence:.2f}%"
        )

    # ======================================
    # CURRENT ACTIVITY
    # ======================================

    print("\nCurrent Activity")

    print("-" * 60)

    print(
        f"Application       : "
        f"{latest['active_app']}"
    )

    print(
        f"Idle seconds      : "
        f"{latest['idle_seconds']:.2f}"
    )

    print(
        f"App switch        : "
        f"{int(latest['app_switch'])}"
    )

    print(
        f"Idle rolling mean : "
        f"{latest['idle_rolling_mean']:.2f}"
    )

    print(
        f"Switch count      : "
        f"{latest['switch_count']:.0f}"
    )

    print(
        f"Distraction       : "
        f"{int(latest['distraction'])}"
    )

    # ======================================
    # AI FOCUS ANALYSIS
    # ======================================

    print("\nAI Focus Analysis")

    print("-" * 60)

    if status == "DISTRACTED":

        print(
            f"Main Reason : {main_reason}"
        )

        if reasons:

            print("\nPossible Reasons:")

            for reason in reasons:

                print(
                    f"  - {reason}"
                )

    else:

        print(
            "Main Reason : No major distraction detected."
        )

        if reasons:

            print("\nCurrent Analysis:")

            for reason in reasons:

                print(
                    f"  - {reason}"
                )

    print("=" * 60)

    # ======================================
    # RETURN RESULT
    # Useful for dashboard later
    # ======================================

    return {

        "status": status,

        "confidence": confidence,

        "application":
            latest["active_app"],

        "idle_seconds":
            latest["idle_seconds"],

        "app_switch":
            latest["app_switch"],

        "switch_count":
            latest["switch_count"],

        "distraction":
            latest["distraction"],

        "main_reason":
            main_reason,

        "reasons":
            reasons
    }


# ==========================================
# REAL-TIME MONITOR
# ==========================================

def run_monitor():

    print("\n" + "=" * 60)

    print(
        "STARTING REAL-TIME AI FOCUS MONITOR"
    )

    print("=" * 60)

    print(
        "Monitoring activity_log.csv"
    )

    print(
        "Prediction interval: 5 seconds"
    )

    print(
        "AI Reason Detection: ENABLED"
    )

    print(
        "Press Ctrl+C to stop."
    )

    print("=" * 60)

    # ======================================
    # Load ML model once
    # ======================================

    model = load_model()

    if model is None:
        return

    # ======================================
    # Continuous monitoring
    # ======================================

    try:

        while True:

            result = predict_live_focus(
                model
            )

            print(
                "\nNext prediction in 5 seconds..."
            )

            time.sleep(5)

    except KeyboardInterrupt:

        print(
            "\n\nReal-Time Focus Monitor stopped."
        )


# ==========================================
# PROGRAM ENTRY
# ==========================================

if __name__ == "__main__":

    run_monitor()