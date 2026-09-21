# Product Requirements Document

## 1. Product

**Learning Behaviour & Course Completion Intelligence** is a batch analytics product for an EdTech platform. It converts student, course, session, and quiz data into data-quality reports, learner behavior features, course-completion KPIs, and dropout-risk segments for educators and business stakeholders.

This PRD describes the product represented by the repository as of September 2026. The repository is primarily a Python analytics and reporting system; it is not yet a production online prediction service.

## 2. Problem Statement

The platform has activity and assessment data but lacks a repeatable way to answer:

- Which learning behaviors correlate with completion?
- Which learners are disengaging or becoming inactive?
- Which courses, demographics, or devices show weak outcomes?
- Can stakeholders inspect data quality before trusting the metrics?

The product must make those questions answerable from reproducible, auditable data transformations rather than manual spreadsheet work.

## 3. Users and Decisions

| User | Primary decisions | Required outputs |
| --- | --- | --- |
| Academic or course teams | Find low-performing courses and intervention cohorts | Completion, quiz, progress, and engagement breakdowns |
| Student-success teams | Prioritize outreach | High/critical dropout-risk learners and inactivity indicators |
| Business stakeholders | Monitor platform health | Executive KPIs and category summaries |
| Data engineers/analysts | Trust and operate the pipeline | Schema checks, profiling, validation, join, deduplication, and audit reports |
| Developers | Extend the product safely | Modular APIs, tests, typed contracts, and deterministic local execution |

## 4. Goals

1. Ingest supported learning datasets from CSV, JSON, or Excel files.
2. Reject or flag malformed, empty, incomplete, and inconsistent data before analytics.
3. Clean duplicate records, missing values, text, identifiers, categories, dates, timestamps, and types with auditable decisions.
4. Build one Student 360 analytical row per student by aggregating session and quiz events before joining them to student and course data.
5. Compute interpretable engagement, progress, consistency, inactivity, completion, and dropout-risk features.
6. Persist analytical data in SQLite and expose repeatable SQL business metrics and cohort analyses.
7. Provide a Streamlit entry point for stakeholder-facing views and preserve automated test coverage.

## 5. Non-goals

- Real-time event ingestion or streaming computation.
- A trained machine-learning model; risk is a deterministic score, not a calibrated probability.
- Automated student messaging or intervention execution.
- Multi-tenant authorization, cloud deployment, or enterprise data governance.
- Replacing the standalone educational scripts for customer/order analytics; those scripts are supporting sprint exercises, not part of the EdTech domain model.

## 6. Functional Requirements

### FR-1: Intake

- Discover `students`, `courses`, `sessions`, and `quizzes` in `data/raw/`.
- Support `.csv`, `.json`, `.xlsx`, and `.xls` where the ingestion API is used.
- Support flexible JSON orientations and CSV encoding fallback.
- Allow callers to pass a path or in-memory DataFrame dictionary.
- Return a structured load error for missing, unreadable, malformed, or unsupported sources.

### FR-2: Schema and quality validation

- Validate required columns and minimum row count for each core entity.
- Validate source existence, file size, and extension.
- Apply business rules for identifiers, statuses, age, session duration/timestamps, quiz scores, and related fields.
- Produce structured errors, warnings, row counts, column counts, missing columns, rule summaries, and violation records.
- Preserve invalid records for audit when a rule validator flags them; do not silently rewrite them.

### FR-3: Cleaning and standardization

- Remove exact and entity-specific business-key duplicates with deterministic tie-breaking.
- Apply entity-aware missing-value strategies.
- Normalize whitespace, text, IDs, dates, timestamps, category synonyms, percentages, and boolean flags.
- Record deduplication and imputation decisions in output artifacts where applicable.
- Keep transformations idempotent where practical and avoid mutating caller-owned DataFrames.

### FR-4: Relational integration

- Join students to courses using `students.target_course_id = courses.course_id`.
- Aggregate sessions and quizzes to one row per student before joining to prevent one-to-many Cartesian multiplication.
- Use left joins so every student remains in the Student 360 population.
- Report unmatched left/right records, joined row counts, expansion factors, and join steps.

### FR-5: Feature and risk analytics

- Derive session, quiz, progress, temporal, consistency, engagement, and inactivity features.
- Compute engagement on a 0-100 scale and dropout risk on a 0-100 scale.
- Classify risk as Low, Moderate, High, or Critical.
- Use an explicit benchmark/as-of date for reproducible recency calculations.
- Expose feature formulas in a machine-readable feature dictionary.

### FR-6: Storage and SQL analytics

- Initialize `data/database/learning_analytics.db` from `sql/schema.sql`.
- Load core tables and `behavioural_features` with controlled replace/append/fail behavior.
- Validate expected table existence and row counts after loading.
- Execute named queries from `sql/business_metrics.sql` and `sql/aggregation.sql`.
- Produce JSON summaries for executive KPIs and aggregation results.

### FR-7: Presentation

- Provide a Streamlit dashboard entry point with overview, engagement, risk, and SQL analytics navigation.
- Render KPI cards and reusable header components.
- The current implementation must be treated as a shell: its displayed KPI values are placeholders and it does not yet read SQLite results.

## 7. Data Contracts

Core required fields are defined in `src/validation.py` and detailed in `docs/data_dictionary.md`.

- Students: `student_id`, `registration_date`, `age`, `gender`, `education_level`, `device_type`, `target_course_id`, `completion_status`.
- Courses: `course_id`, `course_title`, `category`, `total_modules`, `total_quizzes`, `estimated_duration_hours`.
- Sessions: `session_id`, `student_id`, `course_id`, `session_start`, `session_end`, `duration_minutes`, `active_minutes`, `idle_minutes`.
- Quizzes: `quiz_attempt_id`, `student_id`, `course_id`, `quiz_id`, `attempt_number`, `attempt_date`, `score_percentage`, `time_taken_minutes`, `passed`.

Relational keys are `student_id`, `course_id`, `session_id`, and `quiz_attempt_id`. Foreign-key intent is represented in SQLite schema, while pandas joins and SQLite loading are the operational integration mechanisms.

## 8. Success Metrics and Acceptance Criteria

- A valid local dataset can be ingested, profiled, transformed, and exported without manual edits.
- Invalid source/schema data produces actionable structured validation output.
- Student 360 output retains one analytical row per student and has no unintended many-to-many expansion.
- Engagement and risk outputs remain within their documented ranges.
- SQLite initialization, loading, row-count validation, KPI queries, and aggregation queries pass automated tests.
- Test suite covers the core modules and regression-sensitive calculations.
- Stakeholders can trace a KPI back to its SQL query and source table.

## 9. Non-functional Requirements

- **Reproducibility:** deterministic synthetic data uses fixed random seeds; risk calculations accept an explicit as-of date.
- **Auditability:** validation, deduplication, join, imputation, and export operations expose reports or logs.
- **Maintainability:** domain functionality stays in `src/`; scripts remain executable adapters and examples.
- **Performance:** use pandas/NumPy vectorization for batch calculations and pre-aggregate event tables before joins.
- **Portability:** Python 3.10+, SQLite, and local filesystem operation; Windows console output is handled by the entry point.
- **Failure visibility:** exceptions are typed as workflow, load, validation, transformation, or export errors and timed steps log failures.

## 10. Risks and Open Product Decisions

- Risk scores are heuristic and require calibration and outcome monitoring before intervention use.
- The generic `main.py` path does not currently execute cleaning, Student 360 feature engineering, or SQL report generation end to end.
- Dashboard KPI values are hard-coded placeholders and must be connected to `execute_business_metrics` before being used for decisions.
- Sample-data fallback in `scripts/sql_integration.py` can make a run appear healthy without real source data; the report must identify whether data is synthetic.
- SQLite is appropriate for local batch analytics but not concurrent production serving.
- The repository contains customer/order sprint scripts with separate schemas and business semantics; they should not be mixed into EdTech production tables.

## 11. Delivery Priorities

1. Keep the tested ingestion, validation, transformation, merge, feature, and SQL paths stable.
2. Connect the dashboard to SQLite reports and replace hard-coded metrics.
3. Add a single documented production orchestration command that performs cleaning, Student 360 construction, feature generation, database load, and report export.
4. Add model calibration, data freshness metadata, access control, and deployment only after the batch product is operationally coherent.
