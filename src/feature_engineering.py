"""
Feature engineering module for EduPro learner analytics.
Aggregates transactional history into granular, learner-centric behavioral profiles.
Calculates engagement, specialization, category preference, and learning depth metrics.
"""

from typing import Dict, Tuple, List, Optional
import pandas as pd
import numpy as np

# Map difficulty strings to numeric scale for learning depth computation
LEVEL_MAP = {
    "beginner": 1.0,
    "intermediate": 2.0,
    "advanced": 3.0
}


def engineer_learner_features(
    users_df: pd.DataFrame,
    courses_df: pd.DataFrame,
    transactions_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms relational user, course, and transaction logs into a unified,
    learner-level feature matrix.
    """
    # 1. Base users table
    if users_df.empty or "UserID" not in users_df.columns:
        raise ValueError("Users DataFrame must contain 'UserID' column.")

    users = users_df.copy()
    
    # 2. If transactions are empty, return cold-start user records
    if transactions_df.empty or courses_df.empty:
        users["total_enrollments"] = 0
        users["distinct_categories"] = 0
        users["primary_category"] = "None"
        users["category_concentration"] = 0.0
        users["learning_depth_index"] = 1.0
        users["beginner_ratio"] = 0.0
        users["intermediate_ratio"] = 0.0
        users["advanced_ratio"] = 0.0
        users["paid_ratio"] = 0.0
        users["tenure_days"] = 0
        return users

    # 3. Merge transactions with course metadata
    merged_tx = transactions_df.merge(
        courses_df[["CourseID", "CourseCategory", "CourseType", "CourseLevel"]],
        on="CourseID",
        how="inner"
    )

    if merged_tx.empty:
        raise ValueError("No matching CourseID records between transactions and courses.")

    # 4. Standardize text values for consistency
    merged_tx["CourseCategory"] = merged_tx["CourseCategory"].astype(str).str.strip().str.title()
    merged_tx["CourseLevel"] = merged_tx["CourseLevel"].astype(str).str.strip().str.title()
    merged_tx["CourseType"] = merged_tx["CourseType"].astype(str).str.strip().str.title()
    merged_tx["LevelScore"] = merged_tx["CourseLevel"].str.lower().map(LEVEL_MAP).fillna(1.5)

    # 5. Group by UserID
    records = []
    grouped = merged_tx.groupby("UserID")

    for uid, group in grouped:
        total_enr = len(group)
        distinct_courses = group["CourseID"].nunique()
        distinct_cats = group["CourseCategory"].nunique()

        # Category distribution & concentration
        cat_counts = group["CourseCategory"].value_counts()
        primary_cat = cat_counts.index[0] if not cat_counts.empty else "General"
        primary_cat_count = cat_counts.iloc[0] if not cat_counts.empty else 0
        cat_concentration = round(primary_cat_count / total_enr, 3)

        # Level distribution
        level_counts = group["CourseLevel"].value_counts()
        beg_ratio = round(level_counts.get("Beginner", 0) / total_enr, 3)
        int_ratio = round(level_counts.get("Intermediate", 0) / total_enr, 3)
        adv_ratio = round(level_counts.get("Advanced", 0) / total_enr, 3)
        depth_index = round(group["LevelScore"].mean(), 2)

        # Type distribution (Paid vs Free or Self-Paced)
        type_counts = group["CourseType"].value_counts()
        paid_ratio = round(type_counts.get("Paid", 0) / total_enr, 3)

        # Temporal tenure
        if "TransactionDate" in group.columns and pd.api.types.is_datetime64_any_dtype(group["TransactionDate"]):
            dates = group["TransactionDate"].dropna()
            if not dates.empty:
                tenure = (dates.max() - dates.min()).days
                first_date = dates.min()
                last_date = dates.max()
            else:
                tenure, first_date, last_date = 0, None, None
        else:
            tenure, first_date, last_date = 0, None, None

        records.append({
            "UserID": str(uid),
            "total_enrollments": total_enr,
            "distinct_courses": distinct_courses,
            "distinct_categories": distinct_cats,
            "primary_category": primary_cat,
            "category_concentration": cat_concentration,
            "learning_depth_index": depth_index,
            "beginner_ratio": beg_ratio,
            "intermediate_ratio": int_ratio,
            "advanced_ratio": adv_ratio,
            "paid_ratio": paid_ratio,
            "tenure_days": tenure,
            "first_enrollment": first_date,
            "last_enrollment": last_date
        })

    agg_df = pd.DataFrame(records)

    # 6. Merge with base users table
    learner_features = users.merge(agg_df, on="UserID", how="left")

    # 7. Fill non-enrolled (cold-start) users with realistic defaults
    learner_features["total_enrollments"] = learner_features["total_enrollments"].fillna(0).astype(int)
    learner_features["distinct_courses"] = learner_features["distinct_courses"].fillna(0).astype(int)
    learner_features["distinct_categories"] = learner_features["distinct_categories"].fillna(0).astype(int)
    learner_features["primary_category"] = learner_features["primary_category"].fillna("Undeclared")
    learner_features["category_concentration"] = learner_features["category_concentration"].fillna(0.0)
    learner_features["learning_depth_index"] = learner_features["learning_depth_index"].fillna(1.0)
    learner_features["beginner_ratio"] = learner_features["beginner_ratio"].fillna(1.0)
    learner_features["intermediate_ratio"] = learner_features["intermediate_ratio"].fillna(0.0)
    learner_features["advanced_ratio"] = learner_features["advanced_ratio"].fillna(0.0)
    learner_features["paid_ratio"] = learner_features["paid_ratio"].fillna(0.0)
    learner_features["tenure_days"] = learner_features["tenure_days"].fillna(0).astype(int)

    return learner_features


def get_clustering_feature_matrix(
    features_df: pd.DataFrame,
    include_tenure: bool = True
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Extracts purely behavioral numeric features for K-Means clustering.
    Avoids demographic bias (excludes Age, Gender, UserID) to satisfy ethical AI requirements.
    """
    feature_cols = [
        "total_enrollments",
        "distinct_categories",
        "category_concentration",
        "learning_depth_index",
        "beginner_ratio",
        "advanced_ratio"
    ]
    if include_tenure and "tenure_days" in features_df.columns:
        feature_cols.append("tenure_days")

    # Filter to enrolled learners (total_enrollments > 0)
    enrolled_mask = features_df["total_enrollments"] > 0
    sub_df = features_df.loc[enrolled_mask, feature_cols].copy()

    # Fill any remaining NaNs
    sub_df = sub_df.fillna(sub_df.median())

    return sub_df, feature_cols
