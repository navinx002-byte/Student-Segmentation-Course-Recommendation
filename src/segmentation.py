"""
Student segmentation module using K-Means clustering.
Implements scaling, cluster count evaluation (Elbow & Silhouette),
automated cluster profiling, PCA 2D projections, and model persistence.
Leverages robust machine learning utilities to guarantee cross-platform execution.
"""

from typing import Dict, Tuple, List, Optional, Any
import numpy as np
import pandas as pd
import joblib

from src.ml_utils import (
    RobustScaler,
    RobustKMeans,
    RobustPCA,
    robust_silhouette_score,
    robust_calinski_harabasz_score,
    robust_davies_bouldin_score
)


def evaluate_cluster_range(
    X_scaled: np.ndarray,
    min_k: int = 2,
    max_k: int = 8,
    random_state: int = 42
) -> List[Dict[str, Any]]:
    """
    Computes Inertia and Silhouette scores across a range of K values.
    Handles small datasets gracefully.
    """
    n_samples = X_scaled.shape[0]
    results = []
    
    # Cap max_k if dataset has fewer samples
    effective_max_k = min(max_k, max(2, n_samples - 1))
    
    for k in range(min_k, effective_max_k + 1):
        if k >= n_samples:
            break
        km = RobustKMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X_scaled)
        
        unique_labels = len(np.unique(labels))
        if unique_labels > 1 and unique_labels < n_samples:
            sil = robust_silhouette_score(X_scaled, labels)
            ch = robust_calinski_harabasz_score(X_scaled, labels)
            db = robust_davies_bouldin_score(X_scaled, labels)
        else:
            sil, ch, db = 0.0, 0.0, 0.0

        results.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": round(sil, 4),
            "calinski_harabasz": round(ch, 2),
            "davies_bouldin": round(db, 3)
        })
    return results


def generate_cluster_persona(profile: Dict[str, float]) -> Tuple[str, str]:
    """
    Derives an interpretable persona name and narrative description
    from relative feature averages in a cluster profile.
    """
    depth = profile.get("learning_depth_index", 1.5)
    conc = profile.get("category_concentration", 0.5)
    enr = profile.get("total_enrollments", 3.0)
    adv = profile.get("advanced_ratio", 0.1)
    beg = profile.get("beginner_ratio", 0.5)
    cats = profile.get("distinct_categories", 2.0)

    # Heuristic rules based on observed profile features
    if adv >= 0.35 or depth >= 2.3:
        name = "Advanced Mastery Seekers"
        desc = "Learners targeting rigorous advanced courses and deepening expertise with high completion rigor."
    elif conc >= 0.70:
        name = "Focused Domain Specialists"
        desc = "Learners with high concentration in a single discipline, seeking concentrated domain competence."
    elif cats >= 3.0 and conc < 0.50:
        name = "Exploratory Career Builders"
        desc = "Curious learners exploring multiple subject domains to cross-skill and discover new interests."
    elif beg >= 0.65 or depth <= 1.3:
        name = "Foundational Beginners"
        desc = "Entry-level learners primarily engaging with foundational courses and building core fundamentals."
    elif enr >= 5.0:
        name = "High-Cadence Lifelong Learners"
        desc = "Highly active and frequent learners with elevated enrollment volume across various topics."
    else:
        name = "Balanced Core Learners"
        desc = "Mainstream learners maintaining steady engagement across intermediate and introductory subjects."

    return name, desc


class StudentSegmenter:
    """End-to-end clustering pipeline for student segmentation."""

    def __init__(self, k_clusters: int = 4, random_state: int = 42):
        self.k_clusters = k_clusters
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.kmeans: Optional[RobustKMeans] = None
        self.pca: Optional[RobustPCA] = None
        self.feature_names: List[str] = []
        self.cluster_profiles: Dict[int, Dict[str, Any]] = {}
        self.metrics: Dict[str, Any] = {}

    def fit_predict(
        self,
        features_df: pd.DataFrame,
        feature_cols: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fits scaler, KMeans, PCA, and generates cluster assignments & 2D coordinates.
        """
        self.feature_names = feature_cols
        X = features_df[feature_cols].values
        
        # 1. Scale
        X_scaled = self.scaler.fit_transform(X)

        # 2. Fit KMeans
        self.kmeans = RobustKMeans(
            n_clusters=self.k_clusters,
            random_state=self.random_state,
            n_init=10
        )
        labels = self.kmeans.fit_predict(X_scaled)

        # 3. Fit PCA for 2D visualization
        self.pca = RobustPCA(n_components=2, random_state=self.random_state)
        pca_coords = self.pca.fit_transform(X_scaled)

        # 4. Compute metrics
        n_samples = len(X_scaled)
        if len(np.unique(labels)) > 1 and n_samples > self.k_clusters:
            sil = robust_silhouette_score(X_scaled, labels)
            ch = robust_calinski_harabasz_score(X_scaled, labels)
            db = robust_davies_bouldin_score(X_scaled, labels)
        else:
            sil, ch, db = 0.0, 0.0, 0.0

        self.metrics = {
            "k_clusters": self.k_clusters,
            "silhouette_score": round(sil, 4),
            "calinski_harabasz_score": round(ch, 2),
            "davies_bouldin_index": round(db, 3),
            "inertia": round(float(self.kmeans.inertia_), 2),
            "pca_explained_variance_ratio": [round(float(v), 4) for v in self.pca.explained_variance_ratio_]
        }

        # 5. Build cluster profiles & assign persona names
        temp_df = features_df.copy()
        temp_df["Cluster"] = labels
        self.cluster_profiles = {}

        for c_id in range(self.k_clusters):
            c_mask = (temp_df["Cluster"] == c_id)
            c_data = temp_df[c_mask]
            count = len(c_data)
            pct = round((count / n_samples) * 100, 1) if n_samples > 0 else 0.0

            mean_vals = {col: round(float(c_data[col].mean()), 2) for col in feature_cols} if not c_data.empty else {}
            persona_name, persona_desc = generate_cluster_persona(mean_vals)

            self.cluster_profiles[c_id] = {
                "cluster_id": c_id,
                "persona_name": persona_name,
                "description": persona_desc,
                "count": count,
                "percentage": pct,
                "means": mean_vals
            }

        return labels, pca_coords

    def get_cluster_name(self, cluster_id: int) -> str:
        """Returns the persona name for a given cluster ID."""
        if cluster_id in self.cluster_profiles:
            return self.cluster_profiles[cluster_id]["persona_name"]
        return f"Cluster {cluster_id}"

    def save(self, filepath: str):
        """Saves fitted model objects to disk."""
        payload = {
            "scaler": self.scaler,
            "kmeans": self.kmeans,
            "pca": self.pca,
            "feature_names": self.feature_names,
            "cluster_profiles": self.cluster_profiles,
            "metrics": self.metrics,
            "k_clusters": self.k_clusters
        }
        joblib.dump(payload, filepath)

    @classmethod
    def load(cls, filepath: str) -> "StudentSegmenter":
        """Loads fitted segmenter pipeline from disk."""
        payload = joblib.load(filepath)
        instance = cls(k_clusters=payload["k_clusters"])
        instance.scaler = payload["scaler"]
        instance.kmeans = payload["kmeans"]
        instance.pca = payload["pca"]
        instance.feature_names = payload["feature_names"]
        instance.cluster_profiles = payload["cluster_profiles"]
        instance.metrics = payload["metrics"]
        return instance
