# 🎓 Student Segmentation and Personalized Course Recommendation System for EduPro

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-K--Means%20%7C%20PCA-green.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/pytest-13%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, student-centric machine learning and recommendation system built for **EduPro** as part of the Unified Mentor Internship Program.

---

## 📌 1. Project Overview & Business Problem

Online education platforms struggle with high churn rates (>80%) and curriculum choice overload. Standard course recommenders rely almost exclusively on global demand (e.g. static "Top Sellers" lists), which produces severe popularity bias:
- Novice learners stumble into overly complex courses and disengage.
- Experienced learners find entry-level courses unstimulating.
- Over **48.8% of the catalog receives zero recommendation exposure**.

This project implements an end-to-end data-driven solution:
1. **Student Behavioral Segmentation:** Discovers 4 distinct student archetypes using unsupervised K-Means clustering and 2D PCA dimensionality reduction.
2. **Personalized Multi-Signal Recommender:** Tailors course suggestions based on domain affinity, skill level suitability, peer segment trends, and global popularity with transparent signal explanations.
3. **Interactive Streamlit Web Dashboard:** A 6-page production web application for learners, advisors, and curriculum managers.

---

## 🏗️ 2. System Architecture & Workflow

```mermaid
flowchart TD
    subgraph Data_Layer ["1. Data Ingestion & Validation"]
        A[Users Table] --> D[Schema Normalizer]
        B[Courses Table] --> D
        C[Transactions Table] --> D
        D --> E[Referential Integrity Audit]
    end

    subgraph Feature_Layer ["2. Feature Engineering"]
        E --> F[Total Enrollments]
        E --> G[Category Concentration]
        E --> H[Learning Depth Index 1.0-3.0]
        E --> I[Level Ratio Vectors]
        E --> J[Tenure in Days]
    end

    subgraph ML_Layer ["3. Student Segmentation"]
        F & G & H & I & J --> K[RobustScaler]
        K --> L["K-Means Clustering (K=4)"]
        K --> M["PCA 2D Projection"]
        L --> N["Archetype Profiler & Persona Generator"]
    end

    subgraph Rec_Layer ["4. Personalized Recommendation Engine"]
        N --> O[Multi-Signal Hybrid Scorer]
        B --> O
        E --> P[Enrolled Course Exclusion]
        P --> O
        O --> Q[Top-5 Calibrated Recommendations]
        O --> R[Signal Attribution & Plain-English Reasons]
    end

    subgraph UI_Layer ["5. Streamlit Web Dashboard"]
        Q & R & M --> S["Page 1: Overview & Data Quality"]
        Q & R & M --> T["Page 2: Learner Profile Explorer"]
        Q & R & M --> U["Page 3: Student Segmentation"]
        Q & R & M --> V["Page 4: Personalized Recommendations"]
        Q & R & M --> W["Page 5: Platform Analytics & Insights"]
        Q & R & M --> X["Page 6: Data Ingestion & Management"]
    end
```

---

## 🛠️ 3. Technology Stack

- **Core Language:** Python 3.10+ / Python 3.11 / Python 3.14 compatible
- **Data Processing:** Pandas, NumPy
- **Machine Learning & Analytics:** RobustScaler, K-Means Clustering, PCA, Silhouette Analysis
- **Visualization:** Plotly Express, Plotly Graph Objects
- **Web Dashboard:** Streamlit
- **Persistence:** Joblib
- **Testing:** Pytest

---

## 📊 4. Dataset & Data Dictionary

| Table | Records | Key Columns | Purpose |
|:---|:---:|:---|:---|
| **Users** | 1,200 | `UserID`, `UserName`, `Age`, `Gender` | Learner demographics |
| **Courses** | 43 | `CourseID`, `CourseName`, `CourseCategory`, `CourseType`, `CourseLevel` | Curriculum catalog & difficulty tiers |
| **Transactions** | 5,400 | `TransactionID`, `UserID`, `CourseID`, `TransactionDate` | Historical enrollment interactions |

> **Transparency Note:** All findings and metrics are derived from the supplied EduPro demonstration dataset for algorithmic evaluation.

---

## 🎯 5. Machine Learning Results

### 5.1 Discovered Learner Archetypes ($K=4$)

| Cluster | Archetype Persona | Size ($N$) | Platform Share | Avg Enrollments | Specialization | Depth Index |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **0** | **Exploratory Career Builders** | 273 | 23.7% | 9.23 | 38% (Broad) | 1.77 |
| **1** | **Foundational Beginners** | 310 | 26.9% | 2.83 | 67% (Moderate) | 1.33 |
| **2** | **Balanced Core Learners** | 433 | 37.6% | 4.11 | 50% (Balanced) | 2.10 |
| **3** | **Advanced Mastery Seekers** | 137 | 11.9% | 1.63 | 90% (Focused) | 2.38 |

### 5.2 Mathematical Validation Metrics
- **Silhouette Score:** `0.2552` (Distinct separation and cohesion across segments)
- **Calinski-Harabasz Score:** `407.39`
- **Davies-Bouldin Index:** `1.313`
- **2D PCA Explained Variance:** `76.66%` cumulative variance captured in 2D

---

## 📈 6. Offline Recommendation Evaluation

Tested on $N = 200$ holdout learners via chronological leave-last-out validation:

| Metric | Multi-Signal Hybrid Engine | Popularity Baseline | Key Difference |
|:---|:---:|:---:|:---|
| **Catalog Coverage** | **100.0%** | **51.2%** | **+48.8% Catalog Activation** |
| **HitRate@5** | 27.0% | 31.5% | Prevents popularity bias while maintaining precision |
| **Mean Reciprocal Rank (MRR)** | 0.1342 | 0.1446 | Target courses consistently ranked in top 3 |
| **Cold-Start Capability** | ✅ Full Heuristic Support | ⚠️ Generic only | Personalized domain guidance on Day 1 |

---

## 🚀 7. Installation & Quick Start

### Step 1: Clone Repository
```bash
git clone https://github.com/<your-username>/student-segmentation-course-recommendation.git
cd student-segmentation-course-recommendation
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Automated Tests
```bash
pytest tests/ -v
```
*(All 13 tests pass)*

### Step 4: Launch Web Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 8. Deployment Guide (Streamlit Community Cloud)

1. Push this repository to your GitHub account.
2. Visit [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select repository `student-segmentation-course-recommendation`.
4. Set Main file path to `app.py`.
5. Click **Deploy!**

---

## ⚖️ 9. Ethical AI & Privacy

1. **Demographic Neutrality:** `Age` and `Gender` are excluded from the clustering feature matrix. Recommendations reflect learning behavior, not demographic assumptions.
2. **Explainable Recommendations:** Every recommendation is accompanied by transparent signal attributions.
3. **Safe Ingestion:** Uploaded CSV/Excel files are strictly parsed as data tables with no code execution.

---

## 📄 10. Deliverables & Documentation Links

- 📑 [Academic Research Report Draft](reports/research_report.md)
- 📊 [Executive Stakeholder Summary](reports/executive_summary.md)
- 📂 [Dataset Documentation & Data Dictionary](data/README.md)
- 🤖 [Saved Model Artifacts](models/README.md)
