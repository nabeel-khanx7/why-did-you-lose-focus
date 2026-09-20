from recommendations import generate_recommendations
from feature_engineering import create_features
from predict_focus import predict_focus
from focus_score import calculate_focus_score
from focus_reason import detect_focus_reasons


def run_full_analysis():

    print("\n" + "=" * 55)
    print("        WHY DID YOU LOSE FOCUS? - AI")
    print("=" * 55)

    # 1. Feature Engineering
    print("\n[1] Creating features...")
    create_features()

    # 2. ML Prediction
    print("\n[2] AI Focus Prediction...")
    predict_focus()

    # 3. Focus Score
    print("\n[3] Focus Score...")
    calculate_focus_score()

    # 4. Focus Reasons
    print("\n[4] Focus Reasons...")
    detect_focus_reasons()

    # 5. Personalized Recommendations
    print("\n[5] Personalized Recommendations...")
    generate_recommendations()

    print("\n" + "=" * 55)
    print("              ANALYSIS COMPLETE")
    print("=" * 55)


if __name__ == "__main__":
    run_full_analysis()