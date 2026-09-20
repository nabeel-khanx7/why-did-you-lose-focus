import pandas as pd


DATA_FILE = "data/features.csv"


def generate_recommendations():

    df = pd.read_csv(DATA_FILE)

    total_records = len(df)
    switch_count = int(df["app_switch"].sum())
    total_idle = df["idle_seconds"].sum()
    distraction_count = int(df["distraction"].sum())

    print("\n" + "=" * 55)
    print("        PERSONALIZED FOCUS RECOMMENDATIONS")
    print("=" * 55)

    recommendations = []

    # Application switching
    if switch_count >= 20:
        recommendations.append(
            f"⚠️ You switched applications {switch_count} times.\n"
            "   💡 Try staying in one application for 25 minutes."
        )
    elif switch_count >= 10:
        recommendations.append(
            f"⚠️ Application switching is moderate ({switch_count} switches).\n"
            "   💡 Try reducing unnecessary app switching."
        )

    # Idle time
    if total_idle >= 300:
        recommendations.append(
            f"⚠️ High idle time detected ({total_idle:.2f} seconds).\n"
            "   💡 Try using a 25-minute focused work session."
        )

    # Distractions
    if distraction_count >= 10:
        recommendations.append(
            f"⚠️ Frequent distraction detected ({distraction_count} records).\n"
            "   💡 Close distracting applications during study/work."
        )

    # No major problem
    if not recommendations:
        recommendations.append(
            "✅ Your focus behaviour looks healthy.\n"
            "   💡 Keep maintaining your current work pattern."
        )

    for i, recommendation in enumerate(recommendations, 1):
        print(f"\n{i}. {recommendation}")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    generate_recommendations()