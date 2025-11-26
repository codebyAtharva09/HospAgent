import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class SurgeForecastAgent:
    """
    Surge Forecast Agent
    Predicts next 3/7/14 days patient load.
    """

    def __init__(self):
        pass

    def predict_load(self, days=7, context=None):
        """
        Predict patient load using multi-factor regression logic (Mocked for demo).
        """
        if context is None: context = {}
        
        forecasts = []
        base_load = 150
        
        # Extract features
        aqi = context.get('aqi', 100)
        temp = context.get('temperature', 25)
        humidity = context.get('humidity', 50)
        epidemic_severity = context.get('epidemic_severity', 0) # 0-10
        recent_slope = context.get('patient_slope_24h', 1.0)
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            day_of_week = date.weekday()
            
            # 1. Day of Week (Mon/Fri busy)
            dow_factor = 1.15 if day_of_week in [0, 4] else (0.85 if day_of_week == 6 else 1.0)
            
            # 2. AQI Impact (Linear above 100)
            aqi_factor = 1.0 + max(0, (aqi - 100) / 400.0)
            
            # 3. Weather Impact (Cold + Dry or Hot + Humid)
            weather_factor = 1.0
            if temp < 15 or temp > 35: weather_factor += 0.1
            
            # 4. Epidemic Impact
            epidemic_factor = 1.0 + (epidemic_severity * 0.08)
            
            # 5. Momentum (Slope) - decays over time
            momentum_factor = 1.0 + ((recent_slope - 1.0) * (0.8 ** i))
            
            # Calculate Total
            total = int(base_load * dow_factor * aqi_factor * weather_factor * epidemic_factor * momentum_factor)
            
            # Breakdown
            resp_pct = 0.15 + (0.2 if aqi > 200 else 0) + (0.1 if epidemic_severity > 5 else 0)
            icu_pct = 0.05 + (0.05 if epidemic_severity > 7 else 0)
            
            forecasts.append({
                "date": date.strftime('%Y-%m-%d'),
                "total_patients": total,
                "breakdown": {
                    "respiratory": int(total * resp_pct),
                    "trauma": int(total * 0.1),
                    "icu_candidates": int(total * icu_pct)
                },
                "staff_demand": {
                    "doctors": int(total / 15),
                    "nurses": int(total / 6)
                }
            })
            
        return forecasts
