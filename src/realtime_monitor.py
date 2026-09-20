import time
import pandas as pd
import joblib

MODEL_FILE = "models/focus_model.pkl"
DATA_FILE = "data/features.csv"


def get_latest_features(model):
    """
    Get the latest row using exactly the same
    features that were used while training the model.
    """

    df = pd.read_csv(DATA_FILE)

    # Get exact feature names used during model training
    feature_names = model.feature_names_in_

    # Latest record
    latest = df.iloc[[-1]]

    # Select only training features, in the same order
    X = latest[feature_names]

    return X


def predict_focus():
    """
    Load the trained model and predict the
    focus state of the latest activity.
    """

    # Load trained ML model
    model = joblib.load(MODEL_FILE)

    # Get latest features
    X = get_latest_features(model)

    # Make prediction
    prediction = model.predict(X)[0]

    # Get prediction confidence
    probability = model.predict_proba(X).max() * 100

    # Convert prediction into readable status
    if prediction == 1:
        status = "FOCUSED"
    else:
        status = "DISTRACTED"

    print("\n" + "=" * 55)
    print("             REAL-TIME FOCUS MONITOR")
    print("=" * 55)

    print(f"Focus Status : {status}")
    print(f"Confidence   : {probability:.2f}%")

    print("\nCurrent Features:")

    for column, value in X.iloc[0].items():
        print(f"{column:<22}: {value}")

    print("=" * 55)


if __name__ == "__main__":

    print("Starting Real-Time Focus Monitor...")

    while True:
        try:
            predict_focus()

            print("\nNext prediction in 5 seconds...")
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\nReal-Time Focus Monitor stopped.")
            break

        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(5)