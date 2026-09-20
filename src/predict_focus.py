import pandas as pd
import joblib


MODEL_FILE = "models/focus_model.pkl"
DATA_FILE = "data/features.csv"


def predict_focus():
    """
    Load trained ML model and predict the latest focus state.

    Returns:
        dict: Prediction result and latest activity information.
    """

    try:
        # Load trained model
        model = joblib.load(MODEL_FILE)

        # Load feature data
        df = pd.read_csv(DATA_FILE)

        if df.empty:
            return {
                "status": "NO DATA",
                "prediction": 0,
                "confidence": 0.0,
                "idle_seconds": 0.0,
                "app_switches": 0,
                "switch_count": 0,
                "distraction": 0,
            }

        features = [
            "idle_seconds",
            "hour",
            "minute",
            "app_switch",
            "idle_rolling_mean",
            "switch_count",
            "distraction",
        ]

        # Latest activity
        latest = df[features].iloc[-1:]

        # ML prediction
        prediction = int(model.predict(latest)[0])

        # Prediction probability
        probability = model.predict_proba(latest)[0]

        confidence = float(max(probability))

        if prediction == 1:
            status = "FOCUSED"
        else:
            status = "DISTRACTED"

        result = {
            "status": status,
            "prediction": prediction,
            "confidence": confidence,
            "idle_seconds": float(
                latest["idle_seconds"].iloc[0]
            ),
            "app_switches": int(
                latest["app_switch"].iloc[0]
            ),
            "switch_count": int(
                latest["switch_count"].iloc[0]
            ),
            "distraction": int(
                latest["distraction"].iloc[0]
            ),
        }

        # Terminal output
        print("=" * 50)
        print("FOCUS PREDICTION")
        print("=" * 50)

        print(f"Prediction : {status}")
        print(f"Confidence : {confidence:.2%}")

        print("\nLatest activity:")
        print(
            f"Idle time      : "
            f"{result['idle_seconds']:.2f} sec"
        )
        print(
            f"App switches   : "
            f"{result['app_switches']}"
        )
        print(
            f"Switch count   : "
            f"{result['switch_count']}"
        )
        print(
            f"Distraction    : "
            f"{result['distraction']}"
        )

        print("=" * 50)

        return result

    except FileNotFoundError as e:

        print("Required file not found:", e)

        return {
            "status": "ERROR",
            "prediction": 0,
            "confidence": 0.0,
            "idle_seconds": 0.0,
            "app_switches": 0,
            "switch_count": 0,
            "distraction": 0,
        }

    except Exception as e:

        print("Prediction error:", e)

        return {
            "status": "ERROR",
            "prediction": 0,
            "confidence": 0.0,
            "idle_seconds": 0.0,
            "app_switches": 0,
            "switch_count": 0,
            "distraction": 0,
        }


if __name__ == "__main__":
    predict_focus()