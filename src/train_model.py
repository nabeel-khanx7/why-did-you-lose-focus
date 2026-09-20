import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


INPUT_FILE = "data/features.csv"
MODEL_FILE = "models/focus_model.pkl"


def train_model():

    # ============================================================
    # LOAD DATA
    # ============================================================

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        print("No feature data found.")
        return

    # ============================================================
    # FEATURES
    # ============================================================

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

    # ============================================================
    # CHRONOLOGICAL TRAIN / TEST SPLIT
    # ============================================================
    #
    # Since this is a time-series activity dataset,
    # we should train on earlier activity and test on
    # later activity.
    #
    # This is more realistic than randomly mixing
    # past and future records.
    # ============================================================

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    # ============================================================
    # MODEL
    # ============================================================

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    # ============================================================
    # TRAIN
    # ============================================================

    model.fit(
        X_train,
        y_train
    )

    # ============================================================
    # PREDICTION
    # ============================================================

    y_pred = model.predict(X_test)

    # ============================================================
    # METRICS
    # ============================================================

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print("=" * 60)
    print("FOCUS ML MODEL TRAINING")
    print("=" * 60)

    print(f"Total records    : {len(df)}")
    print(f"Training records : {len(X_train)}")
    print(f"Testing records  : {len(X_test)}")

    print("\nClass distribution:")

    print(
        y.value_counts()
        .sort_index()
        .rename(
            index={
                0: "Distracted",
                1: "Focused"
            }
        )
    )

    print("\nAccuracy:")
    print(f"{accuracy:.2%}")

    # ============================================================
    # CLASSIFICATION REPORT
    # ============================================================

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Distracted",
                "Focused"
            ],
            zero_division=0
        )
    )

    # ============================================================
    # CONFUSION MATRIX
    # ============================================================

    print("Confusion Matrix:")
    print(
        "                 Predicted"
    )
    print(
        "              Distracted  Focused"
    )

    print(
        f"Actual Distracted   {cm[0][0]:4d}      {cm[0][1]:4d}"
    )

    print(
        f"Actual Focused      {cm[1][0]:4d}      {cm[1][1]:4d}"
    )

    # ============================================================
    # FEATURE IMPORTANCE
    # ============================================================

    print("\nFeature Importance:")

    importance = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    for _, row in importance.iterrows():

        print(
            f"{row['feature']:20s} "
            f"{row['importance']:.4f}"
        )

    # ============================================================
    # SAVE MODEL
    # ============================================================

    joblib.dump(
        model,
        MODEL_FILE
    )

    print("\n" + "=" * 60)
    print(
        f"Model saved to: {MODEL_FILE}"
    )
    print("=" * 60)


if __name__ == "__main__":
    train_model()