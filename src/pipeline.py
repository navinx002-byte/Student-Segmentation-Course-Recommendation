"""
Central pipeline initialization and session state manager.
Ensures that all pages automatically initialize and share the EduPro pipeline,
regardless of which page the user opens first or refreshes.
"""

from pathlib import Path
import streamlit as st
import config
from src.data_loader import EduProDataLoader
from src.feature_engineering import engineer_learner_features, get_clustering_feature_matrix
from src.segmentation import StudentSegmenter
from src.recommender import CourseRecommender


@st.cache_resource(show_spinner="⚡ Initializing EduPro AI Pipeline & Preloading Dataset...")
def get_default_pipeline():
    """Cached pipeline loader guaranteeing zero cold-start latency across all pages."""
    loader = EduProDataLoader()
    if config.DEFAULT_EXCEL_PATH.exists():
        u_df, c_df, t_df = loader.load_from_excel(config.DEFAULT_EXCEL_PATH)
    else:
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


def get_active_pipeline():
    """
    Returns the active pipeline from session_state, automatically
    bootstrapping the default cached pipeline if not already present.
    """
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = get_default_pipeline()
    return st.session_state.pipeline


def set_active_pipeline(new_pipeline_dict):
    """Sets a newly uploaded custom pipeline into session state."""
    st.session_state.pipeline = new_pipeline_dict
