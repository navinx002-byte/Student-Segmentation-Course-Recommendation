"""
Unit tests for personalized course recommender.
"""

import pytest
import pandas as pd
from src.recommender import CourseRecommender


@pytest.fixture
def sample_rec_data():
    courses_df = pd.DataFrame({
        "CourseID": ["C1", "C2", "C3", "C4", "C5", "C6"],
        "CourseName": ["Python 101", "Advanced PyTorch", "Financial Accounting", "Corporate Strategy", "Quantum Physics", "Astronomy"],
        "CourseCategory": ["Technology", "Technology", "Business", "Business", "Science", "Science"],
        "CourseType": ["Paid", "Paid", "Free", "Paid", "Paid", "Free"],
        "CourseLevel": ["Beginner", "Advanced", "Beginner", "Intermediate", "Advanced", "Beginner"]
    })

    transactions_df = pd.DataFrame({
        "TransactionID": ["T1", "T2", "T3", "T4", "T5"],
        "UserID": ["U1", "U1", "U2", "U2", "U2"],
        "CourseID": ["C1", "C2", "C3", "C4", "C5"],
        "TransactionDate": ["2024-01-01", "2024-01-05", "2024-01-02", "2024-01-08", "2024-01-15"]
    })

    features_df = pd.DataFrame({
        "UserID": ["U1", "U2", "U3"],
        "UserName": ["Alice", "Bob", "NewUser"],
        "total_enrollments": [2, 3, 0],
        "primary_category": ["Technology", "Business", "Undeclared"],
        "learning_depth_index": [2.0, 1.67, 1.0],
        "Cluster": [0, 1, -1],
        "PersonaName": ["Tech Specialist", "Business Explorer", "New Learner"]
    })

    return courses_df, transactions_df, features_df


def test_recommender_basic_and_exclusion(sample_rec_data):
    courses_df, transactions_df, features_df = sample_rec_data
    rec_engine = CourseRecommender(courses_df, transactions_df, features_df)

    # U1 took C1 and C2. Recommendations should exclude C1 and C2.
    recs = rec_engine.recommend(user_id="U1", n_recommendations=5, exclude_enrolled=True)
    assert len(recs) > 0
    assert len(recs) <= 5
    rec_ids = [r["CourseID"] for r in recs]
    assert "C1" not in rec_ids
    assert "C2" not in rec_ids
    assert all("Explanation" in r and r["Explanation"] != "" for r in recs)


def test_recommender_cold_start(sample_rec_data):
    courses_df, transactions_df, features_df = sample_rec_data
    rec_engine = CourseRecommender(courses_df, transactions_df, features_df)

    # U3 has 0 prior enrollments
    recs = rec_engine.recommend(user_id="U3", n_recommendations=3)
    assert len(recs) == 3
    assert all(r["IsColdStart"] is True for r in recs)
    assert "Cold-Start" in recs[0]["Explanation"] or "baseline" in recs[0]["Explanation"]


def test_recommender_category_and_level_filter(sample_rec_data):
    courses_df, transactions_df, features_df = sample_rec_data
    rec_engine = CourseRecommender(courses_df, transactions_df, features_df)

    recs = rec_engine.recommend(
        user_id="U1",
        n_recommendations=5,
        filter_category="Business",
        filter_level="Beginner",
        exclude_enrolled=False
    )
    for r in recs:
        assert r["CourseCategory"] == "Business"
        assert r["CourseLevel"] == "Beginner"
