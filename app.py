"""
EduPro Student Segmentation & Personalized Course Recommendation System
Main Streamlit Application Entrypoint.
"""

import sys
import os
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.data_loader import EduProDataLoader
from src.feature_engineering import engineer_learner_features, get_clustering_feature_matrix
from src.segmentation import StudentSegmenter
from src.recommender import CourseRecommender

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
    /* Info Callout */
    .custom-callout {
        background-color: #F8FAFC;
        border-left: 4px solid #2563EB;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Initializing EduPro Analytics Engine...")
def init_system(excel_path: Path):
    """Loads default dataset, computes features, fits segmentation and recommender."""
    loader = EduProDataLoader()
    if excel_path.exists():
        u_df, c_df, t_df = loader.load_from_excel(excel_path)
    else:
        # Fallback to CSV files
        u_df, c_df, t_df = loader.load_from_csv_files(
            config.DEFAULT_USERS_CSV,
            config.DEFAULT_COURSES_CSV,
            config.DEFAULT_TRANSACTIONS_CSV
        )

    # 1. Feature Engineering
    features_df = engineer_learner_features(u_df, c_df, t_df)

    # 2. Fit Student Segmentation (K-Means)
    clust_X, feat_cols = get_clustering_feature_matrix(features_df)
    segmenter = StudentSegmenter(k_clusters=config.DEFAULT_K_CLUSTERS, random_state=config.RANDOM_STATE)
    labels, pca_coords = segmenter.fit_predict(clust_X, feat_cols)

    # Map cluster persona back to features_df
    features_df["Cluster"] = -1
    features_df["PersonaName"] = "Unsegmented"
    enrolled_idx = features_df[features_df["total_enrollments"] > 0].index
    features_df.loc[enrolled_idx, "Cluster"] = labels
    features_df.loc[enrolled_idx, "PersonaName"] = [segmenter.get_cluster_name(c) for c in labels]

    # 3. Initialize Recommender
    recommender = CourseRecommender(c_df, t_df, features_df)

    return {
        "loader": loader,
        "users": u_df,
        "courses": c_df,
        "transactions": t_df,
        "features": features_df,
        "segmenter": segmenter,
        "pca_coords": pca_coords,
        "recommender": recommender
    }


def main():
    # Initialize session state
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = init_system(config.DEFAULT_EXCEL_PATH)

    pipeline = st.session_state.pipeline

    # Sidebar Header & Quick Controls
    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&auto=format&fit=crop&q=60", use_container_width=True)
        st.markdown("### 🎓 **EduPro AI Suite**")
        st.caption("Student Segmentation & Personalization Platform")
        st.divider()

        st.markdown("**System Status**")
        st.markdown(f"📦 Data Source: `{pipeline['loader'].data_source_type}`")
        st.markdown(f"👥 Active Learners: **{len(pipeline['users']):,}**")
        st.markdown(f"📚 Available Courses: **{len(pipeline['courses']):,}**")
        st.markdown(f"📝 Total Enrollments: **{len(pipeline['transactions']):,}**")
        st.markdown(f"🎯 Clusters Active: **{pipeline['segmenter'].k_clusters} Segments**")
        st.divider()

        st.info("💡 **Navigation:** Use the left sidebar pages above to explore segments, test real-time course recommendations, inspect analytics, or upload custom datasets.")

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

    # Interactive Navigation Cards
    st.markdown("### 🚀 Module Directory")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        #### 1. 📊 [Overview & Data Quality](Overview)
        - Data dictionary and schema audit
        - Missing value and duplicate checks
        - Global enrollment cadence and demographics
        """)
        st.markdown("""
        #### 2. 👤 [Learner Profile Explorer](Learner_Explorer)
        - Individual student dossier lookup
        - Behavioral engagement metrics
        - Dynamic persona badge and trajectory summary
        """)

    with c2:
        st.markdown("""
        #### 3. 🎯 [Student Segmentation](Student_Segmentation)
        - Interactive 2D PCA cluster projection
        - Radar spider-chart of segment dimensions
        - Elbow & Silhouette mathematical validation
        """)
        st.markdown("""
        #### 4. 💡 [Course Recommendations](Course_Recommendations)
        - Live, student-centric Top-5 course recommender
        - Signal attribution waterfall charts
        - Real-time filters and cold-start support
        """)

    with c3:
        st.markdown("""
        #### 5. 📈 [Analytics & Business Insights](Analytics)
        - Course popularity and demand-supply gap
        - Learning depth distribution across domains
        - Actionable stakeholder recommendations
        """)
        st.markdown("""
        #### 6. ⚙️ [Data Management](Data_Management)
        - Upload custom CSV or Excel datasets
        - Live schema validation & orphan record audit
        - Export clean feature tables and segment maps
        """)


if __name__ == "__main__":
    main()
