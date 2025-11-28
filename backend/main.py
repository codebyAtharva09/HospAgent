from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import os

# Import Agents
from agents.risk_agent import RiskAssessmentAgent
from agents.surge_forecast_agent import SurgeForecastAgent
from agents.resource_optimizer_agent import ResourceOptimizerAgent
from agents.calendar_agent import CalendarAgent
from agents.burnout_agent import BurnoutAgent
from agents.advisory_agent import AdvisoryAgent
from agents.simulation_agent import SimulationAgent

# Import Services
from services.env_client import EnvironmentClient

# Import new routers
from routers.festivals import router as festivals_router
from routers.predict import router as predict_router
from routers.calendar import router as calendar_router
from routers.auth import router as auth_router
from routers.alerts import router as alerts_router
from routers.command_center import router as command_center_router
from db_config import create_db_and_tables, get_session
from models.auth import User, UserRole
from services.auth_service import get_password_hash
from sqlmodel import Session, select

app = FastAPI(title="HospAgent SurgeOps", version="2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents & Services
risk_agent = RiskAssessmentAgent()
forecast_agent = SurgeForecastAgent()
resource_agent = ResourceOptimizerAgent()
calendar_agent = CalendarAgent()
burnout_agent = BurnoutAgent()
advisory_agent = AdvisoryAgent()
simulation_agent = SimulationAgent()
env_client = EnvironmentClient()

# Register new routers
from routers import predict, festivals, ai_command
app.include_router(predict.router, prefix="/api")
app.include_router(festivals.router, prefix="/api")
app.include_router(ai_command.router, prefix="/api")

from routers import alerts
app.include_router(alerts.router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(command_center_router, prefix="/api")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Seed users
    with Session(next(get_session()).bind) as session:
        if not session.exec(select(User)).first():
            users = [
                User(email="director@hospital.com", full_name="Super Admin", hashed_password=get_password_hash("password123"), role=UserRole.SUPER_ADMIN),
                User(email="ops@hospital.com", full_name="Admin", hashed_password=get_password_hash("password123"), role=UserRole.ADMIN),
                User(email="frontdesk@hospital.com", full_name="Receptionist", hashed_password=get_password_hash("password123"), role=UserRole.RECEPTION),
                User(email="pharmacy@hospital.com", full_name="Pharmacist", hashed_password=get_password_hash("password123"), role=UserRole.PHARMACIST),
            ]
            for user in users:
                session.add(user)
            session.commit()

from routers import vapi_tools
app.include_router(vapi_tools.router, prefix="/api")

# --- Data Models ---
class LivePredictionResponse(BaseModel):
    env: Dict[str, Any]
    risk: Dict[str, Any]
    forecast: List[Dict[str, Any]]
    staffing: List[Dict[str, Any]]
    supplies: List[Dict[str, Any]]

# --- Routes ---

@app.get("/")
def root():
    return {"message": "HospAgent SurgeOps Live v2.1"}

@app.get("/api/health")
def health():
    """
    Simple health check endpoint.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "HospAgent Backend"
    }

@app.get("/env/live")
async def get_live_env(lat: float = None, lon: float = None):
    """
    Fetch live environmental data (AQI + Weather).
    """
    data = await env_client.get_live_data(lat, lon)
    if "error" in data:
        # If error, we still return the mock data inside 'data' key but with error flag
        return data.get("data", data)
    return data

# Legacy routes for simulation mode
@app.get("/risk/now")
def get_risk_now(aqi: int = 150, slope: float = 1.0, epidemic: float = 2.0, icu: float = 0.7, override_festival: bool = False):
    festivals = calendar_agent.get_upcoming_festivals(days=3)
    is_festival = any(f['is_high_risk'] for f in festivals) or override_festival
    
    inputs = {
        "aqi": aqi,
        "patient_slope_6h": slope,
        "epidemic_index": epidemic,
        "festival_nearby": is_festival,
        "icu_occupancy": icu
    }
    return risk_agent.calculate_risk(inputs)

@app.get("/forecast/patients")
def get_forecast(days: int = 7, aqi: int = 150):
    context = {"aqi": aqi}
    return forecast_agent.predict_load(days, context)

@app.get("/plan/staffing")
def get_staffing_plan(days: int = 3):
    forecast = forecast_agent.predict_load(days)
    holidays = calendar_agent.get_upcoming_festivals(days)
    return resource_agent.optimize_resources(forecast, [], holidays)['staffing']

@app.get("/plan/supplies")
def get_supply_plan(days: int = 3):
    forecast = forecast_agent.predict_load(days)
    holidays = calendar_agent.get_upcoming_festivals(days)
    return resource_agent.optimize_resources(forecast, [], holidays)['supplies']

@app.get("/festivals/upcoming")
def get_festivals(days: int = 30):
    return calendar_agent.get_upcoming_festivals(days)

@app.get("/risk/burnout")
def get_burnout():
    history = [
        {"id": "D1", "consecutive_nights": 4, "weekly_hours": 70},
        {"id": "N1", "consecutive_nights": 1, "weekly_hours": 40}
    ]
    return burnout_agent.calculate_burnout_risk(history)

@app.post("/simulate/scenario")
def run_simulation(scenario: dict):
    return simulation_agent.run_simulation(scenario)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
