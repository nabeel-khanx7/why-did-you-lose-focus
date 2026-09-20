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

DATA_FILE = Path("data/activity_log.csv")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if not DATA_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["idle_seconds"] = pd.to_numeric(
        df["idle_seconds"],
        errors="coerce"
    ).fillna(0)

    df["active_app"] = df["active_app"].fillna("Unknown")

    df = df.dropna(subset=["timestamp"])

    return df


df = load_data()


# ============================================================
# HEADER
# ============================================================

st.title("🎯 Why Did You Lose Focus?")
st.caption("AI-powered Focus & Productivity Analytics")


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

unique_apps = df["active_app"].nunique()

total_idle = df["idle_seconds"].sum()

average_idle = df["idle_seconds"].mean()

# Number of application switches
app_switches = (
    df["active_app"]
    .ne(df["active_app"].shift())
    .sum() - 1
)

if app_switches < 0:
    app_switches = 0


# ============================================================
# DISTRACTION APPS
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

    app_lower = str(app).lower()

    return any(
        keyword in app_lower
        for keyword in distraction_keywords
    )


df["distraction"] = df["active_app"].apply(is_distraction)

distraction_records = int(df["distraction"].sum())


# ============================================================
# FOCUS SCORE
# ============================================================

score = 100

# Application switching penalty
switch_penalty = min(app_switches * 1.5, 30)

# Idle penalty
idle_penalty = min(total_idle / 30, 30)

# Distraction penalty
distraction_penalty = min(distraction_records * 1.0, 30)

score -= switch_penalty
score -= idle_penalty
score -= distraction_penalty

score = max(0, min(100, round(score)))


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
# METRICS
# ============================================================

st.subheader("📊 Focus Overview")

col1, col2, col3, col4 = st.columns(4)

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
# STATUS
# ============================================================

st.subheader("🧠 Current Analysis")

st.info(status)


# ============================================================
# TWO COLUMNS
# ============================================================

left, right = st.columns(2)


# ============================================================
# APPLICATION USAGE
# ============================================================

with left:

    st.subheader("💻 Application Usage")

    app_usage = (
        df["active_app"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(app_usage)


# ============================================================
# IDLE TIME
# ============================================================

with right:

    st.subheader("⏱️ Idle Time")

    idle_chart = df[
        ["timestamp", "idle_seconds"]
    ].copy()

    idle_chart = idle_chart.set_index("timestamp")

    st.line_chart(
        idle_chart["idle_seconds"]
    )


# ============================================================
# DISTRACTION ANALYSIS
# ============================================================

st.divider()

st.subheader("🚨 Distraction Analysis")

col1, col2, col3 = st.columns(3)

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
# FOCUS REASONS
# ============================================================

st.divider()

st.subheader("❓ Why Did You Lose Focus?")


reasons = []

if app_switches >= 20:

    reasons.append(
        f"Frequent application switching detected ({app_switches} switches)."
    )

if total_idle >= 300:

    reasons.append(
        f"High idle time detected ({total_idle:.1f} seconds)."
    )

if distraction_records >= 10:

    reasons.append(
        f"Frequent distraction-app usage detected ({distraction_records} records)."
    )

if not reasons:

    reasons.append(
        "No major distraction pattern detected."
    )


for i, reason in enumerate(reasons, 1):

    st.write(
        f"**{i}.** {reason}"
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("💡 Personalized Recommendations")


recommendations = []

if app_switches >= 20:

    recommendations.append(
        "Try staying in one application for at least 25 minutes."
    )

if total_idle >= 300:

    recommendations.append(
        "Use a 25-minute focused work session with fewer idle periods."
    )

if distraction_records >= 10:

    recommendations.append(
        "Close distracting applications during study/work."
    )

if score >= 80:

    recommendations.append(
        "Great focus! Try maintaining the same work pattern."
    )

if not recommendations:

    recommendations.append(
        "Keep monitoring your activity to discover more patterns."
    )


for recommendation in recommendations:

    st.write(
        f"💡 {recommendation}"
    )


# ============================================================
# TOP APPLICATION
# ============================================================

st.divider()

st.subheader("🏆 Most Used Application")

st.success(
    f"{top_app}"
)


# ============================================================
# RAW DATA
# ============================================================

with st.expander("🔍 View Activity Data"):

    st.dataframe(
        df.tail(100),
        use_container_width=True
    )


# ============================================================
# REFRESH
# ============================================================

st.divider()

if st.button("🔄 Refresh Dashboard"):

    st.cache_data.clear()

    st.rerun()


st.caption(
    "Why Did You Lose Focus? — AI Focus Analytics System"
)