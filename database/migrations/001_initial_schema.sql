-- Database Schema for Wellness Dashboard

CREATE TYPE data_source AS ENUM ('manual', 'google_fit');
CREATE TYPE insight_type AS ENUM ('daily', 'weekly', 'pattern');
CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high', 'critical');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    google_id VARCHAR(255) UNIQUE,
    google_access_token TEXT,
    google_refresh_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);

-- Health records table
CREATE TABLE health_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sleep_hours FLOAT,
    stress_level INTEGER,
    steps INTEGER,
    screen_time FLOAT,
    heart_rate INTEGER,
    calories FLOAT,
    data_source data_source DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_records_user_id ON health_records(user_id);
CREATE INDEX idx_health_records_date ON health_records(date);

-- Wellness scores table
CREATE TABLE wellness_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_score FLOAT NOT NULL,
    sleep_score FLOAT,
    activity_score FLOAT,
    heart_rate_score FLOAT,
    stress_score FLOAT
);

CREATE INDEX idx_wellness_scores_user_id ON wellness_scores(user_id);
CREATE INDEX idx_wellness_scores_date ON wellness_scores(date);

-- Patterns table
CREATE TABLE patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    signals_involved TEXT,
    severity severity_level DEFAULT 'medium',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patterns_user_id ON patterns(user_id);
CREATE INDEX idx_patterns_detected_at ON patterns(detected_at);

-- Insights table
CREATE TABLE insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insight_text TEXT NOT NULL,
    suggestions TEXT,
    ai_model VARCHAR(255),
    insight_type insight_type DEFAULT 'daily'
);

CREATE INDEX idx_insights_user_id ON insights(user_id);
CREATE INDEX idx_insights_date ON insights(date);
