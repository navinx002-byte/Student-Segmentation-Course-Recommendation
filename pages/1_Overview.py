"""
Page 1: Project Overview & Exploratory Data Analysis (EDA)
Comprehensive dataset diagnostics, data dictionary, demographic profiles, and quality audits.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.visualizations import THEME_LAYOUT, plot_category_distribution
from src.pipeline import get_active_pipeline
from src.theme import apply_theme

st.set_page_config(page_title="EduPro | Overview & Data Quality", page_icon="📊", layout="wide")
apply_theme()

pipeline = get_active_pipeline()
users_df = pipeline["users"]
courses_df = pipeline["courses"]
tx_df = pipeline["transactions"]
val_report = pipeline["loader"].get_summary()

st.title("📊 Project Overview & Exploratory Data Analysis")
st.markdown("Comprehensive audit of the EduPro learning platform dataset, schema contracts, and baseline distributions.")

# Data Provenance Notice
st.info(
    "📌 **Dataset Provenance & Transparency Statement:**\n\n"
    "This system processes the supplied EduPro multi-table schema (`Users`, `Courses`, `Transactions`). "
    "All statistics, cluster profiles, and recommendations below are dynamically derived from the active dataset. "
    "If using demonstration or synthetic data, insights reflect simulated learner behavior designed for algorithmic evaluation."
)

st.markdown("---")

# High-Level Metric Tiles
st.subheader("Platform Vital Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"""
<div class="kpi-card kpi-card-blue">
    <div class="kpi-title">Registered Learners</div>
    <div class="kpi-value">{len(users_df):,}</div>
    <span class="kpi-badge badge-blue">Active Student Base</span>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="kpi-card kpi-card-emerald">
    <div class="kpi-title">Curriculum Catalog</div>
    <div class="kpi-value">{len(courses_df):,}</div>
    <span class="kpi-badge badge-emerald">Available Courses</span>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="kpi-card kpi-card-purple">
    <div class="kpi-title">Total Enrollments</div>
    <div class="kpi-value">{len(tx_df):,}</div>
    <span class="kpi-badge badge-purple">Historical Events</span>
</div>
""", unsafe_allow_html=True)

c4.markdown(f"""
<div class="kpi-card kpi-card-amber">
    <div class="kpi-title">Date Span</div>
    <div class="kpi-value" style="font-size:1.4rem;">{val_report.get('date_range', 'N/A')}</div>
    <span class="kpi-badge badge-amber">Reporting Period</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for Structured Exploration
tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Quality & Audit", "👥 Learner Demographics", "📚 Course Distribution", "📅 Enrollment Timeline"])

with tab1:
    st.markdown("### Schema & Data Quality Summary")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### Table Record Counts & Cleaning Audit")
        audit_data = [
            {"Table": "Users", "Loaded Records": len(users_df), "Missing Fields": sum(val_report.get("missing_users", {}).values()), "Status": "Valid"},
            {"Table": "Courses", "Loaded Records": len(courses_df), "Missing Fields": sum(val_report.get("missing_courses", {}).values()), "Status": "Valid"},
            {"Table": "Transactions", "Loaded Records": len(tx_df), "Missing Fields": sum(val_report.get("missing_transactions", {}).values()), "Status": "Valid"}
        ]
        st.dataframe(pd.DataFrame(audit_data), use_container_width=True, hide_index=True)

        if val_report.get("orphan_user_transactions_removed", 0) > 0 or val_report.get("orphan_course_transactions_removed", 0) > 0:
            st.warning(
                f"Referential integrity filter: Sanitized "
                f"{val_report.get('orphan_user_transactions_removed', 0)} orphan user logs and "
                f"{val_report.get('orphan_course_transactions_removed', 0)} orphan course logs."
            )
        else:
            st.success("✅ 100% Referential Integrity: All transactions correspond to valid Learner and Course IDs.")

    with col_b:
        st.markdown("#### Data Dictionary")
        dd_data = [
            {"Entity": "Learners (Users)", "Key Attributes": "UserID, UserName, Age, Gender", "Role": "Learner demographic identification"},
            {"Entity": "Curriculum (Courses)", "Key Attributes": "CourseID, CourseName, CourseCategory, CourseType, CourseLevel", "Role": "Catalog metadata and difficulty taxonomy"},
            {"Entity": "Interactions (Transactions)", "Key Attributes": "TransactionID, UserID, CourseID, TransactionDate", "Role": "Historical behavioral enrollment logs"}
        ]
        st.dataframe(pd.DataFrame(dd_data), use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Learner Demographic Profiles")
    col1, col2 = st.columns(2)

    with col1:
        if "Age" in users_df.columns:
            fig_age = px.histogram(
                users_df,
                x="Age",
                nbins=20,
                color_discrete_sequence=["#2563EB"],
                title="Learner Age Distribution"
            )
            fig_age.update_layout(**THEME_LAYOUT)
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("Age field not present in current dataset.")

    with col2:
        if "Gender" in users_df.columns:
            gender_counts = users_df["Gender"].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]
            fig_gender = px.pie(
                gender_counts,
                values="Count",
                names="Gender",
                color_discrete_sequence=["#3B82F6", "#EC4899", "#10B981"],
                title="Learner Gender Representation",
                hole=0.4
            )
            fig_gender.update_layout(**THEME_LAYOUT)
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("Gender field not present in current dataset.")

with tab3:
    st.markdown("### Curriculum Architecture & Demand")
    col1, col2 = st.columns(2)

    with col1:
        fig_cat = plot_category_distribution(courses_df, tx_df)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        level_counts = courses_df["CourseLevel"].value_counts().reset_index()
        level_counts.columns = ["Level", "Count"]
        fig_level = px.bar(
            level_counts,
            x="Level",
            y="Count",
            color="Level",
            color_discrete_sequence=["#10B981", "#F59E0B", "#EF4444"],
            title="Course Difficulty Level Distribution"
        )
        fig_level.update_layout(**THEME_LAYOUT)
        st.plotly_chart(fig_level, use_container_width=True)

with tab4:
    st.markdown("### Temporal Enrollment Cadence")
    if "TransactionDate" in tx_df.columns and pd.api.types.is_datetime64_any_dtype(tx_df["TransactionDate"]):
        daily_enr = tx_df.set_index("TransactionDate").resample("W")["TransactionID"].count().reset_index()
        daily_enr.columns = ["Date", "WeeklyEnrollments"]
        
        fig_trend = px.line(
            daily_enr,
            x="Date",
            y="WeeklyEnrollments",
            markers=True,
            line_shape="spline",
            title="Weekly Platform Enrollment Trajectory"
        )
        fig_trend.update_traces(line_color="#2563EB", marker=dict(color="#1D4ED8", size=5))
        fig_trend.update_layout(**THEME_LAYOUT)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Enrollment timestamp data unavailable or in non-standard format.")
