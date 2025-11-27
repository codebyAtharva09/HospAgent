from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import Services & Engines
from services.env_client import EnvironmentClient
from services.festival_client import FestivalClient
from services.festival_repository import FestivalRepository
from engines.risk_engine import RiskEngine
from engines.forecast_engine import ForecastEngine
from engines.staffing_engine import StaffingEngine
from engines.supply_engine import SupplyEngine

router = APIRouter(tags=["vapi-tools"])

# Initialize services
env_client = EnvironmentClient()
festival_client = FestivalClient()
festival_repo = FestivalRepository()
risk_engine = RiskEngine()
forecast_engine = ForecastEngine()
staffing_engine = StaffingEngine()
supply_engine = SupplyEngine()

# --- Constants & Configuration ---
HOSPITAL_CAPACITY = {
    "name": "Goregaon City Hospital",
    "location": "Goregaon, Mumbai",
    "total_doctors": 25,
    "total_nurses": 70,
    "total_ward_beds": 120,
    "total_icu_beds": 18,
    "total_ots": 4,
    "total_ventilators": 10,
    "total_ambulances": 3
}

# --- Helper Functions ---
async def get_shared_context():
    """
    Helper to fetch common context data (Env, Festivals, Forecast) 
    used by multiple tools.
    """
    # 1. Fetch live environmental data
    try:
        real_env = await env_client.get_live_data()
    except Exception:
        # Fallback if API fails
        real_env = {"aqi_index_1_5": 3, "temperature_c": 28, "humidity": 60, "weather": "Haze"}

    # Map AQI index (1-5) to 0-500 scale
    aqi_index = real_env.get("aqi_index_1_5", 3)
    aqi_map = {1: 50, 2: 100, 3: 200, 4: 300, 5: 400}
    internal_aqi_score = aqi_map.get(aqi_index, 200)

    # 2. Get upcoming festivals
    festivals = festival_repo.get_upcoming_festivals(days_ahead=30)
    if not festivals:
        festivals = festival_client.fetch_festivals(days_ahead=30)
        if festivals:
            festival_repo.upsert_festivals(festivals)

    festival_features = festival_client.calculate_festival_features(festivals)

    return {
        "real_env": real_env,
        "internal_aqi_score": internal_aqi_score,
        "festivals": festivals,
        "festival_features": festival_features
    }

# --- Endpoints ---

@router.get("/risk")
async def get_risk_summary():
    """
    Returns risk index, level, env data, and explanation.
    Tool Name: risk-summary
    """
    ctx = await get_shared_context()
    
    # Prepare risk inputs
    current_patients = 160 
    risk_inputs = {
        "aqi": ctx["internal_aqi_score"],
        "pm2_5": ctx["real_env"].get("pollutants", {}).get("pm2_5", 0),
        "pm10": ctx["real_env"].get("pollutants", {}).get("pm10", 0),
        "temperature": ctx["real_env"].get("temperature_c", 25),
        "humidity": ctx["real_env"].get("humidity", 50),
        "patient_slope_6h": 1.1,
        "epidemic_index": 2.0,
        "festival_nearby": ctx["festival_features"].get("is_high_risk_festival_window", False),
        "icu_occupancy": 0.75,
        "current_patients": current_patients,
    }

    risk_result = risk_engine.calculate_comprehensive_risk(risk_inputs)
    
    # Format explanation
    explanations = []
    if ctx["internal_aqi_score"] > 200:
        explanations.append(f"AQI is {ctx['internal_aqi_score']}, leading to expected respiratory surge.")
    if ctx["festival_features"].get("is_high_risk_festival_window"):
        explanations.append("Upcoming festival window may increase trauma/injury cases.")
    if risk_result.get("breakdown", {}).get("icu_risk", 0) > 70:
        explanations.append("ICU occupancy is moderately high.")
    
    if not explanations:
        explanations.append("Hospital operations are currently stable.")

    return {
        "risk_index": risk_result.get("hospital_risk_index", 0),
        "risk_level": risk_result.get("level", "UNKNOWN"),
        "env": {
            "aqi": ctx["internal_aqi_score"],
            "aqi_label": "Poor" if ctx["internal_aqi_score"] > 200 else "Moderate",
            "temperature_c": ctx["real_env"].get("temperature_c"),
            "weather": ctx["real_env"].get("weather", "Unknown")
        },
        "explanation": explanations
    }

@router.get("/staffing")
async def get_staffing_summary():
    """
    Returns required vs available doctors/nurses and shortages.
    Tool Name: staffing-summary
    """
    ctx = await get_shared_context()
    
    # Generate Forecast
    forecast_context = {
        "aqi": ctx["internal_aqi_score"],
        "temperature": ctx["real_env"].get("temperature_c", 25),
        "humidity": ctx["real_env"].get("humidity", 50),
        "epidemic_severity": 2.0,
        "patient_slope_24h": 1.1,
        "festivals": ctx["festivals"],
        "current_load": 160,
    }
    forecast_result = forecast_engine.generate_forecast(2, forecast_context)
    
    # Calculate Staffing for Today
    today_forecast = forecast_result[0] if forecast_result else {}
    predicted_patients_today = today_forecast.get("total_patients", 160)
    
    staffing_rec = staffing_engine.recommend_staffing(
        predicted_patients_today=predicted_patients_today,
        icu_risk=60,
        epidemic_index=2.0,
        aqi_level=ctx["internal_aqi_score"],
        respiratory_cases=today_forecast.get("breakdown", {}).get("respiratory", 0)
    )
    
    today_req = staffing_rec[0] if staffing_rec else {}
    req_docs = today_req.get("doctors", 0)
    req_nurses = today_req.get("nurses", 0)
    
    avail_docs = HOSPITAL_CAPACITY["total_doctors"]
    avail_nurses = HOSPITAL_CAPACITY["total_nurses"]
    
    # Calculate Shortage
    shortage_docs = max(0, req_docs - avail_docs)
    shortage_nurses = max(0, req_nurses - avail_nurses)

    # Calculate Tomorrow
    tomorrow_forecast = forecast_result[1] if len(forecast_result) > 1 else {}
    predicted_patients_tmrw = tomorrow_forecast.get("total_patients", 160)
    req_docs_tmrw = int(req_docs * (predicted_patients_tmrw / predicted_patients_today)) if predicted_patients_today else req_docs
    req_nurses_tmrw = int(req_nurses * (predicted_patients_tmrw / predicted_patients_today)) if predicted_patients_today else req_nurses

    return {
        "today": {
            "required": { "doctors": req_docs, "nurses": req_nurses },
            "available": { "doctors": avail_docs, "nurses": avail_nurses },
            "shortage": { "doctors": shortage_docs, "nurses": shortage_nurses }
        },
        "tomorrow": {
            "required": { "doctors": req_docs_tmrw, "nurses": req_nurses_tmrw }
        }
    }

@router.get("/supplies")
async def get_supplies_summary():
    """
    Returns list of supply items with status (LOW / MEDIUM / OK).
    Tool Name: supplies-summary
    """
    ctx = await get_shared_context()
    
    # Generate Forecast
    forecast_context = {
        "aqi": ctx["internal_aqi_score"],
        "temperature": ctx["real_env"].get("temperature_c", 25),
        "humidity": ctx["real_env"].get("humidity", 50),
        "epidemic_severity": 2.0,
        "patient_slope_24h": 1.1,
        "festivals": ctx["festivals"],
        "current_load": 160,
    }
    forecast_result = forecast_engine.generate_forecast(3, forecast_context)
    
    supply_recs = supply_engine.recommend_supplies(
        forecast=forecast_result,
        current_stock=None,
        festival_window=ctx["festival_features"].get("is_high_risk_festival_window", False),
        aqi_level=ctx["internal_aqi_score"],
        epidemic_index=2.0,
    )
    
    formatted_supplies = []
    for item in supply_recs:
        status_map = {
            "Critical": "LOW",
            "Low": "LOW",
            "Warning": "MEDIUM",
            "Adequate": "OK",
            "Surplus": "OK"
        }
        engine_status = item.get("status", "Adequate")
        simple_status = status_map.get(engine_status, "OK")
        
        formatted_supplies.append({
            "name": item.get("item"),
            "status": simple_status
        })
        
    return {
        "supplies": formatted_supplies
    }

@router.get("/hospital-overview")
def get_hospital_overview():
    """
    Returns static hospital capacity data.
    Tool Name: hospital-overview
    """
    return HOSPITAL_CAPACITY
