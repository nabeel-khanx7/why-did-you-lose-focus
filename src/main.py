from analyze_activity import analyze_activity
from focus_score import calculate_focus_score
from focus_reason import detect_focus_reasons


def run_full_analysis():
    print("\n" + "=" * 50)
    print("       WHY DID YOU LOSE FOCUS? AI")
    print("=" * 50)

    print("\n[1] Activity Analysis")
    analyze_activity()

    print("\n[2] Focus Score")
    calculate_focus_score()

    print("\n[3] Focus Reasons")
    detect_focus_reasons()

    print("\n" + "=" * 50)
    print("          ANALYSIS COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    run_full_analysis()