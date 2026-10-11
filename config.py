"""
Configuration module for EduPro Student Segmentation and Course Recommendation System.
Centralizes paths, parameters, model configurations, and recommendation weights.
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Default Sample Files
DEFAULT_EXCEL_PATH = SAMPLE_DATA_DIR / "edupro_data.xlsx"
DEFAULT_USERS_CSV = SAMPLE_DATA_DIR / "users.csv"
DEFAULT_COURSES_CSV = SAMPLE_DATA_DIR / "courses.csv"
DEFAULT_TRANSACTIONS_CSV = SAMPLE_DATA_DIR / "transactions.csv"

# Segmentation Hyperparameters
DEFAULT_K_CLUSTERS = 4
MIN_CLUSTERS = 2
MAX_CLUSTERS = 8
RANDOM_STATE = 42

# Recommendation Engine Scoring Weights (Configurable in Dashboard)
DEFAULT_RECOMMENDATION_WEIGHTS = {
    "category_pref": 0.35,     # Weight for learner's category preference match
    "level_suitability": 0.25, # Weight for learner's historical difficulty level match
    "cluster_popularity": 0.25,# Weight for course popularity within the student's segment
    "global_popularity": 0.15  # Fallback baseline weight for overall course engagement
}

# Recommendation Rules
MAX_RECOMMENDATIONS = 5

# Categorical Definitions
AGE_BINS = [0, 17, 24, 34, 49, 120]
AGE_LABELS = ["Under 18", "18-24 (College/Young Pro)", "25-34 (Early Career)", "35-49 (Mid Career)", "50+ (Senior)"]

LEVEL_HIERARCHY = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}

# Theme and Visualization Styling
BRAND_COLORS = {
    "primary": "#2563EB",
    "secondary": "#10B981",
    "accent": "#F59E0B",
    "danger": "#EF4444",
    "purple": "#8B5CF6",
    "dark": "#1E293B",
    "card_bg": "#FFFFFF",
    "background": "#F8FAFC"
}

CLUSTER_PALETTE = [
    "#2563EB",  # Blue
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
    "#F97316",  # Orange
    "#64748B"   # Slate
]
