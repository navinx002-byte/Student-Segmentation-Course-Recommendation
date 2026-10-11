"""
Unit tests for offline evaluation module.
"""

import pytest
import pandas as pd
from src.evaluation import evaluate_recommendations_offline


def test_evaluate_recommendations_offline():
    users_df = pd.DataFrame({
        "UserID": [f"U{i}" for i in range(1, 10)],
        "UserName": [f"User {i}" for i in range(1, 10)],
        "Age": [20 + i for i in range(1, 10)],
        "Gender": ["Female" if i % 2 == 0 else "Male" for i in range(1, 10)]
    })

    courses_df = pd.DataFrame({
        "CourseID": [f"C{j}" for j in range(1, 11)],
        "CourseName": [f"Course {j}" for j in range(1, 11)],
        "CourseCategory": ["Technology" if j <= 5 else "Business" for j in range(1, 11)],
        "CourseType": ["Paid" if j % 2 == 0 else "Free" for j in range(1, 11)],
        "CourseLevel": ["Beginner" if j <= 3 else "Intermediate" if j <= 7 else "Advanced" for j in range(1, 11)]
    })

    # Generate transactions where users have >= 3 interactions
    records = []
    tid = 1
    for u in [f"U{i}" for i in range(1, 6)]:
        for c in ["C1", "C2", "C3", "C4"]:
            records.append({
                "TransactionID": f"T{tid}",
                "UserID": u,
                "CourseID": c,
                "TransactionDate": f"2024-01-0{tid % 25 + 1}"
            })
            tid += 1

    tx_df = pd.DataFrame(records)

    eval_res = evaluate_recommendations_offline(
        users_df, courses_df, tx_df, k_eval=3, min_interactions=3, sample_size=5
    )

    assert "model_metrics" in eval_res
    assert "baseline_metrics" in eval_res
    assert "Precision@K" in eval_res["model_metrics"]
    assert "Recall@K" in eval_res["model_metrics"]
    assert "CatalogCoverage_Pct" in eval_res["model_metrics"]
