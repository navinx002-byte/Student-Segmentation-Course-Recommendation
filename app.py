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

# Set page configuration
st.set_page_config(
    page_title="EduPro | AI Learner Segmentation & Course Recommendation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, production-grade appearance
st.markdown("""
<style>
    /* Global Typography & Spacing */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    /* Card Styles */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease-in-out;
    }
    .metric-card:hover {
        border-color: #2563EB;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    /* Badges */
    .badge-primary {
        background-color: #EFF6FF;
        color: #2563EB;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-success {
        background-color: #ECFDF5;
        color: #059669;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-amber {
        background-color: #FFFBEB;
        color: #D97706;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


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

        st.info("💡 **Navigation:** Use the sidebar above or the interactive cards below to navigate across all modules.")

    # Home Landing Page Content
    st.markdown('<div class="main-header">Student Segmentation & Personalized Course Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Unified Mentor Internship Capstone Project | Enterprise Educational Data Mining Architecture</div>', unsafe_allow_html=True)

    # KPI Top Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Learners</div>
            <div class="metric-value">{len(pipeline['users']):,}</div>
            <span class="badge-primary">Registered Accounts</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Course Catalog</div>
            <div class="metric-value">{len(pipeline['courses']):,}</div>
            <span class="badge-primary">Active Curriculum</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Enrollments</div>
            <div class="metric-value">{len(pipeline['transactions']):,}</div>
            <span class="badge-success">Historical Interactions</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        avg_enr = round(len(pipeline['transactions']) / max(len(pipeline['users']), 1), 2)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Enrollments / Learner</div>
            <div class="metric-value">{avg_enr}</div>
            <span class="badge-amber">Engagement Intensity</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Core Value Proposition & System Architecture Overview
    st.markdown("### 📌 Executive Problem Context")
    st.markdown("""
    EduPro serves a diverse, heterogeneous learner population spanning differing educational goals, career trajectories,
    prior knowledge levels, and study pacing. Conventional platforms default to uniform, demand-driven recommendations
    (e.g., surface-level top seller lists), which induces choice overload, mismatches course difficulty, and leaves niche domains underserved.
    
    This platform delivers a **bipartite data-driven solution**:
    1. **Unsupervised Behavioral Segmentation:** Discovers distinct learner archetypes using multi-dimensional engagement, learning depth, and domain specialization vectors (via K-Means Clustering & PCA).
    2. **Multi-Signal Hybrid Recommendation:** Combines content-based domain affinity, difficulty level calibration, collaborative segment peer trends, and platform baseline popularity with transparent explainability.
    """)

    st.markdown("---")

    # Native Streamlit Interactive Page Navigation Links
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
