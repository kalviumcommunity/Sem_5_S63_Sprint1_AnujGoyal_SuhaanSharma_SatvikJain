-- Learning Behaviour & Course Completion Intelligence Database Schema

-- Courses Table
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_title TEXT NOT NULL,
    category TEXT NOT NULL,
    total_modules INTEGER NOT NULL,
    total_quizzes INTEGER NOT NULL,
    estimated_duration_hours REAL NOT NULL,
    difficulty_level TEXT
);

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    registration_date TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    education_level TEXT,
    device_type TEXT,
    target_course_id TEXT,
    completion_status TEXT DEFAULT 'In Progress',
    completion_date TEXT,
    FOREIGN KEY (target_course_id) REFERENCES courses(course_id)
);

-- Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    session_start TEXT NOT NULL,
    session_end TEXT NOT NULL,
    duration_minutes REAL NOT NULL,
    active_minutes REAL NOT NULL,
    idle_minutes REAL NOT NULL,
    video_watched_minutes REAL DEFAULT 0,
    reading_minutes REAL DEFAULT 0,
    modules_accessed INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Quizzes Table
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_attempt_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    quiz_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    attempt_date TEXT NOT NULL,
    score_percentage REAL NOT NULL,
    time_taken_minutes REAL NOT NULL,
    passed INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Student Behaviour Summary Table
CREATE TABLE IF NOT EXISTS student_behaviour_summary (
    student_id TEXT PRIMARY KEY,
    total_sessions INTEGER DEFAULT 0,
    total_active_hours REAL DEFAULT 0,
    avg_session_gap_days REAL DEFAULT 0,
    avg_quiz_score REAL DEFAULT 0,
    course_progress_percentage REAL DEFAULT 0,
    engagement_score REAL DEFAULT 0,
    dropout_risk_level TEXT DEFAULT 'Low',
    completed INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Behavioural Features Table
CREATE TABLE IF NOT EXISTS behavioural_features (
    student_id TEXT PRIMARY KEY,
    average_session_duration REAL DEFAULT 0,
    sessions_per_week REAL DEFAULT 0,
    quiz_average REAL DEFAULT 0,
    quiz_attempt_count INTEGER DEFAULT 0,
    course_progress REAL DEFAULT 0,
    progress_velocity REAL DEFAULT 0,
    days_since_last_activity INTEGER DEFAULT 0,
    learning_consistency REAL DEFAULT 0,
    engagement_score REAL DEFAULT 0,
    completion_rate REAL DEFAULT 0,
    dropout_risk_level TEXT DEFAULT 'Low',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Analytical Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_students_target_course ON students(target_course_id);
CREATE INDEX IF NOT EXISTS idx_students_reg_date ON students(registration_date);
CREATE INDEX IF NOT EXISTS idx_sessions_student_start ON sessions(student_id, session_start);
CREATE INDEX IF NOT EXISTS idx_sessions_course ON sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_student_quiz ON quizzes(student_id, quiz_id, attempt_number);
CREATE INDEX IF NOT EXISTS idx_quizzes_course ON quizzes(course_id);
CREATE INDEX IF NOT EXISTS idx_behavioural_risk ON behavioural_features(dropout_risk_level);
CREATE INDEX IF NOT EXISTS idx_behavioural_inactivity ON behavioural_features(days_since_last_activity);
