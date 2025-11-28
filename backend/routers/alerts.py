from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import uuid

# Import Agents
from agents.risk_agent import RiskAssessmentAgent
from agents.surge_forecast_agent import SurgeForecastAgent
from agents.resource_optimizer_agent import ResourceOptimizerAgent
from agents.calendar_agent import CalendarAgent
from services.env_client import EnvironmentClient

router = APIRouter(tags=["alerts"])

# Initialize Agents
risk_agent = RiskAssessmentAgent()
forecast_agent = SurgeForecastAgent()
resource_agent = ResourceOptimizerAgent()
calendar_agent = CalendarAgent()
env_client = EnvironmentClient()

# Hospital Capacity Config (Mock)
HOSPITAL_CAPACITY = {
    "doctors": 25,
    "nurses": 60,
    "oxygen_cylinders": 100,
    "n95_masks": 500,
    "iv_fluids": 200
}

class Alert(BaseModel):
    id: str
    type: str # AQI_SURGE, FESTIVAL_RISK, SUPPLY_SHORTAGE, STAFF_SHORTAGE
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    title: str
    message: str
    timestamp: str
    recommendation: str
    data: Dict[str, Any]

def generate_ai_recommendation(alert_type: str, context: Dict[str, Any]) -> str:
    """
    Rule-based AI recommendation generator.
    In a full production system, this would call an LLM.
    """
    if alert_type == "AQI_SURGE":
        aqi = context.get('aqi', 0)
        return f"AI Recommendation: Activate Respiratory Protocol Level {2 if aqi > 300 else 1}. Increase Pulmonology staff by 2 and ensure Oxygen reserves > 80%."
    
    elif alert_type == "FESTIVAL_RISK":
        name = context.get('name', 'Event')
        return f"AI Recommendation: Deploy Trauma Team Alpha for {name}. Pre-position 2 ambulances at high-traffic zones."
        
    elif alert_type == "SUPPLY_SHORTAGE":
        items = context.get('items', [])
        return f"AI Recommendation: Initiate Emergency Procurement for {', '.join(items)}. Contact alternate suppliers list B."
        
    elif alert_type == "STAFF_SHORTAGE":
        docs = context.get('doctors', 0)
        nurses = context.get('nurses', 0)
        return f"AI Recommendation: Critical Staffing Gap. Call in {docs} off-duty doctors and {nurses} nurses. Authorize overtime pay."
        
    return "AI Recommendation: Monitor situation closely."

from services.data_loader import data_loader

@router.get("/hospital-overview")
def get_hospital_overview_endpoint():
    """
    Returns hospital capacity overview from CSV data.
    Used ONLY by the Overview page.
    """
    try:
        overview = data_loader.get_hospital_overview()
        specializations = data_loader.get_doctor_specializations()
        
        # Add extra fields if not present in overview (mocking if missing from CSV)
        overview["wards"] = overview.get("wards", 8)
        overview["operating_theaters"] = overview.get("operating_theaters", 4)
        overview["doctors_by_specialization"] = specializations
        
        return overview
    except Exception as e:
        print(f"Error fetching hospital overview: {e}")
        # Fallback
        return {
            "total_doctors": 25,
            "total_nurses": 70,
            "total_beds": 120,
            "icu_beds": 18,
            "ventilators": 10,
            "ambulances": 3,
            "wards": 8,
            "operating_theaters": 4,
            "doctors_by_specialization": [
                {"name": "General Medicine", "count": 8},
                {"name": "Surgery", "count": 5},
                {"name": "Pediatrics", "count": 4},
                {"name": "Orthopedics", "count": 3}
            ]
        }
@router.get("/command-center")
async def get_command_center_data():
    """
    Unified endpoint for n8n and Frontend.
    Returns current status of all monitored metrics.
    ALWAYS fetches live data.
    """
    # 1. Env Data
    try:
        env_data = await env_client.get_live_data()
        if not env_data:
            # If live data returns None/Empty but no exception, raise error
            raise HTTPException(status_code=503, detail="Live environment data unavailable")
    except Exception as e:
        print(f"Live env fetch failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch live environment data: {str(e)}")

    aqi = env_data.get("aqi_number", env_data.get("aqi_index_1_5", 0) * 50)
    temp = env_data.get("temperature_c", 25)
    humidity = env_data.get("humidity", 50)
    
    # 2. Forecast (Mock logic using agents, but could be CSV backed)
    # Pass dynamic context to make forecast responsive
    forecast_context = {
        "aqi": aqi,
        "temperature": temp,
        "humidity": humidity,
        "patient_slope_24h": random.uniform(0.9, 1.1) # Simulate changing trends
    }
    forecast = forecast_agent.predict_load(days=7, context=forecast_context)
    today_forecast = forecast[0] if forecast else {"total_patients": 150}
    
    # 3. Festivals
    festivals = calendar_agent.get_upcoming_festivals(days=7)
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    festival_tomorrow = next((f for f in festivals if f['date'] == tomorrow_date), None)
    
    # 4. Resources (Staff & Supply)
    # Use DataLoader for baseline capacity
    overview = data_loader.get_hospital_overview()
    
    # Calculate requirements based on forecast
    resource_plan = resource_agent.optimize_resources(forecast, [], festivals)
    staff_today = resource_plan['staffing'][0]['requirements'] if resource_plan['staffing'] else {"doctors": 20, "nurses": 50}
    supplies_today = resource_plan['supplies'][0]['items'] if resource_plan['supplies'] else {}
    
    # Calculate Shortages / Status
    staff_shortage = {
        "doctors": max(0, staff_today.get('doctors', 0) - overview['total_doctors']),
        "nurses": max(0, staff_today.get('nurses', 0) - overview['total_nurses'])
    }
    
    supply_status = {}
    # Use CSV supplies as base, then override with dynamic status if needed
    csv_supplies = data_loader.get_default_supplies()
    for item in csv_supplies:
        supply_status[item['name']] = item['status']

    # Dynamic check against requirements
    for item, req in supplies_today.items():
        # Simple logic: if req > 100 (mock capacity), flag it
        # In real app, compare against inventory.csv
        if req > 100: 
             supply_status[item] = "LOW"
    
    # 5. Risk Calculation
    risk_inputs = {
        "aqi": aqi,
        "pm2_5": env_data.get("pollutants", {}).get("pm2_5", 0),
        "pm10": env_data.get("pollutants", {}).get("pm10", 0),
        "temperature": env_data.get("temperature_c", 25),
        "humidity": env_data.get("humidity", 50),
        "patient_slope_6h": 1.1, 
        "epidemic_index": 2.0, 
        "festival_nearby": bool(festival_tomorrow),
        "icu_occupancy": 0.75, 
        "current_patients": today_forecast.get('total_patients', 150)
    }
    risk_result = risk_agent.calculate_risk(risk_inputs)

    # Format supplies as list
    # Format supplies as list
    formatted_supplies = []
    
    # Get base inventory list
    csv_supplies = data_loader.get_default_supplies()
    
    for item_obj in csv_supplies:
        name = item_obj['name']
        # Get required from resource agent
        # Normalize name to match resource agent keys (Title Case -> snake_case)
        key = name.lower().replace(' ', '_')
        required = supplies_today.get(key, 0)
        
        # Mock available inventory (since CSV doesn't have it)
        # In a real app, this would come from an inventory DB
        # We'll make it dynamic based on status to be consistent
        status = supply_status.get(name, item_obj.get('status', 'OK'))
        
        if status == 'CRITICAL':
            available = int(required * 0.3)
        elif status == 'LOW':
            available = int(required * 0.6)
        elif status == 'MEDIUM':
            available = int(required * 0.9)
        else: # OK
            available = int(max(required * 1.5, 100)) # At least 100 or 1.5x required
            
        formatted_supplies.append({
            "name": name,
            "status": status,
            "required": required,
            "available": available
        })

    # Map forecast to requested keys
    formatted_forecast = []
    if forecast:
        for day in forecast:
            formatted_forecast.append({
                "date": day.get("date"),
                "total": day.get("total_patients", 0),
                "respiratory": day.get("breakdown", {}).get("respiratory", 0)
            })

    return {
        "env": {
            "aqi": int(aqi),
            "pm25": float(env_data.get("pollutants", {}).get("pm2_5", 0)),
            "temp_c": float(env_data.get("temperature_c", 25)),
            "weather_label": str(env_data.get("weather", "Clear")),
            "last_updated_utc": env_data.get("last_updated_utc")
        },
        "risk": {
            "index": int(risk_result.get("hospital_risk_index", 0)),
            "level": str(risk_result.get("level", "UNKNOWN"))
        },
        "risk_analysis": {
            "factors": risk_result.get("contributing_factors", []),
            "confidence": risk_result.get("confidence", 0.95)
        },
        "festival": {
            "name": festival_tomorrow['name'] if festival_tomorrow else None,
            "date": festival_tomorrow['date'] if festival_tomorrow else None,
            "risk_level": "HIGH" if festival_tomorrow and festival_tomorrow.get('is_high_risk') else "LOW",
            "is_tomorrow": bool(festival_tomorrow),
            "advisory": festival_tomorrow.get('advisory') if festival_tomorrow else None
        },
        "forecast": {
            "days": formatted_forecast,
            "peak_load": int(max([d.get('total_patients', 0) for d in forecast]) if forecast else 0),
            "avg_respiratory": int(sum([d.get("breakdown", {}).get("respiratory", 0) for d in forecast]) / len(forecast)) if forecast else 0
        },
        "staffing": {
            "today": {
                "required": staff_today,
                "available": {"doctors": overview['total_doctors'], "nurses": overview['total_nurses']},
                "shortage": staff_shortage
            }
        },
        "supplies": formatted_supplies,
        "hospital_overview": overview
    }

@router.get("/alerts/test")
def test_alerts():
    """
    Returns sample alert data for frontend testing.
    """
    return {
        "alerts": [
            {
                "id": "test-1",
                "type": "AQI_SURGE",
                "severity": "HIGH",
                "title": "High Pollution Surge Detected",
                "message": "AQI is 312. Respiratory cases expected to rise by +27.",
                "recommendation": "AI Recommendation: Activate Respiratory Protocol Level 2. Increase Pulmonology staff by 2.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "test-2",
                "type": "SUPPLY_SHORTAGE",
                "severity": "CRITICAL",
                "title": "Critical Supply Shortage",
                "message": "Oxygen Cylinders LOW. Forecasted depletion within 14 hours.",
                "recommendation": "AI Recommendation: Initiate Emergency Procurement for Oxygen. Contact alternate suppliers.",
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat()
            }
        ]
    }

@router.post("/alerts/log")
async def log_alert(alert: Dict[str, Any]):
    """
    Log an alert sent by the n8n workflow.
    """
    # In a real system, save to DB. For now, just print or store in memory.
    print(f"[{datetime.now().isoformat()}] ALERT LOGGED: {alert}")
    
    # Optional: Store in history for deduplication if needed, though n8n handles its own logic
    key = f"{alert.get('type')}_{alert.get('message')[:20]}"
    ALERT_HISTORY[key] = {"timestamp": datetime.now(), "severity": alert.get('severity')}
    
    return {"status": "logged", "timestamp": datetime.now().isoformat()}

