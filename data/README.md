# 📂 EduPro Dataset Documentation & Data Dictionary

This directory contains the sample dataset files utilized by the **Student Segmentation and Personalized Course Recommendation System**.

---

## 1. Dataset Provenance & Demonstration Transparency Notice

The provided dataset (`edupro_data.xlsx` and companion CSV files) models transactional learning behaviors for **EduPro**, a synthetic digital education platform. All findings, cluster profiles, and evaluation metrics reported by the system are derived from this dataset for methodological benchmarking and demonstration purposes.

---

## 2. Relational Schema & Data Dictionary

The data architecture comprises three primary relational tables connected via relational keys:

```
[Users Table] (1,200 rows)
   │ UserID (Primary Key)
   ▼
[Transactions Table] (5,400 rows) ── CourseID (Foreign Key) ──► [Courses Table] (43 rows)
                                                                    CourseID (Primary Key)
```

### Table 1: `Users` (Learners)
| Attribute | Data Type | Null Count | Description |
|:---|:---|:---:|:---|
| `UserID` | String | 0 | Unique learner identifier (e.g., `U1001` - `U2200`). Serves as Primary Key. |
| `UserName` | String | 0 | Learner full name / profile handle. |
| `Age` | Integer | 0 | Learner chronological age (range: 16–58). |
| `Gender` | String | 0 | Reported demographic gender (Male, Female, Non-Binary). |

> **Ethical AI Safeguard:** Demographic attributes (`Age`, `Gender`, `UserName`) are strictly isolated from the clustering and recommendation algorithms to prevent bias and ensure recommendations are driven exclusively by observed educational behavior.

---

### Table 2: `Courses` (Curriculum Catalog)
| Attribute | Data Type | Null Count | Description |
|:---|:---|:---:|:---|
| `CourseID` | String | 0 | Unique curriculum catalog identifier (e.g., `C101` - `C143`). Primary Key. |
| `CourseName` | String | 0 | Official curriculum title. |
| `CourseCategory` | String | 0 | Domain discipline (Technology, Business, Science, Arts, Health, Mathematics, Language). |
| `CourseType` | String | 0 | Delivery format / monetization mode (`Self-Paced`, `Live`, `Paid`, `Free`). |
| `CourseLevel` | String | 0 | Difficulty hierarchy (`Beginner`, `Intermediate`, `Advanced`). |

---

### Table 3: `Transactions` (Enrollment Interactions)
| Attribute | Data Type | Null Count | Description |
|:---|:---|:---:|:---|
| `TransactionID` | String | 0 | Unique transaction log identifier (e.g., `T50001` - `T55400`). Primary Key. |
| `UserID` | String | 0 | Foreign Key referencing `Users.UserID`. |
| `CourseID` | String | 0 | Foreign Key referencing `Courses.CourseID`. |
| `TransactionDate` | Date/String | 0 | Timestamp of enrollment event (`YYYY-MM-DD`). |

---

## 3. Data Cleaning & Integrity Rules

The automated data ingestion pipeline (`src/data_loader.py`) enforces the following validation checks:
1. **Column Normalization:** Case-insensitive alias matching to handle variations (e.g., `user_id`, `learner_id` mapped to `UserID`).
2. **Referential Integrity Audit:** Orphan transaction records referencing non-existent `UserID` or `CourseID` entities are automatically pruned.
3. **Duplicate De-duplication:** Duplicate transactions and identical user records are purged.
4. **Cold-Start Handling:** Learners registered in `Users` with 0 transactional records are safely flagged as new learners rather than discarded.
