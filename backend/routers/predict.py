from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.env_client import EnvironmentClient
from services.festival_client import FestivalClient
from services.festival_repository import FestivalRepository
from engines.risk_engine import RiskEngine
from engines.forecast_engine import ForecastEngine
from engines.staffing_engine import StaffingEngine
from engines.supply_engine import SupplyEngine

router = APIRouter(prefix="/predict", tags=["prediction"])

# Initialize services
env_client = EnvironmentClient()
festival_client = FestivalClient()
festival_repo = FestivalRepository()
risk_engine = RiskEngine()
forecast_engine = ForecastEngine()
staffing_engine = StaffingEngine()
supply_engine = SupplyEngine()

# Pydantic models for response
class LiveResponse(BaseModel):
    env: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None
    forecast: List[Dict[str, Any]] = []
    staffing: List[Dict[str, Any]] = []
    supplies: List[Dict[str, Any]] = []
    festivals: List[Dict[str, Any]] = []
    error: Optional[str] = None

@router.get("/live", response_model=LiveResponse)
async def predict_live(
    days: int = Query(default=7, ge=1, le=14, description="Forecast days")
) -> LiveResponse:
    """
    Complete live prediction pipeline with festival, staffing, and supplies.

    Returns a JSON with env, risk, forecast, staffing, supplies, festivals.
    """
    try:
        # 1. Fetch live environmental data
        # This now raises an exception if API fails
        real_env = await env_client.get_live_data()

        # Map AQI index (1-5) to 0-500 scale for internal engines
        aqi_index = real_env.get("aqi_index_1_5", 3)
        aqi_map = {1: 50, 2: 100, 3: 200, 4: 300, 5: 400}
        internal_aqi_score = aqi_map.get(aqi_index, 200)

        # 2. Get upcoming festivals
        festivals = festival_repo.get_upcoming_festivals(days_ahead=30)
        if not festivals:
            festivals = festival_client.fetch_festivals(days_ahead=30)
            if festivals:
                festival_repo.upsert_festivals(festivals)

        # 3. Calculate festival features
        festival_features = festival_client.calculate_festival_features(festivals)

        # 4. Prepare risk inputs (placeholder values for demo)
        patient_slope_6h = 1.1
        epidemic_index = 2.0
        icu_occupancy = 0.75
        current_patients = 160
        risk_inputs = {
            "aqi": internal_aqi_score,
            "pm2_5": real_env.get("pollutants", {}).get("pm2_5", 0),
            "pm10": real_env.get("pollutants", {}).get("pm10", 0),
            "temperature": real_env.get("temperature_c", 25),
            "humidity": real_env.get("humidity", 50),
            "patient_slope_6h": patient_slope_6h,
            "epidemic_index": epidemic_index,
            "festival_nearby": festival_features.get("is_high_risk_festival_window", False),
            "icu_occupancy": icu_occupancy,
            "current_patients": current_patients,
        }

        # 5. Run risk assessment
        risk_result = risk_engine.calculate_comprehensive_risk(risk_inputs)

        # 6. Run forecast
        forecast_context = {
            "aqi": internal_aqi_score,
            "temperature": real_env.get("temperature_c", 25),
            "humidity": real_env.get("humidity", 50),
            "epidemic_severity": epidemic_index,
            "patient_slope_24h": patient_slope_6h,
            "festivals": festivals,
            "current_load": current_patients,
        }
        forecast_result = forecast_engine.generate_forecast(days, forecast_context)

        # 7. Calculate staffing requirements
        today_forecast = forecast_result[0] if forecast_result else None
        predicted_patients_today = today_forecast["total_patients"] if today_forecast else current_patients
        respiratory_cases = today_forecast["breakdown"]["respiratory"] if today_forecast else 0
        staffing_result = staffing_engine.recommend_staffing(
            predicted_patients_today=predicted_patients_today,
            icu_risk=risk_result["breakdown"]["icu_risk"],
            epidemic_index=epidemic_index,
            aqi_level=internal_aqi_score,
            respiratory_cases=respiratory_cases,
        )

        # 8. Calculate supply requirements
        supply_result = supply_engine.recommend_supplies(
            forecast=forecast_result,
            current_stock=None,
            festival_window=festival_features.get("is_high_risk_festival_window", False),
            aqi_level=internal_aqi_score,
            epidemic_index=epidemic_index,
        )

        # Normalize festivals for frontend (name/is_high_risk vs summary/high_risk)
        normalized_festivals = []
        for f in festivals:
            normalized_festivals.append({
                "date": f.get("date"),
                "name": f.get("summary", f.get("name", "Unknown")),
                "is_high_risk": f.get("high_risk", f.get("is_high_risk", False))
            })

        # 9. Return structured response
        return LiveResponse(
            env=real_env, # Return the clean OpenWeather env without modification
            risk=risk_result,
            forecast=forecast_result,
            staffing=staffing_result,
            supplies=supply_result,
            festivals=normalized_festivals[:10],
        )
    except Exception as e:
        # Return a JSON error payload instead of HTML error page
        return LiveResponse(
            error=str(e),
            env=None,
            risk=None,
            forecast=[],
            staffing=[],
        )

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

@router.post("/chat")
async def chat_with_bot(request: ChatRequest):
    """
    Simple AI Hospital Command Bot endpoint.
    In production, this would call OpenAI/Groq API.
    Here we use a heuristic RAG-lite approach for the MVP.
    """
    msg = request.message.lower()
    context = request.context or {}
    
    # Extract context
    risk = context.get('risk', {})
    forecast = context.get('forecast', [])
    staffing = context.get('staffing', [])
    
    response = "I can help you with hospital operations. Ask about risk, staffing, or supplies."
    
    if "risk" in msg or "surge" in msg:
        level = risk.get('level', 'UNKNOWN')
        score = risk.get('hospital_risk_index', 0)
        response = f"Current Hospital Risk is **{level}** (Index: {score}/100). "
        if level in ['HIGH', 'CRITICAL']:
            response += "Immediate action required. Check the Explainability Panel for details."
        else:
            response += "Operations are stable."
            
    elif "staff" in msg or "doctor" in msg or "nurse" in msg:
        if staffing:
            docs = staffing[0].get('doctors', 0)
            nurses = staffing[0].get('nurses', 0)
            response = f"Recommended staffing for next shift: **{docs} Doctors** and **{nurses} Nurses**."
        else:
            response = "No staffing data available currently."
            
    elif "oxygen" in msg or "supply" in msg:
        response = "Supply chain analysis indicates **Oxygen** demand is stable, but monitor **N95 Masks** if AQI rises."
        
    elif "diwali" in msg or "festival" in msg:
        response = "Festivals historically cause a **15-20% surge** in trauma and respiratory cases. Prepare Level 2 protocols."
        
    return {"response": response}

@router.get("/alerts/trigger")
async def trigger_alerts():
    """
    N8N Webhook Endpoint.
    Returns current status for automation workflows.
    """
    # Reuse the live prediction logic (simplified)
    # In a real app, we might cache the last prediction
    try:
        live_data = await predict_live(days=1)
        
        if live_data.error:
            return {"error": live_data.error}
            
        risk = live_data.risk
        env = live_data.env
        forecast = live_data.forecast[0] if live_data.forecast else {}
        staffing = live_data.staffing[0] if live_data.staffing else {}
        
        alerts = []
        
        # 1. Pollution Alert
        if env and env.get('aqi_number', 0) > 200:
            alerts.append({
                "type": "POLLUTION_WARNING",
                "message": f"High AQI detected ({env.get('aqi_number')}). Respiratory surge expected.",
                "severity": "HIGH"
            })
            
        # 2. Risk Alert
        if risk and risk.get('hospital_risk_index', 0) > 70:
            alerts.append({
                "type": "SURGE_RISK",
                "message": f"Hospital Risk Index is {risk.get('hospital_risk_index')}. Activate surge protocols.",
                "severity": "CRITICAL"
            })
            
        # 3. Staffing Alert
        if staffing and staffing.get('doctors', 0) > 20: # Arbitrary threshold
            alerts.append({
                "type": "STAFF_SHORTAGE",
                "message": "High doctor requirement detected for next shift.",
                "severity": "MEDIUM"
            })

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "OK",
            "risk_level": risk.get('level') if risk else "UNKNOWN",
            "alerts": alerts,
            "summary": {
                "aqi": env.get('aqi_number') if env else 0,
                "predicted_patients": forecast.get('total_patients', 0),
                "recommended_doctors": staffing.get('doctors', 0)
            }
        }
        
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
