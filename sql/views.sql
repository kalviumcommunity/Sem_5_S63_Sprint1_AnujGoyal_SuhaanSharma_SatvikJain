-- Learning Behaviour & Course Completion Analytics - Reusable Analytical SQL Views

-- 1. Student Engagement View
-- Name: student_engagement_view
-- Purpose: Consolidates student demographic metadata, target course information, and behavioural metrics into a unified presentation layer view.
CREATE VIEW IF NOT EXISTS student_engagement_view AS
SELECT 
    s.student_id,
    s.registration_date,
    s.age,
    s.gender,
    s.education_level,
    s.device_type,
    s.target_course_id,
    c.course_title,
    c.category,
    s.completion_status,
    COALESCE(bf.average_session_duration, 0.0) AS avg_session_duration,
    COALESCE(bf.sessions_per_week, 0.0) AS sessions_per_week,
    COALESCE(bf.quiz_average, 0.0) AS quiz_average,
    COALESCE(bf.course_progress, 0.0) AS course_progress,
    COALESCE(bf.engagement_score, 0.0) AS engagement_score,
    COALESCE(bf.dropout_risk_level, 'Low') AS dropout_risk_level
FROM students s
LEFT JOIN courses c ON s.target_course_id = c.course_id
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id;


-- 2. Course Performance View
-- Name: course_performance_view
-- Purpose: Aggregates enrollment volume, completion rates, dropout counts, average progress, and engagement benchmarks by course.
CREATE VIEW IF NOT EXISTS course_performance_view AS
SELECT 
    c.course_id,
    c.course_title,
    c.category,
    c.difficulty_level,
    c.total_modules,
    c.total_quizzes,
    c.estimated_duration_hours,
    COUNT(s.student_id) AS total_enrolled,
    SUM(CASE WHEN LOWER(s.completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_count,
    SUM(CASE WHEN LOWER(s.completion_status) = 'dropped' THEN 1 ELSE 0 END) AS dropped_count,
    ROUND(
        COALESCE(
            CAST(SUM(CASE WHEN LOWER(s.completion_status) = 'completed' THEN 1 ELSE 0 END) AS REAL) / NULLIF(COUNT(s.student_id), 0) * 100.0,
            0.0
        ), 
        2
    ) AS completion_rate_pct,
    ROUND(COALESCE(AVG(bf.engagement_score), 0.0), 2) AS avg_engagement_score,
    ROUND(COALESCE(AVG(bf.course_progress), 0.0), 2) AS avg_course_progress,
    ROUND(COALESCE(AVG(bf.quiz_average), 0.0), 2) AS avg_quiz_score
FROM courses c
LEFT JOIN students s ON c.course_id = s.target_course_id
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
GROUP BY c.course_id, c.course_title, c.category, c.difficulty_level, c.total_modules, c.total_quizzes, c.estimated_duration_hours;


-- 3. Dropout Risk View
-- Name: dropout_risk_view
-- Purpose: Filters and surfaces at-risk learners displaying key risk telemetry (inactivity days, quiz score, risk level) for intervention dashboards.
CREATE VIEW IF NOT EXISTS dropout_risk_view AS
SELECT 
    s.student_id,
    s.target_course_id,
    c.course_title,
    c.category,
    s.completion_status,
    COALESCE(bf.dropout_risk_level, 'Low') AS dropout_risk_level,
    COALESCE(bf.days_since_last_activity, 0) AS days_since_last_activity,
    COALESCE(bf.quiz_average, 0.0) AS quiz_average,
    COALESCE(bf.sessions_per_week, 0.0) AS sessions_per_week,
    COALESCE(bf.engagement_score, 0.0) AS engagement_score,
    CASE 
        WHEN LOWER(COALESCE(bf.dropout_risk_level, 'Low')) IN ('high', 'critical') THEN 1 
        ELSE 0 
    END AS is_at_risk
FROM students s
LEFT JOIN courses c ON s.target_course_id = c.course_id
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id;


-- 4. Weekly Activity View
-- Name: weekly_activity_view
-- Purpose: Aggregates session count, active learning minutes, and unique active learners grouped by calendar week.
CREATE VIEW IF NOT EXISTS weekly_activity_view AS
SELECT 
    strftime('%Y-%W', session_start) AS activity_week,
    COUNT(session_id) AS total_sessions,
    COUNT(DISTINCT student_id) AS active_learners,
    ROUND(COALESCE(SUM(duration_minutes), 0.0), 2) AS total_duration_minutes,
    ROUND(COALESCE(AVG(duration_minutes), 0.0), 2) AS avg_session_duration,
    ROUND(COALESCE(AVG(active_minutes), 0.0), 2) AS avg_active_minutes
FROM sessions
WHERE session_start IS NOT NULL AND session_start != ''
GROUP BY strftime('%Y-%W', session_start);
