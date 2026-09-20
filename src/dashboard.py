from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
from pathlib import Path

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

score = 100


# Application switching penalty
switch_penalty = min(
    app_switches * 1.5,
    30
)


# Idle penalty
idle_penalty = min(
    total_idle / 30,
    30
)


# Distraction penalty
distraction_penalty = min(
    distraction_records * 1.0,
    30
)


score -= switch_penalty
score -= idle_penalty
score -= distraction_penalty


score = max(
    0,
    min(
        100,
        round(score)
    )
)


# ============================================================
# FOCUS LEVEL
# ============================================================

if score >= 80:

    focus_level = "Excellent"
    status = "🟢 Highly Focused"

elif score >= 60:

    focus_level = "Good"
    status = "🟢 Focused"

elif score >= 40:

    focus_level = "Average"
    status = "🟡 Moderate Focus"

else:

    focus_level = "Poor"
    status = "🔴 Distracted"


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
        f"{score}/100"
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

st.subheader(
    "🧠 Current Analysis"
)

st.info(status)


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

st.subheader(
    "❓ Why Did You Lose Focus?"
)


reasons = []


if app_switches >= 20:

    reasons.append(
        f"Frequent application switching detected "
        f"({app_switches} switches)."
    )


if total_idle >= 300:

    reasons.append(
        f"High idle time detected "
        f"({total_idle:.1f} seconds)."
    )


if distraction_records >= 10:

    reasons.append(
        f"Frequent distraction-app usage detected "
        f"({distraction_records} records)."
    )


if not reasons:

    reasons.append(
        "No major distraction pattern detected."
    )


# Main reason
if app_switches >= 20:

    main_reason = (
        "Frequent application switching"
    )

elif total_idle >= 300:

    main_reason = (
        "High idle time"
    )

elif distraction_records >= 10:

    main_reason = (
        "Distraction application usage"
    )

else:

    main_reason = (
        "No major distraction detected"
    )


st.error(
    f"🔴 Main Reason: {main_reason}"
)


st.write(
    "### 🧠 Possible Reasons"
)


for i, reason in enumerate(
    reasons,
    1
):

    st.write(
        f"**{i}.** {reason}"
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.divider()

st.subheader(
    "💡 Personalized Recommendations"
)


recommendations = []


if app_switches >= 20:

    recommendations.append(
        "Try staying in one application "
        "for at least 25 minutes."
    )


if total_idle >= 300:

    recommendations.append(
        "Use a 25-minute focused work session "
        "with fewer idle periods."
    )


if distraction_records >= 10:

    recommendations.append(
        "Close distracting applications "
        "during study/work."
    )


if longest_focus_minutes < 25:

    recommendations.append(
        "Try building a longer uninterrupted "
        "focus session."
    )


if score >= 80:

    recommendations.append(
        "Great focus! Try maintaining "
        "the same work pattern."
    )


if not recommendations:

    recommendations.append(
        "Keep monitoring your activity "
        "to discover more patterns."
    )


for recommendation in recommendations:

    st.write(
        f"💡 {recommendation}"
    )


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