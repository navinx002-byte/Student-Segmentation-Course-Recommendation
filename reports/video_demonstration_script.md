# 🎥 Project Demonstration & Video Walkthrough Script

**Project Title:** Student Segmentation and Personalized Course Recommendation System for EduPro  
**Target Duration:** 3 to 5 Minutes  
**Presenter:** Unified Mentor Data Science Intern  
**Target Platform:** YouTube (Unlisted) or Loom / Google Drive (Public Link)

---

## ⏱️ Video Presentation Script (Minute-by-Minute)

### 00:00 – 00:45 | 1. Introduction & Problem Statement
> **Visual:** Open browser showing the Home page of the EduPro Streamlit Dashboard (`app.py`).  
> **Speaker Script:**  
> "Hello everyone, my name is [Your Name], and today I am excited to present my end-to-end data science capstone project for the Unified Mentor Internship: **Student Segmentation and Personalized Course Recommendation System for EduPro**.  
> In modern e-learning, over 80% of learners drop out. Traditional platforms rely on generic top-seller lists, causing decision fatigue, difficulty mismatches, and catalog starvation where half the courses never get seen. Our solution is a student-centric platform combining unsupervised behavioral clustering with a hybrid personalized recommender."

---

### 00:45 – 01:30 | 2. Dataset & Exploratory Data Analysis
> **Visual:** Navigate to **Page 1: Overview & Data Quality**. Scroll through KPI cards, schema audit table, and age/gender distributions.  
> **Speaker Script:**  
> "The dataset consists of three relational tables: 1,200 learners, 43 courses across 8 domains, and 5,400 enrollment events.  
> Our data loader automatically validates foreign key relationships, handles missing values, and checks referential integrity. As shown here in the exploratory dashboard, 51% of enrollments concentrate in Technology and Business, with learners having an average age of 26. We also see that nearly half the courses are at the beginner level."

---

### 01:30 – 02:30 | 3. Student Segmentation Using Machine Learning
> **Visual:** Navigate to **Page 3: Student Segmentation**. Display the 2D PCA cluster projection, radar chart, and cluster profile table.  
> **Speaker Script:**  
> "Next, in our segmentation engine, we engineered behavioral features: enrollment volume, domain concentration, learning depth index, and active tenure. Notice that demographic attributes like Age and Gender are strictly excluded to avoid bias.  
> Using K-Means clustering with k-means++ and validating across K=2 through 8 using Silhouette and Davies-Bouldin scores, we identified 4 clear learner archetypes:
> 1. **Exploratory Career Builders (23.7%):** High activity, cross-skilling across 4+ domains.
> 2. **Foundational Beginners (26.9%):** Entry-level learners focusing on introductory fundamentals.
> 3. **Balanced Core Learners (37.6%):** Mainstream learners with steady progress.
> 4. **Advanced Mastery Seekers (11.9%):** Focused specialists pursuing high-depth technical topics.  
> The 2D PCA projection captures over 76.6% of total feature variance, showing clear geometric boundaries."

---

### 02:30 – 03:30 | 4. Personalized Recommendations & Live Demo
> **Visual:** Navigate to **Page 4: Course Recommendations**. Select a student (e.g., `U1001`), show top recommendations, toggle filters, and highlight the Signal Attribution chart.  
> **Speaker Script:**  
> "Now let's examine the personalized recommendation engine. Unlike black-box algorithms, our hybrid model combines 4 signals: category preference, difficulty suitability, peer segment trends, and global popularity.  
> For student `U1001`, the system recommends relevant courses, excluding courses they've already completed. Look at the signal attribution chart: learners can clearly see why each course was suggested.  
> The system also handles new learners with zero history through cold-start onboarding heuristics."

---

### 03:30 – 04:30 | 5. Evaluation, Impact & Business Insights
> **Visual:** Navigate to **Page 5: Analytics & Business Insights**, then show the offline evaluation metrics.  
> **Speaker Script:**  
> "To validate our recommender, we performed chronological leave-last-out offline evaluation across 200 holdout learners.  
> The most critical finding: our personalized engine achieves **100% catalog coverage**, compared to only 51.2% for the standard popularity baseline—a +48.8% expansion! This completely eliminates catalog starvation and ensures specialized courses get discovered.  
> For EduPro stakeholders, we recommend implementing progression bundles for beginners and capstone credentials for advanced mastery seekers."

---

### 04:30 – 05:00 | 6. Conclusion & Wrap-Up
> **Visual:** Return to Home page or show GitHub repository with all tests passing.  
> **Speaker Script:**  
> "In summary, we built a reproducible, tested, and ethical recommendation system backed by 13 automated tests and full documentation. Thank you for your time, and I look forward to your questions and feedback!"

---

## 📋 Screen Recording & Upload Checklist

- [ ] **Recording Tool:** Use OBS Studio, Loom, or Windows Game Bar (`Win + G`).
- [ ] **Resolution & Audio:** 1080p, clear microphone audio, browser set to 100% zoom.
- [ ] **Pre-Launch Checklist:**
  - [ ] Terminal running `streamlit run app.py` on `localhost:8501`.
  - [ ] Browser tabs prepared: Dashboard, GitHub Repo, and Research Report.
  - [ ] Rehearse timing to ensure it stays between 3 and 5 minutes.
- [ ] **Upload to YouTube:**
  - [ ] Upload as **Unlisted** (or Public).
  - [ ] Video title: `EduPro Student Segmentation & Personalized Course Recommendation - Unified Mentor Project Demo`.
  - [ ] Description: Include GitHub repository URL and project summary.
  - [ ] Ensure permission is set so anyone with the link can view.
