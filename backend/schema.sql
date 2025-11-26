-- HospAgent SurgeOps Database Schema
-- Optimized for PostgreSQL + TimescaleDB

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 1. Patient Events (Time-Series)
-- Stores every admission, discharge, and triage event
CREATE TABLE patient_events (
    time TIMESTAMPTZ NOT NULL,
    patient_id TEXT NOT NULL,
    event_type TEXT NOT NULL, -- 'ADMISSION', 'DISCHARGE', 'TRIAGE', 'TRANSFER'
    department TEXT NOT NULL, -- 'ER', 'ICU', 'OPD', 'PEDIATRICS'
    triage_category TEXT, -- 'RED', 'YELLOW', 'GREEN'
    complaint_type TEXT, -- 'RESPIRATORY', 'TRAUMA', 'VIRAL', 'CARDIAC'
    age_group TEXT -- 'CHILD', 'ADULT', 'ELDERLY'
);

-- Convert to hypertable for efficient time-series queries
SELECT create_hypertable('patient_events', 'time');

-- 2. Environmental Context (Time-Series)
-- Stores external factors like AQI, Weather, Epidemic signals
CREATE TABLE environmental_context (
    time TIMESTAMPTZ NOT NULL,
    aqi INTEGER,
    temperature DECIMAL,
    humidity DECIMAL,
    epidemic_index DECIMAL, -- 0-10 scale based on surveillance
    is_festival_nearby BOOLEAN DEFAULT FALSE
);

SELECT create_hypertable('environmental_context', 'time');

-- 3. Forecasts
-- Stores generated predictions for accuracy tracking
CREATE TABLE forecasts (
    created_at TIMESTAMPTZ DEFAULT NOW(),
    target_date DATE NOT NULL,
    department TEXT NOT NULL,
    predicted_count INTEGER,
    confidence_interval_low INTEGER,
    confidence_interval_high INTEGER,
    model_version TEXT
);

-- 4. Staffing & Resources
CREATE TABLE staff_roster (
    staff_id TEXT PRIMARY KEY,
    name TEXT,
    role TEXT, -- 'DOCTOR', 'NURSE', 'SUPPORT'
    department TEXT,
    shift_preference TEXT
);

CREATE TABLE staff_schedule (
    date DATE NOT NULL,
    shift TEXT NOT NULL, -- 'MORNING', 'EVENING', 'NIGHT'
    staff_id TEXT REFERENCES staff_roster(staff_id),
    is_holiday BOOLEAN DEFAULT FALSE,
    actual_hours_worked DECIMAL
);

CREATE TABLE inventory (
    item_id TEXT PRIMARY KEY,
    item_name TEXT NOT NULL, -- 'OXYGEN_CYLINDER', 'N95_MASK'
    current_stock INTEGER,
    daily_usage_rate DECIMAL,
    reorder_level INTEGER,
    lead_time_days INTEGER
);

-- Indexes for performance
CREATE INDEX idx_patient_dept ON patient_events(department, time DESC);
CREATE INDEX idx_forecast_date ON forecasts(target_date);
