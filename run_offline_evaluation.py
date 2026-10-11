import json
from pathlib import Path
import config
from src.data_loader import EduProDataLoader
from src.feature_engineering import engineer_learner_features, get_clustering_feature_matrix
from src.segmentation import StudentSegmenter
from src.evaluation import evaluate_recommendations_offline

loader = EduProDataLoader()
u_df, c_df, t_df = loader.load_from_excel(config.DEFAULT_EXCEL_PATH)

print(f"Loaded: Users={len(u_df)}, Courses={len(c_df)}, Transactions={len(t_df)}")

# Features
features_df = engineer_learner_features(u_df, c_df, t_df)
clust_X, feat_cols = get_clustering_feature_matrix(features_df)

# Segmentation
seg = StudentSegmenter(k_clusters=4, random_state=42)
labels, pca = seg.fit_predict(clust_X, feat_cols)

print("\n--- SEGMENTATION RESULTS (K=4) ---")
print("Metrics:", json.dumps(seg.metrics, indent=2))
for cid, prof in seg.cluster_profiles.items():
    print(f"\nCluster {cid}: {prof['persona_name']}")
    print(f"  Count: {prof['count']} ({prof['percentage']}%)")
    print(f"  Means: {prof['means']}")

# Offline Evaluation
print("\n--- OFFLINE RECOMMENDATION EVALUATION ---")
eval_res = evaluate_recommendations_offline(u_df, c_df, t_df, k_eval=5, min_interactions=3)
print(json.dumps(eval_res, indent=2))
