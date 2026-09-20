import pandas as pd


def detect_focus_reasons():

    try:
        df = pd.read_csv("data/activity_log.csv")

        if df.empty:
            print("No activity data found.")
            return

        total_records = len(df)

        app_switches = (df["active_app"] != df["active_app"].shift()).sum() - 1
        app_switches = max(app_switches, 0)

        total_idle = df["idle_seconds"].sum()

        high_idle = (df["idle_seconds"] >= 5).sum()

        most_used_app = df["active_app"].value_counts().idxmax()

        distraction_apps = [
            "WhatsApp",
            "Google Chrome",
            "Safari",
            "Instagram",
            "YouTube",
            "Telegram"
        ]

        distraction_count = len(
            df[df["active_app"].isin(distraction_apps)]
        )

        print("\n" + "=" * 45)
        print("        WHY DID YOU LOSE FOCUS?")
        print("=" * 45)

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
            reasons.append("No major distraction pattern detected.")

        print("\nPossible reasons:")

        for i, reason in enumerate(reasons, 1):
            print(f"{i}. {reason}")

        print("\nMain distraction:")

        if app_switches >= 10:
            print("Frequent application switching")
        elif total_idle >= 30:
            print("High idle time")
        elif distraction_count >= 5:
            print("Distraction application usage")
        else:
            print("No major distraction detected")

        print("\nMost used application:", most_used_app)
        print("High-idle records:", high_idle)

        print("\n" + "=" * 45)

    except FileNotFoundError:
        print("Activity log file not found.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    detect_focus_reasons()
