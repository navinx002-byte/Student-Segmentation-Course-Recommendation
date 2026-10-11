"""
Unit tests for student segmentation and clustering pipeline.
"""

import pytest
import numpy as np
import pandas as pd
from src.segmentation import StudentSegmenter, evaluate_cluster_range, generate_cluster_persona


def test_evaluate_cluster_range():
    np.random.seed(42)
    X = np.random.randn(50, 4)
    results = evaluate_cluster_range(X, min_k=2, max_k=4)
    assert len(results) == 3
    assert all("k" in r and "silhouette" in r and "inertia" in r for r in results)


def test_student_segmenter_fit_predict():
    np.random.seed(42)
    df = pd.DataFrame({
        "total_enrollments": [1, 2, 8, 10, 1, 2, 7, 9],
        "distinct_categories": [1, 1, 4, 5, 1, 1, 3, 4],
        "category_concentration": [1.0, 0.9, 0.3, 0.25, 1.0, 0.8, 0.4, 0.3],
        "learning_depth_index": [1.0, 1.2, 2.5, 2.8, 1.1, 1.0, 2.6, 2.9],
        "beginner_ratio": [1.0, 0.8, 0.1, 0.0, 0.9, 1.0, 0.1, 0.0],
        "advanced_ratio": [0.0, 0.0, 0.5, 0.7, 0.0, 0.0, 0.6, 0.8],
        "tenure_days": [0, 10, 120, 150, 5, 15, 100, 140]
    })
    feature_cols = list(df.columns)

    segmenter = StudentSegmenter(k_clusters=2, random_state=42)
    labels, pca_coords = segmenter.fit_predict(df, feature_cols)

    assert len(labels) == 8
    assert len(np.unique(labels)) == 2
    assert pca_coords.shape == (8, 2)
    assert segmenter.metrics["silhouette_score"] > 0


def test_persona_generation():
    advanced_profile = {"learning_depth_index": 2.6, "advanced_ratio": 0.5, "category_concentration": 0.4}
    name, desc = generate_cluster_persona(advanced_profile)
    assert name == "Advanced Mastery Seekers"

    specialist_profile = {"learning_depth_index": 1.5, "advanced_ratio": 0.1, "category_concentration": 0.85}
    name, desc = generate_cluster_persona(specialist_profile)
    assert name == "Focused Domain Specialists"


def test_segmenter_save_and_load(tmp_path):
    df = pd.DataFrame({
        "feat1": [1.0, 2.0, 5.0, 6.0],
        "feat2": [2.0, 1.0, 7.0, 8.0]
    })
    model_path = str(tmp_path / "test_model.joblib")
    seg = StudentSegmenter(k_clusters=2, random_state=42)
    labels, _ = seg.fit_predict(df, ["feat1", "feat2"])
    seg.save(model_path)

    loaded_seg = StudentSegmenter.load(model_path)
    assert loaded_seg.k_clusters == 2
    assert loaded_seg.feature_names == ["feat1", "feat2"]
