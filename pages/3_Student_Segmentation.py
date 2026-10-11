"""
Page 3: Student Segmentation Engine
Unsupervised machine learning clustering, 2D PCA projections, radar profiles,
and validation metrics (Silhouette, Davies-Bouldin, Calinski-Harabasz).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.visualizations import THEME_LAYOUT, plot_pca_clusters, plot_cluster_radar
from src.segmentation import evaluate_cluster_range, StudentSegmenter
from src.feature_engineering import get_clustering_feature_matrix
from src.pipeline import get_active_pipeline
from src.theme import apply_theme

st.set_page_config(page_title="EduPro | Student Segmentation", page_icon="🎯", layout="wide")
apply_theme()

pipeline = get_active_pipeline()
features_df = pipeline["features"]
segmenter = pipeline["segmenter"]
pca_coords = pipeline["pca_coords"]

st.title("🎯 Student Segmentation via Unsupervised Clustering")
st.markdown("Discover actionable learner segments using multi-dimensional behavioral clustering (K-Means), PCA projection, and mathematical validation.")

st.markdown("---")

# Re-clustering Controls
with st.expander("⚙️ Clustering Hyperparameter Controls & Diagnostics", expanded=False):
    col_k1, col_k2 = st.columns([2, 3])
    with col_k1:
        selected_k = st.slider("Select Number of Clusters (K):", min_value=config.MIN_CLUSTERS, max_value=config.MAX_CLUSTERS, value=segmenter.k_clusters)
        recluster_btn = st.button("🔄 Refit Clustering Model", use_container_width=True)

    with col_k2:
        st.markdown("**Clustering Pipeline Specifications:**")
        st.markdown("""
        - **Algorithm:** K-Means with k-means++ initialization (`n_init=10`)
        - **Preprocessing:** `StandardScaler` (zero mean, unit variance scaling)
        - **Features:** `total_enrollments`, `distinct_categories`, `category_concentration`, `learning_depth_index`, `beginner_ratio`, `advanced_ratio`, `tenure_days`
        - **Ethical Safeguard:** Demographics (`Age`, `Gender`, `UserID`) strictly excluded to eliminate algorithmic bias.
        """)

    if recluster_btn and selected_k != segmenter.k_clusters:
        with st.spinner(f"Refitting K-Means with K={selected_k}..."):
            clust_X, feat_cols = get_clustering_feature_matrix(features_df)
            new_segmenter = StudentSegmenter(k_clusters=selected_k, random_state=config.RANDOM_STATE)
            new_labels, new_pca = new_segmenter.fit_predict(clust_X, feat_cols)

            enrolled_idx = features_df[features_df["total_enrollments"] > 0].index
            features_df.loc[enrolled_idx, "Cluster"] = new_labels
            features_df.loc[enrolled_idx, "PersonaName"] = [new_segmenter.get_cluster_name(c) for c in new_labels]

            pipeline["segmenter"] = new_segmenter
            pipeline["pca_coords"] = new_pca
            pipeline["recommender"].learner_features_df = features_df
            pipeline["recommender"]._precompute_cluster_popularity()
            segmenter = new_segmenter
            pca_coords = new_pca
            st.success(f"Successfully re-clustered into {selected_k} student segments!")

# Validation Metrics Dashboard
st.subheader("Model Validation & Cluster Quality")
m_cols = st.columns(4)
metrics = segmenter.metrics

m_cols[0].markdown(f"""
<div class="kpi-card kpi-card-blue">
    <div class="kpi-title">Active Clusters (K)</div>
    <div class="kpi-value">{metrics.get('k_clusters', 4)}</div>
    <span class="kpi-badge badge-blue">Optimal Partitions</span>
</div>
""", unsafe_allow_html=True)

m_cols[1].markdown(f"""
<div class="kpi-card kpi-card-emerald">
    <div class="kpi-title">Silhouette Score</div>
    <div class="kpi-value">{metrics.get('silhouette_score', 0):.4f}</div>
    <span class="kpi-badge badge-emerald">Cohesion vs Separation</span>
</div>
""", unsafe_allow_html=True)

m_cols[2].markdown(f"""
<div class="kpi-card kpi-card-amber">
    <div class="kpi-title">Davies-Bouldin Index</div>
    <div class="kpi-value">{metrics.get('davies_bouldin_index', 0):.3f}</div>
    <span class="kpi-badge badge-amber">Cluster Separation</span>
</div>
""", unsafe_allow_html=True)

m_cols[3].markdown(f"""
<div class="kpi-card kpi-card-purple">
    <div class="kpi-title">Calinski-Harabasz</div>
    <div class="kpi-value" style="font-size:1.6rem;">{metrics.get('calinski_harabasz_score', 0):,.1f}</div>
    <span class="kpi-badge badge-purple">Variance Ratio Score</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations: PCA 2D Scatter + Radar Chart
st.subheader("Interactive Segment Projections")
col_vis1, col_vis2 = st.columns([1, 1])

with col_vis1:
    fig_pca = plot_pca_clusters(features_df[features_df["total_enrollments"] > 0], pca_coords, segmenter.cluster_profiles)
    st.plotly_chart(fig_pca, use_container_width=True)

with col_vis2:
    fig_radar = plot_cluster_radar(segmenter.cluster_profiles, segmenter.feature_names)
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# Segment Persona Dossiers
st.subheader("Segment Archetypes & Population Distribution")

archetype_rows = []
for c_id, prof in segmenter.cluster_profiles.items():
    archetype_rows.append({
        "Cluster ID": f"Cluster {c_id}",
        "Persona Archetype": prof["persona_name"],
        "Learner Count": f"{prof['count']:,}",
        "Platform Share": f"{prof['percentage']}%",
        "Learning Depth": f"{prof['means'].get('learning_depth_index', 0):.2f} / 3.0",
        "Category Specialization": f"{int(prof['means'].get('category_concentration', 0)*100)}%",
        "Avg Total Enrollments": f"{prof['means'].get('total_enrollments', 0):.1f}",
        "Primary Profile Description": prof["description"]
    })

st.dataframe(pd.DataFrame(archetype_rows), use_container_width=True, hide_index=True)

st.markdown("---")

# Cluster Interpretability Guidance & Methodological Limitations
st.markdown("### ⚠️ Methodological Context & Responsible AI Considerations")
st.markdown("""
1. **Statistical Grouping vs Human Identity:** K-Means clustering identifies observational behavior patterns in historical log interactions. It is a statistical categorization tool and does not represent permanent traits, intrinsic capability, or intellectual aptitude.
2. **Dynamic Evolution:** As a student continues taking courses, their learning depth index, category diversity, and cadence change. Re-clustering dynamically transitions students across segments as they grow.
3. **Spherical Assumption:** K-Means optimizes for Euclidean distance around spherical centroids. While appropriate for normalized behavioral features, density-based algorithms (DBSCAN) or probabilistic models (Gaussian Mixtures) can be evaluated in subsequent iterations.
""")
