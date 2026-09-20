from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
from pathlib import Path
from recommendations import generate_recommendations
from focus_reason import detect_focus_reasons
from predict_focus import predict_focus
from focus_score import calculate_focus_score
# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Why Did You Lose Focus?",
    page_icon="🎯",
    layout="wide"
)

st_autorefresh(
    interval=5000,
    key="focus_dashboard_refresh"
)

DATA_FILE = Path("data/activity_log.csv")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=5)
def load_data():

    if not DATA_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return df

    # Timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Idle seconds
    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    ).fillna(0)

    # Active app
    df["active_app"] = (
        df["active_app"]
        .fillna("Unknown")
        .astype(str)
    )

    # Remove invalid timestamps
    df = df.dropna(
        subset=["timestamp"]
    )

    # Sort by time
    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return df


df = load_data()

# ============================================================
# AI FOCUS PREDICTION
# ============================================================

ml_result = None
ml_status = "ERROR"
ml_confidence = 0.0

# ============================================================
# HEADER
# ============================================================

st.title("🎯 Why Did You Lose Focus?")

st.caption(
    "AI-powered Focus & Productivity Analytics"
)


# ============================================================
# CHECK DATA
# ============================================================

if df.empty:

    st.warning(
        "No activity data found. "
        "Run the activity tracker first."
    )

    st.stop()


# ============================================================
# BASIC CALCULATIONS
# ============================================================

total_records = len(df)

unique_apps = df[
    "active_app"
].nunique()

total_idle = df[
    "idle_seconds"
].sum()

average_idle = df[
    "idle_seconds"
].mean()


# ============================================================
# APPLICATION SWITCHES
# ============================================================

app_switches = (
    df["active_app"]
    .ne(
        df["active_app"].shift()
    )
    .sum()
    - 1
)

app_switches = max(
    int(app_switches),
    0
)


# ============================================================
# DISTRACTION DETECTION
# ============================================================

distraction_keywords = [

    "youtube",
    "instagram",
    "facebook",
    "whatsapp",
    "telegram",
    "tiktok",
    "netflix",
    "reddit",
    "twitter",
    "x.com"
]


def is_distraction(app):

    app_lower = str(
        app
    ).lower()

    return any(
        keyword in app_lower
        for keyword in distraction_keywords
    )


df["distraction"] = (
    df["active_app"]
    .apply(is_distraction)
)

distraction_records = int(
    df["distraction"].sum()
)


# ============================================================
# FOCUS SCORE
# ============================================================

# Use the shared scoring engine so the dashboard and focus_score.py
# always calculate the same Focus Score.
focus_score_result = calculate_focus_score()

if focus_score_result:
    score = focus_score_result["focus_score"]
    focus_level = focus_score_result["focus_level"]
else:
    score = 0
    focus_level = "Unknown"

# Run the ML model once and expose a safe fallback.
ml_result = predict_focus()

if ml_result is None:
    ml_result = {
        "status": "ERROR",
        "prediction": 0,
        "confidence": 0.0,
        "idle_seconds": 0.0,
        "app_switches": 0,
        "switch_count": 0,
        "distraction": 0
    }

ml_status = ml_result.get("status", "ERROR")
ml_confidence = ml_result.get("confidence", 0.0)

# ============================================================
# TOP APPLICATION
# ============================================================

top_app = (
    df["active_app"]
    .value_counts()
    .idxmax()
)


# ============================================================
# FOCUS SESSION DETECTION
# ============================================================

session_df = df.copy()


# Time gap between records
session_df["time_gap"] = (
    session_df["timestamp"]
    .diff()
    .dt.total_seconds()
    .fillna(0)
)


# Focus conditions:
#
# 1. Idle time < 5 seconds
# 2. Time gap <= 10 seconds
# 3. Same application is active
#

session_df["focused"] = (

    (session_df["idle_seconds"] < 5)

    &

    (session_df["time_gap"] <= 10)

    &

    (
        session_df["active_app"]
        ==
        session_df["active_app"].shift()
    )
)


# ============================================================
# BUILD FOCUS SESSIONS
# ============================================================

sessions = []

session_start = None


for i, row in session_df.iterrows():

    if row["focused"]:

        if session_start is None:

            session_start = row[
                "timestamp"
            ]

    else:

        if session_start is not None:

            previous_index = i - 1

            session_end = (
                session_df
                .loc[
                    previous_index,
                    "timestamp"
                ]
            )

            duration = (
                session_end
                - session_start
            ).total_seconds()

            # Only count sessions >= 1 minute
            if duration >= 60:

                sessions.append(
                    duration
                )

            session_start = None


# ============================================================
# FINAL SESSION
# ============================================================

if session_start is not None:

    session_end = (
        session_df
        .iloc[-1]["timestamp"]
    )

    duration = (
        session_end
        - session_start
    ).total_seconds()

    if duration >= 60:

        sessions.append(
            duration
        )


# ============================================================
# SESSION STATISTICS
# ============================================================

focus_sessions = len(
    sessions
)


if sessions:

    total_focus_minutes = (
        sum(sessions) / 60
    )

    longest_focus_minutes = (
        max(sessions) / 60
    )

else:

    total_focus_minutes = 0

    longest_focus_minutes = 0


# ============================================================
# FOCUS OVERVIEW
# ============================================================

st.subheader(
    "📊 Focus Overview"
)


col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "Focus Score",
        f"{score:.1f}/100"
    )


with col2:

    st.metric(
        "Focus Level",
        focus_level
    )


with col3:

    st.metric(
        "App Switches",
        app_switches
    )


with col4:

    st.metric(
        "Idle Time",
        f"{total_idle:.1f}s"
    )


st.divider()


# ============================================================
# CURRENT ANALYSIS
# ============================================================

# ============================================================
# AI FOCUS PREDICTION
# ============================================================

# ==========================================
# WHY DID YOU LOSE FOCUS?
# ==========================================

st.divider()

st.subheader("🧠 Why Did You Lose Focus?")

# Detect focus reasons
reason_data = detect_focus_reasons()

main_reason = reason_data.get(
    "main_reason",
    "No major distraction detected"
)

reasons = reason_data.get(
    "reasons",
    []
)

# Main reason
if main_reason == "No major distraction detected":

    st.success(
        "🟢 No major distraction detected"
    )

else:

    st.error(
        f"🔴 Main Reason: {main_reason}"
    )

# Possible reasons
if reasons:

    st.markdown("### 📋 Possible Reasons")

    for reason in reasons:

        st.write(
            f"• {reason}"
        )

# Activity summary
st.markdown("### 📊 Activity Summary")

reason_col1, reason_col2, reason_col3, reason_col4 = st.columns(4)

with reason_col1:

    st.metric(
        "App Switches",
        reason_data.get("app_switches", 0)
    )

with reason_col2:

    st.metric(
        "Total Idle",
        f"{reason_data.get('total_idle', 0):.1f}s"
    )

with reason_col3:

    st.metric(
        "High Idle Records",
        reason_data.get("high_idle_records", 0)
    )

with reason_col4:

    st.metric(
        "Distraction Records",
        reason_data.get("distraction_records", 0)
    )

st.caption(
    f"Most used application: "
    f"{reason_data.get('most_used_app', 'None')}"
)
# ==========================================
# PERSONALIZED FOCUS RECOMMENDATIONS
# ==========================================

st.divider()

st.subheader("💡 Personalized Focus Recommendations")

recommendation_data = generate_recommendations()

recommendations = recommendation_data

if recommendations:

    for recommendation in recommendations:

        rec_type = recommendation.get(
            "type",
            "info"
        )

        title = recommendation.get(
            "title",
            "Focus Recommendation"
        )

        message = recommendation.get(
            "message",
            ""
        )

        tip = recommendation.get(
            "tip",
            ""
        )

        if rec_type == "warning":

            st.warning(
                f"⚠️ **{title}**\n\n"
                f"{message}\n\n"
                f"💡 **Tip:** {tip}"
            )

        elif rec_type == "success":

            st.success(
                f"✅ **{title}**\n\n"
                f"{message}\n\n"
                f"💡 **Tip:** {tip}"
            )

        elif rec_type == "error":

            st.error(
                f"❌ **{title}**\n\n"
                f"{message}\n\n"
                f"💡 **Tip:** {tip}"
            )

        else:

            st.info(
                f"ℹ️ **{title}**\n\n"
                f"{message}\n\n"
                f"💡 **Tip:** {tip}"
            )

else:

    st.info(
        "No personalized recommendations available."
    )
# ============================================================
# FOCUS SESSION OVERVIEW
# ============================================================

st.divider()

st.subheader(
    "🎯 Focus Session Analysis"
)


session_col1, session_col2, session_col3 = (
    st.columns(3)
)


with session_col1:

    st.metric(
        "Focus Sessions",
        focus_sessions
    )


with session_col2:

    st.metric(
        "Total Focus Time",
        f"{total_focus_minutes:.2f} min"
    )


with session_col3:

    st.metric(
        "Longest Session",
        f"{longest_focus_minutes:.2f} min"
    )


# ============================================================
# SESSION LIST
# ============================================================

if sessions:

    st.write(
        "### 📋 Detected Focus Sessions"
    )

    session_rows = []

    current_session_start = None


    for i, row in session_df.iterrows():

        if row["focused"]:

            if current_session_start is None:

                current_session_start = (
                    row["timestamp"]
                )

        else:

            if current_session_start is not None:

                session_end = (
                    session_df
                    .loc[
                        i - 1,
                        "timestamp"
                    ]
                )

                duration = (
                    session_end
                    - current_session_start
                ).total_seconds()


                if duration >= 60:

                    session_rows.append({

                        "Start":
                            current_session_start.strftime(
                                "%H:%M:%S"
                            ),

                        "End":
                            session_end.strftime(
                                "%H:%M:%S"
                            ),

                        "Duration":
                            f"{duration / 60:.2f} min"

                    })


                current_session_start = None


    # Final session
    if current_session_start is not None:

        session_end = (
            session_df
            .iloc[-1]["timestamp"]
        )

        duration = (
            session_end
            - current_session_start
        ).total_seconds()


        if duration >= 60:

            session_rows.append({

                "Start":
                    current_session_start.strftime(
                        "%H:%M:%S"
                    ),

                "End":
                    session_end.strftime(
                        "%H:%M:%S"
                    ),

                "Duration":
                    f"{duration / 60:.2f} min"

            })


    if session_rows:

        session_table = pd.DataFrame(
            session_rows
        )

        st.dataframe(
            session_table,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TWO COLUMNS
# ============================================================

left, right = st.columns(2)


# ============================================================
# APPLICATION USAGE
# ============================================================

with left:

    st.subheader(
        "💻 Application Usage"
    )

    app_usage = (
        df["active_app"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(
        app_usage
    )


# ============================================================
# IDLE TIME
# ============================================================

with right:

    st.subheader(
        "⏱️ Idle Time"
    )

    idle_chart = df[
        [
            "timestamp",
            "idle_seconds"
        ]
    ].copy()

    idle_chart = (
        idle_chart
        .set_index("timestamp")
    )

    st.line_chart(
        idle_chart[
            "idle_seconds"
        ]
    )


# ============================================================
# DISTRACTION ANALYSIS
# ============================================================

st.divider()

st.subheader(
    "🚨 Distraction Analysis"
)


col1, col2, col3 = (
    st.columns(3)
)


with col1:

    st.metric(
        "Distraction Records",
        distraction_records
    )


with col2:

    st.metric(
        "Unique Applications",
        unique_apps
    )


with col3:

    st.metric(
        "Average Idle",
        f"{average_idle:.2f}s"
    )


# ============================================================
# WHY DID YOU LOSE FOCUS?
# ============================================================

st.divider()

st.subheader("❓ Why Did You Lose Focus?")

switch_rate = focus_score_result.get("switch_rate", 0) if focus_score_result else 0
high_idle_rate = focus_score_result.get("high_idle_rate", 0) if focus_score_result else 0
distraction_rate = focus_score_result.get("distraction_rate", 0) if focus_score_result else 0

reasons = []

if switch_rate >= 0.10:
    reasons.append(f"Frequent application switching detected ({app_switches} switches, {switch_rate:.1%} switch rate).")

if high_idle_rate >= 0.10:
    reasons.append(f"High idle activity detected ({high_idle_rate:.1%} of records had 5+ seconds idle).")

if distraction_rate >= 0.10:
    reasons.append(f"Frequent distraction-app usage detected ({distraction_records} records, {distraction_rate:.1%} of activity).")

if ml_status == "DISTRACTED":
    reasons.append(f"ML model currently classifies the latest activity as DISTRACTED with {ml_confidence:.1%} confidence.")

if not reasons:
    reasons.append("No major distraction pattern detected.")

if focus_score_result:
    penalties = {
        "Frequent application switching": focus_score_result["switch_penalty"],
        "High idle time": focus_score_result["idle_penalty"],
        "Distraction application usage": focus_score_result["distraction_penalty"]
    }
    main_reason = max(penalties, key=penalties.get)
    if max(penalties.values()) <= 0:
        main_reason = "No major distraction detected"
else:
    main_reason = "Unable to calculate reason"

st.error(f"🔴 Main Reason: {main_reason}")
st.write("### 🧠 Possible Reasons")

for i, reason in enumerate(reasons, 1):
    st.write(f"**{i}.** {reason}")

# ============================================================
# RECOMMENDATIONS
# ============================================================

# ============================================================
# MOST USED APPLICATION
# ============================================================

st.divider()

st.subheader(
    "🏆 Most Used Application"
)


st.success(
    f"💻 {top_app}"
)


# ============================================================
# RAW ACTIVITY DATA
# ============================================================

with st.expander(
    "🔍 View Activity Data"
):

    st.dataframe(
        df.tail(100),
        use_container_width=True
    )


# ============================================================
# MANUAL REFRESH
# ============================================================

st.divider()


if st.button(
    "🔄 Refresh Dashboard"
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Why Did You Lose Focus? — "
    "AI Focus Analytics System"
)