import pandas as pd


# ==========================================
# CONFIGURATION
# ==========================================

DATA_FILE = "data/features.csv"


# ==========================================
# GENERATE PERSONALIZED RECOMMENDATIONS
# ==========================================

def generate_recommendations():

    try:

        df = pd.read_csv(DATA_FILE)

    except FileNotFoundError:

        return [
            {
                "type": "error",
                "title": "No Activity Data",
                "message": "Activity data was not found.",
                "tip": "Run the activity tracker first."
            }
        ]

    except Exception as error:

        return [
            {
                "type": "error",
                "title": "Data Loading Error",
                "message": str(error),
                "tip": "Check the activity data file."
            }
        ]

    # ==========================================
    # EMPTY DATA CHECK
    # ==========================================

    if df.empty:

        return [
            {
                "type": "info",
                "title": "No Activity Data",
                "message": "No activity records are available.",
                "tip": "Start the activity tracker to collect data."
            }
        ]

    # ==========================================
    # REQUIRED COLUMNS CHECK
    # ==========================================

    required_columns = {
        "app_switch",
        "idle_seconds",
        "distraction"
    }

    if not required_columns.issubset(df.columns):

        missing_columns = required_columns - set(df.columns)

        return [
            {
                "type": "error",
                "title": "Invalid Activity Data",
                "message": (
                    "Required columns are missing: "
                    + ", ".join(missing_columns)
                ),
                "tip": "Run the feature engineering pipeline again."
            }
        ]

    # ==========================================
    # CLEAN NUMERIC DATA
    # ==========================================

    df["app_switch"] = pd.to_numeric(
        df["app_switch"],
        errors="coerce"
    ).fillna(0)

    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    ).fillna(0)

    df["distraction"] = pd.to_numeric(
        df["distraction"],
        errors="coerce"
    ).fillna(0)

    # ==========================================
    # CALCULATE METRICS
    # ==========================================

    total_records = len(df)

    switch_count = int(
        df["app_switch"].sum()
    )

    total_idle = float(
        df["idle_seconds"].sum()
    )

    distraction_count = int(
        df["distraction"].sum()
    )

    recommendations = []

    # ==========================================
    # APPLICATION SWITCHING
    # ==========================================

    if switch_count >= 20:

        recommendations.append(
            {
                "type": "warning",
                "title": "Frequent application switching",
                "message": (
                    f"You switched applications "
                    f"{switch_count} times."
                ),
                "tip": (
                    "Try staying in one application "
                    "for at least 25 minutes."
                )
            }
        )

    elif switch_count >= 10:

        recommendations.append(
            {
                "type": "warning",
                "title": "Moderate application switching",
                "message": (
                    f"You switched applications "
                    f"{switch_count} times."
                ),
                "tip": (
                    "Try reducing unnecessary "
                    "application switching."
                )
            }
        )

    # ==========================================
    # HIGH IDLE TIME
    # ==========================================

    if total_idle >= 300:

        recommendations.append(
            {
                "type": "warning",
                "title": "High idle time",
                "message": (
                    f"Your total idle time is "
                    f"{total_idle:.2f} seconds."
                ),
                "tip": (
                    "Try using a 25-minute "
                    "focused work session."
                )
            }
        )

    # ==========================================
    # DISTRACTION
    # ==========================================

    if distraction_count >= 10:

        recommendations.append(
            {
                "type": "warning",
                "title": "Frequent distraction detected",
                "message": (
                    f"{distraction_count} distraction "
                    f"records were detected."
                ),
                "tip": (
                    "Close distracting applications "
                    "during study or work sessions."
                )
            }
        )

    # ==========================================
    # NO MAJOR PROBLEM
    # ==========================================

    if not recommendations:

        recommendations.append(
            {
                "type": "success",
                "title": "Healthy focus behaviour",
                "message": (
                    "Your current focus behaviour "
                    "looks healthy."
                ),
                "tip": (
                    "Keep maintaining your "
                    "current work pattern."
                )
            }
        )

    # ==========================================
    # RETURN RESULT
    # ==========================================

    return recommendations


# ==========================================
# TERMINAL TEST
# ==========================================

if __name__ == "__main__":

    results = generate_recommendations()

    print("\n" + "=" * 60)
    print("        PERSONALIZED FOCUS RECOMMENDATIONS")
    print("=" * 60)

    for index, recommendation in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{recommendation['title']}"
        )

        print(
            f"   {recommendation['message']}"
        )

        print(
            f"   Tip: {recommendation['tip']}"
        )

    print("\n" + "=" * 60)