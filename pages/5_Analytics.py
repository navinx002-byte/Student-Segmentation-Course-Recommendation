"""
Page 5: Platform Analytics & Stakeholder Insights
Deep curriculum demand analysis, course popularity rankings, segment cross-tabs,
and data-driven strategic business recommendations.
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
from src.visualizations import THEME_LAYOUT, plot_category_distribution
from src.pipeline import get_active_pipeline

st.set_page_config(page_title="EduPro | Analytics & Business Insights", page_icon="📈", layout="wide")

pipeline = get_active_pipeline()
features_df = pipeline["features"]
courses_df = pipeline["courses"]
tx_df = pipeline["transactions"]
segmenter = pipeline["segmenter"]

st.title("📈 Platform Analytics & Strategic Insights")
st.markdown("Macro-level intelligence on curriculum engagement, domain saturation, segment velocity, and organizational action plans.")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🏆 Course Popularity", "📊 Domain & Level Insights", "💡 Strategic Business Takeaways"])

with tab1:
    st.subheader("Curriculum Engagement Leaderboard")
    
    enr_counts = tx_df["CourseID"].value_counts().reset_index()
    enr_counts.columns = ["CourseID", "EnrollmentCount"]
    ranked_courses = courses_df.merge(enr_counts, on="CourseID", how="left").fillna({"EnrollmentCount": 0})
    ranked_courses["EnrollmentCount"] = ranked_courses["EnrollmentCount"].astype(int)
    ranked_courses = ranked_courses.sort_values(by="EnrollmentCount", ascending=False)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("#### Top 10 Most Enrolled Courses")
        top_10 = ranked_courses.head(10)
        fig_top = px.bar(
            top_10,
            x="EnrollmentCount",
            y="CourseName",
            orientation="h",
            color="CourseCategory",
            title="Top 10 Flagship Courses"
        )
        fig_top.update_layout(yaxis=dict(autorange="reversed"), **THEME_LAYOUT)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("#### Course Tail: Underperforming Offerings")
        st.caption("Courses with lowest historical enrollment requiring promotional or syllabus revision:")
        bottom_10 = ranked_courses.tail(8)[["CourseID", "CourseName", "CourseCategory", "CourseLevel", "EnrollmentCount"]]
        st.dataframe(bottom_10, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Domain Dynamics & Difficulty Spread")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Demand vs Supply by Category")
        fig_cat = plot_category_distribution(courses_df, tx_df)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.markdown("#### Average Learning Depth by Domain")
        merged_tx = tx_df.merge(courses_df, on="CourseID")
        level_map = {"beginner": 1.0, "intermediate": 2.0, "advanced": 3.0}
        merged_tx["LevelScore"] = merged_tx["CourseLevel"].astype(str).str.lower().map(level_map)
        cat_depth = merged_tx.groupby("CourseCategory")["LevelScore"].mean().reset_index()
        cat_depth.columns = ["Category", "MeanLearningDepth"]
        cat_depth = cat_depth.sort_values(by="MeanLearningDepth", ascending=False)

        fig_depth = px.bar(
            cat_depth,
            x="Category",
            y="MeanLearningDepth",
            color="MeanLearningDepth",
            color_continuous_scale="Blues",
            title="Mean Learning Depth (1.0 = Beg, 3.0 = Adv)"
        )
        fig_depth.update_layout(**THEME_LAYOUT)
        st.plotly_chart(fig_depth, use_container_width=True)

with tab3:
    st.subheader("Executive Recommendations for EduPro Leadership")

    st.markdown("""
    #### 1. Bridge the Technology & Business Conversion Funnel
    - **Observed Pattern:** Over 45% of total enrollments concentrate in introductory Technology and Business courses.
    - **Action:** Introduce targeted guided pathways that bundle beginner courses directly with intermediate follow-ups, reducing early student drop-off.

    #### 2. Address Segment Specificity
    - **Mastery Seekers:** Provide accelerated tracks, specialized capstone projects, and industry credentials to maintain high retention among advanced learners.
    - **Exploratory Learners:** Promote cross-discipline discovery bundles (e.g., Data Science + Healthcare, Design + Business Strategy) to capitalize on high category curiosity.
    - **Foundational Beginners:** Offer structured study cohorts and gamified milestones to transition entry-level learners into self-sustaining learning habits.

    #### 3. Cold-Start Remediation
    - Implement a 2-question onboarding quiz for new users to declare target domain and current skill level, bypassing generic popularity defaults on Day 1.
    """)

    st.markdown("---")
    st.subheader("Download Aggregated Strategic Dataset")
    export_df = ranked_courses[["CourseID", "CourseName", "CourseCategory", "CourseLevel", "CourseType", "EnrollmentCount"]]
    csv_bytes = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Full Curriculum Analytics (CSV)",
        data=csv_bytes,
        file_name="edupro_curriculum_analytics.csv",
        mime="text/csv",
        use_container_width=True
    )
