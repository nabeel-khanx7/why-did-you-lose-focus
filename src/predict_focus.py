import pandas as pd
import joblib


MODEL_FILE = "models/focus_model.pkl"
DATA_FILE = "data/features.csv"


def predict_focus():
    # Load trained model
    model = joblib.load(MODEL_FILE)

    # Load latest feature data
    df = pd.read_csv(DATA_FILE)

    features = [
        "idle_seconds",
        "hour",
        "minute",
        "app_switch",
        "idle_rolling_mean",
        "switch_count",
        "distraction"
    ]

    # Take latest activity
    latest = df[features].iloc[-1:]

    # Prediction
    prediction = model.predict(latest)[0]

    # Probability
    probability = model.predict_proba(latest)[0]

    if prediction == 1:
        status = "FOCUSED"
    else:
        status = "DISTRACTED"

    print("=" * 50)
    print("FOCUS PREDICTION")
    print("=" * 50)

    print(f"Prediction : {status}")
    print(f"Confidence : {max(probability):.2%}")

    print("\nLatest activity:")
    print(f"Idle time      : {latest['idle_seconds'].iloc[0]:.2f} sec")
    print(f"App switches   : {latest['app_switch'].iloc[0]}")
    print(f"Switch count   : {latest['switch_count'].iloc[0]}")
    print(f"Distraction    : {latest['distraction'].iloc[0]}")

    print("=" * 50)


if __name__ == "__main__":
    predict_focus()