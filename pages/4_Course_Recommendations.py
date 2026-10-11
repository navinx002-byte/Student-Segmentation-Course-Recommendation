"""
Page 4: Personalized Course Recommendations
Hybrid multi-signal recommendation engine, interactive signal weighting,
filtering, cold-start handling, and transparent signal attribution.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.visualizations import plot_recommendation_score_breakdown

st.set_page_config(page_title="EduPro | Personalized Recommendations", page_icon="💡", layout="wide")

if "pipeline" not in st.session_state:
    st.warning("⚠️ Session uninitialized. Please return to the Home page to initialize the pipeline.")
    st.stop()

pipeline = st.session_state.pipeline
features_df = pipeline["features"]
courses_df = pipeline["courses"]
recommender = pipeline["recommender"]

st.title("💡 Personalized Course Recommendation Engine")
st.markdown("Dynamic course ranking tailored to each learner's domain affinity, skill trajectory, peer segment patterns, and platform trends.")

st.markdown("---")

# Learner Selector & Options
user_list = features_df["UserID"].astype(str).tolist()
user_display = [f"{row['UserID']} - {row.get('UserName', 'Learner')} ({row.get('PersonaName', 'General')})" for _, row in features_df.iterrows()]
user_dict = dict(zip(user_display, user_list))

c_u1, c_u2 = st.columns([3, 1])
with c_u1:
    selected_label = st.selectbox("Select Target Learner:", user_display, index=0)
    selected_uid = user_dict[selected_label]
with c_u2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎲 Pick Random Learner", use_container_width=True):
        import random
        selected_uid = random.choice(user_list)
        selected_label = next(k for k, v in user_dict.items() if v == selected_uid)

learner = features_df[features_df["UserID"].astype(str) == selected_uid].iloc[0]

# Student Snapshot Callout
st.markdown(f"""
<div style="background-color:#F0FDF4; border-left:4px solid #10B981; padding:0.8rem 1.2rem; border-radius:0 8px 8px 0; margin-bottom:1.5rem;">
    <strong>Learner Dossier:</strong> {learner.get('UserName', 'Learner')} (<code>{selected_uid}</code>) &nbsp;|&nbsp;
    <strong>Segment:</strong> <span style="color:#059669; font-weight:600;">{learner.get('PersonaName', 'New Learner')}</span> &nbsp;|&nbsp;
    <strong>Preferred Domain:</strong> <b>{learner.get('primary_category', 'All')}</b> &nbsp;|&nbsp;
    <strong>Skill Depth:</strong> <b>{learner.get('learning_depth_index', 1.0)} / 3.0</b> &nbsp;|&nbsp;
    <strong>Prior Enrollments:</strong> <b>{learner.get('total_enrollments', 0)}</b>
</div>
""", unsafe_allow_html=True)

# Recommendation Filters & Sliders in Sidebar/Expander
with st.expander("🎛️ Recommendation Tuning & Filter Settings", expanded=False):
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        cat_options = ["All Categories"] + sorted(courses_df["CourseCategory"].dropna().unique().tolist())
        filter_cat = st.selectbox("Filter by Category:", cat_options, index=0)
        
    with f_col2:
        level_options = ["All Levels"] + sorted(courses_df["CourseLevel"].dropna().unique().tolist())
        filter_lvl = st.selectbox("Filter by Difficulty:", level_options, index=0)

    with f_col3:
        exclude_enrolled = st.toggle("Exclude Previously Enrolled Courses", value=True, help="Prevents recommending courses already in the learner's transaction history.")
        top_n = st.slider("Number of Recommendations:", min_value=3, max_value=10, value=5)

    st.markdown("##### Multi-Signal Weight Calibration")
    w1, w2, w3, w4 = st.columns(4)
    w_cat = w1.slider("Category Affinity", 0.0, 1.0, 0.35, 0.05)
    w_lvl = w2.slider("Skill Level Match", 0.0, 1.0, 0.25, 0.05)
    w_cl = w3.slider("Peer Segment Trend", 0.0, 1.0, 0.25, 0.05)
    w_gl = w4.slider("Global Platform Trend", 0.0, 1.0, 0.15, 0.05)

    custom_weights = {
        "category_pref": w_cat,
        "level_suitability": w_lvl,
        "cluster_popularity": w_cl,
        "global_popularity": w_gl
    }

# Generate Recommendations
recommendations = recommender.recommend(
    user_id=selected_uid,
    n_recommendations=top_n,
    exclude_enrolled=exclude_enrolled,
    filter_category=filter_cat,
    filter_level=filter_lvl,
    custom_weights=custom_weights
)

if not recommendations:
    st.warning("⚠️ No suitable courses found matching the active filters and exclusion criteria. Try loosening the category or level filters.")
else:
    st.subheader(f"Top {len(recommendations)} Personalized Recommendations")

    col_cards, col_vis = st.columns([3, 2])

    with col_cards:
        for idx, rec in enumerate(recommendations, 1):
            score_pct = int(rec["Score"] * 100)
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:1.2rem; margin-bottom:1rem; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <span style="background:#EFF6FF; color:#2563EB; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.8rem;">#{idx} MATCH ({score_pct}%)</span>
                        <h4 style="margin:0.4rem 0 0.2rem 0; color:#1E293B;">{rec['CourseName']}</h4>
                        <div style="font-size:0.85rem; color:#64748B;">
                            🏷️ <b>{rec['CourseCategory']}</b> &nbsp;|&nbsp; 
                            📊 Level: <b>{rec['CourseLevel']}</b> &nbsp;|&nbsp; 
                            🖥️ Type: <b>{rec['CourseType']}</b> &nbsp;|&nbsp; 
                            ID: <code>{rec['CourseID']}</code>
                        </div>
                    </div>
                </div>
                <div style="margin-top:0.6rem; padding-top:0.6rem; border-top:1px dashed #E2E8F0; font-size:0.85rem; color:#059669;">
                    ✨ <b>Why Recommended:</b> {rec['Explanation']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_vis:
        st.markdown("#### Primary Recommendation Signal Attribution")
        st.caption(f"Decomposition of ranking signals for Course: **{recommendations[0]['CourseName'][:32]}...**")
        fig_attr = plot_recommendation_score_breakdown(recommendations[0])
        st.plotly_chart(fig_attr, use_container_width=True)

        st.markdown("---")
        # Export Recommendations
        rec_export_df = pd.DataFrame(recommendations)[["CourseID", "CourseName", "CourseCategory", "CourseLevel", "Score", "Explanation"]]
        csv_data = rec_export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Recommendations (CSV)",
            data=csv_data,
            file_name=f"edupro_recs_{selected_uid}.csv",
            mime="text/csv",
            use_container_width=True
        )
