-- Learning Behaviour & Course Completion Analytics - SQL Window Functions & Ranking Systems

-- 1. Course-Level Learner Performance Rankings & Course Benchmarks
-- Name: course_learner_rankings
-- Purpose: Ranks students within their enrolled course by engagement score and quiz average, comparing against course-level average engagement using AVG() OVER().
WITH learner_prep AS (
    SELECT 
        s.target_course_id,
        c.course_title,
        s.student_id,
        s.completion_status,
        COALESCE(bf.engagement_score, 0.0) AS engagement_score,
        COALESCE(bf.quiz_average, 0.0) AS quiz_average
    FROM students s
    LEFT JOIN courses c ON s.target_course_id = c.course_id
    LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
)
SELECT 
    target_course_id,
    course_title,
    student_id,
    completion_status,
    engagement_score,
    quiz_average,
    ROW_NUMBER() OVER (
        PARTITION BY target_course_id 
        ORDER BY engagement_score DESC, student_id ASC
    ) AS course_engagement_rank,
    RANK() OVER (
        PARTITION BY target_course_id 
        ORDER BY quiz_average DESC
    ) AS course_quiz_rank,
    ROUND(
        AVG(engagement_score) OVER (PARTITION BY target_course_id), 
        2
    ) AS course_avg_engagement_benchmark
FROM learner_prep
ORDER BY target_course_id, course_engagement_rank;

-- 2. Previous Session Activity Comparison (LAG Window Function)
-- Name: session_previous_activity_comparison
-- Purpose: Uses LAG() to compare each session's duration and active minutes against the learner's previous session.
WITH session_lags AS (
    SELECT 
        session_id,
        student_id,
        course_id,
        session_start,
        duration_minutes,
        active_minutes,
        LAG(duration_minutes, 1) OVER (
            PARTITION BY student_id 
            ORDER BY session_start
        ) AS prev_session_duration_mins,
        ROW_NUMBER() OVER (
            PARTITION BY student_id 
            ORDER BY session_start
        ) AS student_session_sequence
    FROM sessions
)
SELECT 
    session_id,
    student_id,
    course_id,
    session_start,
    duration_minutes,
    active_minutes,
    prev_session_duration_mins,
    ROUND(
        duration_minutes - COALESCE(prev_session_duration_mins, duration_minutes), 
        2
    ) AS session_duration_change_mins,
    student_session_sequence
FROM session_lags
ORDER BY student_id, session_start;

-- 3. Sequential Quiz Progression & Next Attempt Delta (LAG & LEAD Window Functions)
-- Name: quiz_attempt_sequence_lead_lag
-- Purpose: Evaluates quiz score progression across attempt numbers using LAG() for previous score and LEAD() for subsequent score.
WITH quiz_lags AS (
    SELECT 
        quiz_attempt_id,
        student_id,
        course_id,
        quiz_id,
        attempt_number,
        attempt_date,
        score_percentage,
        passed,
        LAG(score_percentage, 1) OVER (
            PARTITION BY student_id, quiz_id 
            ORDER BY attempt_number
        ) AS previous_attempt_score,
        LEAD(score_percentage, 1) OVER (
            PARTITION BY student_id, quiz_id 
            ORDER BY attempt_number
        ) AS next_attempt_score
    FROM quizzes
)
SELECT 
    quiz_attempt_id,
    student_id,
    course_id,
    quiz_id,
    attempt_number,
    attempt_date,
    score_percentage,
    passed,
    previous_attempt_score,
    next_attempt_score,
    ROUND(
        score_percentage - COALESCE(previous_attempt_score, score_percentage),
        2
    ) AS score_improvement_from_prev
FROM quiz_lags
ORDER BY student_id, quiz_id, attempt_number;

-- 4. Rolling 3-Session Average Duration & Benchmark (AVG OVER Window Function)
-- Name: rolling_session_metrics
-- Purpose: Computes a 3-session rolling average duration per learner using ROWS BETWEEN 2 PRECEDING AND CURRENT ROW.
SELECT 
    session_id,
    student_id,
    session_start,
    duration_minutes,
    active_minutes,
    ROUND(
        AVG(duration_minutes) OVER (
            PARTITION BY student_id 
            ORDER BY session_start 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS rolling_3_session_avg_duration,
    ROUND(
        AVG(active_minutes) OVER (
            PARTITION BY student_id 
            ORDER BY session_start 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS rolling_3_session_avg_active_mins,
    ROW_NUMBER() OVER (
        PARTITION BY student_id 
        ORDER BY session_start
    ) AS session_num
FROM sessions
ORDER BY student_id, session_start;

-- 5. Overall Platform Leaderboard & Global Benchmark
-- Name: overall_learner_rankings
-- Purpose: Ranks all platform learners using RANK() and DENSE_RANK() while comparing against platform-wide average engagement.
WITH learner_features AS (
    SELECT 
        s.student_id,
        s.target_course_id,
        s.completion_status,
        COALESCE(bf.engagement_score, 0.0) AS engagement_score,
        COALESCE(bf.quiz_average, 0.0) AS quiz_average
    FROM students s
    LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
)
SELECT 
    student_id,
    target_course_id,
    completion_status,
    engagement_score,
    quiz_average,
    RANK() OVER (
        ORDER BY engagement_score DESC
    ) AS overall_engagement_rank,
    DENSE_RANK() OVER (
        ORDER BY quiz_average DESC
    ) AS overall_quiz_dense_rank,
    ROUND(
        AVG(engagement_score) OVER (), 
        2
    ) AS global_avg_engagement_baseline
FROM learner_features
ORDER BY overall_engagement_rank ASC
LIMIT 50;
