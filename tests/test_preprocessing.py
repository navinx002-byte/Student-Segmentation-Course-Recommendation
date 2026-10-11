"""
Unit tests for data loading, schema normalization, and preprocessing.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_loader import EduProDataLoader, normalize_columns, USER_ALIASES, COURSE_ALIASES, TRANSACTION_ALIASES


def test_normalize_columns():
    df = pd.DataFrame({
        "user_id": ["U1", "U2"],
        "user_name": ["Alice", "Bob"],
        "user_age": [22, 28]
    })
    norm_df = normalize_columns(df, USER_ALIASES)
    assert "UserID" in norm_df.columns
    assert "UserName" in norm_df.columns
    assert "Age" in norm_df.columns


def test_data_loader_csv_and_integrity(tmp_path):
    # Create sample CSVs with an orphan transaction
    users_csv = tmp_path / "users.csv"
    courses_csv = tmp_path / "courses.csv"
    trans_csv = tmp_path / "trans.csv"

    pd.DataFrame({
        "UserID": ["U1", "U2"],
        "UserName": ["Alice", "Bob"],
        "Age": [22, 30],
        "Gender": ["Female", "Male"]
    }).to_csv(users_csv, index=False)

    pd.DataFrame({
        "CourseID": ["C1", "C2"],
        "CourseName": ["Python 101", "Data Viz"],
        "CourseCategory": ["Technology", "Business"],
        "CourseType": ["Paid", "Free"],
        "CourseLevel": ["Beginner", "Intermediate"]
    }).to_csv(courses_csv, index=False)

    pd.DataFrame({
        "TransactionID": ["T1", "T2", "T3"],
        "UserID": ["U1", "U2", "U999"],  # U999 is orphan
        "CourseID": ["C1", "C2", "C1"],
        "TransactionDate": ["2024-01-01", "2024-01-02", "2024-01-03"]
    }).to_csv(trans_csv, index=False)

    loader = EduProDataLoader()
    u_df, c_df, t_df = loader.load_from_csv_files(users_csv, courses_csv, trans_csv)

    assert len(u_df) == 2
    assert len(c_df) == 2
    # Orphan record U999 must be sanitized
    assert len(t_df) == 2
    assert "U999" not in t_df["UserID"].values
    assert loader.validation_report["orphan_user_transactions_removed"] == 1


def test_missing_and_malformed_values():
    u_df = pd.DataFrame({
        "UserID": ["U1", "U2", "U3"],
        "Age": ["25", "invalid", None]
    })
    norm = normalize_columns(u_df, USER_ALIASES)
    norm["Age"] = pd.to_numeric(norm["Age"], errors="coerce").fillna(25).astype(int)
    assert norm["Age"].tolist() == [25, 25, 25]
