# 📖 Data Dictionary & Business Context Mapping

## Learning Behaviour & Course Completion Analytics

This document connects technical database schema columns to their business definitions, domain boundaries, data types, validation constraints, and analytical usage within the course completion analytics platform.

---

## 🧑‍🎓 1. Students Dataset (`students.csv` / `students.json`)

| Column Name | Data Type | Required | Valid Range / Categories | Business Meaning | Analysis Application |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`student_id`** | `string` | **Yes** | Alphanumeric (e.g. `S001`) | Unique learner platform ID. | Primary key for student cohort aggregations, retention modeling, and personalized intervention tracking. |
| **`registration_date`** | `datetime` | **Yes** | `>= 2020-01-01` | Account creation & enrollment date. | Cohort grouping, onboarding velocity, and registration seasonality analysis. |
| **`age`** | `integer` | No | `15` to `80` | Age of learner in full years. | Demographic segmentation and completion correlation by age bracket. |
| **`gender`** | `string` | No | `Male`, `Female`, `Non-Binary`, `Other`, `Prefer not to say` | Self-reported gender identity. | Demographic equity and platform participation analysis. |
| **`education_level`** | `string` | No | `High School`, `Undergraduate`, `Postgraduate`, `Doctorate`, `Other` | Highest prior education degree. | Prior knowledge correlation with course difficulty and quiz performance. |
| **`device_type`** | `string` | No | `Desktop`, `Laptop`, `Tablet`, `Mobile` | Primary study device. | Accessibility, study continuity, and hardware impact on session length. |
| **`target_course_id`** | `string` | **Yes** | Foreign key to `courses.course_id` | Enrolled target course. | Connects learner to curriculum milestones and graduation requirements. |
| **`completion_status`** | `string` | **Yes** | `Completed`, `In Progress`, `Dropped`, `Inactive` | Ground truth business outcome. | Target variable for dropout prediction models and retention benchmarks. |

---

## 📚 2. Courses Dataset (`courses.csv` / `courses.json`)

| Column Name | Data Type | Required | Valid Range / Categories | Business Meaning | Analysis Application |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`course_id`** | `string` | **Yes** | Alphanumeric (e.g. `C101`) | Unique course catalog ID. | Primary key for curriculum difficulty benchmarks and course performance KPIs. |
| **`course_title`** | `string` | **Yes** | Non-empty descriptive string | Official course title. | Dashboard filters, catalog labeling, and stakeholder reporting. |
| **`category`** | `string` | **Yes** | `Data Science`, `AI & Machine Learning`, `Web Development`, `Cloud Computing`, etc. | Technical discipline domain. | Subject-level completion benchmarking and cross-discipline comparisons. |
| **`total_modules`** | `integer` | **Yes** | `1` to `50` | Total lessons/modules in course. | Denominator for calculating individual student percentage course progress. |
| **`total_quizzes`** | `integer` | **Yes** | `1` to `20` | Graded milestone assessments. | Assessment completion velocity and milestone checkpoint monitoring. |
| **`estimated_duration_hours`** | `float` | **Yes** | `5.0` to `200.0` hrs | Estimated required study hours. | Expected vs. actual study pacing to identify struggling or lagging learners. |

---

## ⏱️ 3. Sessions Dataset (`sessions.csv` / `sessions.json`)

| Column Name | Data Type | Required | Valid Range / Categories | Business Meaning | Analysis Application |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`session_id`** | `string` | **Yes** | Alphanumeric (e.g. `SES_001`) | Unique login session event ID. | Primary key for telemetry event logs and study sequence reconstruction. |
| **`student_id`** | `string` | **Yes** | Foreign key to `students.student_id` | ID of learner initiating session. | Total study time, session frequency, and habit regularity aggregations. |
| **`course_id`** | `string` | **Yes** | Foreign key to `courses.course_id` | Course accessed in session. | Subject focus and time allocation tracking per course. |
| **`session_start`** | `datetime` | **Yes** | Timestamp `<= session_end` | Session start timestamp. | Time-of-day study habit analysis and inactivity gap calculation between sessions. |
| **`session_end`** | `datetime` | **Yes** | Timestamp `>= session_start` | Session termination timestamp. | Session continuity verification and boundary logging. |
| **`duration_minutes`** | `float` | **Yes** | `0.1` to `600.0` mins | Total session elapsed duration. | Gross platform engagement volume and study length distribution. |
| **`active_minutes`** | `float` | **Yes** | `0.0` to `duration_minutes` | Active interaction duration. | Core study effort metric: separates real engagement from passive idle tabs. |
| **`idle_minutes`** | `float` | **Yes** | `0.0` to `duration_minutes` | Inactive / idle duration. | Attention leakage metric and distraction ratio calculation (`idle / duration`). |

---

## 📝 4. Quizzes Dataset (`quizzes.csv` / `quizzes.json`)

| Column Name | Data Type | Required | Valid Range / Categories | Business Meaning | Analysis Application |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`quiz_attempt_id`** | `string` | **Yes** | Alphanumeric (e.g. `QA_001`) | Unique assessment attempt ID. | Primary key for quiz event logs and attempt history. |
| **`student_id`** | `string` | **Yes** | Foreign key to `students.student_id` | Student taking the quiz. | Academic performance and mastery tracking per student. |
| **`course_id`** | `string` | **Yes** | Foreign key to `courses.course_id` | Associated course. | Assessment difficulty comparisons across curriculum domains. |
| **`quiz_id`** | `string` | **Yes** | Alphanumeric (e.g. `QZ_MOD_01`) | Assessment module ID. | Bottleneck detection: identifying specific quizzes with elevated failure rates. |
| **`attempt_number`** | `integer` | **Yes** | `1` to `10` | Sequential attempt counter. | Persistence indicator: retry behavior strongly correlates with completion. |
| **`attempt_date`** | `datetime` | **Yes** | Calendar date | Date quiz was submitted. | Assessment velocity and milestone pacing analysis. |
| **`score_percentage`** | `float` | **Yes** | `0.0` to `100.0%` | Score achieved (0–100%). | Primary academic performance KPI and knowledge competency indicator. |
| **`time_taken_minutes`** | `float` | **Yes** | `1.0` to `180.0` mins | Duration spent taking quiz. | Guessing vs. mastery detection (unusually rapid submissions vs. diligent effort). |
| **`passed`** | `integer` | **Yes** | `1` (Passed), `0` (Failed) | Met passing threshold (>=70%). | Milestone completion gatekeeper requirement for course completion. |

---

## 🎯 5. Core Analytical & Derived Metrics Mapping

| Metric Name | Business Definition | Underlying Formula / Source | Analytical Impact |
| :--- | :--- | :--- | :--- |
| **`session_date`** | Calendar day of learning activity. | `DATE(session_start)` | Daily Active Users (DAU), day-of-week learning routines, and inactive gap days. |
| **`session_duration`** | Total learning session length. | `duration_minutes` | Study volume and learning depth measurement. |
| **`quiz_score`** | Graded quiz exam result. | `score_percentage` | Knowledge retention assessment and academic strength scoring. |
| **`progress_pct`** | Percentage of course completed. | `(completed_modules / total_modules) * 100` | Pacing velocity, milestone completion, and drop-off point identification. |
| **`completion_status`** | Final course completion outcome. | `students.completion_status` | Ground-truth target for dropout risk modeling and retention benchmarking. |
