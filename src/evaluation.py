"""
Offline evaluation and validation engine for EduPro segmentation and recommendation.
Implements leave-last-out offline holdout evaluation, Precision@K, Recall@K,
HitRate@K, MRR, Catalog Coverage, Popularity Baseline comparison, and clustering metrics.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd


def evaluate_recommendations_offline(
    users_df: pd.DataFrame,
    courses_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    k_eval: int = 5,
    min_interactions: int = 3,
    sample_size: int = 200,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Conducts leave-last-out chronological validation for recommendation quality.
    Compares the Personalized Multi-Signal Engine against a Global Popularity Baseline.
    """
    if transactions_df.empty or courses_df.empty:
        return {"error": "Transactions or courses empty. Cannot run offline evaluation."}

    # Filter to users with at least min_interactions
    tx = transactions_df.copy()
    user_counts = tx["UserID"].value_counts()
    eligible_users = user_counts[user_counts >= min_interactions].index.tolist()

    if not eligible_users:
        return {
            "error": f"No learners with at least {min_interactions} enrollments found for offline split."
        }

    # Sample users if large to maintain fast runtime
    np.random.seed(random_state)
    if len(eligible_users) > sample_size:
        eval_users = list(np.random.choice(eligible_users, size=sample_size, replace=False))
    else:
        eval_users = eligible_users

    # Sort transactions chronologically if dates exist
    if "TransactionDate" in tx.columns:
        tx = tx.sort_values(by=["UserID", "TransactionDate"])

    # Leave-last-out split
    train_tx_list = []
    test_dict: Dict[str, List[str]] = {}

    for uid, grp in tx.groupby("UserID"):
        uid_str = str(uid)
        if uid_str in eval_users:
            all_courses = grp["CourseID"].astype(str).tolist()
            train_c = all_courses[:-1]
            test_c = [all_courses[-1]]
            test_dict[uid_str] = test_c
            # Add train portion
            train_sub = grp.iloc[:-1]
            train_tx_list.append(train_sub)
        else:
            train_tx_list.append(grp)

    train_tx = pd.concat(train_tx_list, ignore_index=True) if train_tx_list else pd.DataFrame()

    # Precompute global popularity baseline on training data
    top_global = train_tx["CourseID"].value_counts().index.astype(str).tolist()
    global_recs = [c for c in top_global if c in set(courses_df["CourseID"].astype(str))]

    # Build model on training data
    from src.feature_engineering import engineer_learner_features
    from src.recommender import CourseRecommender

    train_features = engineer_learner_features(users_df, courses_df, train_tx)
    recommender = CourseRecommender(courses_df, train_tx, train_features)

    # Metrics accumulators
    model_precisions, model_recalls, model_hits, model_mrrs = [], [], [], []
    base_precisions, base_recalls, base_hits, base_mrrs = [], [], [], []

    all_model_recommended = set()
    all_base_recommended = set()

    for uid in eval_users:
        test_ground_truth = set(test_dict.get(uid, []))
        if not test_ground_truth:
            continue

        # 1. Model recommendations
        recs = recommender.recommend(uid, n_recommendations=k_eval, exclude_enrolled=True)
        rec_ids = [r["CourseID"] for r in recs]
        all_model_recommended.update(rec_ids)

        hits_m = [1 if cid in test_ground_truth else 0 for cid in rec_ids]
        num_hits_m = sum(hits_m)
        prec_m = num_hits_m / k_eval
        rec_m = num_hits_m / len(test_ground_truth)
        hit_m = 1.0 if num_hits_m > 0 else 0.0

        mrr_m = 0.0
        for rank_idx, h in enumerate(hits_m, 1):
            if h == 1:
                mrr_m = 1.0 / rank_idx
                break

        model_precisions.append(prec_m)
        model_recalls.append(rec_m)
        model_hits.append(hit_m)
        model_mrrs.append(mrr_m)

        # 2. Popularity baseline recommendations (excluding enrolled in train)
        train_taken = set(train_tx[train_tx["UserID"].astype(str) == uid]["CourseID"].astype(str))
        base_recs = [c for c in global_recs if c not in train_taken][:k_eval]
        all_base_recommended.update(base_recs)

        hits_b = [1 if cid in test_ground_truth else 0 for cid in base_recs]
        num_hits_b = sum(hits_b)
        prec_b = num_hits_b / k_eval
        rec_b = num_hits_b / len(test_ground_truth)
        hit_b = 1.0 if num_hits_b > 0 else 0.0

        mrr_b = 0.0
        for rank_idx, h in enumerate(hits_b, 1):
            if h == 1:
                mrr_b = 1.0 / rank_idx
                break

        base_precisions.append(prec_b)
        base_recalls.append(rec_b)
        base_hits.append(hit_b)
        base_mrrs.append(mrr_b)

    total_catalog = courses_df["CourseID"].nunique()
    model_cov = round(len(all_model_recommended) / total_catalog * 100, 1) if total_catalog > 0 else 0.0
    base_cov = round(len(all_base_recommended) / total_catalog * 100, 1) if total_catalog > 0 else 0.0

    return {
        "k_eval": k_eval,
        "n_evaluated_learners": len(eval_users),
        "total_catalog_size": total_catalog,
        "model_metrics": {
            "Precision@K": round(float(np.mean(model_precisions)), 4),
            "Recall@K": round(float(np.mean(model_recalls)), 4),
            "HitRate@K": round(float(np.mean(model_hits)), 4),
            "MRR": round(float(np.mean(model_mrrs)), 4),
            "CatalogCoverage_Pct": model_cov
        },
        "baseline_metrics": {
            "Precision@K": round(float(np.mean(base_precisions)), 4),
            "Recall@K": round(float(np.mean(base_recalls)), 4),
            "HitRate@K": round(float(np.mean(base_hits)), 4),
            "MRR": round(float(np.mean(base_mrrs)), 4),
            "CatalogCoverage_Pct": base_cov
        },
        "lift": {
            "Precision_Lift": round(
                (float(np.mean(model_precisions)) - float(np.mean(base_precisions))) / (float(np.mean(base_precisions)) + 1e-6) * 100, 1
            ),
            "Coverage_Lift": round(model_cov - base_cov, 1)
        }
    }
