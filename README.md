# 🎓 Learning Behaviour & Course Completion Intelligence

> An end-to-end data analytics and prediction product that identifies the learning behaviours associated with long-term course completion and detects students at risk of silently dropping out.

---

## 📌 Project Overview

EdTech platforms collect huge amounts of student data such as course progress, quiz scores, login sessions, learning duration, and activity history. However, collecting data alone does not explain **why some students complete courses while others gradually disengage and disappear**.

This project analyzes student learning behaviour to discover the patterns that are associated with:

* Long-term course completion
* Consistent learning
* Student engagement
* Quiz performance
* Course progress
* Behavioural changes
* Silent drop-offs
* Student risk levels

The final product converts raw student activity into an **interactive business intelligence dashboard** using Python, Pandas, NumPy, SQL/SQLite, Plotly, Streamlit, and GitHub Actions.

---

# 🎯 Problem Statement

An EdTech platform tracks course completion records, quiz performance, and student session activity, but no analysis identifies which learning behaviours actually predict long-term course completion versus silent drop-offs.

The project aims to answer:

1. Which learning behaviours are associated with successful course completion?
2. What behavioural patterns indicate student disengagement?
3. Can a decline in activity be detected before a student completely drops out?
4. Which metrics have the strongest relationship with completion?
5. Which students currently show high dropout risk?
6. How can these insights be presented to educators and business stakeholders?

---

# 🎯 Project Objectives

### Primary Objectives

* Analyze student learning behaviour.
* Clean and validate raw student activity data.
* Create meaningful behavioural features.
* Perform exploratory and statistical analysis.
* Identify completion and dropout patterns.
* Build business-oriented SQL metrics.
* Detect behavioural anomalies and risk.
* Create interactive visualizations.
* Build a Streamlit analytics dashboard.
* Automate data processing and validation using GitHub Actions.

---

# 🧰 Technology Stack

The project follows the required Sprint 1 technology stack.

| Technology         | Purpose                                       |
| ------------------ | --------------------------------------------- |
| **Python**         | Main programming and analysis language        |
| **Pandas**         | Data manipulation and transformation          |
| **NumPy**          | Numerical and vectorized computation          |
| **SQL / SQLite**   | Database querying and business analytics      |
| **Plotly**         | Interactive data visualization                |
| **Streamlit**      | Interactive dashboard and data product        |
| **GitHub Actions** | Automation, validation and pipeline execution |

---

# 🏗️ End-to-End Architecture

```text
                    ┌─────────────────────┐
                    │   Raw Data Sources  │
                    │                     │
                    │ CSV / JSON / SQLite │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Dataset Validation  │
                    │ & Data Profiling    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Cleaning       │
                    │ & Standardisation   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Feature Engineering │
                    │ & Behaviour Metrics │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Python EDA          │
                    │ Behaviour Analysis  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ SQLite Database     │
                    │ SQL Analytics Layer │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Business KPIs       │
                    │ Risk & Insights     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Plotly Visualisation│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Dashboard │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Reports / Alerts    │
                    │ & Stakeholder Share │
                    └─────────────────────┘
                               ▲
                               │
                    ┌──────────┴──────────┐
                    │   GitHub Actions    │
                    │ Automation & CI/CD  │
                    └─────────────────────┘
```

---

# 📂 Recommended Project Structure

```text
learning-behaviour-intelligence/
│
├── data/
│   ├── raw/
│   │   ├── students.csv
│   │   ├── sessions.csv
│   │   ├── quizzes.csv
│   │   └── courses.csv
│   │
│   ├── processed/
│   │   ├── cleaned_students.csv
│   │   ├── cleaned_sessions.csv
│   │   └── behavioural_features.csv
│   │
│   └── database/
│       └── learning_analytics.db
│
├── notebooks/
│   ├── 01_data_profiling.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_behavioural_analysis.ipynb
│   └── 06_sql_analysis.ipynb
│
├── src/
│   ├── ingestion.py
│   ├── validation.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   ├── analysis.py
│   ├── anomaly_detection.py
│   ├── database.py
│   └── pipeline.py
│
├── sql/
│   ├── schema.sql
│   ├── business_metrics.sql
│   ├── behavioural_analysis.sql
│   ├── risk_analysis.sql
│   └── optimisation.sql
│
├── dashboard/
│   ├── app.py
│   ├── components.py
│   └── utils.py
│
├── reports/
│   ├── charts/
│   ├── insights/
│   └── executive_report.md
│
├── tests/
│   ├── test_cleaning.py
│   ├── test_features.py
│   └── test_pipeline.py
│
├── .github/
│   └── workflows/
│       └── data_pipeline.yml
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🔄 The 50 Required Concepts

The project is intentionally designed to cover **all 50 concepts** from the Sprint.

---

## 🟦 Phase 1 — Environment & Git

### 01. Development Environment & Workspace Setup

Set up:

* Python environment
* VS Code
* Git
* Project folders
* Virtual environment
* Dependencies

Example:

```text
Python
Pandas
NumPy
SQLite
Plotly
Streamlit
Pytest
```

---

### 02. GitHub Repository & Team Workflow Setup

Create a GitHub repository and establish:

* Main branch
* Development branch
* Feature branches
* Pull requests
* Issues
* Commit conventions

Example:

```text
main
│
├── development
│
├── feature/data-cleaning
├── feature/sql-analysis
└── feature/dashboard
```

---

### 03. Python Data Workflow Foundations

Build the basic Python pipeline:

```text
Load
 ↓
Inspect
 ↓
Transform
 ↓
Analyze
 ↓
Export
```

Use Pandas and NumPy as the primary analysis tools.

---

# 🟪 Phase 2 — Data Ingestion

### 04. Dataset Intake & Source Validation

Before processing the data:

* Verify file existence.
* Check file format.
* Check required columns.
* Check row counts.
* Validate data types.
* Detect corrupted records.

---

### 05. CSV & JSON Data Ingestion

Support both:

```text
students.csv
sessions.csv
quizzes.csv
courses.csv
```

and JSON sources where required.

Python will load the data into Pandas DataFrames.

---

# 🟩 Phase 3 — Data Cleaning

### 06. Dataset Profiling & Quality Assessment

Generate a profile containing:

* Number of rows
* Number of columns
* Missing values
* Unique values
* Data types
* Duplicate records
* Numerical statistics

---

### 07. Data Dictionary & Business Context Mapping

Create a data dictionary.

Example:

| Column            | Meaning                      |
| ----------------- | ---------------------------- |
| student_id        | Unique student               |
| course_id         | Course identifier            |
| session_date      | Date of learning activity    |
| session_duration  | Time spent learning          |
| quiz_score        | Quiz performance             |
| progress_pct      | Course completion percentage |
| completion_status | Completed / Dropped          |

This connects technical columns to actual business meaning.

---

### 08. Missing Value Detection & Imputation

Identify missing values in:

* Quiz scores
* Session duration
* Course progress
* Course information

Apply appropriate strategies such as:

* Mean/median
* Forward filling
* Business rules
* Removing invalid records

---

### 09. Data Type Enforcement & Standardisation

Standardize:

* Dates
* Numeric columns
* Boolean values
* Categories
* Student IDs

Example:

```text
"85%" → 85.0
"2026/08/01" → datetime
"Completed" → completed
```

---

### 10. Duplicate Detection & Record Deduplication

Detect duplicate:

* Student records
* Session records
* Quiz attempts
* Course activity

Remove duplicates using appropriate business keys.

---

### 11. String Cleaning & Text Normalisation

Normalize text fields such as:

```text
" Data Science "
"data science"
"DATA SCIENCE"
```

into a consistent representation.

---

### 12. Date & Time Transformation Pipeline

Convert timestamps into useful features:

```text
date
day
week
month
weekday
hour
week number
```

These features help identify learning patterns.

---

### 13. Outlier Detection with Statistical Methods

Detect abnormal values such as:

* Extremely long sessions
* Impossible quiz scores
* Abnormally high activity
* Unrealistic progress values

Possible methods:

* IQR
* Z-score
* Percentile analysis

---

### 14. Data Consistency & Validation Rules

Create business rules such as:

```text
quiz_score must be between 0 and 100

progress must be between 0 and 100

session_duration must be positive

completion_status must be valid

session_date cannot be before enrollment_date
```

---

### 15. Multi-Source Merging & Join Validation

Merge:

```text
Students
   +
Courses
   +
Sessions
   +
Quizzes
```

Validate that joins do not unexpectedly increase or decrease record counts.

---

# 🟩 Phase 4 — Feature Engineering

### 16. Feature Engineering & Derived Business Columns

Create behavioural metrics such as:

```text
average_session_duration
sessions_per_week
quiz_average
quiz_attempt_count
progress_velocity
days_since_last_activity
completion_rate
engagement_score
```

These features become the foundation of the analysis.

---

### 17. NumPy Vectorised Computation Workflow

Use NumPy instead of slow row-by-row operations where possible.

Example calculations:

```text
engagement_score
risk_score
progress_velocity
normalised_metrics
```

This demonstrates efficient numerical processing.

---

# 🟧 Phase 5 — Analysis & EDA

### 18. Distribution Analysis for Business Trends

Analyze distributions of:

* Session duration
* Quiz scores
* Course progress
* Engagement score

Identify normal and unusual behaviour.

---

### 19. Correlation & Relationship Analysis

Study relationships between:

```text
Session Frequency ↔ Completion

Quiz Score ↔ Completion

Session Duration ↔ Completion

Inactivity ↔ Dropout

Progress Velocity ↔ Completion
```

Correlation analysis helps identify potentially important behavioural indicators.

---

### 20. GroupBy Aggregation & Segment Insights

Create groups such as:

```text
High Engagement
Medium Engagement
Low Engagement
```

Then compare:

* Completion rate
* Quiz score
* Session frequency
* Average progress

---

### 21. Time-Series Trend & Rolling Metrics

Analyze behaviour over time.

Examples:

```text
Weekly active students
Weekly session count
Weekly average learning time
Weekly completion rate
```

Use rolling averages to identify behavioural trends.

---

### 22. Behavioural Analysis & User Segmentation

Segment students into behavioural groups.

Example:

```text
Segment A → Consistent Learners
Segment B → High Performers
Segment C → Sporadic Learners
Segment D → Disengaging Learners
Segment E → Silent Drop-offs
```

---

### 23. Funnel Analysis & Drop-Off Detection

Build the learning funnel:

```text
Enrolled
   ↓
Started Course
   ↓
25% Progress
   ↓
50% Progress
   ↓
75% Progress
   ↓
Completed
```

Identify where students are leaving the learning journey.

---

### 24. KPI Definition & Business Metric Design

Define important business KPIs.

### Core KPIs

```text
Course Completion Rate
Student Engagement Rate
Average Session Duration
Average Quiz Score
Dropout Rate
At-Risk Student Count
Average Course Progress
Weekly Active Learners
```

---

### 25. Anomaly Detection & Risk Identification

Create a student risk score based on behavioural indicators.

Example:

```text
High inactivity
+
Declining session frequency
+
Low progress
+
Repeated quiz failures
        ↓
High Dropout Risk
```

Risk categories:

```text
LOW
MEDIUM
HIGH
```

---

### 26. Root Cause Investigation Workflow

When dropout increases, investigate:

```text
Dropout Increase
      ↓
Which Course?
      ↓
Which Student Segment?
      ↓
What Behaviour Changed?
      ↓
Session Frequency?
Quiz Performance?
Progress?
Inactivity?
      ↓
Potential Root Cause
```

This moves the project from simple reporting to business analysis.

---

# 🟦 Phase 6 — SQL

### 27. SQL Environment & Database Integration

Create a SQLite database:

```text
learning_analytics.db
```

Tables:

```text
students
courses
sessions
quizzes
behavioural_features
```

---

### 28. SQL Business Metrics Query Design

Create SQL queries for:

* Completion rate
* Dropout rate
* Average quiz score
* Average session duration
* Active students
* At-risk students

---

### 29. SQL Filtering, Grouping & Aggregation

Use:

```sql
WHERE
GROUP BY
HAVING
COUNT()
AVG()
SUM()
```

to produce business insights.

---

### 30. SQL Joins & Multi-Table Analysis

Use:

```sql
INNER JOIN
LEFT JOIN
```

to combine:

```text
students
sessions
quizzes
courses
```

---

### 31. SQL Window Functions & Ranking Systems

Use window functions such as:

```text
ROW_NUMBER()
RANK()
LAG()
LEAD()
AVG() OVER()
```

Applications:

* Rank students
* Calculate previous activity
* Compare current vs previous week
* Calculate rolling metrics

---

### 32. Analytical SQL Query Optimisation

Improve query performance through:

* Selecting only required columns
* Appropriate indexes
* Avoiding unnecessary joins
* Reusing intermediate results
* Query inspection

---

### 33. SQL Views & Aggregation Layer Design

Create reusable views such as:

```text
student_engagement_view
course_performance_view
dropout_risk_view
weekly_activity_view
```

This creates a clean SQL analytics layer for the dashboard.

---

### 34. SQL-Based Insight Validation

Compare SQL results against Pandas calculations.

Example:

```text
Pandas Completion Rate
        =
SQL Completion Rate
```

If they differ, investigate the pipeline.

This ensures analytical reliability.

---

# 🟥 Phase 7 — Visualisation

### 35. Business Visualisation Principles

Charts should answer business questions rather than simply look attractive.

Examples:

```text
"What is happening?"
"Why is it happening?"
"Which students are at risk?"
"Which courses have the highest dropout?"
```

---

### 36. Interactive Plotly Charts

Create interactive:

* Line charts
* Bar charts
* Scatter plots
* Histograms
* Heatmaps
* Funnel charts

Use Plotly for dashboard visualizations.

---

### 37. KPI Card & Summary Metric Design

The dashboard should begin with KPI cards:

```text
┌────────────────┐
│ Completion     │
│     72.4%      │
└────────────────┘

┌────────────────┐
│ Dropout Rate   │
│     18.6%      │
└────────────────┘

┌────────────────┐
│ At Risk        │
│      342       │
└────────────────┘

┌────────────────┐
│ Avg Quiz Score │
│     78.2       │
└────────────────┘
```

---

### 38. Data Storytelling & Insight Narrative

Each visualization should communicate:

```text
Observation
     ↓
Interpretation
     ↓
Business Impact
     ↓
Recommended Action
```

Example:

> Students whose weekly session frequency falls for three consecutive weeks show substantially lower completion rates. This indicates that declining engagement may be an early warning signal for course abandonment.

---

### 39. Executive Reporting & Stakeholder Communication

Create an executive-level summary covering:

* Current performance
* Major trends
* Key risks
* Root causes
* Recommended actions

The report should be understandable without technical knowledge.

---

### 40. Insight Export & Report Generation

Allow results to be exported as:

```text
CSV
PDF / Report
Charts
Summary tables
```

The dashboard should provide useful outputs beyond visualization.

---

# 🟣 Phase 8 — Streamlit Application

### 41. Streamlit App Structure & Navigation

Create a multi-page dashboard.

Suggested navigation:

```text
Dashboard
│
├── Overview
├── Student Behaviour
├── Course Analytics
├── Dropout Risk
├── Behaviour Trends
├── SQL Insights
└── Reports
```

---

### 42. Dataset Upload & Dynamic Preview System

Allow users to upload CSV/JSON files.

The interface should show:

* File name
* Row count
* Column count
* Preview
* Data types
* Missing values

---

### 43. Streamlit Filters & Interactive Widgets

Provide filters such as:

```text
Course
Student Segment
Risk Level
Date Range
Completion Status
Quiz Score
Engagement Level
```

All charts should update according to the selected filters.

---

### 44. Streamlit Session State & Workflow Persistence

Use Streamlit session state to preserve:

* Selected filters
* Uploaded dataset
* Current page
* User selections
* Generated analysis

This prevents the application from feeling like a collection of disconnected pages.

---

### 45. Real-Time KPI Dashboard Development

When users change filters, KPIs should update dynamically.

Example:

```text
Selected Course:
Data Science

↓

Completion Rate: 78%
Avg Quiz Score: 81%
At-Risk Students: 43
Avg Session Time: 34 min
```

---

# 🟪 Phase 9 — Delivery & Operations

### 46. Alert Monitoring & Metric Threshold Detection

Create thresholds such as:

```text
Dropout Rate > 25%
        ↓
WARNING

Completion Rate < 60%
        ↓
WARNING

High Risk Students > 20%
        ↓
CRITICAL
```

This allows the platform to identify unusual changes automatically.

---

### 47. Insight Sharing & Email Report Integration

Generate a summary report that can be shared with:

* Course managers
* Teachers
* Academic teams
* Business stakeholders

Optional email integration can send:

```text
Weekly Learning Behaviour Report
```

---

### 48. Automated Data Pipeline Execution

Create an automated workflow:

```text
New Data
   ↓
Validation
   ↓
Cleaning
   ↓
Feature Engineering
   ↓
SQL Database Update
   ↓
Analysis
   ↓
Report
```

This pipeline can be executed automatically.

---

### 49. GitHub Workflow Automation & Validation

GitHub Actions will automatically:

* Install dependencies
* Run tests
* Validate data
* Run pipeline checks
* Check code quality
* Verify SQL queries

Example workflow:

```text
git push
   ↓
GitHub Actions
   ↓
Install Python
   ↓
Install dependencies
   ↓
Run tests
   ↓
Run validation
   ↓
Run pipeline
   ↓
Build successful
```

---

### 50. Data Product Documentation & Delivery

Document:

* Project objective
* Data sources
* Data dictionary
* Pipeline architecture
* SQL layer
* KPIs
* Dashboard
* Business insights
* Limitations
* Setup instructions
* Deployment instructions

This README itself forms part of the final documentation.

---

# 📊 Dashboard Design

The final Streamlit application should have the following structure.

## 1. Executive Overview

Display:

```text
Total Students
Active Students
Completion Rate
Dropout Rate
At-Risk Students
Average Quiz Score
```

Charts:

* Completion vs dropout
* Weekly activity trend
* Course performance

---

## 2. Behaviour Analysis

Display:

* Session frequency
* Session duration
* Learning consistency
* Quiz performance
* Course progress

Charts:

```text
Session Frequency vs Completion
Quiz Score vs Completion
Inactivity vs Dropout
```

---

## 3. Student Segmentation

Show segments:

| Segment              | Description                          |
| -------------------- | ------------------------------------ |
| Consistent Learners  | Regular sessions and steady progress |
| High Performers      | Strong quiz performance              |
| Sporadic Learners    | Irregular activity                   |
| Disengaging Learners | Activity is declining                |
| Silent Drop-offs     | Very low/recently stopped activity   |

---

## 4. Dropout Risk Dashboard

Example:

```text
HIGH RISK
────────────
342 Students

MEDIUM RISK
────────────
517 Students

LOW RISK
────────────
2,841 Students
```

Show the major behavioural factors associated with high-risk students.

---

## 5. Course Analytics

For every course:

```text
Course Name
Enrollment
Active Students
Completion Rate
Dropout Rate
Average Quiz Score
Average Progress
At-Risk Students
```

---

## 6. Time-Series Analytics

Show:

* Weekly active learners
* Weekly session duration
* Completion trend
* Dropout trend
* Engagement trend

Use rolling averages to smooth short-term fluctuations.

---

# 🧮 Proposed Behavioural Score

One of the main derived metrics can be an **Engagement Score**.

Example conceptual model:

```text
Engagement Score =
    Session Consistency
    + Progress Velocity
    + Quiz Performance
    + Recency of Activity
```

The exact weights should be determined from analysis rather than arbitrarily assumed.

Similarly, a **Dropout Risk Score** can combine:

```text
Inactivity
+
Declining Sessions
+
Low Progress
+
Low Quiz Performance
+
Irregular Learning
```

The project should clearly distinguish between **observed behavioural associations** and claims of causation.

---

# 🔬 Main Research Questions

The project will investigate:

### RQ1

**Does consistent learning behaviour predict course completion?**

### RQ2

**Does declining session activity act as an early warning signal for dropout?**

### RQ3

**What relationship exists between quiz performance and course completion?**

### RQ4

**Which behavioural features have the strongest association with successful completion?**

### RQ5

**Can students be segmented into meaningful behavioural groups?**

### RQ6

**Can silent drop-offs be detected before final course abandonment?**

---

# 📈 Example Business Insights

The final analysis should produce insights in this format:

```text
INSIGHT

Students with consistent weekly activity have a higher
completion rate than students with highly irregular activity.

WHY IT MATTERS

Consistency appears to be an important behavioural indicator
for long-term engagement.

ACTION

Students showing a sustained decline in weekly activity can
be prioritized for early engagement interventions.
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone <repository-url>

cd learning-behaviour-intelligence
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Data Pipeline

Run the complete pipeline:

```bash
python src/pipeline.py
```

The pipeline will:

```text
Load Data
   ↓
Validate
   ↓
Clean
   ↓
Transform
   ↓
Feature Engineering
   ↓
Analysis
   ↓
SQLite Update
```

---

# 📊 Running the Dashboard

Start Streamlit:

```bash
streamlit run dashboard/app.py
```

The application will open in your browser.

---

# 🗄️ Database

SQLite is used as the analytical database.

### Main Tables

```text
students
courses
sessions
quizzes
behavioural_features
```

### Analytical Views

```text
student_engagement_view
course_performance_view
dropout_risk_view
weekly_activity_view
```

---

# 🔁 Data Pipeline

The complete workflow is:

```text
        RAW DATA
           │
           ▼
    Source Validation
           │
           ▼
      Data Profiling
           │
           ▼
     Data Cleaning
           │
           ▼
   Data Standardisation
           │
           ▼
   Feature Engineering
           │
           ▼
       Python EDA
           │
           ▼
 Behavioural Segmentation
           │
           ▼
     Risk Detection
           │
           ▼
      SQLite / SQL
           │
           ▼
   Business KPI Layer
           │
           ▼
      Plotly Charts
           │
           ▼
 Streamlit Dashboard
           │
           ▼
 Reports / Alerts
```

---

# 🔐 Data Quality & Reliability

The project includes validation at multiple levels.

### Source Level

```text
File exists?
Correct format?
Required columns?
```

### Data Level

```text
Missing values?
Duplicates?
Invalid types?
Outliers?
```

### Business Level

```text
Progress valid?
Quiz score valid?
Session duration valid?
Dates consistent?
```

### Analytical Level

```text
Pandas result
      =
SQL result
```

This creates confidence in the final dashboard.

---

# 🚦 Risk Classification

A simple initial classification can be:

| Risk      | Example Behaviour                        |
| --------- | ---------------------------------------- |
| 🟢 Low    | Consistent activity and steady progress  |
| 🟡 Medium | Irregular activity or slowing progress   |
| 🔴 High   | Long inactivity and declining engagement |

These categories should be calibrated against historical outcomes.

---

# 🤖 Automation

GitHub Actions will automate the data product workflow.

```text
Developer Push
      ↓
GitHub Actions
      ↓
Install Dependencies
      ↓
Run Tests
      ↓
Validate Dataset
      ↓
Run Data Pipeline
      ↓
Validate SQL
      ↓
Generate Outputs
```

---

# 🧪 Testing Strategy

Tests should cover:

### Data Tests

* Missing required columns
* Invalid values
* Duplicate records
* Incorrect data types

### Feature Tests

* Engagement score calculation
* Progress calculation
* Risk calculation

### SQL Tests

* Completion rate
* Student counts
* Aggregations
* Join correctness

### Pipeline Tests

* Pipeline runs successfully
* Output files are generated
* Database is updated correctly

---

# 📋 Success Criteria

The project will be considered successful when:

* [x] All 50 Sprint concepts are implemented.
* [ ] Raw datasets can be ingested.
* [ ] Data quality checks are performed.
* [ ] Data cleaning pipeline is implemented.
* [ ] Behavioural features are generated.
* [ ] EDA identifies meaningful patterns.
* [ ] SQL analytics layer is implemented.
* [ ] KPIs are defined.
* [ ] Dropout risk is identified.
* [ ] Plotly visualizations are implemented.
* [ ] Streamlit dashboard is functional.
* [ ] Dataset upload works.
* [ ] Dashboard filters work.
* [ ] Session state is implemented.
* [ ] Alerts and thresholds are implemented.
* [ ] Reports can be generated.
* [ ] GitHub Actions automates validation.
* [ ] Complete documentation is provided.

---

# 🌱 Future Scope

The project can later be extended with:

* Machine learning-based dropout prediction
* SHAP-based explainability
* Personalized intervention recommendations
* Real-time learning analytics
* Email/SMS notifications
* LMS integration
* Student-level recommendation systems
* Advanced time-series modelling
* A/B testing of intervention strategies

---

# ⚠️ Limitations

Behavioural data can show **association**, but association does not automatically mean causation.

For example:

```text
Low session activity
        ↓
High dropout rate
```

does not necessarily prove that low activity *causes* dropout.

Other factors may influence completion, including:

* Course difficulty
* Personal circumstances
* Course quality
* Instructor quality
* Technical problems
* External commitments

Therefore, the project should present findings as **data-driven behavioural indicators**, not absolute causal conclusions.

---

# 👥 Intended Stakeholders

### Students

Receive earlier support when engagement begins to decline.

### Teachers & Mentors

Identify students who may require intervention.

### Course Managers

Understand where learners disengage.

### EdTech Business Teams

Monitor course performance and retention.

### Academic Administrators

Track overall learning engagement and outcomes.

---

# 🏁 Final Goal

The ultimate goal of this project is to transform an EdTech platform from:

```text
"Students are dropping out."
```

into:

```text
"These students are showing behavioural signals
associated with dropout risk, and here is what
changed in their learning behaviour."
```

The project therefore combines **data engineering, data cleaning, statistical analysis, SQL analytics, visualization, dashboard development, and automation** into one complete data product.

---

# 👨‍💻 Project Status

**Current Phase:** Sprint 1 — End-to-End Data Product

**Pipeline:**

```text
Python
   +
Pandas
   +
NumPy
   +
SQLite / SQL
   +
Plotly
   +
Streamlit
   +
GitHub Actions
```

**Concept Coverage:** `50 / 50`

**Project Type:** EdTech Learning Analytics & Behaviour Intelligence

---

# 📜 License

This project is developed for educational and academic purposes.
