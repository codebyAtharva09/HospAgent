from fastapi import APIRouter
from routers.predict import predict_live, LiveResponse
from services.data_loader import data_loader

router = APIRouter(tags=["command-center"])

@router.get("/command-center")
async def get_command_center_data():
    """
    Aggregated data for the Command Center Dashboard.
    Transforms the internal prediction engine output to match the frontend schema.
    """
    # Get raw data from prediction engines
    live_data = await predict_live(days=7)
    
    # Handle error case from predict_live
    if live_data.error:
        # Return a safe fallback structure with the error message
        return {
            "env": live_data.env or {},
            "risk": {"index": 0, "level": "UNKNOWN"},
            "risk_analysis": {"factors": [f"Error: {live_data.error}"], "confidence": 0.0},
            "staffing": {"today": {"required": {"doctors": 0, "nurses": 0}, "available": {"doctors": 0, "nurses": 0}, "shortage": {"doctors": 0, "nurses": 0}}},
            "supplies": [],
            "festival": {"name": None, "date": None, "risk_level": None, "is_tomorrow": False, "advisory": None},
            "forecast": {"days": [], "peak_load": 0, "avg_respiratory": 0},
            "hospital_overview": live_data.hospital_overview or {},
            "wellbeing": {"burnout_risk_level": "LOW", "note": "Data unavailable"}
        }

    # 1. Transform Staffing
    # Backend: List[Dict] -> Frontend: { today: { ... } }
    staffing_today = live_data.staffing[0] if live_data.staffing else {}
    req_doctors = staffing_today.get("doctors", 0)
    req_nurses = staffing_today.get("nurses", 0)
    
    # Mock available staff (usually from DB, here we simulate)
    avail_doctors = int(req_doctors * 0.9) # Simulate slight shortage
    avail_nurses = int(req_nurses * 0.95)
    
    staffing_transformed = {
        "today": {
            "required": {
                "doctors": req_doctors,
                "nurses": req_nurses
            },
            "available": {
                "doctors": avail_doctors,
                "nurses": avail_nurses
            },
            "shortage": {
                "doctors": max(0, req_doctors - avail_doctors),
                "nurses": max(0, req_nurses - avail_nurses)
            }
        }
    }

    # 2. Transform Supplies
    # Backend: List[Dict] -> Frontend: List[Dict] (rename item -> name, add available)
    supplies_transformed = []
    for s in live_data.supplies:
        req = s.get("required", 0)
        status = s.get("status", "OK")
        # Mock available based on status
        if status == "OK":
            avail = int(req * 1.5)
        elif status == "MEDIUM":
            avail = int(req * 1.1)
        else:
            avail = int(req * 0.8)
            
        supplies_transformed.append({
            "name": s.get("item"),
            "status": status,
            "required": req,
            "available": avail
        })

    # 3. Transform Forecast
    # Backend: List[Dict] -> Frontend: { days: [...], peak_load: ..., avg_respiratory: ... }
    forecast_days = []
    peak_load = 0
    total_resp = 0
    
    for f in live_data.forecast:
        total = f.get("total_patients", 0)
        resp = f.get("breakdown", {}).get("respiratory", 0)
        peak_load = max(peak_load, total)
        total_resp += resp
        
        forecast_days.append({
            "date": f.get("date"),
            "total": total,
            "respiratory": resp
        })
        
    avg_resp = int(total_resp / len(live_data.forecast)) if live_data.forecast else 0
    
    forecast_transformed = {
        "days": forecast_days,
        "peak_load": peak_load,
        "avg_respiratory": avg_resp
    }

    # 4. Transform Festival
    # Backend: List[Dict] -> Frontend: Single Object
    festival_transformed = {
        "name": None,
        "date": None,
        "risk_level": "LOW",
        "is_tomorrow": False,
        "advisory": None
    }
    
    if live_data.festivals:
        # Find next high risk festival or just the next one
        next_fest = live_data.festivals[0]
        
        # Calculate days until
        try:
            fest_date = datetime.strptime(next_fest.get("date"), "%Y-%m-%d").date()
            days_until = (fest_date - datetime.now().date()).days
        except:
            days_until = 999

        is_high_risk = next_fest.get("is_high_risk")
        is_close = days_until <= 7
        
        festival_transformed = {
            "name": next_fest.get("name"),
            "date": next_fest.get("date"),
            "risk_level": "HIGH" if (is_high_risk and is_close) else "LOW",
            "is_tomorrow": days_until == 1,
            "advisory": "High patient load expected" if (is_high_risk and is_close) else "Standard operations"
        }

    # 5. Wellbeing / Burnout
    # Extracted from risk result
    burnout_count = live_data.risk.get("burnout_high_count", 0) if live_data.risk else 0
    burnout_note = live_data.risk.get("burnout_note", "Staff workload normal") if live_data.risk else ""
    
    wellbeing_transformed = {
        "burnout_risk_level": "HIGH" if burnout_count > 0 else "LOW",
        "note": burnout_note
    }

    # 6. Risk Analysis
    risk_factors = live_data.risk.get("contributing_factors", []) if live_data.risk else []

    return {
        "env": live_data.env,
        "risk": live_data.risk,
        "risk_analysis": {
            "factors": risk_factors,
            "confidence": 0.92 # Mock confidence score
        },
        "staffing": staffing_transformed,
        "supplies": supplies_transformed,
        "festival": festival_transformed,
        "forecast": forecast_transformed,
        "hospital_overview": live_data.hospital_overview,
        "wellbeing": wellbeing_transformed
    }

@router.get("/hospital-overview")
def get_hospital_overview():
    overview = data_loader.get_hospital_overview()
    specs = data_loader.get_doctor_specializations()
    
    # Add missing fields (mock or default if not in CSV)
    # DataLoader returns dict, we can extend it
    overview["wards"] = 8 # Default
    overview["operating_theaters"] = 4 # Default
    overview["doctors_by_specialization"] = specs
    
    return overview
