# Sprint Concept-to-File Mapping

This mapping is an evidence index for the 50 Sprint concepts. `Implemented` means
there is executable code and/or tests in the referenced files. `Documented gap`
means the concept is described in the project but does not have a dedicated
implementation that should be claimed as complete.

| # | Concept | Status | Primary evidence |
|---:|---|---|---|
| 1 | Development environment and workspace setup | Implemented | [pyproject.toml](../pyproject.toml), [requirements.txt](../requirements.txt), [tests/test_environment.py](../tests/test_environment.py) |
| 2 | GitHub repository and team workflow | Implemented | [CONTRIBUTING.md](../CONTRIBUTING.md), [.github/pull_request_template.md](../.github/pull_request_template.md) |
| 3 | Python data workflow foundations | Implemented | [src/workflow.py](../src/workflow.py), [tests/test_workflow.py](../tests/test_workflow.py) |
| 4 | Dataset intake and source validation | Implemented | [src/validation.py](../src/validation.py), [tests/test_validation.py](../tests/test_validation.py) |
| 5 | CSV and JSON ingestion | Implemented | [src/ingestion.py](../src/ingestion.py), [tests/test_ingestion.py](../tests/test_ingestion.py) |
| 6 | Dataset profiling and quality assessment | Implemented | [src/profiling.py](../src/profiling.py), [tests/test_profiling.py](../tests/test_profiling.py) |
| 7 | Data dictionary and business context mapping | Implemented | [src/data_dictionary.py](../src/data_dictionary.py), [docs/data_dictionary.md](data_dictionary.md), [tests/test_data_dictionary.py](../tests/test_data_dictionary.py) |
| 8 | Missing-value detection and imputation | Implemented | [src/imputation.py](../src/imputation.py), [tests/test_imputation.py](../tests/test_imputation.py) |
| 9 | Data-type enforcement and standardisation | Implemented | [src/standardization.py](../src/standardization.py), [src/transformation.py](../src/transformation.py), [tests/test_standardization.py](../tests/test_standardization.py) |
| 10 | Duplicate detection and record deduplication | Implemented | [src/deduplication.py](../src/deduplication.py), [tests/test_deduplication.py](../tests/test_deduplication.py) |
| 11 | String cleaning and text normalisation | Implemented | [src/text_cleaning.py](../src/text_cleaning.py), [scripts/string_cleaning_pipeline.py](../scripts/string_cleaning_pipeline.py), [tests/test_string_cleaning.py](../tests/test_string_cleaning.py) |
| 12 | Date and time transformation pipeline | Implemented | [src/datetime_pipeline.py](../src/datetime_pipeline.py), [scripts/datetime_feature_engineering.py](../scripts/datetime_feature_engineering.py), [tests/test_datetime_pipeline.py](../tests/test_datetime_pipeline.py) |
| 13 | Statistical outlier detection | Implemented | [src/outliers.py](../src/outliers.py), [src/anomaly_detection.py](../src/anomaly_detection.py), [tests/test_outliers.py](../tests/test_outliers.py) |
| 14 | Data consistency and validation rules | Implemented | [src/consistency.py](../src/consistency.py), [tests/test_consistency.py](../tests/test_consistency.py) |
| 15 | Multi-source merging and join validation | Implemented | [src/merging.py](../src/merging.py), [tests/test_merging.py](../tests/test_merging.py) |
| 16 | Feature engineering and derived business columns | Implemented | [src/features.py](../src/features.py), [tests/test_features.py](../tests/test_features.py) |
| 17 | NumPy vectorised computation workflow | Implemented | [src/vectorization.py](../src/vectorization.py), [tests/test_vectorization.py](../tests/test_vectorization.py) |
| 18 | Distribution analysis for business trends | Implemented | [src/visualization.py](../src/visualization.py) (`create_distribution_histogram`), [tests/test_visualization.py](../tests/test_visualization.py) |
| 19 | Correlation and relationship analysis | Implemented | [src/visualization.py](../src/visualization.py) (`create_correlation_scatter_chart`), [tests/test_visualization.py](../tests/test_visualization.py) |
| 20 | GroupBy aggregation and segment insights | Implemented | [sql/aggregation.sql](../sql/aggregation.sql), [scripts/sql_aggregation.py](../scripts/sql_aggregation.py), [tests/test_sql_aggregation.py](../tests/test_sql_aggregation.py) |
| 21 | Time-series trend and rolling metrics | Implemented | [sql/views.sql](../sql/views.sql) (`weekly_activity_view`), [src/visualization.py](../src/visualization.py) (`plot_session_trends`) |
| 22 | Behavioural analysis and user segmentation | Implemented | [src/features.py](../src/features.py), [dashboard/filters.py](../dashboard/filters.py), [src/visualization.py](../src/visualization.py) |
| 23 | Funnel analysis and drop-off detection | Documented gap | The funnel is specified in [README.md](../README.md), but no dedicated funnel-analysis function, output, or test exists yet. |
| 24 | KPI definition and business metric design | Implemented | [sql/business_metrics.sql](../sql/business_metrics.sql), [src/database.py](../src/database.py), [tests/test_sql_business_metrics.py](../tests/test_sql_business_metrics.py) |
| 25 | Anomaly detection and risk identification | Implemented | [src/vectorization.py](../src/vectorization.py), [src/anomaly_detection.py](../src/anomaly_detection.py), [tests/test_vectorization.py](../tests/test_vectorization.py) |
| 26 | Root-cause investigation workflow | Implemented | [src/storytelling.py](../src/storytelling.py), [src/reporting.py](../src/reporting.py), [tests/test_storytelling.py](../tests/test_storytelling.py) |
| 27 | SQL environment and database integration | Implemented | [src/database.py](../src/database.py), [sql/schema.sql](../sql/schema.sql), [tests/test_sql_integration.py](../tests/test_sql_integration.py) |
| 28 | SQL business metrics query design | Implemented | [sql/business_metrics.sql](../sql/business_metrics.sql), [scripts/sql_business_metrics.py](../scripts/sql_business_metrics.py) |
| 29 | SQL filtering, grouping, and aggregation | Implemented | [sql/aggregation.sql](../sql/aggregation.sql), [tests/test_sql_aggregation.py](../tests/test_sql_aggregation.py) |
| 30 | SQL joins and multi-table analysis | Implemented | [sql/multi_table_joins.sql](../sql/multi_table_joins.sql), [scripts/sql_joins.py](../scripts/sql_joins.py), [tests/test_sql_joins.py](../tests/test_sql_joins.py) |
| 31 | SQL window functions and ranking | Implemented | [sql/window_functions.sql](../sql/window_functions.sql), [scripts/sql_window_functions.py](../scripts/sql_window_functions.py), [tests/test_sql_window_functions.py](../tests/test_sql_window_functions.py) |
| 32 | Analytical SQL query optimisation | Implemented | [tests/test_sql_optimization.py](../tests/test_sql_optimization.py), [src/database.py](../src/database.py) (`explain_query_plan`) |
| 33 | SQL views and aggregation layer | Implemented | [sql/views.sql](../sql/views.sql), [src/database.py](../src/database.py) (`execute_analytical_views`), [tests/test_sql_views.py](../tests/test_sql_views.py) |
| 34 | SQL-based insight validation | Implemented | [src/database.py](../src/database.py), [scripts/sql_insight_validation.py](../scripts/sql_insight_validation.py), [tests/test_sql_insight_validation.py](../tests/test_sql_insight_validation.py) |
| 35 | Business visualisation principles | Implemented | [docs/visualization_principles.md](visualization_principles.md), [src/visualization.py](../src/visualization.py), [tests/test_visualization.py](../tests/test_visualization.py) |
| 36 | Interactive Plotly charts | Implemented | [src/visualization.py](../src/visualization.py), [tests/test_visualization.py](../tests/test_visualization.py) |
| 37 | KPI cards and summary metric design | Implemented | [dashboard/components.py](../dashboard/components.py), [dashboard/utils.py](../dashboard/utils.py), [tests/test_kpi_components.py](../tests/test_kpi_components.py) |
| 38 | Data storytelling and insight narratives | Implemented | [src/storytelling.py](../src/storytelling.py), [tests/test_storytelling.py](../tests/test_storytelling.py) |
| 39 | Executive reporting and stakeholder communication | Implemented | [src/reporting.py](../src/reporting.py), [tests/test_reporting.py](../tests/test_reporting.py) |
| 40 | Insight export and report generation | Implemented | [src/export.py](../src/export.py), [tests/test_export.py](../tests/test_export.py) |
| 41 | Streamlit app structure and navigation | Implemented | [dashboard/app.py](../dashboard/app.py), [dashboard/views.py](../dashboard/views.py), [tests/test_streamlit_structure.py](../tests/test_streamlit_structure.py) |
| 42 | Dataset upload and dynamic preview | Implemented | [dashboard/utils.py](../dashboard/utils.py), [dashboard/views.py](../dashboard/views.py), [tests/test_dashboard_upload.py](../tests/test_dashboard_upload.py) |
| 43 | Streamlit filters and interactive widgets | Implemented | [dashboard/filters.py](../dashboard/filters.py), [tests/test_dashboard_filters.py](../tests/test_dashboard_filters.py) |
| 44 | Streamlit session state and workflow persistence | Implemented | [dashboard/state.py](../dashboard/state.py), [tests/test_dashboard_state.py](../tests/test_dashboard_state.py) |
| 45 | Real-time KPI dashboard | Implemented | [dashboard/filters.py](../dashboard/filters.py) (`calculate_realtime_kpis`), [dashboard/views.py](../dashboard/views.py), [tests/test_dashboard_filters.py](../tests/test_dashboard_filters.py) |
| 46 | Alert monitoring and metric thresholds | Implemented | [dashboard/alerts.py](../dashboard/alerts.py), [dashboard/components.py](../dashboard/components.py), [tests/test_dashboard_alerts.py](../tests/test_dashboard_alerts.py) |
| 47 | Insight sharing and email report integration | Implemented | [dashboard/sharing.py](../dashboard/sharing.py), [dashboard/components.py](../dashboard/components.py), [tests/test_dashboard_sharing.py](../tests/test_dashboard_sharing.py) |
| 48 | Automated end-to-end data pipeline | Implemented | [src/pipeline.py](../src/pipeline.py), [tests/test_pipeline.py](../tests/test_pipeline.py) |
| 49 | GitHub Workflow automation and validation | Implemented | [.github/workflows/data_pipeline.yml](../.github/workflows/data_pipeline.yml) |
| 50 | Data product documentation and delivery | Implemented | [README.md](../README.md), [docs/concept_mapping.md](concept_mapping.md) |

## Known Mapping Caveat

Concept 23 is intentionally marked as a documented gap. The repository has
completion/dropout metrics, risk detection, and trend views, but no dedicated
multi-stage learning-funnel computation. This prevents the delivery documentation
from claiming behavior that is not present in the code.
