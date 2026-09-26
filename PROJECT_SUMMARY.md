# 🎓 Learning Behaviour & Course Completion Intelligence

> A concise, end-to-end guide on what this project does, how it works, and how to run it.

---

## 📌 1. What is this Project?

This project is an **EdTech Data Analytics & Predictive Intelligence Platform**. It analyzes student activity patterns across online courses to:
* Identify learning habits linked to successful course completion.
* Calculate an **Engagement Score** (0–100) and **Dropout Risk Score**.
* Predict early signs of student disengagement and silent drop-offs before students quit.
* Provide educators and stakeholders with an interactive **Streamlit Dashboard** and automated executive reports.

---

## ⚙️ 2. How It Works (Pipeline Architecture)

The system transforms raw student records into actionable insights in 5 clear stages:

```
[Raw CSV / JSON] 
       │
       ▼
1. INGESTION & VALIDATION    ── Checks required columns, types, and business rules
       │
       ▼
2. CLEANING & ENRICHMENT     ── Trims text, handles missing data, extracts datetime metrics
       │
       ▼
3. STUDENT 360 MERGE         ── Combines student, course, session, and quiz data
       │
       ▼
4. FEATURE ENGINEERING       ── Calculates engagement velocity, risk scores, and tiers
       │
       ▼
5. SQLITE & DASHBOARD        ── Stores in learning_analytics.db; renders in Streamlit
```

---

## 📊 3. Core Entities & Key Fields

The data model uses 4 intake entities and 1 derived analytical entity:

| Entity | Primary Key | Key Fields | Purpose |
| :--- | :--- | :--- | :--- |
| **`students`** | `student_id` | `registration_date`, `age`, `gender`, `device_type`, `target_course_id`, `completion_status` | Learner profile and completion outcome |
| **`courses`** | `course_id` | `course_title`, `category`, `total_modules`, `total_quizzes`, `estimated_duration_hours` | Course metadata and curriculum scale |
| **`sessions`** | `session_id` | `student_id`, `session_start`, `session_end`, `duration_minutes`, `active_minutes`, `idle_minutes` | Timestamped study durations and habits |
| **`quizzes`** | `quiz_attempt_id` | `student_id`, `course_id`, `attempt_date`, `score_percentage`, `passed` | Assessment scores and pass/fail flags |
| **`behavioural_features`** | `student_id` | `engagement_score`, `course_progress`, `days_since_last_activity`, `dropout_risk_score`, `dropout_risk_level` | Engineered predictive metrics and risk tiers |

---

## 🖥️ 4. Streamlit Dashboard Pages

Running the dashboard provides 8 interactive views:

1. **Overview**: Executive KPI scorecards, macro completion rates, and platform risk breakdown.
2. **Student Behaviour**: Study session distributions, active vs. idle habits, and module consumption.
3. **Course Analytics**: Enrolment numbers, completion rates, and quiz performance across categories.
4. **Dropout Risk**: High-risk student detection table, risk tier distribution (Low/Moderate/High/Critical).
5. **Behaviour Trends**: Weekly active learners, study velocity, and activity patterns over time.
6. **SQL Insights**: Database query executions, category aggregation, and window function rankings.
7. **Reports**: Markdown export, storytelling narrative summaries, and email report builder.
8. **Data Upload**: Upload custom CSV/JSON files for instant schema validation and live preview.

---

## 🚀 5. How to Run the Project

### Prerequisites
* Python 3.10+
* Virtual environment (`.venv`)

### Step 1: Install Dependencies
```powershell
uv pip install -r requirements.txt
# or: pip install -r requirements.txt
```

### Step 2: Initialize Database with Sample Data
```powershell
.venv\Scripts\python scripts/sql_integration.py
```
*(Initializes `data/database/learning_analytics.db` with all tables, views, and 50 student records).*

### Step 3: Run the Streamlit Dashboard
```powershell
.venv\Scripts\streamlit run dashboard/app.py
```
Open your browser at **`http://localhost:8501`**.

### Step 4: Run Tests (Optional)
```powershell
.venv\Scripts\pytest -q
```
*(Runs all 340 unit and integration tests).*

---

## 📁 6. Minimal Folder Map

```text
├── dashboard/        # Streamlit web application & page views
├── data/
│   ├── database/     # SQLite database (learning_analytics.db)
│   ├── processed/    # Cleaned and engineered feature datasets
│   └── raw/          # Raw intake source files
├── reports/          # Generated KPI summaries, risk tables, and executive reports
├── scripts/          # Standalone SQL and feature engineering scripts
├── sql/              # Schema DDL, views, metrics, and aggregation queries
├── src/              # Core processing logic (cleaning, features, validation, storage)
└── tests/            # Automated test suite (340 pytest tests)
```
