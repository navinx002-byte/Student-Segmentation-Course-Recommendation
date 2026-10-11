"""
Personalized Course Recommendation Engine for EduPro.
Combines content-based category affinity, difficulty-level suitability,
peer segment popularity, and global platform trends with transparent explanations.
"""

from typing import Dict, List, Optional, Any, Set
import numpy as np
import pandas as pd


class CourseRecommender:
    """
    Multi-signal hybrid recommendation engine.
    Supports cold-start, historical exclusion, configurable weights, and explainability.
    """

    def __init__(
        self,
        courses_df: pd.DataFrame,
        transactions_df: pd.DataFrame,
        learner_features_df: pd.DataFrame,
        weights: Optional[Dict[str, float]] = None
    ):
        self.courses_df = courses_df.copy()
        self.transactions_df = transactions_df.copy()
        self.learner_features_df = learner_features_df.copy()
        
        # Default weights
        self.weights = weights or {
            "category_pref": 0.35,
            "level_suitability": 0.25,
            "cluster_popularity": 0.25,
            "global_popularity": 0.15
        }

        # Normalize weights to sum to 1.0
        total_w = sum(self.weights.values())
        if total_w > 0:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

        # Precompute lookup tables
        self._precompute_global_popularity()
        self._precompute_cluster_popularity()
        self._precompute_user_histories()

    def _precompute_global_popularity(self):
        """Calculates global enrollment frequency per course."""
        if self.transactions_df.empty:
            self.global_pop_scores = {cid: 0.5 for cid in self.courses_df["CourseID"]}
            return

        counts = self.transactions_df["CourseID"].value_counts()
        max_c = counts.max() if not counts.empty and counts.max() > 0 else 1
        self.global_pop_scores = (counts / max_c).to_dict()

    def _precompute_cluster_popularity(self):
        """Calculates course enrollment popularity conditioned on cluster segment."""
        self.cluster_pop_scores: Dict[int, Dict[str, float]] = {}
        
        if "Cluster" not in self.learner_features_df.columns or self.transactions_df.empty:
            return

        user_cluster_map = dict(zip(
            self.learner_features_df["UserID"].astype(str),
            self.learner_features_df["Cluster"]
        ))

        tx = self.transactions_df.copy()
        tx["UserID_str"] = tx["UserID"].astype(str)
        tx["Cluster"] = tx["UserID_str"].map(user_cluster_map)
        valid_tx = tx.dropna(subset=["Cluster"])

        for cluster_id, grp in valid_tx.groupby("Cluster"):
            counts = grp["CourseID"].value_counts()
            max_c = counts.max() if not counts.empty and counts.max() > 0 else 1
            self.cluster_pop_scores[int(cluster_id)] = (counts / max_c).to_dict()

    def _precompute_user_histories(self):
        """Builds fast lookup set of courses already taken by each student."""
        self.user_history_map: Dict[str, Set[str]] = {}
        if self.transactions_df.empty:
            return

        for uid, grp in self.transactions_df.groupby("UserID"):
            self.user_history_map[str(uid)] = set(grp["CourseID"].astype(str))

    def _calculate_level_suitability(self, course_level: str, depth_index: float) -> float:
        """
        Computes compatibility score [0.0 - 1.0] between course level
        and student's historical learning depth index (1.0 to 3.0).
        """
        norm_level = str(course_level).strip().lower()
        if norm_level == "beginner":
            c_score = 1.0
        elif norm_level == "intermediate":
            c_score = 2.0
        elif norm_level == "advanced":
            c_score = 3.0
        else:
            c_score = 1.5

        # Distance penalty
        diff = abs(c_score - depth_index)
        # diff is at most 2.0. Map diff 0 -> 1.0, diff 1 -> 0.65, diff 2 -> 0.25
        if diff <= 0.3:
            return 1.0
        elif diff <= 0.8:
            return 0.85
        elif diff <= 1.3:
            return 0.60
        else:
            return 0.25

    def recommend(
        self,
        user_id: str,
        n_recommendations: int = 5,
        exclude_enrolled: bool = True,
        filter_category: Optional[str] = None,
        filter_level: Optional[str] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates ranked recommendations for a given learner.
        """
        user_id_str = str(user_id).strip()
        weights = custom_weights or self.weights
        total_w = sum(weights.values())
        if total_w > 0:
            weights = {k: v / total_w for k, v in weights.items()}

        # 1. Identify learner profile
        user_rows = self.learner_features_df[self.learner_features_df["UserID"].astype(str) == user_id_str]
        is_cold_start = bool(user_rows.empty or (user_rows.iloc[0]["total_enrollments"] == 0))

        if not user_rows.empty:
            user_prof = user_rows.iloc[0]
            primary_cat = user_prof.get("primary_category", "Technology")
            depth_index = float(user_prof.get("learning_depth_index", 1.5))
            cluster_id = int(user_prof.get("Cluster", -1)) if "Cluster" in user_prof and pd.notna(user_prof.get("Cluster")) else -1
            cluster_name = str(user_prof.get("PersonaName", f"Cluster {cluster_id}"))
        else:
            # Cold-start fallback
            primary_cat = "Technology"
            depth_index = 1.2  # Default to beginner-intermediate
            cluster_id = -1
            cluster_name = "New Learner (No Segment Assigned)"

        # 2. Get past enrolled course IDs
        enrolled_courses = self.user_history_map.get(user_id_str, set())

        # 3. Candidate pool
        candidates = self.courses_df.copy()

        # Apply user explicit filters
        if filter_category and filter_category != "All Categories":
            candidates = candidates[candidates["CourseCategory"].str.lower() == filter_category.lower()]
        if filter_level and filter_level != "All Levels":
            candidates = candidates[candidates["CourseLevel"].str.lower() == filter_level.lower()]

        if candidates.empty:
            return []

        # 4. Score each candidate course
        scored_courses = []
        cluster_scores_lookup = self.cluster_pop_scores.get(cluster_id, {})

        for _, course in candidates.iterrows():
            cid = str(course["CourseID"])

            # Exclude already enrolled courses if requested
            if exclude_enrolled and cid in enrolled_courses:
                continue

            c_cat = str(course["CourseCategory"]).strip()
            c_lvl = str(course["CourseLevel"]).strip()

            # Signal 1: Category Match
            if is_cold_start:
                cat_score = 0.5
            else:
                cat_score = 1.0 if c_cat.lower() == primary_cat.lower() else 0.2

            # Signal 2: Difficulty Level Suitability
            lvl_score = self._calculate_level_suitability(c_lvl, depth_index)

            # Signal 3: Cluster Popularity
            cl_score = cluster_scores_lookup.get(cid, 0.0)

            # Signal 4: Global Popularity
            gl_score = self.global_pop_scores.get(cid, 0.1)

            # Weighted composite score
            final_score = (
                weights.get("category_pref", 0.35) * cat_score +
                weights.get("level_suitability", 0.25) * lvl_score +
                weights.get("cluster_popularity", 0.25) * cl_score +
                weights.get("global_popularity", 0.15) * gl_score
            )

            # Explanation generation
            reasons = []
            if is_cold_start:
                reasons.append("Trending baseline recommendation for new learners")
                if lvl_score >= 0.8:
                    reasons.append(f"Ideal {c_lvl} onboarding curriculum")
            else:
                if cat_score >= 0.8:
                    reasons.append(f"Strongly aligns with your preferred domain ({c_cat})")
                if lvl_score >= 0.8:
                    reasons.append(f"Optimal difficulty ({c_lvl}) for your learning trajectory")
                if cl_score >= 0.5:
                    reasons.append(f"High engagement among peer learners ({cluster_name})")
                elif gl_score >= 0.7:
                    reasons.append("Highly rated and popular across EduPro")

            explanation = " • ".join(reasons) if reasons else "Selected by personalized multi-signal ranking"

            scored_courses.append({
                "CourseID": cid,
                "CourseName": course.get("CourseName", f"Course {cid}"),
                "CourseCategory": c_cat,
                "CourseLevel": c_lvl,
                "CourseType": course.get("CourseType", "Self-Paced"),
                "Score": round(float(final_score), 3),
                "CategoryScore": round(float(cat_score), 2),
                "LevelScore": round(float(lvl_score), 2),
                "ClusterScore": round(float(cl_score), 2),
                "GlobalScore": round(float(gl_score), 2),
                "Explanation": explanation,
                "IsColdStart": is_cold_start
            })

        # 5. Sort descending by score
        scored_courses.sort(key=lambda x: x["Score"], reverse=True)
        return scored_courses[:n_recommendations]
