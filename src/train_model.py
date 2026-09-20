import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

import joblib


INPUT_FILE = "data/features.csv"
MODEL_FILE = "models/focus_model.pkl"


def train_model():

    # Load dataset
    df = pd.read_csv(INPUT_FILE)

    # Features
    features = [
        "idle_seconds",
        "hour",
        "minute",
        "app_switch",
        "idle_rolling_mean",
        "switch_count",
        "distraction"
    ]

    X = df[features]
    y = df["focus_label"]

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Random Forest model
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    # Train
    model.fit(X_train, y_train)

    # Prediction
    y_pred = model.predict(X_test)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)

    print("=" * 50)
    print("FOCUS ML MODEL TRAINING")
    print("=" * 50)

    print(f"Training records : {len(X_train)}")
    print(f"Testing records  : {len(X_test)}")
    print(f"Accuracy         : {accuracy:.2%}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, MODEL_FILE)

    print("=" * 50)
    print(f"Model saved to: {MODEL_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    train_model()