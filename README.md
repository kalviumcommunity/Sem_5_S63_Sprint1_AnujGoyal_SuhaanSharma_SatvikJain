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

#### 🛠️ Setup Instructions

1. **Clone the Repository & Navigate to Workspace:**
   ```bash
   git clone <repository_url>
   cd Sem_5_S63_Sprint1_AnujGoyal_SuhaanSharma_SatvikJain
   ```

2. **Create and Activate Python Virtual Environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Core Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify Environment & Run Entry Point:**
   ```bash
   python main.py
   ```

5. **Run Automated Test Suite:**
   ```bash
   pytest
   ```

6. **Launch Streamlit Analytics Dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

#### 📦 Core Tech Stack & Dependencies:
- **Python**: `>=3.10` (Main programming & computation engine)
- **Pandas**: `>=2.0.0` (DataFrames, transformations, aggregations)
- **NumPy**: `>=1.24.0` (Vectorized numerical computations)
- **SQLite3**: Built-in Python DB for SQL analytics layer
- **Plotly**: `>=5.18.0` (Interactive charts and figures)
- **Streamlit**: `>=1.30.0` (Interactive web UI and analytics dashboard)
- **Pytest**: `>=7.4.0` (Automated testing and QA)

---

### 02. GitHub Repository & Team Workflow Setup

#### 👥 3-Member Team Collaboration Model
- **Contributors:** Anuj Goyal, Suhaan Sharma, Satvik Jain
- **Repository Structure & Workflow Guide:** See [`CONTRIBUTING.md`](CONTRIBUTING.md)

#### 🌿 Branching Strategy & Conventions
- **`main`**: Production-ready, stable releases.
- **`develop`**: Integration branch for ongoing sprint concepts.
- **`feature/<concept-id>-<name>`**: Dedicated branch per sprint concept (e.g., `feature/02-github-workflow`).
- **`fix/<issue-id>-<name>`**: Dedicated bugfix branches.

#### 💬 Commit Conventions (Conventional Commits)
- `feat:` Introduces a new sprint concept or feature.
- `fix:` Patches a bug or regression in data pipelines.
- `docs:` Documentation or guideline updates.
- `test:` Adds or modifies automated unit tests.
- `refactor:` Code restructuring without functional changes.
- `chore:` Maintenance, configuration, or environment changes.

#### 📋 PR & Issue Templates
- Pull Request Template: [`.github/pull_request_template.md`](.github/pull_request_template.md)
- Issue Templates:
  - Sprint Concept Task: [`.github/ISSUE_TEMPLATE/concept_task.md`](.github/ISSUE_TEMPLATE/concept_task.md)
  - Bug Report: [`.github/ISSUE_TEMPLATE/bug_report.md`](.github/ISSUE_TEMPLATE/bug_report.md)
  - Feature Request: [`.github/ISSUE_TEMPLATE/feature_request.md`](.github/ISSUE_TEMPLATE/feature_request.md)

#### 🔍 Review & Quality Gate
1. All changes require feature branches (no direct commits to `main`).
2. Mandatory local validation (`python -m pytest` and `python main.py`) before opening PRs.
3. At least one peer review approval before merging.

---

### 03. Python Data Workflow Foundations

#### 🏗️ Architecture & Pipeline Flow
The project establishes a modular, reusable Python data processing architecture:

```text
┌─────────────────┐
│  Load Datasets  │ ➔ CSV / JSON loader with type detection (src/ingestion.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Inspect & Profile│ ➔ Shape, dtypes, nulls, duplicates, memory profiling (src/inspection.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Transform    │ ➔ Sanitized column names, type casting, datetime parsing (src/transformation.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Save & Export │ ➔ Processed CSV / JSON and SQLite database tables (src/storage.py)
└─────────────────┘
```

#### 📦 Reusable Workflow Components
1. **Ingestion Layer (`src/ingestion.py`):**
   - `load_dataset(file_path, format)` — Robust file loader supporting CSV, JSON, and Excel with error handling (`DataLoadError`).
   - `load_all_raw_data()` — Batch loader for all raw project datasets.
2. **Inspection Layer (`src/inspection.py`):**
   - `inspect_dataframe(df, dataset_name)` — Profiles row counts, column counts, missing values, duplicates, and memory footprint in MB.
   - `get_column_summary(df)` — Detailed column-level summary and distinct value profiling.
3. **Transformation Layer (`src/transformation.py`):**
   - `standardize_column_names(df)` — Cleans whitespace, lowercases, and replaces special characters with underscores.
   - `cast_column_types(df, type_mapping)` — Robust type casting.
   - `parse_datetime_columns(df, columns)` — Coerced datetime conversions.
   - `derive_column(df, new_col, func)` — Vectorized column derivations.
4. **Storage & Export Layer (`src/storage.py`):**
   - `save_dataframe(df, file_path, format)` — Saves dataframes to CSV or JSON with automatic directory creation.
   - `save_to_database(df, table_name, db_path)` — Persists DataFrames directly into SQLite tables.
5. **Workflow Orchestrator (`src/workflow.py`):**
   - `DataWorkflow` class providing a fluent interface: `.load() -> .inspect() -> .transform() -> .export()`.
6. **Error Handling & Timing (`src/utils.py`):**
   - Custom exceptions: `DataWorkflowError`, `DataLoadError`, `TransformationError`, `DataExportError`.
   - `@timed_step` decorator for benchmarking pipeline step execution times.

---

# 🟪 Phase 2 — Data Ingestion

### 04. Dataset Intake & Source Validation

#### 🛡️ Intake Validation Architecture
The validation layer (`src/validation.py`) enforces rigorous quality gates on raw datasets before downstream transformations:

```text
Incoming Dataset 
  │
  ├── 1. Physical File Validation ──► validate_file_source() [Existence, readability, non-empty 0-byte check, format]
  │
  ├── 2. Schema Structure Check   ──► validate_dataset_schema() [Required columns, column counts, missing keys]
  │
  ├── 3. Volume & Thresholds      ──► validate_row_thresholds() [Non-empty dataframe, minimum row limits]
  │
  └── 4. Entity-Level Integrity   ──► validate_entity_dataset() [Students, Sessions, Quizzes, Courses schemas]
```

#### 📋 Core Entity Schemas
- **`students`**: `student_id`, `registration_date`, `age`, `gender`, `education_level`, `device_type`, `target_course_id`, `completion_status`
- **`sessions`**: `session_id`, `student_id`, `course_id`, `session_start`, `session_end`, `duration_minutes`, `active_minutes`, `idle_minutes`
- **`quizzes`**: `quiz_attempt_id`, `student_id`, `course_id`, `quiz_id`, `attempt_number`, `attempt_date`, `score_percentage`, `time_taken_minutes`, `passed`
- **`courses`**: `course_id`, `course_title`, `category`, `total_modules`, `total_quizzes`, `estimated_duration_hours`

#### 🚨 Error Handling & Reporting
- Fails clearly with `ValidationError` when required columns, formats, or entity structures are violated.
- Returns structured `ValidationResult` objects with boolean `is_valid`, detailed `errors`, `warnings`, and dimension statistics.

---

### 05. CSV & JSON Data Ingestion

#### 📥 Multi-Source Ingestion Engine (`src/ingestion.py`)
The ingestion layer enables seamless ingestion of both CSV and JSON student datasets into Pandas DataFrames:

```text
┌─────────────────────────────────────────────────────────────┐
│                 Supported Core Entities                     │
├─────────────────┬──────────────────┬────────────────────────┤
│ Entity          │ CSV Source       │ JSON Source            │
├─────────────────┼──────────────────┼────────────────────────┤
│ Students        │ students.csv     │ students.json          │
│ Courses         │ courses.csv      │ courses.json           │
│ Sessions        │ sessions.csv     │ sessions.json          │
│ Quizzes         │ quizzes.csv      │ quizzes.json           │
└─────────────────┴──────────────────┴────────────────────────┘
```

#### ⚙️ Key Ingestion Capabilities
1. **`load_dataset(file_path, format, validate_source, entity_name)`:**
   - Universal dataset loader with format auto-detection (`csv`, `json`, `xlsx`).
   - Integrated source validation and entity-level schema checks.
   - Encoding resilience with automated Latin-1 fallback if UTF-8 fails.
2. **`read_json_flexible(file_path)`:**
   - Multi-orientation JSON reader supporting record lists, split arrays, and nested key-value dictionaries.
3. **`ingest_entity(entity_name, directory, preferred_formats)`:**
   - Reusable entity discoverer that locates and ingests whichever format is present.
4. **`ingest_all_entities(directory, preferred_formats)`:**
   - Batch intake loader returning a dictionary of all 4 project DataFrames.

---

# 🟩 Phase 3 — Data Cleaning

### 06. Dataset Profiling & Quality Assessment

#### 📊 Reusable Profiling Engine (`src/profiling.py`)
The profiling engine generates structured quality assessments across all ingested datasets without modifying raw records:

```text
Dataset Input
  │
  ├── 1. Volume & Memory Metrics ──► Rows, Columns, Total Cells, Memory Usage (MB)
  │
  ├── 2. Integrity & Quality     ──► Duplicate Counts, Missing Cell %, Completeness %, Quality Score (0-100)
  │
  ├── 3. Column-Level Profiles   ──► Data Types, Null Frequencies, Unique Counts, Top Sample Values
  │
  ├── 4. Numerical Summaries     ──► Mean, Std Dev, Min, 25%, Median (50%), 75%, Max
  │
  └── 5. Categorical Summaries   ──► Distinct Categories, Mode, Frequency Distribution
```

#### 📋 Structured Profiling Data Structures
- **`DatasetProfile`**: Structured dataclass encapsulating all dimensional, column-level, and statistical indicators.
- **`profile_dataset(df, dataset_name)`**: Generates a complete profile object for a single dataset.
- **`profile_all_datasets(datasets)`**: Batch profiles all ingested entities.
- **`generate_quality_scorecard(datasets)`**: Produces a consolidated comparative scorecard DataFrame ready for Streamlit dashboard display.
- **`to_column_summary_df()` & `to_numerical_summary_df()`**: Formats profiling metadata into Pandas DataFrames for interactive tabular viewing.

---

### 07. Data Dictionary & Business Context Mapping

#### 📖 Full Data Dictionary
See detailed technical specification: [`docs/data_dictionary.md`](docs/data_dictionary.md) and programmatic interface in `src/data_dictionary.py`.

#### 🧭 Business Context Mapping for Key Analytics Columns

| Column Name | Technical Type | Required | Valid Range / Categories | Business Definition | Analysis Application |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`student_id`** | `string` | **Yes** | Unique alphanumeric ID | Platform learner identifier. | Key for student-level aggregations, cohort tracking, and risk models. |
| **`course_id`** | `string` | **Yes** | Unique alphanumeric ID | Course catalog identifier. | Baseline for curriculum difficulty and course completion KPIs. |
| **`session_date`** | `date` | **Yes** | `YYYY-MM-DD` | Calendar day of learning. | Daily active users (DAU), day-of-week habits, and study regularity. |
| **`session_duration`** | `float` | **Yes** | `0.1` to `600.0` mins | Total session duration. | Platform engagement depth and gross learning time. |
| **`quiz_score`** | `float` | **Yes** | `0.0` to `100.0%` | Graded quiz exam score. | Academic performance KPI and knowledge competency indicator. |
| **`progress_pct`** | `float` | **Yes** | `0.0` to `100.0%` | Course modules completed %. | Progress velocity, milestone tracking, and dropout points. |
| **`completion_status`** | `string` | **Yes** | `Completed`, `Dropped`, `In Progress` | Ground-truth outcome. | Target variable for dropout prediction models and business reporting. |

---

### 08. Missing Value Detection & Imputation

#### 🧹 Domain-Specific Imputation Rules (`src/imputation.py`)
Rather than blindly filling missing entries with zeros, the pipeline implements business-driven imputation strategies:

```text
Missing Value Detection
  │
  ├── 1. Primary / Foreign Key Nulls ──► Dropped (Records cannot be safely recovered without learner ID)
  │
  ├── 2. Numerical Demographics (Age) ──► Median Imputation (Preserves distribution without artificial skew)
  │
  ├── 3. Categorical Attributes       ──► Explicit Category 'Unknown' (Preserves absence of information)
  │
  ├── 4. Session Time Components      ──► Delta Recovery (duration = active + idle, active = duration - idle)
  │
  └── 5. Assessment Metrics (Quizzes) ──► Quiz-Specific Median Score & Logical Pass/Fail derivation
```

#### 📋 Treatment Rules Matrix

| Entity | Column | Treatment Strategy | Business Rationale |
| :--- | :--- | :--- | :--- |
| **`students`** | `student_id` | **Drop Null Row** | Core primary key; unidentifiable learner records cannot be analyzed. |
| **`students`** | `age` | **Median Imputation** | Preserves learner demographic distribution without zero-skewing. |
| **`students`** | `gender`, `education_level`, `device_type` | **Explicit `'Unknown'`** | Categorical transparency; prevents false classification. |
| **`courses`** | `category` | **Explicit `'General'`** | Fallback course classification. |
| **`sessions`** | `duration_minutes` | **`active_minutes + idle_minutes` / Median** | Recovers total elapsed session time mathematically. |
| **`sessions`** | `active_minutes` | **`duration_minutes - idle_minutes` / Median** | Derives real active study duration. |
| **`quizzes`** | `score_percentage` | **Quiz Median Score** | Replaces nulls with typical cohort exam achievement (never zero). |
| **`quizzes`** | `passed` | **Derived (`score >= 70%`)** | Consistent boolean flag derived from final score. |

#### 📊 Quality Audit Reporting
- **`ImputationReport`**: Tracks initial vs. final rows, dropped records, cell completeness percentage before & after, and per-column action logs.
- **`detect_missing_values(df)`**: Audits missingness frequency across datasets.

---

### 09. Data Type Enforcement & Standardisation

#### 🔠 Standardisation & Type Enforcement Layer (`src/standardization.py`)
The pipeline standardizes heterogeneous, messy data inputs into clean, SQL-ready, strictly typed representations:

```text
Raw Inconsistent Values ────────► Standardized Schema Type
-----------------------------------------------------------
"85%", " 92.5 % ", 0.85 ────────► 85.0, 92.5 (Float)
"2026/08/01", "01-08-2026" ─────► datetime64 / "YYYY-MM-DD"
"s001", " stu_102 " ────────────► "S001", "STU_102" (Uppercase String)
"completed", "passed" ──────────► "Completed" (Domain Category)
"undergrad", "bachelors" ───────► "Undergraduate" (Domain Category)
"PASS", "true", "1", True ──────► 1 (Integer Boolean Flag)
"FAIL", "false", "0", False ────► 0 (Integer Boolean Flag)
```

#### 🛠️ Standardisation Functions
- **`clean_percentage_value(val)`**: Converts string percentages and fractional numbers into standardized `0.0`–`100.0` floats.
- **`clean_boolean_flag(val)`**: Maps diverse truthy/falsy inputs (`PASS`, `FAIL`, `true`, `false`, `1`, `0`) to integer flags (`1` or `0`).
- **`standardize_identifiers(df, id_cols)`**: Trims whitespace, strips string artifacts, and converts identifiers to uppercase.
- **`standardize_dates(df, date_cols)` & `standardize_timestamps(df, ts_cols)`**: Parses dates into `datetime64` and ISO-standard strings (`YYYY-MM-DD` / `YYYY-MM-DD HH:MM:SS`).
- **`standardize_categories(df)`**: Applies domain synonym mapping for `completion_status`, `gender`, `device_type`, and `education_level`.
- **`standardize_entity(df, entity_name)`**: Orchestrates all standardizations per entity model for seamless SQLite insertion.

---

### 10. Duplicate Detection & Record Deduplication

#### 🔍 Business-Key Deduplication Engine (`src/deduplication.py`)
Rather than blindly dropping arbitrary rows, the engine performs structured multi-stage deduplication:

```text
Deduplication Strategy
  │
  ├── Stage 1: Exact Full-Row Deduplication ──► Eliminates identical telemetry replay events
  │
  └── Stage 2: Business-Key Deduplication   ──► Resolves record collisions via domain tie-breaking:
        ├── Students:  Key = student_id          ──► Preserves most complete non-null record
        ├── Courses:   Key = course_id           ──► Preserves curriculum with highest module detail
        ├── Sessions:  Key = session_id / Comp.  ──► Preserves record with highest active duration
        └── Quizzes:   Key = quiz_attempt_id     ──► Preserves record with highest validated score
```

#### 📋 Business Keys & Tie-Breaking Matrix

| Entity | Primary Business Key | Composite Natural Key | Tie-Breaking Strategy |
| :--- | :--- | :--- | :--- |
| **`students`** | `student_id` | `[student_id, target_course_id]` | Keeps record with maximum non-null profile completeness. |
| **`courses`** | `course_id` | `[course_id]` | Keeps record with highest `total_modules` and title details. |
| **`sessions`** | `session_id` | `[student_id, course_id, session_start]` | Keeps record with highest `duration_minutes` & `active_minutes`. |
| **`quizzes`** | `quiz_attempt_id` | `[student_id, quiz_id, attempt_number]` | Keeps record with highest `score_percentage` and pass validation. |

#### 📊 Quality Scorecards & Reporting
- **`DeduplicationReport`**: Captures initial rows, final rows, exact duplicates removed, business-key duplicates removed, and duplicate percentages.
- **`generate_deduplication_scorecard(reports)`**: Builds comparative deduplication scorecard DataFrames for Streamlit dashboard visualization.

---

### 11. String Cleaning & Text Normalisation

#### 🔤 Reusable Text Cleaning Suite (`src/text_cleaning.py`)
Provides granular text sanitisation while safeguarding technical abbreviations and alphanumeric identifiers:

```text
Raw Inconsistent Text ─────────────────► Clean Standardized String
-------------------------------------------------------------------
"   Data Science   " ──────────────────► "Data Science" (Whitespace Trimmed)
"Python   for    Data   Science" ──────► "Python for Data Science" (Multi-Space Collapsed)
"intro to machine learning (ai/ml)" ───► "Intro to Machine Learning (AI/ML)" (Acronyms Preserved)
"advanced sql and aws architecture" ───► "Advanced SQL and AWS Architecture"
"web dev", "web-dev", "frontend" ──────► "Web Development" (Canonical Domain)
"cyber security", "cyber-sec" ─────────► "Cybersecurity" (Canonical Domain)
"ds", "data_science", "DATA SCIENCE" ──► "Data Science" (Canonical Domain)
```

#### 🛠️ Text Cleaning Modules
- **`normalize_whitespace(text)`**: Cleans tabs (`\t`), newlines (`\n`), non-breaking spaces (`\xa0`), and collapses internal consecutive whitespace.
- **`clean_text_string(text, casing)`**: Applies intelligent grammar-aware title casing, keeping grammatical particles lowercase and capitalizing technical acronyms (`AI`, `ML`, `SQL`, `AWS`, `GCP`, `API`, `HTML`, `CSS`, `JS`, `UI`, `UX`).
- **`clean_course_title(title)`**: Sanitizes catalog titles with acronym preservation (e.g. `(AI/ML)`).
- **`clean_category_label(category)`**: Maps informal subject aliases into canonical vertical categories.
- **`clean_text_dataframe(df, entity_name)`**: Applies vectorized text standardisation across all string columns in an entity DataFrame.

---

### 12. Date & Time Transformation Pipeline

#### ⏳ Temporal Feature Extraction Engine (`src/datetime_pipeline.py`)
Converts raw timestamps and session telemetry into rich time-series and behavioral features:

```text
Raw Timestamp ("2026-08-01 09:15:00")
  │
  ├── 1. Calendar Components ──► date ("2026-08-01"), year (2026), month (8), month_name ("August"), day (1)
  │
  ├── 2. Weekly & Day Pacing  ──► weekday (5), weekday_name ("Saturday"), is_weekend (1), week / week_number (31)
  │
  └── 3. Diurnal Activity     ──► hour (9), day_part ("Morning" / "Afternoon" / "Evening" / "Night")
```

#### 🛠️ Core Transformation Capabilities
- **`parse_datetime_series(series, strip_timezone)`**: Robustly parses diverse date formats into UTC / timezone-naive `datetime64[ns]`, coercing corrupted records to `NaT` safely.
- **`extract_datetime_features(df, col, prefix)`**: Automatically derives 12 standardized date/time attributes per timestamp column.
- **`categorize_day_part(hour)`**: Classifies study times into behavioral buckets (`Morning`, `Afternoon`, `Evening`, `Night`).
- **`calculate_session_duration_minutes(df)`**: Mathematically derives active study duration from `session_end - session_start`.
- **`transform_entity_datetimes(df, entity_name)`**: Enriches sessions, students, and quizzes with time-series features for behavioral cohort analysis.

---

### 13. Outlier Detection with Statistical Methods

#### 📈 Non-Destructive Statistical Outlier Engine (`src/outliers.py`)
Rather than blindly deleting records with unusual values, the engine mathematically detects and classifies records while preserving the underlying telemetry:

```text
Numerical Feature Input
  │
  ├── 1. IQR Method    ──► Normal: [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
  │                        Mild Outlier: (1.5*IQR to 3.0*IQR)
  │                        Extreme Outlier: (> 3.0*IQR)
  │
  ├── 2. Z-Score Method ──► Normal: |Z| < 3.0
  │                        Outlier: |Z| >= 3.0, Extreme: |Z| >= 3.5
  │
  └── 3. Domain Check  ──► Domain Anomaly (e.g. score > 100%, session < 0 mins, duration > 12h)
```

#### 📋 Monitored Telemetry Variables

| Variable Name | Method | Normal Range / Bounds | Classification Tiers |
| :--- | :--- | :--- | :--- |
| **`duration_minutes`** | **IQR** | $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$ | `Normal`, `Mild Outlier` (Power study), `Extreme Outlier`, `Domain Anomaly` ($>720$m). |
| **`score_percentage`** | **Z-Score** | $|Z| < 3.0$ & $[0.0, 100.0\%]$ | `Normal`, `Mild Outlier`, `Domain Anomaly` ($<0\%$ or $>100\%$). |
| **`progress_pct`** | **Domain / IQR** | $[0.0, 100.0\%]$ | `Normal`, `Domain Anomaly` ($>100\%$). |
| **`active_minutes`** | **IQR** | $\le \text{duration\_minutes}$ | `Normal`, `Extreme Outlier`, `Domain Anomaly` ($>\text{duration}$). |

#### 📊 Outlier Reports & Scorecards
- **`ColumnOutlierSummary`**: Statistical breakdown capturing $Q_1$, $Q_3$, $IQR$, mean, std dev, lower/upper bounds, and anomaly frequencies.
- **`tag_dataset_outliers(df, entity_name)`**: Enriches records with `{col}_is_outlier` binary flags and `{col}_outlier_class` tags for downstream investigation and dashboard filtering without row loss.
- **`generate_outlier_scorecard(reports)`**: Builds multi-entity comparative outlier scorecards for Streamlit monitoring.

---

### 14. Data Consistency & Validation Rules

#### ⚖️ Business Consistency Engine (`src/consistency.py`)
Enforces domain rules and cross-entity relationship constraints with full audit tracking:

```text
Business Rule Validation Checks
  │
  ├── 1. Assessment Scores   ──► 0.0 <= score_percentage <= 100.0%
  │
  ├── 2. Learning Progress   ──► 0.0 <= progress_pct <= 100.0%
  │
  ├── 3. Session Durations   ──► duration_minutes > 0.0 (Strictly Positive)
  │
  ├── 4. Categorical Status  ──► completion_status in {'Completed', 'In Progress', 'Dropped', 'Inactive'}
  │
  ├── 5. Logical Timestamps  ──► session_start <= session_end
  │
  └── 6. Cross-Entity Timing ──► student registration_date <= activity date (session_start / attempt_date)
```

#### 📋 Business Rules Matrix

| Rule Name | Target Column / Entity | Constraint Definition | Action on Violation |
| :--- | :--- | :--- | :--- |
| **Score Bounds** | `quizzes.score_percentage` | $0.0 \le \text{score} \le 100.0\%$ | Logged in `RuleViolation` audit trail. |
| **Progress Bounds** | `students.progress_pct` | $0.0 \le \text{progress} \le 100.0\%$ | Logged in `RuleViolation` audit trail. |
| **Positive Duration** | `sessions.duration_minutes` | $\text{duration} > 0.0$ mins | Logged in `RuleViolation` audit trail. |
| **Approved Status** | `students.completion_status` | Status in approved category domain | Flagged for remediation. |
| **Valid Identifiers** | `*_id` across all entities | Non-empty, no `"NAN"`/`"NULL"` strings | Flagged in audit report. |
| **Session Sequence** | `sessions.session_start/end` | $\text{session\_start} \le \text{session\_end}$ | Flagged in audit report. |
| **Enrollment Precedence** | Cross-Entity (`students` + `sessions`) | $\text{registration\_date} \le \text{session\_date}$ | Flagged in audit report. |

#### 📊 Validation Reports & Audit Logging
- **`RuleViolation`**: Structured error log capturing rule name, entity, row index, record ID, invalid value, reason, and action taken.
- **`ConsistencyReport`**: Captures total checked records, passed count, violation count, and pass percentage.
- **`generate_consistency_scorecard(reports)`**: Builds a comparative multi-entity rule compliance scorecard for Streamlit and analytics audit.

---

### 15. Multi-Source Merging & Join Validation

#### 🔗 Relational Merging Pipeline (`src/merging.py`)
Combines disparate student profile, course catalog, session telemetry, and quiz assessment entities into unified analytical tables with strict join validation:

```text
Students (Base: 1 Row/Student)
  │
  ├── 1. Left Join Courses           ──► target_course_id == course_id (Course dimensions)
  │
  ├── 2. Left Join Aggregated Sessions──► student_id == student_id (Study volume, active minutes, frequency)
  │
  ├── 3. Left Join Aggregated Quizzes ──► student_id == student_id (Attempts, pass rate, avg score, progress %)
  │
  └── 4. Output: Student 360 Dataset  ──► Preserves exact student granularity (Expansion factor: 1.00x)
```

#### 📋 Relational Join Keys & Aggregations

| Entity Pair | Join Key(s) | Join Type | Aggregation Strategy / Output |
| :--- | :--- | :--- | :--- |
| **`Students` + `Courses`** | `target_course_id` $\rightarrow$ `course_id` | `LEFT` | Adds `course_title`, `category`, `total_modules`, `total_quizzes`. |
| **`Students` + `Sessions`** | `student_id` $\rightarrow$ `student_id` | `LEFT` | Pre-aggregates `total_sessions`, `total_duration_minutes`, `active_learning_ratio`. |
| **`Students` + `Quizzes`** | `student_id` $\rightarrow$ `student_id` | `LEFT` | Pre-aggregates `total_quiz_attempts`, `quizzes_passed`, `avg_quiz_score`, `quiz_pass_rate`. |

#### 📊 Join Validation & Orphan Auditing
- **`validate_two_table_join()`**: Tracks unmatched left rows, unmatched right rows, and duplicate expansion factors ($> 1.0$ alerts on Cartesian product fan-out).
- **`build_student_360_dataset()`**: Generates student 360 master table while maintaining strict 1-to-1 learner grain.
- **`JoinAuditReport`**: Exposes orphan diagnostics (unregistered students with sessions, inactive students with 0 logins, unassessed students) without hiding data gaps.

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
