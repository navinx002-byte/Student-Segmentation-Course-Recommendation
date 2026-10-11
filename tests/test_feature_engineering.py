"""
Unit tests for feature engineering module.
"""

import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import engineer_learner_features, get_clustering_feature_matrix


def test_engineer_learner_features_basic():
    users_df = pd.DataFrame({
        "UserID": ["U1", "U2", "U3"],
        "UserName": ["Alice", "Bob", "Charlie"],
        "Age": [22, 28, 35],
        "Gender": ["Female", "Male", "Male"]
    })

    courses_df = pd.DataFrame({
        "CourseID": ["C1", "C2", "C3"],
        "CourseCategory": ["Technology", "Technology", "Business"],
        "CourseType": ["Paid", "Free", "Paid"],
        "CourseLevel": ["Beginner", "Intermediate", "Advanced"]
    })

    transactions_df = pd.DataFrame({
        "TransactionID": ["T1", "T2", "T3", "T4"],
        "UserID": ["U1", "U1", "U2", "U2"],
        "CourseID": ["C1", "C2", "C3", "C3"],
        "TransactionDate": ["2024-01-01", "2024-01-15", "2024-02-01", "2024-02-10"]
    })

    feat_df = engineer_learner_features(users_df, courses_df, transactions_df)

    assert len(feat_df) == 3
    # U1 took C1 (Beg, Tech) and C2 (Int, Tech) -> total 2, primary Tech, concentration 1.0, depth 1.5
    u1 = feat_df[feat_df["UserID"] == "U1"].iloc[0]
    assert u1["total_enrollments"] == 2
    assert u1["primary_category"] == "Technology"
    assert u1["category_concentration"] == 1.0
    assert u1["learning_depth_index"] == 1.5

    # U3 is a cold-start user (0 transactions)
    u3 = feat_df[feat_df["UserID"] == "U3"].iloc[0]
    assert u3["total_enrollments"] == 0
    assert u3["primary_category"] == "Undeclared"


def test_get_clustering_feature_matrix():
    feat_df = pd.DataFrame({
        "UserID": ["U1", "U2", "U3"],
        "total_enrollments": [3, 4, 0],
        "distinct_categories": [2, 1, 0],
        "category_concentration": [0.67, 1.0, 0.0],
        "learning_depth_index": [2.0, 1.0, 1.0],
        "beginner_ratio": [0.33, 1.0, 1.0],
        "advanced_ratio": [0.33, 0.0, 0.0],
        "tenure_days": [30, 10, 0]
    })

    sub_df, cols = get_clustering_feature_matrix(feat_df)
    # Only enrolled users (U1, U2) should be included in clustering matrix
    assert len(sub_df) == 2
    assert "total_enrollments" in cols
    assert "category_concentration" in cols
    assert "UserID" not in cols  # Demographics/IDs excluded
