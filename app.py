"""
EduPro Student Segmentation & Personalized Course Recommendation System
Main Streamlit Application Entrypoint.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.pipeline import get_active_pipeline
from src.theme import apply_theme

# Set page configuration
st.set_page_config(
    page_title="EduPro | AI Learner Segmentation & Course Recommendation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply cohesive modern CSS theme
apply_theme()


def main():
    # Automatically get or initialize the active pipeline
    pipeline = get_active_pipeline()

    # Sidebar Header & Quick Controls
    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&auto=format&fit=crop&q=60", use_container_width=True)
        st.markdown("### 🎓 **EduPro AI Suite**")
        st.caption("Student Segmentation & Personalization Platform")
        st.divider()

        st.markdown("**System Status**")
        st.markdown(f"📦 Source: `{pipeline['loader'].data_source_type}`")
        st.markdown(f"👥 Active Learners: **{len(pipeline['users']):,}**")
        st.markdown(f"📚 Available Courses: **{len(pipeline['courses']):,}**")
        st.markdown(f"📝 Total Enrollments: **{len(pipeline['transactions']):,}**")
        st.markdown(f"🎯 Clusters Active: **{pipeline['segmenter'].k_clusters} Segments**")
        st.divider()

        st.info("💡 **Navigation:** Use the sidebar above or the module directory below to navigate across all sections.")

    # High-impact Hero Header Banner
    st.markdown("""
    <div class="hero-banner">
        <span style="background:rgba(255,255,255,0.2); padding:5px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">
            ✨ UNIFIED MENTOR INTERNSHIP CAPSTONE
        </span>
        <h1 style="margin-top:0.6rem;">Student Segmentation & Course Recommendation</h1>
        <p>
            An end-to-end educational data mining system combining unsupervised behavioral clustering (K-Means & PCA)
            with an explainable, multi-signal course recommendation engine.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Vibrant KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-card-blue">
            <div class="kpi-title">Total Learners</div>
            <div class="kpi-value">{len(pipeline['users']):,}</div>
            <span class="kpi-badge badge-blue">Registered Accounts</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card kpi-card-emerald">
            <div class="kpi-title">Course Catalog</div>
            <div class="kpi-value">{len(pipeline['courses']):,}</div>
            <span class="kpi-badge badge-emerald">Active Curriculum</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card kpi-card-purple">
            <div class="kpi-title">Total Enrollments</div>
            <div class="kpi-value">{len(pipeline['transactions']):,}</div>
            <span class="kpi-badge badge-purple">Historical Events</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        avg_enr = round(len(pipeline['transactions']) / max(len(pipeline['users']), 1), 2)
        st.markdown(f"""
        <div class="kpi-card kpi-card-amber">
            <div class="kpi-title">Avg Enrollments / Learner</div>
            <div class="kpi-value">{avg_enr}</div>
            <span class="kpi-badge badge-amber">Platform Engagement</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive Problem Context in Glass Card
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top:0; color:#1E293B;">📌 Executive Problem Context</h3>
        <p style="color:#475569; font-size:0.95rem; line-height:1.6;">
            EduPro serves a diverse, heterogeneous learner population spanning differing educational goals, career trajectories,
            prior knowledge levels, and study pacing. Conventional platforms default to uniform, demand-driven recommendations
            (e.g., surface-level top seller lists), which induces choice overload, mismatches course difficulty, and leaves niche domains underserved.
        </p>
        <p style="color:#475569; font-size:0.95rem; line-height:1.6; margin-bottom:0;">
            This platform delivers a <b>bipartite data-driven solution</b>:
            <br>• <b>Unsupervised Behavioral Segmentation:</b> Groups learners into 4 archetypes (via K-Means & PCA) using engagement volume, learning depth, and domain concentration.
            <br>• <b>Multi-Signal Hybrid Recommendation:</b> Combines category affinity, difficulty level calibration, collaborative segment peer trends, and platform baseline popularity with transparent explainability.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Page Navigation Links
    st.markdown("### 🚀 Module Directory")
    st.caption("Click any module below to open it instantly:")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.page_link("pages/1_Overview.py", label="1. 📊 Overview & Data Quality", icon="📊")
        st.caption("• Data dictionary, schema audit, and demographic distributions.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link("pages/2_Learner_Explorer.py", label="2. 👤 Learner Profile Explorer", icon="👤")
        st.caption("• Search individual students, view behavioral metrics and assigned archetypes.")

    with c2:
        st.page_link("pages/3_Student_Segmentation.py", label="3. 🎯 Student Segmentation", icon="🎯")
        st.caption("• Interactive 2D PCA cluster projection, radar profiles, and validation metrics.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link("pages/4_Course_Recommendations.py", label="4. 💡 Course Recommendations", icon="💡")
        st.caption("• Real-time Top-5 recommendations, signal attribution charts, and filters.")

    with c3:
        st.page_link("pages/5_Analytics.py", label="5. 📈 Analytics & Insights", icon="📈")
        st.caption("• Course popularity rankings, category demand-supply analysis, and strategic advice.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link("pages/6_Data_Management.py", label="6. ⚙️ Data Management & Upload", icon="⚙️")
        st.caption("• Upload custom CSV or Excel datasets, audit schema, and export cleaned tables.")


if __name__ == "__main__":
    main()
