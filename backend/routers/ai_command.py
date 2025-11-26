import os
import json
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import os

# Force load .env file
load_dotenv()

# Import services/engines to build context
from services.env_client import EnvironmentClient
from services.festival_client import FestivalClient
from services.festival_repository import FestivalRepository
from engines.risk_engine import RiskEngine
from engines.forecast_engine import ForecastEngine
from engines.staffing_engine import StaffingEngine
from engines.supply_engine import SupplyEngine

router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize services
env_client = EnvironmentClient()
festival_client = FestivalClient()
festival_repo = FestivalRepository()
risk_engine = RiskEngine()
forecast_engine = ForecastEngine()
staffing_engine = StaffingEngine()
supply_engine = SupplyEngine()

class CommandRequest(BaseModel):
    question: str

class CommandResponse(BaseModel):
    answer: str

async def build_context() -> Dict[str, Any]:
    """
    Gather all relevant HospAgent context for the LLM.
    """
    try:
        # 1. Live Environment
        # Note: In a real scenario, we might want to cache this or handle failures gracefully
        # For now, we'll try to fetch live, fallback to defaults if needed
        try:
            real_env = await env_client.get_live_data()
        except:
            real_env = {}

        # Map AQI for internal engines
        aqi_index = real_env.get("aqi_index_1_5", 3)
        aqi_map = {1: 50, 2: 100, 3: 200, 4: 300, 5: 400}
        internal_aqi_score = aqi_map.get(aqi_index, 200)

        # 2. Festivals
        festivals = festival_repo.get_upcoming_festivals(days_ahead=30)
        if not festivals:
            festivals = festival_client.fetch_festivals(days_ahead=30)
        
        festival_features = festival_client.calculate_festival_features(festivals)

        # 3. Risk Calculation (using placeholder operational data for now)
        risk_inputs = {
            "aqi": internal_aqi_score,
            "pm2_5": real_env.get("pollutants", {}).get("pm2_5", 0),
            "pm10": real_env.get("pollutants", {}).get("pm10", 0),
            "temperature": real_env.get("temperature_c", 25),
            "humidity": real_env.get("humidity", 50),
            "patient_slope_6h": 1.1,
            "epidemic_index": 2.0,
            "festival_nearby": festival_features.get("is_high_risk_festival_window", False),
            "icu_occupancy": 0.75,
            "current_patients": 160,
        }
        risk_result = risk_engine.calculate_comprehensive_risk(risk_inputs)

        # 4. Forecast
        forecast_context = {
            "aqi": internal_aqi_score,
            "temperature": real_env.get("temperature_c", 25),
            "humidity": real_env.get("humidity", 50),
            "epidemic_severity": 2.0,
            "patient_slope_24h": 1.1,
            "festivals": festivals,
            "current_load": 160,
        }
        forecast_result = forecast_engine.generate_forecast(days=7, context=forecast_context)

        # 5. Staffing
        today_forecast = forecast_result[0] if forecast_result else None
        predicted_patients = today_forecast["total_patients"] if today_forecast else 160
        respiratory_cases = today_forecast["breakdown"]["respiratory"] if today_forecast else 0
        
        staffing_result = staffing_engine.recommend_staffing(
            predicted_patients_today=predicted_patients,
            icu_risk=risk_result["breakdown"]["icu_risk"],
            epidemic_index=2.0,
            aqi_level=internal_aqi_score,
            respiratory_cases=respiratory_cases,
        )

        # 6. Supplies
        supply_result = supply_engine.recommend_supplies(
            forecast=forecast_result,
            current_stock=None,
            festival_window=festival_features.get("is_high_risk_festival_window", False),
            aqi_level=internal_aqi_score,
            epidemic_index=2.0,
        )

        return {
            "environment": {
                "aqi": internal_aqi_score,
                "temperature": real_env.get("temperature_c"),
                "weather": real_env.get("weather_desc"),
                "pollutants": real_env.get("pollutants")
            },
            "risk": {
                "level": risk_result["level"],
                "score": risk_result["hospital_risk_index"],
                "factors": risk_result["contributing_factors"],
                "explanations": risk_result.get("explanations", [])
            },
            "forecast_summary": [
                {"date": f["date"], "patients": f["total_patients"]} for f in forecast_result[:3]
            ],
            "staffing_recommendation": staffing_result[0] if staffing_result else {},
            "critical_supplies": [s for s in supply_result if s["status"] in ["LOW", "CRITICAL"]],
            "upcoming_festivals": [
                {"name": f.get("summary", f.get("name")), "date": f.get("date"), "high_risk": f.get("high_risk", False)} 
                for f in festivals[:3]
            ]
        }
    except Exception as e:
        print(f"Error building context: {e}")
        return {"error": "Could not fetch full context"}

async def call_llm(prompt: str) -> str:
    """
    Call the configured LLM provider.
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    api_key = os.getenv("LLM_API_KEY")
    
    print(f"DEBUG: LLM Provider: {provider}")
    if api_key:
        print(f"DEBUG: API Key loaded: {api_key[:4]}...{api_key[-4:]} (Length: {len(api_key)})")
    else:
        print("DEBUG: API Key is MISSING or EMPTY")

    if not api_key:
        return "LLM_API_KEY is missing. Please configure the backend environment."

    try:
        if provider == "groq":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "You are HospAgent."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    },
                    timeout=10.0
                )
                if response.status_code != 200:
                    return f"Groq API Error: {response.text}"
                return response.json()["choices"][0]["message"]["content"]
        
        elif provider == "openai":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are HospAgent."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    },
                    timeout=10.0
                )
                if response.status_code != 200:
                    return f"OpenAI API Error: {response.text}"
                return response.json()["choices"][0]["message"]["content"]
        
        elif provider == "gemini":
             # Simplified Gemini REST call
             url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
             async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}]
                    },
                    timeout=10.0
                )
                if response.status_code != 200:
                    return f"Gemini API Error: {response.text}"
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        else:
            return f"Unsupported LLM provider: {provider}"

    except Exception as e:
        return f"LLM Call Failed: {str(e)}"

@router.post("/command", response_model=CommandResponse)
async def handle_command(request: CommandRequest):
    """
    Main AI Command endpoint.
    """
    context = await build_context()
    
    system_prompt = """
You are the AI Hospital Command Bot for HospAgent SurgeOps.
You talk ONLY to hospital administrators, ER managers, and operations staff.
You NEVER give medical or treatment advice to individual patients.
You must base your answers ONLY on the provided HospAgent context JSON.

If the user asks for medical advice, tell them to contact a doctor and steer the answer back to hospital operations.

When possible, respond with:
1. A short summary (2–3 lines)
2. 3–5 bullet points
3. A clear recommendation action

Context:
"""
    
    full_prompt = f"{system_prompt}\n{json.dumps(context, indent=2)}\n\nUser Question: {request.question}"
    
    answer = await call_llm(full_prompt)
    
    return CommandResponse(answer=answer)
