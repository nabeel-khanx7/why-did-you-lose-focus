import pandas as pd
from pathlib import Path


# ============================================
# Configuration
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_log.csv"


# ============================================
# Focus Score Calculation
# ============================================

def calculate_focus_score():

    try:
        # ----------------------------------------
        # Load activity data
        # ----------------------------------------

        df = pd.read_csv(DATA_FILE)

        if df.empty:
            print("No activity data found.")
            return None

        required_columns = {
            "timestamp",
            "active_app",
            "idle_seconds"
        }

        if not required_columns.issubset(df.columns):
            print("Required columns are missing.")
            print("Required:", required_columns)
            print("Found:", set(df.columns))
            return None

        # ----------------------------------------
        # Clean data
        # ----------------------------------------

        df["idle_seconds"] = pd.to_numeric(
            df["idle_seconds"],
            errors="coerce"
        ).fillna(0)

        df["active_app"] = (
            df["active_app"]
            .fillna("Unknown")
            .astype(str)
        )

        total_records = len(df)

        # ========================================
        # Application Switching
        # ========================================

        app_switches = (
            df["active_app"]
            .ne(df["active_app"].shift())
            .sum()
        )

        # First record is not an actual switch
        app_switches = max(app_switches - 1, 0)

        # Switch rate
        switch_rate = (
            app_switches / max(total_records - 1, 1)
        )

        # ========================================
        # Idle Time
        # ========================================

        total_idle_time = df["idle_seconds"].sum()

        average_idle_time = df["idle_seconds"].mean()

        high_idle_records = (
            df["idle_seconds"] >= 5
        ).sum()

        high_idle_rate = (
            high_idle_records / total_records
        )

        # ========================================
        # Distraction Applications
        # ========================================

        distraction_apps = [
            "Google Chrome",
            "Chrome",
            "WhatsApp",
            "Instagram",
            "Facebook",
            "YouTube",
            "Netflix",
            "TikTok",
            "Spotify"
        ]

        distraction_records = df[
            df["active_app"].isin(distraction_apps)
        ]

        distraction_count = len(distraction_records)

        distraction_rate = (
            distraction_count / total_records
        )

        # ========================================
        # Calculate Penalties
        # ========================================

        # Application switching
        switch_penalty = min(
            switch_rate * 100 * 1.5,
            30
        )

        # Idle behaviour
        idle_penalty = min(
            high_idle_rate * 100 * 0.8,
            30
        )

        # Distraction applications
        distraction_penalty = min(
            distraction_rate * 100 * 1.2,
            30
        )

        # ========================================
        # Final Focus Score
        # ========================================

        total_penalty = (
            switch_penalty
            + idle_penalty
            + distraction_penalty
        )

        focus_score = 100 - total_penalty

        focus_score = max(
            0,
            min(100, focus_score)
        )

        focus_score = round(focus_score, 1)

        # ========================================
        # Focus Level
        # ========================================

        if focus_score >= 80:
            focus_level = "Excellent"

        elif focus_score >= 65:
            focus_level = "Good"

        elif focus_score >= 45:
            focus_level = "Moderate"

        else:
            focus_level = "Poor"

        # ========================================
        # Most Used Application
        # ========================================

        most_used_app = (
            df["active_app"]
            .value_counts()
            .idxmax()
        )

        # ========================================
        # Display Results
        # ========================================

        print("\n" + "=" * 55)
        print("              FOCUS SCORE ANALYSIS")
        print("=" * 55)

        print(
            f"\nTotal activity records : {total_records}"
        )

        print(
            f"Application switches   : {app_switches}"
        )

        print(
            f"Switch rate            : "
            f"{switch_rate:.2%}"
        )

        print(
            f"Total idle time        : "
            f"{total_idle_time:.2f} seconds"
        )

        print(
            f"Average idle time      : "
            f"{average_idle_time:.2f} seconds"
        )

        print(
            f"High-idle records      : "
            f"{high_idle_records}"
        )

        print(
            f"High-idle rate         : "
            f"{high_idle_rate:.2%}"
        )

        print(
            f"Distraction records    : "
            f"{distraction_count}"
        )

        print(
            f"Distraction rate       : "
            f"{distraction_rate:.2%}"
        )

        print(
            f"Most used application  : "
            f"{most_used_app}"
        )

        print("\n" + "-" * 55)

        print(
            f"Focus Score             : "
            f"{focus_score}/100"
        )

        print(
            f"Focus Level             : "
            f"{focus_level}"
        )

        print("-" * 55)

        print("\nScore penalties:")

        print(
            f"Switch penalty          : "
            f"-{switch_penalty:.1f}"
        )

        print(
            f"Idle penalty            : "
            f"-{idle_penalty:.1f}"
        )

        print(
            f"Distraction penalty     : "
            f"-{distraction_penalty:.1f}"
        )

        print("\n" + "=" * 55)

        # ========================================
        # Return Results
        # ========================================

        return {
            "focus_score": focus_score,
            "focus_level": focus_level,
            "total_records": total_records,
            "app_switches": app_switches,
            "switch_rate": switch_rate,
            "total_idle_time": total_idle_time,
            "average_idle_time": average_idle_time,
            "high_idle_records": high_idle_records,
            "high_idle_rate": high_idle_rate,
            "distraction_count": distraction_count,
            "distraction_rate": distraction_rate,
            "most_used_app": most_used_app,
            "switch_penalty": switch_penalty,
            "idle_penalty": idle_penalty,
            "distraction_penalty": distraction_penalty
        }

    except FileNotFoundError:
        print("\nActivity data file not found.")
        return None

    except Exception as error:
        print(
            f"\nAn error occurred: {error}"
        )
        return None


# ============================================
# Program Entry Point
# ============================================

if __name__ == "__main__":
    calculate_focus_score()