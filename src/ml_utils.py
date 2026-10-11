"""
Machine learning utilities providing high-performance, robust clustering,
scaling, PCA dimensionality reduction, and cluster quality scoring.
Includes transparent pure-NumPy fallbacks to guarantee 100% environment compatibility
across restricted enterprise platforms, Windows WDAC policies, and cloud containers.
"""

from typing import Tuple, List, Optional
import numpy as np


class RobustScaler:
    """Standardizes features by removing mean and scaling to unit variance."""
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X):
        X_arr = np.asarray(X, dtype=float)
        self.mean_ = np.mean(X_arr, axis=0)
        self.scale_ = np.std(X_arr, axis=0)
        self.scale_ = np.where(self.scale_ == 0.0, 1.0, self.scale_)
        return self

    def transform(self, X):
        X_arr = np.asarray(X, dtype=float)
        return (X_arr - self.mean_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class RobustKMeans:
    """K-Means clustering with k-means++ initialization and Lloyd's iterative optimization."""
    def __init__(self, n_clusters: int = 4, random_state: int = 42, max_iter: int = 300, n_init: int = 10):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.max_iter = max_iter
        self.n_init = n_init
        self.cluster_centers_ = None
        self.labels_ = None
        self.inertia_ = None

    def _init_kmeans_pp(self, X: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
        n_samples = X.shape[0]
        centers = [X[rng.choice(n_samples)]]
        for _ in range(1, self.n_clusters):
            dists = np.min([np.sum((X - c) ** 2, axis=1) for c in centers], axis=0)
            probs = dists / (np.sum(dists) + 1e-10)
            next_center = X[rng.choice(n_samples, p=probs)]
            centers.append(next_center)
        return np.array(centers)

    def fit(self, X):
        X_arr = np.asarray(X, dtype=float)
        n_samples = X_arr.shape[0]
        rng = np.random.RandomState(self.random_state)

        # Cap clusters if samples < clusters
        effective_k = min(self.n_clusters, max(1, n_samples))
        if effective_k != self.n_clusters:
            self.n_clusters = effective_k

        best_inertia = float("inf")
        best_centers = None
        best_labels = None

        for _ in range(self.n_init):
            centers = self._init_kmeans_pp(X_arr, rng)
            for _ in range(self.max_iter):
                dists = np.linalg.norm(X_arr[:, np.newaxis, :] - centers[np.newaxis, :, :], axis=2)
                labels = np.argmin(dists, axis=1)

                new_centers = np.array([
                    X_arr[labels == k].mean(axis=0) if np.any(labels == k) else centers[k]
                    for k in range(self.n_clusters)
                ])
                if np.allclose(centers, new_centers, atol=1e-4):
                    break
                centers = new_centers

            min_dists_sq = np.min(np.sum((X_arr[:, np.newaxis, :] - centers[np.newaxis, :, :]) ** 2, axis=2), axis=1)
            inertia = np.sum(min_dists_sq)
            if inertia < best_inertia:
                best_inertia = inertia
                best_centers = centers
                best_labels = labels

        self.cluster_centers_ = best_centers
        self.labels_ = best_labels
        self.inertia_ = best_inertia
        return self

    def fit_predict(self, X):
        self.fit(X)
        return self.labels_

    def predict(self, X):
        X_arr = np.asarray(X, dtype=float)
        dists = np.linalg.norm(X_arr[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :], axis=2)
        return np.argmin(dists, axis=1)


class RobustPCA:
    """Principal Component Analysis using eigenvalue decomposition."""
    def __init__(self, n_components: int = 2, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self.components_ = None
        self.explained_variance_ratio_ = None
        self.mean_ = None

    def fit(self, X):
        X_arr = np.asarray(X, dtype=float)
        self.mean_ = np.mean(X_arr, axis=0)
        X_centered = X_arr - self.mean_

        cov = np.cov(X_centered, rowvar=False)
        # Handle 1D feature case
        if cov.ndim == 0:
            cov = np.array([[float(cov)]])
        
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        actual_k = min(self.n_components, eigenvectors.shape[1])
        self.components_ = eigenvectors[:, :actual_k].T

        total_var = np.sum(np.maximum(eigenvalues, 0))
        if total_var > 0:
            self.explained_variance_ratio_ = np.maximum(eigenvalues[:actual_k], 0) / total_var
        else:
            self.explained_variance_ratio_ = np.full(actual_k, 1.0 / actual_k)
        return self

    def transform(self, X):
        X_arr = np.asarray(X, dtype=float)
        X_centered = X_arr - self.mean_
        return X_centered @ self.components_.T

    def fit_transform(self, X):
        return self.fit(X).transform(X)


def robust_silhouette_score(X, labels) -> float:
    """Computes the mean Silhouette Coefficient across samples."""
    X_arr = np.asarray(X, dtype=float)
    labels_arr = np.asarray(labels)
    unique_labels = np.unique(labels_arr)
    n = len(X_arr)

    if len(unique_labels) < 2 or len(unique_labels) >= n:
        return 0.0

    # Subsample if n > 1500 for rapid computation
    if n > 1500:
        rng = np.random.RandomState(42)
        sub_idx = rng.choice(n, size=1500, replace=False)
        X_arr = X_arr[sub_idx]
        labels_arr = labels_arr[sub_idx]
        unique_labels = np.unique(labels_arr)
        n = len(X_arr)

    dist_matrix = np.linalg.norm(X_arr[:, np.newaxis, :] - X_arr[np.newaxis, :, :], axis=2)

    a = np.zeros(n)
    b = np.full(n, np.inf)

    for c in unique_labels:
        mask = (labels_arr == c)
        count = np.sum(mask)
        if count > 1:
            a[mask] = np.sum(dist_matrix[mask][:, mask], axis=1) / (count - 1)
        else:
            a[mask] = 0.0

        for oc in unique_labels:
            if oc == c:
                continue
            other_mask = (labels_arr == oc)
            if np.any(other_mask):
                dist_to_oc = np.mean(dist_matrix[mask][:, other_mask], axis=1)
                b[mask] = np.minimum(b[mask], dist_to_oc)

    denom = np.maximum(a, b)
    s = np.where(denom == 0, 0, (b - a) / denom)
    return float(np.mean(s))


def robust_calinski_harabasz_score(X, labels) -> float:
    """Computes Calinski-Harabasz score (Variance Ratio Criterion)."""
    X_arr = np.asarray(X, dtype=float)
    labels_arr = np.asarray(labels)
    n_samples, n_features = X_arr.shape
    unique_labels = np.unique(labels_arr)
    n_labels = len(unique_labels)

    if n_labels < 2 or n_labels >= n_samples:
        return 0.0

    overall_mean = np.mean(X_arr, axis=0)
    extra_disp = 0.0
    intra_disp = 0.0

    for k in unique_labels:
        cluster_k = X_arr[labels_arr == k]
        mean_k = np.mean(cluster_k, axis=0)
        extra_disp += len(cluster_k) * np.sum((mean_k - overall_mean) ** 2)
        intra_disp += np.sum((cluster_k - mean_k) ** 2)

    if intra_disp == 0.0:
        return 1.0

    return float((extra_disp / (n_labels - 1)) / (intra_disp / (n_samples - n_labels)))


def robust_davies_bouldin_score(X, labels) -> float:
    """Computes Davies-Bouldin index (ratio of within-cluster to between-cluster distances)."""
    X_arr = np.asarray(X, dtype=float)
    labels_arr = np.asarray(labels)
    unique_labels = np.unique(labels_arr)
    n_labels = len(unique_labels)

    if n_labels < 2:
        return 0.0

    centroids = [np.mean(X_arr[labels_arr == k], axis=0) for k in unique_labels]
    dispersions = [
        np.mean(np.linalg.norm(X_arr[labels_arr == k] - centroids[idx], axis=1))
        for idx, k in enumerate(unique_labels)
    ]

    r_values = []
    for i in range(n_labels):
        r_i = []
        for j in range(n_labels):
            if i != j:
                centroid_dist = np.linalg.norm(centroids[i] - centroids[j])
                if centroid_dist > 0:
                    r_i.append((dispersions[i] + dispersions[j]) / centroid_dist)
        if r_i:
            r_values.append(max(r_i))

    return float(np.mean(r_values)) if r_values else 0.0
