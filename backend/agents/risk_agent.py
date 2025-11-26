import datetime
import random

class RiskAssessmentAgent:
    """
    Risk Assessment Engine
    Computes real-time risk scores (0-100) based on multi-modal inputs.
    """

    def __init__(self):
        # Weights for risk formula
        self.W_AQI = 0.25
        self.W_SLOPE = 0.20
        self.W_EPIDEMIC = 0.15
        self.W_FESTIVAL = 0.15
        self.W_HUMIDITY = 0.05
        self.W_ICU = 0.20

    def calculate_risk(self, inputs):
        """
        Compute comprehensive risk assessment using weighted formula.
        
        inputs: {
            "aqi": int,
            "patient_slope_6h": float (e.g., 1.2 means 20% increase),
            "epidemic_index": float (0-10),
            "festival_nearby": bool,
            "humidity": float,
            "icu_occupancy": float (0.0-1.0)
        }
        """
        
        # 1. Normalize Inputs to 0-100 scale
        aqi_score = min(100, (inputs.get('aqi', 0) / 500) * 100)
        
        slope = inputs.get('patient_slope_6h', 1.0)
        slope_score = min(100, max(0, (slope - 1.0) * 200)) # 1.5 slope -> 100 score
        
        epidemic_score = min(100, inputs.get('epidemic_index', 0) * 10)
        
        festival_score = 100 if inputs.get('festival_nearby', False) else 0
        
        # Humidity risk (high humidity + heat or cold can trigger respiratory)
        humidity = inputs.get('humidity', 50)
        humidity_score = 0
        if humidity > 80 or humidity < 30:
            humidity_score = 50
            
        icu_score = min(100, inputs.get('icu_occupancy', 0) * 100)

        # 2. Apply Weighted Formula
        raw_risk = (
            (self.W_AQI * aqi_score) +
            (self.W_SLOPE * slope_score) +
            (self.W_EPIDEMIC * epidemic_score) +
            (self.W_FESTIVAL * festival_score) +
            (self.W_HUMIDITY * humidity_score) +
            (self.W_ICU * icu_score)
        )
        
        # 3. Contributing Factors
        factors = []
        if aqi_score > 60: factors.append(f"High AQI ({inputs.get('aqi')})")
        if slope > 1.1: factors.append("Rising Patient Inflow")
        if inputs.get('festival_nearby'): factors.append("Upcoming Festival")
        if icu_score > 80: factors.append("ICU Capacity Critical")
        if epidemic_score > 50: factors.append("Epidemic Alert")

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "hospital_risk_index": int(raw_risk),
            "level": self._get_level(raw_risk),
            "breakdown": {
                "aqi_risk": int(aqi_score),
                "icu_risk": int(icu_score),
                "respiratory_risk": int((aqi_score + humidity_score)/2)
            },
            "contributing_factors": factors
        }

    def _get_level(self, score):
        if score >= 80: return "CRITICAL"
        if score >= 60: return "HIGH"
        if score >= 30: return "MODERATE"
        return "LOW"

    def get_risk_forecast(self, days=7):
        # Mock forecast
        return [{"date": (datetime.date.today() + datetime.timedelta(days=i)).isoformat(), "risk": random.randint(30, 80)} for i in range(days)]
