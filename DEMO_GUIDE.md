# HospAgent SurgeOps: Demo Guide

This guide explains how to demonstrate the live agentic capabilities of HospAgent SurgeOps.

## 1. Setup
Ensure both backend and frontend are running:
- **Backend**: `python backend/main.py` (Port 8000)
- **Frontend**: `npm run dev` (Port 5173)

## 2. Scenario 1: Pollution Spike (AQI Surge)
**Goal**: Show how environmental factors impact hospital risk and staffing.

1.  Locate the **Simulation Controls** at the top of the dashboard.
2.  Drag the **AQI Slider** from `150` to `400`.
3.  **Observe**:
    *   **Risk Index**: Jumps to `CRITICAL` (>80).
    *   **Contributing Factors**: "High AQI (400)" appears.
    *   **Forecast**: Respiratory patient count increases significantly.
    *   **Supplies**: Oxygen Cylinder requirement spikes.

## 3. Scenario 2: Festival Surge (Diwali Mode)
**Goal**: Show how cultural events impact trauma/burn cases and staffing.

1.  Toggle the **Simulate Festival** switch to `ON`.
2.  **Observe**:
    *   **Risk Index**: Increases due to "Upcoming Festival".
    *   **Forecast**: Total patient load increases (Trauma cases rise).
    *   **Staffing**: Alerts for "High Staff Absence Risk" appear.
    *   **Supplies**: "Order 3 days in advance" action is triggered.

## 4. Scenario 3: Epidemic Outbreak
**Goal**: Show impact of a disease outbreak (e.g., Dengue).

1.  Drag the **Epidemic Severity** slider to `8.0`.
2.  **Observe**:
    *   **Risk Index**: "Epidemic Alert" factor appears.
    *   **Forecast**: Viral cases increase.
    *   **ICU Pressure**: ICU risk component rises.

## 5. Google Calendar Integration
1.  Check the **Calendar Panel** on the right.
2.  It fetches live data from Google Calendar.
3.  High-risk festivals (Diwali, Holi, etc.) are automatically flagged with an orange `HIGH RISK` tag.

## 6. Staff Wellbeing
1.  Check the **Staff Wellbeing Alert** card.
2.  It simulates monitoring of staff shifts.
3.  Shows alerts if staff are overworked (mocked for demo).
