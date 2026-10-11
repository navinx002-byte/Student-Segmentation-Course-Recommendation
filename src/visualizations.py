"""
Visualization module for EduPro analytics and dashboard.
Creates high-contrast, interactive Plotly charts with consistent themes,
clean typography, tooltips, and responsive layout configurations.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Common layout styling for consistent UI
THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=12, color="#1E293B"),
    margin=dict(l=30, r=30, t=40, b=30),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

CLUSTER_COLORS = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4", "#F97316"]


def plot_pca_clusters(
    learner_features_df: pd.DataFrame,
    pca_coords: np.ndarray,
    cluster_profiles: Dict[int, Dict[str, Any]]
) -> go.Figure:
    """Creates a 2D PCA projection scatter plot colored by student segment."""
    plot_df = pd.DataFrame({
        "PC1": pca_coords[:, 0],
        "PC2": pca_coords[:, 1],
        "UserID": learner_features_df["UserID"].astype(str),
        "Cluster": learner_features_df["Cluster"].astype(str),
        "PersonaName": learner_features_df["PersonaName"].astype(str),
        "TotalEnrollments": learner_features_df["total_enrollments"],
        "PrimaryCategory": learner_features_df["primary_category"],
        "DepthIndex": learner_features_df["learning_depth_index"]
    })

    fig = px.scatter(
        plot_df,
        x="PC1",
        y="PC2",
        color="PersonaName",
        hover_data=["UserID", "TotalEnrollments", "PrimaryCategory", "DepthIndex"],
        color_discrete_sequence=CLUSTER_COLORS,
        title="2D PCA Dimensionality Reduction: Student Segments"
    )
    fig.update_layout(**THEME_LAYOUT)
    fig.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color="#FFFFFF")))
    return fig


def plot_cluster_radar(
    cluster_profiles: Dict[int, Dict[str, Any]],
    feature_cols: List[str]
) -> go.Figure:
    """Generates a spider/radar chart comparing feature means across segments."""
    fig = go.Figure()

    # Prettify feature names for chart axes
    clean_labels = [
        c.replace("_", " ").title().replace("Pct", "%").replace("Ratio", "Ratio")
        for c in feature_cols
    ]

    for c_id, profile in cluster_profiles.items():
        color = CLUSTER_COLORS[c_id % len(CLUSTER_COLORS)]
        values = [profile["means"].get(col, 0.0) for col in feature_cols]
        # Close the loop
        values_closed = values + [values[0]]
        labels_closed = clean_labels + [clean_labels[0]]

        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            name=profile["persona_name"],
            line=dict(color=color, width=2),
            opacity=0.6
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showline=False, color="#94A3B8")
        ),
        showlegend=True,
        title="Multidimensional Segment Profile Comparison",
        **THEME_LAYOUT
    )
    return fig


def plot_category_distribution(courses_df: pd.DataFrame, transactions_df: pd.DataFrame) -> go.Figure:
    """Bar chart comparing catalog supply vs learner demand by category."""
    supply = courses_df["CourseCategory"].value_counts().reset_index()
    supply.columns = ["Category", "AvailableCourses"]

    merged = transactions_df.merge(courses_df[["CourseID", "CourseCategory"]], on="CourseID", how="left")
    demand = merged["CourseCategory"].value_counts().reset_index()
    demand.columns = ["Category", "Enrollments"]

    comp = supply.merge(demand, on="Category", how="outer").fillna(0)

    fig = go.Figure(data=[
        go.Bar(name="Available Courses (Supply)", x=comp["Category"], y=comp["AvailableCourses"], marker_color="#93C5FD"),
        go.Bar(name="Total Enrollments (Demand)", x=comp["Category"], y=comp["Enrollments"], marker_color="#2563EB", yaxis="y2")
    ])

    fig.update_layout(
        title="Course Supply vs Enrollment Demand by Domain",
        yaxis=dict(title="Course Count (Supply)"),
        yaxis2=dict(title="Enrollments (Demand)", overlaying="y", side="right"),
        barmode="group",
        **THEME_LAYOUT
    )
    return fig


def plot_recommendation_score_breakdown(rec: Dict[str, Any]) -> go.Figure:
    """Waterfall or bar chart visualizing the component signals behind a single course recommendation."""
    categories = ["Category Match", "Level Suitability", "Segment Peer Trend", "Global Popularity"]
    scores = [
        rec.get("CategoryScore", 0) * 100,
        rec.get("LevelScore", 0) * 100,
        rec.get("ClusterScore", 0) * 100,
        rec.get("GlobalScore", 0) * 100
    ]

    fig = go.Figure(go.Bar(
        x=scores,
        y=categories,
        orientation="h",
        marker=dict(color=["#2563EB", "#10B981", "#8B5CF6", "#F59E0B"]),
        text=[f"{s:.0f}%" for s in scores],
        textposition="auto"
    ))
    fig.update_layout(
        title=f"Signal Attribution: {rec['CourseName'][:30]}...",
        xaxis=dict(title="Signal Compatibility (%)", range=[0, 105]),
        yaxis=dict(autorange="reversed"),
        height=220,
        **THEME_LAYOUT
    )
    return fig
