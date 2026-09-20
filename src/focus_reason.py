import pandas as pd


def detect_focus_reasons():

    try:
        df = pd.read_csv("data/activity_log.csv")

        if df.empty:
            return {
                "main_reason": "No activity data",
                "reasons": [],
                "most_used_app": "None",
                "app_switches": 0,
                "total_idle": 0,
                "high_idle_records": 0,
                "distraction_records": 0
            }

        # -----------------------------
        # BASIC METRICS
        # -----------------------------

        app_switches = (
            df["active_app"] != df["active_app"].shift()
        ).sum() - 1

        app_switches = max(app_switches, 0)

        total_idle = df["idle_seconds"].sum()

        high_idle = (
            df["idle_seconds"] >= 5
        ).sum()

        most_used_app = (
            df["active_app"].value_counts().idxmax()
        )

        # -----------------------------
        # DISTRACTION APPS
        # -----------------------------

        distraction_apps = [
            "WhatsApp",
            "Google Chrome",
            "Safari",
            "Instagram",
            "YouTube",
            "Telegram"
        ]

        distraction_df = df[
            df["active_app"].isin(distraction_apps)
        ]

        distraction_count = len(distraction_df)

        # -----------------------------
        # REASON DETECTION
        # -----------------------------

        reasons = []

        if app_switches >= 10:
            reasons.append(
                f"Frequent application switching ({app_switches} switches)"
            )

        if total_idle >= 30:
            reasons.append(
                f"High idle time ({total_idle:.2f} seconds)"
            )

        if distraction_count >= 5:
            reasons.append(
                f"Frequent distraction-app usage ({distraction_count} records)"
            )

        if not reasons:
            reasons.append(
                "No major distraction pattern detected."
            )

        # -----------------------------
        # MAIN REASON
        # -----------------------------

        if app_switches >= 10:
            main_reason = "Frequent application switching"

        elif total_idle >= 30:
            main_reason = "High idle time"

        elif distraction_count >= 5:
            main_reason = "Distraction application usage"

        else:
            main_reason = "No major distraction detected"

        # -----------------------------
        # RESULT
        # -----------------------------

        result = {
            "main_reason": main_reason,
            "reasons": reasons,
            "most_used_app": most_used_app,
            "app_switches": app_switches,
            "total_idle": round(total_idle, 2),
            "high_idle_records": high_idle,
            "distraction_records": distraction_count
        }

        # -----------------------------
        # TERMINAL OUTPUT
        # -----------------------------

        print("\n" + "=" * 50)
        print("        WHY DID YOU LOSE FOCUS?")
        print("=" * 50)

        print("\nMain Reason:")
        print(main_reason)

        print("\nPossible Reasons:")

        for i, reason in enumerate(reasons, 1):
            print(f"{i}. {reason}")

        print("\nActivity Summary:")
        print(f"App switches       : {app_switches}")
        print(f"Total idle time    : {total_idle:.2f} seconds")
        print(f"High-idle records  : {high_idle}")
        print(f"Distraction records: {distraction_count}")
        print(f"Most used app      : {most_used_app}")

        print("\n" + "=" * 50)

        return result

    except FileNotFoundError:
        print("Activity log file not found.")

        return {
            "main_reason": "Activity data not found",
            "reasons": []
        }

    except Exception as e:
        print("Error:", e)

        return {
            "main_reason": "Analysis error",
            "reasons": []
        }


if __name__ == "__main__":
    detect_focus_reasons()