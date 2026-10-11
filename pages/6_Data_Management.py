"""
Page 6: Data Management & Ingestion Gateway
Upload custom datasets (CSV / Excel), schema validation, orphan log audits,
preprocessing pipeline execution, and processed dataset exports.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.data_loader import EduProDataLoader
from src.feature_engineering import engineer_learner_features, get_clustering_feature_matrix
from src.segmentation import StudentSegmenter
from src.recommender import CourseRecommender

st.set_page_config(page_title="EduPro | Data Management", page_icon="⚙️", layout="wide")

if "pipeline" not in st.session_state:
    st.warning("⚠️ Session uninitialized. Please return to the Home page to initialize the pipeline.")
    st.stop()

pipeline = st.session_state.pipeline

st.title("⚙️ Data Management & Ingestion Gateway")
st.markdown("Safely ingest, validate, preprocess, and export EduPro datasets or test external schemas.")

st.markdown("---")

# Security & Data Safety Callout
st.markdown("""
<div style="background-color:#FEF2F2; border-left:4px solid #EF4444; padding:0.8rem 1.2rem; border-radius:0 8px 8px 0; margin-bottom:1.5rem; color:#991B1B;">
    🔒 <strong>Security & Compliance Notice:</strong> Uploaded datasets are parsed strictly as structured text tabular records using pandas.
    No uploaded code or scripts are executed. Session state resets automatically on browser refresh.
</div>
""", unsafe_allow_html=True)

tab_upload, tab_export, tab_reset = st.tabs(["📤 Upload Datasets", "📥 Export Clean Datasets", "🔄 Reset to Demo"])

with tab_upload:
    st.subheader("Upload Custom Data")
    st.markdown("Select upload method:")
    upload_mode = st.radio("Format:", ["Excel Workbook (.xlsx)", "Three Separate CSV Files (Users, Courses, Transactions)"], horizontal=True)

    if upload_mode == "Excel Workbook (.xlsx)":
        excel_file = st.file_uploader("Upload .xlsx file (containing Users, Courses, Transactions sheets):", type=["xlsx"])
        if excel_file is not None:
            if st.button("🚀 Process & Ingest Excel File", type="primary"):
                try:
                    with st.spinner("Parsing workbook and validating relational schema..."):
                        new_loader = EduProDataLoader()
                        u_df, c_df, t_df = new_loader.load_from_excel(excel_file)
                        
                        features_df = engineer_learner_features(u_df, c_df, t_df)
                        clust_X, feat_cols = get_clustering_feature_matrix(features_df)
                        new_segmenter = StudentSegmenter(k_clusters=config.DEFAULT_K_CLUSTERS, random_state=config.RANDOM_STATE)
                        labels, pca_coords = new_segmenter.fit_predict(clust_X, feat_cols)

                        enrolled_idx = features_df[features_df["total_enrollments"] > 0].index
                        features_df["Cluster"] = -1
                        features_df["PersonaName"] = "Unsegmented"
                        features_df.loc[enrolled_idx, "Cluster"] = labels
                        features_df.loc[enrolled_idx, "PersonaName"] = [new_segmenter.get_cluster_name(c) for c in labels]

                        new_recommender = CourseRecommender(c_df, t_df, features_df)

                        st.session_state.pipeline = {
                            "loader": new_loader,
                            "users": u_df,
                            "courses": c_df,
                            "transactions": t_df,
                            "features": features_df,
                            "segmenter": new_segmenter,
                            "pca_coords": pca_coords,
                            "recommender": new_recommender
                        }
                    st.success("✅ Successfully ingested custom Excel dataset! All dashboard tabs are now updated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to process uploaded Excel: {str(e)}")

    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            u_csv = st.file_uploader("Users CSV:", type=["csv"])
        with c2:
            c_csv = st.file_uploader("Courses CSV:", type=["csv"])
        with c3:
            t_csv = st.file_uploader("Transactions CSV:", type=["csv"])

        if u_csv and c_csv and t_csv:
            if st.button("🚀 Ingest & Validate CSV Trio", type="primary"):
                try:
                    with st.spinner("Processing CSV trio and fitting models..."):
                        new_loader = EduProDataLoader()
                        u_df, c_df, t_df = new_loader.load_from_csv_files(u_csv, c_csv, t_csv, source_label="User Uploaded CSVs")
                        features_df = engineer_learner_features(u_df, c_df, t_df)
                        clust_X, feat_cols = get_clustering_feature_matrix(features_df)
                        new_segmenter = StudentSegmenter(k_clusters=config.DEFAULT_K_CLUSTERS, random_state=config.RANDOM_STATE)
                        labels, pca_coords = new_segmenter.fit_predict(clust_X, feat_cols)

                        enrolled_idx = features_df[features_df["total_enrollments"] > 0].index
                        features_df["Cluster"] = -1
                        features_df["PersonaName"] = "Unsegmented"
                        features_df.loc[enrolled_idx, "Cluster"] = labels
                        features_df.loc[enrolled_idx, "PersonaName"] = [new_segmenter.get_cluster_name(c) for c in labels]

                        new_recommender = CourseRecommender(c_df, t_df, features_df)

                        st.session_state.pipeline = {
                            "loader": new_loader,
                            "users": u_df,
                            "courses": c_df,
                            "transactions": t_df,
                            "features": features_df,
                            "segmenter": new_segmenter,
                            "pca_coords": pca_coords,
                            "recommender": new_recommender
                        }
                    st.success("✅ CSV trio validated and loaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ingestion failed: {str(e)}")

with tab_export:
    st.subheader("Export Cleaned & Engineered Artifacts")
    st.markdown("Download processed datasets for offline research, modeling, or stakeholder review:")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        feat_csv = pipeline["features"].to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Student Behavioral Features & Segments (CSV)",
            data=feat_csv,
            file_name="edupro_learner_features_segmented.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_e2:
        val_summary_df = pd.DataFrame([pipeline["loader"].get_summary()])
        summary_csv = val_summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Data Quality Audit Report (CSV)",
            data=summary_csv,
            file_name="edupro_data_quality_report.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab_reset:
    st.subheader("Reset Environment")
    st.markdown("Revert all loaded datasets, models, and states back to the original default sample data:")
    if st.button("🔄 Reset to Default Sample Dataset", type="secondary"):
        from app import init_system
        st.session_state.pipeline = init_system(config.DEFAULT_EXCEL_PATH)
        st.success("System reset to default EduPro demonstration dataset.")
        st.rerun()
