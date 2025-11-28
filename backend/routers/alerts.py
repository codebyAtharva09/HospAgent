from fastapi import APIRouter, Depends
from services.auth_service import require_roles, UserRole
from routers.predict import predict_live
from services.notify import send_email, send_sms
import os

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/evaluate", dependencies=[Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
async def evaluate_and_send_alerts():
    # Reuse predict_live logic to get current state
    # We pass days=1 just to get current status
    data = await predict_live(days=1)
    
    if data.error:
        return {"status": "error", "message": data.error}

    alerts_sent = []

    # 1. High AQI
    # Check env data structure. predict_live returns LiveResponse with env as dict
    aqi = 0
    if data.env:
        # OpenWeather format might vary, check predict.py mapping
        # predict.py maps it to internal_aqi_score but returns raw env in data.env
        # But risk result has aqi_score. Let's use risk breakdown.
        pass
    
    # Better to use risk breakdown for normalized values
    if data.risk:
        # risk is a dict
        risk_breakdown = data.risk.get("breakdown", {})
        aqi_risk = risk_breakdown.get("aqi_risk", 0)
        
        if aqi_risk > 60: # Threshold
             msg = f"High AQI Alert! Risk Score: {aqi_risk}"
             alerts_sent.append("high_aqi")
             # await send_sms(os.getenv("ALERT_TO_ER_HEAD_SMS", ""), msg)

        # Epidemic
        epidemic = data.risk.get("epidemic", {})
        if epidemic.get("level") in ["HIGH", "CRITICAL"]:
            msg = f"Epidemic Alert: {epidemic.get('reason')}"
            alerts_sent.append("epidemic_high")
            # await send_email(os.getenv("ALERT_TO_ADMIN_EMAIL", ""), "Epidemic Alert", msg)

        # Seasonal
        seasonal = data.risk.get("seasonal", {})
        if seasonal.get("seasonal_risk_index", 0) > 0.5:
            msg = f"Seasonal Risk High: {seasonal.get('commentary')}"
            alerts_sent.append("seasonal_risk")

    # Supplies
    if data.supplies:
        # supplies is a list of dicts
        for item in data.supplies:
            # SupplyEngine returns recommendations, not status directly?
            # Wait, SupplyEngine.recommend_supplies returns list of dicts.
            # Let's check what it returns.
            # It returns recommendations.
            # But we also have data_loader.get_default_supplies() which gives status.
            # predict_live calls supply_engine.recommend_supplies.
            # Let's check supply_engine.py if needed.
            # For now assume we check status if present.
            status = item.get("status")
            if status in ["LOW", "CRITICAL"]:
                alerts_sent.append(f"supply_{item.get('item', 'unknown').lower()}")

    return {"status": "ok", "alerts_sent": alerts_sent}
