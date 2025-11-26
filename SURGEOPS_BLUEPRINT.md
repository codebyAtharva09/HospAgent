# HospAgent SurgeOps: Comprehensive Engineering Blueprint

## 1. System Architecture

The system follows a **Micro-Agent Architecture** where independent agents consume data, process it, and publish insights.

### High-Level Data Flow
1.  **Ingestion Layer**: `Data Ingestion Agent` receives live data (Hospital HMS, AQI APIs, Weather APIs, Google Calendar).
2.  **Storage Layer**: Time-series data stored in PostgreSQL/TimescaleDB.
3.  **Intelligence Layer**:
    *   `Risk Assessment Agent` computes real-time scores.
    *   `Surge Forecast Agent` predicts future load.
    *   `Calendar Agent` fetches and flags high-risk festival days.
4.  **Planning Layer**:
    *   `Resource Optimizer` calculates staffing/supply needs.
    *   `Burnout Agent` monitors staff wellbeing.
5.  **Action Layer**:
    *   `Advisory Agent` generates alerts.
    *   `Simulation Agent` runs "What-if" scenarios.
6.  **Presentation Layer**: React Frontend (Wisteria Blue Theme).

---

## 2. Database Schema (PostgreSQL/TimescaleDB)

```sql
-- 1. Patient Events (Time-Series)
CREATE TABLE patient_events (
    time TIMESTAMPTZ NOT NULL,
    patient_id TEXT,
    event_type TEXT, -- 'ADMISSION', 'DISCHARGE', 'TRIAGE'
    department TEXT, -- 'ER', 'ICU', 'OPD'
    triage_category TEXT, -- 'RED', 'YELLOW', 'GREEN'
    complaint_type TEXT -- 'RESPIRATORY', 'TRAUMA', 'VIRAL'
);
SELECT create_hypertable('patient_events', 'time');

-- 2. Environmental Context (Time-Series)
CREATE TABLE environmental_context (
    time TIMESTAMPTZ NOT NULL,
    aqi INTEGER,
    temperature DECIMAL,
    humidity DECIMAL,
    epidemic_index DECIMAL -- 0-10
);
SELECT create_hypertable('environmental_context', 'time');

-- 3. Forecasts
CREATE TABLE forecasts (
    created_at TIMESTAMPTZ DEFAULT NOW(),
    target_date DATE,
    department TEXT,
    predicted_count INTEGER,
    confidence_interval_low INTEGER,
    confidence_interval_high INTEGER
);

-- 4. Staffing & Resources
CREATE TABLE staff_roster (
    staff_id TEXT PRIMARY KEY,
    role TEXT, -- 'DOCTOR', 'NURSE'
    department TEXT,
    shift_preference TEXT
);

CREATE TABLE staff_schedule (
    date DATE,
    shift TEXT, -- 'MORNING', 'EVENING', 'NIGHT'
    staff_id TEXT,
    is_holiday BOOLEAN
);

CREATE TABLE inventory (
    item_id TEXT PRIMARY KEY,
    item_name TEXT, -- 'OXYGEN_CYLINDER', 'N95_MASK'
    current_stock INTEGER,
    daily_usage_rate DECIMAL
);
```

---

## 3. Agent Specifications & Logic

### Agent 1: Data Ingestion
*   **Role**: Normalizes inputs from HMS webhooks and external APIs.
*   **Endpoints**: `/ingest/*`

### Agent 2: Risk Assessment Engine
*   **Frequency**: Every 10 mins.
*   **Logic**:
    ```python
    risk_score = (
        (w_aqi * normalize(aqi, 0, 500)) +
        (w_slope * patient_slope_6h) +
        (w_epidemic * epidemic_index) +
        (w_festival * festival_proximity_score) +
        (w_icu * (icu_occupancy / total_icu_beds))
    )
    ```

### Agent 3: Surge Forecast Agent
*   **Model**: Random Forest / XGBoost (Mocked for Hackathon).
*   **Features**: `day_of_week`, `is_festival`, `aqi_lag_24h`, `temp_lag_24h`.

### Agent 4: Resource Optimizer
*   **Logic**:
    *   `Doctors = ceil(Predicted_Patients / 15)`
    *   `Nurses = ceil(Predicted_Patients / 6)`
    *   `Oxygen = Predicted_Respiratory * 1.5 cylinders`
    *   **Holiday Constraint**: If `staff_on_leave > 20%`, trigger `Agency_Staff_Request`.

### Agent 5: Burnout Agent
*   **Logic**: Flag staff with >3 consecutive night shifts or >60h/week.

### Agent 6: Advisory Agent
*   **Output**: Templates filled with risk data.
    *   "AQI is {aqi}. Respiratory admissions up {pct}%. Please triage mild asthma to OPD."

### Agent 7: Calendar Agent (Google Integration)
*   **Role**: Syncs with Google Calendar to identify "High Risk" days (Diwali, etc.).

---

## 4. API Design (FastAPI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/risk/now` | Current composite risk score. |
| GET | `/forecast/patients` | 7-day load prediction. |
| GET | `/plan/staffing` | Recommended roster vs actual. |
| GET | `/plan/supplies` | Supply gaps for next 3 days. |
| GET | `/festivals/upcoming` | High-risk dates from Google Calendar. |
| POST | `/simulate/scenario` | Run "What-if" analysis. |

---

## 5. Frontend Design (React)

### Color Palette
*   **Primary**: `#769DD7` (Wisteria Blue)
*   **Background**: `#CDDBE5` (Pale Sky)
*   **Cards**: `#FFFFFF` (White)

### Components
1.  **RiskCard**: Displays live gauges.
2.  **ForecastChart**: Recharts bar graph.
3.  **CalendarPanel**: Custom calendar view with festival dots.
4.  **OperationsTable**: Staffing/Supply rows with status indicators.

---

## 6. Implementation Roadmap

1.  **Setup**: `requirements.txt`, Google Cloud Creds.
2.  **Backend Core**: `app.py`, `agents/*.py`.
3.  **Calendar Integration**: `calendar_agent.py`.
4.  **Frontend**: React components + CSS.
5.  **Integration**: Connect Frontend to Backend APIs.
6.  **Demo**: Run simulation script.
