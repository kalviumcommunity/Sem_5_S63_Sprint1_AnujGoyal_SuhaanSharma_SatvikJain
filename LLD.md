# Low-Level Design

## 1. Package Map

| Area | Files | Responsibility |
| --- | --- | --- |
| Configuration | `src/utils.py` | Root paths, logger, timed decorator, workflow exceptions |
| Intake | `src/ingestion.py` | File readers, JSON orientation handling, entity discovery |
| Validation | `src/validation.py`, `src/consistency.py` | Structural and business-rule checks |
| Inspection | `src/inspection.py`, `src/profiling.py` | DataFrame shape, column, statistical, and quality profiles |
| Cleaning | `src/cleaning.py`, `src/deduplication.py`, `src/imputation.py`, `src/text_cleaning.py` | Composite cleaning and audit reports |
| Standardization | `src/standardization.py`, `src/transformation.py`, `src/datetime_pipeline.py` | Names, types, categories, IDs, dates, timestamps |
| Integration | `src/merging.py` | Aggregation, validated joins, Student 360 |
| Features | `src/features.py`, `src/feature_engineering.py` | Behavioral features; baseline placeholder is separate |
| Numeric scoring | `src/vectorization.py` | Vectorized formulas and risk tiers |
| Persistence | `src/storage.py`, `src/database.py` | CSV/JSON/SQLite persistence and query execution |
| UI | `dashboard/app.py`, `dashboard/components.py`, `dashboard/utils.py` | Streamlit shell and reusable UI helpers |
| SQL | `sql/schema.sql`, `sql/business_metrics.sql`, `sql/aggregation.sql` | Relational schema and named analytics |
| Adapters | `scripts/*.py` | Standalone educational pipelines and SQL runners |

## 2. Core Interfaces

### `run_pipeline(source_data=None, save_to_db=True) -> Dict[str, Any]`

Located in `src/pipeline.py`. Ensures directories, initializes SQLite, invokes `DataWorkflow.run_full_pipeline`, optionally validates expected tables, and returns status, loaded datasets, transformed datasets, database status, and row counts.

### `DataWorkflow`

Stateful orchestration object with these state dictionaries:

- `raw_data: Dict[str, DataFrame]`
- `validation_results: Dict[str, Any]`
- `inspections: Dict[str, Dict[str, Any]]`
- `profiles: Dict[str, DatasetProfile]`
- `transformed_data: Dict[str, DataFrame]`

Methods are chainable for `load`, `validate`, `inspect`, and `transform`; `export` returns saved paths. `run_full_pipeline` returns a summary rather than throwing for ordinary validation failures unless `raise_on_validation_error=True` is passed.

### Ingestion contracts

`load_dataset(path, format=None, validate_source=False, entity_name=None, **kwargs)` returns a DataFrame or raises `DataLoadError`/`ValidationError`. `ingest_all_entities()` returns a dictionary containing all four supported entity names, using empty DataFrames when files are absent.

### Validation contracts

`ValidationResult` contains `is_valid`, dataset name, errors, warnings, row/column counts, and missing columns. `validate_intake_pipeline` returns an overall status and per-entity dictionaries. `ConsistencyReport` contains total/valid/invalid counts, pass rate, rule summaries, and `RuleViolation` objects.

## 3. Data Processing Details

### 3.1 Intake and generic workflow

```text
source path or DataFrame dictionary
    -> load_dataset/load_all_raw_data
    -> validate_intake_pipeline
    -> inspect_dataframe + profile_dataset
    -> standardize_column_names
    -> optional cast_column_types
    -> optional parse_datetime_columns
    -> save_dataframe and/or save_to_database
```

The generic workflow does not automatically invoke the richer `clean_dataframe`, Student 360 merge, or behavioral feature functions. Those are invoked by dedicated callers, especially the SQL integration script.

### 3.2 Cleaning order

`clean_dataframe` applies the following order when enabled:

1. `deduplicate_dataset`: exact duplicates, then entity business-key duplicates.
2. `clean_text_dataframe`: whitespace/text normalization.
3. `impute_dataset`: entity-aware null treatment.
4. `standardize_entity`: identifiers, dates, categories, numeric fields, and booleans.

Entity primary/business keys are students=`student_id`, courses=`course_id`, sessions=`session_id`, quizzes=`quiz_attempt_id`. Tie-breaking retains the most complete student, higher course module count, longer/more active session, or higher quiz score where those fields exist.

### 3.3 Student 360 join algorithm

`build_student_360_dataset` performs:

1. `students LEFT JOIN courses` on `target_course_id = course_id`.
2. `sessions GROUP BY student_id` to calculate counts, duration totals, active ratio, and last session date.
3. Left join aggregated sessions to the student/course frame; fill missing activity metrics with zero.
4. `quizzes GROUP BY student_id` to calculate attempts, passed/failed counts, score averages, pass rate, and latest quiz date.
5. Left join aggregated quizzes; fill missing assessment metrics with zero.
6. Compute `progress_pct = quizzes_passed / total_quizzes * 100`, clamped to 0-100.
7. Return the frame plus `JoinAuditReport`.

The pre-aggregation step is the key cardinality safeguard: event rows are reduced to one row per student before Student 360 joins.

### 3.4 Behavioral feature formulas

Given the Student 360 row and benchmark date:

- `tenure_weeks = max((benchmark_date - registration_date).days, 1) / 7`.
- `average_session_duration = total_duration_minutes / max(total_sessions, 1)`.
- `sessions_per_week = total_sessions / tenure_weeks`.
- `quiz_average = avg_quiz_score`.
- `quiz_attempt_count = total_quiz_attempts`.
- `course_progress = progress_pct`, clamped to 0-100, or passed quizzes divided by total quizzes.
- `progress_velocity = course_progress / tenure_weeks`.
- `days_since_last_activity = benchmark_date - max(last session, latest quiz, registration)`, lower bounded at zero.
- `completion_rate = 1.0` for normalized `Completed`, otherwise `0.0`.
- `learning_consistency = 0.6 * min(1, total_sessions / (tenure_weeks * 2)) + 0.4 * active_learning_ratio`.
- `engagement_score = 0.30*progress + 0.25*quiz_pass_rate + 0.25*min(100, sessions_per_week*25) + 0.20*(active_learning_ratio*100)`.

### 3.5 Dropout risk

`compute_vectorized_dropout_risk` clamps inputs, then calculates:

```text
base_risk = 100 - engagement_score
inactivity_penalty = min(40, days_since_last_activity * 1.5)
quiz_penalty = (50 - quiz_pass_rate) * 0.4 when quiz_pass_rate < 50, otherwise 0
risk = 0.50*base_risk + 0.35*inactivity_penalty + 0.15*quiz_penalty
```

The final score is clipped to `[0, 100]` and classified as:

| Score | Tier |
| --- | --- |
| 0 <= score < 25 | Low |
| 25 <= score < 50 | Moderate |
| 50 <= score < 75 | High |
| 75 <= score <= 100 | Critical |

This is a deterministic heuristic. It is not a probability and has no model calibration or confidence interval.

## 4. SQLite Design

### Tables

- `courses`: catalog attributes; primary key `course_id`.
- `students`: learner attributes and outcome; primary key `student_id`; target-course foreign key.
- `sessions`: event-level activity; primary key `session_id`; student/course foreign keys.
- `quizzes`: attempt-level assessment data; primary key `quiz_attempt_id`; student/course foreign keys.
- `student_behaviour_summary`: reserved summary table, defined in schema.
- `behavioural_features`: one row per student with derived metrics and risk tier.

`save_to_database` uses pandas `to_sql`; the default strategy is `replace`. `init_database` executes the whole schema script. `validate_database_insertion` checks expected table names and counts, not all column-level constraints.

### Named query loading

`load_sql_queries_from_file` parses `-- Name: query_name` markers and returns query strings. `execute_business_metrics` maps single-row queries into a KPI dictionary and stores `metrics_by_category` separately. `execute_aggregation_queries` uses the same named-query pattern for cohort results.

Business metrics include completion rate, dropout rate, average quiz score, average session duration, active learners, at-risk learners, executive KPI overview, and category breakdown. Aggregations cover course performance, learner/device segments, inactivity risk, age cohorts, and quiz performance.

## 5. Output Contracts

- Processed DataFrames: CSV under configured processed/output directories.
- SQL integration: `output/sql_integration_summary.json`.
- Business KPIs: `output/business_metrics_report.json`.
- SQL aggregations: `output/sql_aggregation_report.json`.
- Join audits: `output/join_decision_report.json`, unmatched CSVs, or `JoinAuditReport` objects.
- Cleaning audits: deduplication summaries, removed-record CSV, imputation decisions, validation failures, and dtype conversion report.

## 6. Error and Logging Behavior

All major workflow steps use `timed_step`, which logs start, completion duration, and failure before re-raising. Persistence wraps failures as `DataExportError`; ingestion wraps reader failures as `DataLoadError`; schema/business failures use `ValidationError`. Empty DataFrames generally pass through as empty outputs so callers can decide whether absence is fatal.

## 7. Test Design

Pytest tests cover:

- Environment and dependency availability.
- CSV/JSON ingestion and malformed/unsupported sources.
- Schema, source, business consistency, profiling, and workflow orchestration.
- Deduplication, imputation, standardization, string/date cleaning, and outlier helpers.
- Student 360 joins and aggregation cardinality.
- Feature formulas, vectorized parity, ranges, risk tiers, and benchmark behavior.
- SQLite schema, inserts, row-count validation, named business metrics, and aggregations.
- Standalone customer/order, customer feature, data validation, datetime, and cleaning scripts.

The expected verification command is `python -m pytest`. Tests are mostly unit/integration tests with temporary directories/databases; no external service or browser automation is required.

## 8. Extension Rules

- Add new entities to `SUPPORTED_ENTITIES`, `ENTITY_SCHEMAS`, SQL schema, ingestion tests, and data dictionary together.
- Add a feature formula to `FEATURE_FORMULAS`, implementation, feature tests, and output documentation together.
- Do not join raw one-to-many event tables directly to the student universe; aggregate first.
- Preserve audit objects when adding cleaning or validation behavior.
- Keep SQL query names unique and maintain the `-- Name:` convention.
- Connect UI values to query results rather than duplicating formulas in Streamlit.
