"""
Page 2: Learner Profile Explorer
Individual student dossier lookup, behavioral metric badges, historical enrollments,
and segment persona explanation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.visualizations import THEME_LAYOUT
from src.pipeline import get_active_pipeline
from src.theme import apply_theme

st.set_page_config(page_title="EduPro | Learner Profile Explorer", page_icon="👤", layout="wide")
apply_theme()

pipeline = get_active_pipeline()
features_df = pipeline["features"]
courses_df = pipeline["courses"]
tx_df = pipeline["transactions"]
segmenter = pipeline["segmenter"]

st.title("👤 Learner Profile Explorer")
st.markdown("Inspect individual student dossiers, behavioral traits, historical enrollments, and assigned cluster archetypes.")

st.markdown("---")

# Student Selection Controls
user_list = features_df["UserID"].astype(str).tolist()
user_display = [f"{row['UserID']} - {row.get('UserName', 'Learner')} ({row.get('PersonaName', 'General')})" for _, row in features_df.iterrows()]
user_dict = dict(zip(user_display, user_list))

col_sel1, col_sel2 = st.columns([2, 1])
with col_sel1:
    selected_label = st.selectbox("Search or Select a Learner:", user_display, index=0)
    selected_uid = user_dict[selected_label]
with col_sel2:
    st.markdown("<br>", unsafe_allow_html=True)
    random_btn = st.button("🎲 Random Learner Profile", use_container_width=True)
    if random_btn:
        import random
        selected_uid = random.choice(user_list)
        selected_label = next(k for k, v in user_dict.items() if v == selected_uid)

# Fetch learner record
learner = features_df[features_df["UserID"].astype(str) == selected_uid].iloc[0]

# Profile Header Cards
st.markdown("### Profile Summary")
p1, p2, p3, p4 = st.columns(4)

p1.markdown(f"""
<div class="kpi-card kpi-card-blue">
    <div class="kpi-title">Learner Identity</div>
    <div class="kpi-value" style="font-size:1.5rem;">{learner.get('UserName', 'Learner')}</div>
    <span class="kpi-badge badge-blue">ID: {learner['UserID']}</span>
</div>
""", unsafe_allow_html=True)

p2.markdown(f"""
<div class="kpi-card kpi-card-emerald">
    <div class="kpi-title">Assigned Segment</div>
    <div class="kpi-value" style="font-size:1.25rem; color:#047857;">{learner.get('PersonaName', 'Unsegmented')}</div>
    <span class="kpi-badge badge-emerald">Cluster #{learner.get('Cluster', 'N/A')}</span>
</div>
""", unsafe_allow_html=True)

p3.markdown(f"""
<div class="kpi-card kpi-card-amber">
    <div class="kpi-title">Primary Domain</div>
    <div class="kpi-value" style="font-size:1.35rem; color:#B45309;">{learner.get('primary_category', 'General')}</div>
    <span class="kpi-badge badge-amber">Focus: {int(learner.get('category_concentration', 0)*100)}%</span>
</div>
""", unsafe_allow_html=True)

p4.markdown(f"""
<div class="kpi-card kpi-card-purple">
    <div class="kpi-title">Learning Depth</div>
    <div class="kpi-value" style="font-size:1.5rem; color:#6D28D9;">{learner.get('learning_depth_index', 1.0)} / 3.0</div>
    <span class="kpi-badge badge-purple">Beginner → Advanced</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Segment Persona Deep Dive
cluster_id = int(learner.get("Cluster", -1))
if cluster_id in segmenter.cluster_profiles:
    prof_meta = segmenter.cluster_profiles[cluster_id]
    st.info(f"💡 **Archetype Context:** **{prof_meta['persona_name']}** — {prof_meta['description']} (Accounts for {prof_meta['percentage']}% of active platform learners).")
else:
    st.info("💡 **Archetype Context:** New learner with minimal transaction history. Recommended courses will leverage cold-start onboarding heuristics.")

# Behavioral Metrics & Enrollment History
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("#### Behavioral Signature Breakdown")
    m_data = {
        "Metric": [
            "Total Course Enrollments",
            "Unique Categories Explored",
            "Beginner Course Ratio",
            "Intermediate Course Ratio",
            "Advanced Course Ratio",
            "Tenure Across Platform"
        ],
        "Value": [
            f"{learner.get('total_enrollments', 0)} courses",
            f"{learner.get('distinct_categories', 0)} domains",
            f"{int(learner.get('beginner_ratio', 0)*100)}%",
            f"{int(learner.get('intermediate_ratio', 0)*100)}%",
            f"{int(learner.get('advanced_ratio', 0)*100)}%",
            f"{learner.get('tenure_days', 0)} days active"
        ]
    }
    st.dataframe(pd.DataFrame(m_data), use_container_width=True, hide_index=True)

with col_right:
    st.markdown("#### Course Level Exposure")
    level_dist = pd.DataFrame({
        "Level": ["Beginner", "Intermediate", "Advanced"],
        "Ratio": [
            learner.get("beginner_ratio", 0),
            learner.get("intermediate_ratio", 0),
            learner.get("advanced_ratio", 0)
        ]
    })
    fig_bar = px.bar(
        level_dist,
        x="Level",
        y="Ratio",
        color="Level",
        color_discrete_sequence=["#10B981", "#3B82F6", "#8B5CF6"],
        range_y=[0, 1.05]
    )
    fig_bar.update_layout(showlegend=False, height=250, **THEME_LAYOUT)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Historical Transactions Table
st.markdown("### Historical Enrolled Courses")
user_tx = tx_df[tx_df["UserID"].astype(str) == selected_uid].merge(
    courses_df,
    on="CourseID",
    how="left"
)

if not user_tx.empty:
    display_cols = ["CourseID", "CourseName", "CourseCategory", "CourseLevel", "CourseType"]
    if "TransactionDate" in user_tx.columns:
        display_cols.append("TransactionDate")
    st.dataframe(user_tx[display_cols], use_container_width=True, hide_index=True)
else:
    st.warning("No past course enrollments found for this learner. This is a cold-start learner.")
