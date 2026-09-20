import pandas as pd
from pathlib import Path


# ==============================
# Configuration
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_log.csv"


# ==============================
# Focus Score Calculation
# ==============================

def calculate_focus_score():

    try:
        df = pd.read_csv(DATA_FILE)

        if df.empty:
            print("No activity data found.")
            return

        required_columns = {
            "timestamp",
            "active_app",
            "idle_seconds"
        }

        if not required_columns.issubset(df.columns):
            print("Required columns are missing.")
            print("Required:", required_columns)
            print("Found:", set(df.columns))
            return

        # Convert idle time to numbers
        df["idle_seconds"] = pd.to_numeric(
            df["idle_seconds"],
            errors="coerce"
        ).fillna(0)

        # ==================================
        # Basic Statistics
        # ==================================

        total_records = len(df)

        # ==================================
        # Application Switching
        # ==================================

        app_switches = (
            df["active_app"]
            .ne(df["active_app"].shift())
            .sum()
        )

        app_switches = max(app_switches - 1, 0)

        # ==================================
        # Idle Time
        # ==================================

        total_idle_time = df["idle_seconds"].sum()

        high_idle_records = (
            df["idle_seconds"] >= 5
        ).sum()

        # ==================================
        # Distraction Applications
        # ==================================

        distraction_apps = [
            "WhatsApp",
            "Instagram",
            "Facebook",
            "YouTube",
            "Netflix",
            "TikTok"
        ]

        distraction_records = df[
            df["active_app"].isin(distraction_apps)
        ]

        distraction_count = len(distraction_records)

        # ==================================
        # Penalties
        # ==================================

        switch_penalty = min(
            app_switches * 2,
            30
        )

        idle_penalty = min(
            high_idle_records * 3,
            30
        )

        distraction_penalty = min(
            distraction_count * 4,
            30
        )

        # ==================================
        # Focus Score
        # ==================================

        focus_score = 100 - (
            switch_penalty
            + idle_penalty
            + distraction_penalty
        )

        focus_score = max(
            0,
            min(100, focus_score)
        )

        # ==================================
        # Focus Level
        # ==================================

        if focus_score >= 80:
            focus_level = "Excellent"

        elif focus_score >= 60:
            focus_level = "Good"

        elif focus_score >= 40:
            focus_level = "Moderate"

        else:
            focus_level = "Poor"

        # ==================================
        # Most Used Application
        # ==================================

        most_used_app = (
            df["active_app"]
            .value_counts()
            .idxmax()
        )

        # ==================================
        # Display Results
        # ==================================

        print("\n" + "=" * 45)
        print("          FOCUS SCORE ANALYSIS")
        print("=" * 45)

        print(
            f"\nTotal activity records : {total_records}"
        )

        print(
            f"Application switches  : {app_switches}"
        )

        print(
            f"Total idle time       : "
            f"{total_idle_time:.2f} seconds"
        )

        print(
            f"High-idle records     : "
            f"{high_idle_records}"
        )

        print(
            f"Distraction records   : "
            f"{distraction_count}"
        )

        print(
            f"Most used application : "
            f"{most_used_app}"
        )

        print("\n" + "-" * 45)

        print(
            f"Focus Score            : "
            f"{focus_score}/100"
        )

        print(
            f"Focus Level            : "
            f"{focus_level}"
        )

        print("-" * 45)

        print("\nScore penalties:")

        print(
            f"Switch penalty         : "
            f"-{switch_penalty}"
        )

        print(
            f"Idle penalty           : "
            f"-{idle_penalty}"
        )

        print(
            f"Distraction penalty    : "
            f"-{distraction_penalty}"
        )

        print("\n" + "=" * 45)

    except FileNotFoundError:
        print("\nActivity data file not found.")

    except Exception as error:
        print(
            f"\nAn error occurred: {error}"
        )


# ==============================
# Program Entry Point
# ==============================

if __name__ == "__main__":
    calculate_focus_score()