"""
Risk Engine - Multi-factor hospital risk assessment
Computes real-time risk scores based on environmental and operational factors
"""

from datetime import datetime
from typing import Dict, Any, List, Literal
import json
import os
from pydantic import BaseModel

class SeasonalDiseaseSummary(BaseModel):
    active_diseases: List[str]
    seasonal_risk_index: float  # 0–1
    commentary: str

class EpidemicSummary(BaseModel):
    epidemic_index: float       # 0–1
    level: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    reason: str

class RiskEngine:
    """
    Algorithmic risk calculation engine.
    Can be upgraded to ML model later.
    """
    
    def __init__(self):
        # Risk weights (tunable)
        self.WEIGHTS = {
            'aqi': 0.20,
            'patient_slope': 0.15,
            'epidemic': 0.20,
            'festival': 0.15,
            'icu_pressure': 0.15,
            'seasonal': 0.15
        }
        
        # Thresholds
        self.AQI_CRITICAL = 300
        self.AQI_HIGH = 200
        self.ICU_CRITICAL = 0.85
        self.ICU_HIGH = 0.70
        
        # Load seasonal config
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../data/seasonal_config.json')
            with open(config_path, 'r') as f:
                self.seasonal_config = json.load(f)
        except Exception as e:
            print(f"Error loading seasonal config: {e}")
            self.seasonal_config = {"disease_factors": [], "epidemic_default": 0.1}
        
    def calculate_comprehensive_risk(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate multi-dimensional risk assessment.
        
        Args:
            inputs: {
                'aqi': int,
                'pm2_5': float,
                'pm10': float,
                'temperature': float,
                'humidity': float,
                'patient_slope_6h': float,  # 1.0 = no change, 1.2 = 20% increase
                'epidemic_index': float,    # 0-10 scale
                'festival_nearby': bool,
                'icu_occupancy': float,     # 0.0-1.0
                'current_patients': int
            }
        
        Returns:
            Comprehensive risk assessment with scores and explanations
        """
        
        # Extract inputs with defaults
        aqi = inputs.get('aqi', 100)
        pm2_5 = inputs.get('pm2_5', 0)
        pm10 = inputs.get('pm10', 0)
        temp = inputs.get('temperature', 25)
        humidity = inputs.get('humidity', 50)
        slope = inputs.get('patient_slope_6h', 1.0)
        epidemic = inputs.get('epidemic_index', 0)
        festival = inputs.get('festival_nearby', False)
        icu_occ = inputs.get('icu_occupancy', 0.5)
        current_patients = inputs.get('current_patients', 150)
        
        # Calculate component scores (0-100)
        aqi_score = self._calculate_aqi_risk(aqi, pm2_5, pm10)
        slope_score = self._calculate_slope_risk(slope)
        epidemic_score = self._calculate_epidemic_risk(epidemic)
        festival_score = 100 if festival else 0
        icu_score = self._calculate_icu_risk(icu_occ)
        weather_score = self._calculate_weather_risk(temp, humidity)
        
        # Seasonal Risk
        seasonal_summary = self._calculate_seasonal_risk()
        seasonal_score = seasonal_summary.seasonal_risk_index * 100
        
        # Epidemic Summary
        epidemic_summary = self._generate_epidemic_summary(epidemic)

        # Weighted composite score
        composite_risk = (
            self.WEIGHTS['aqi'] * aqi_score +
            self.WEIGHTS['patient_slope'] * slope_score +
            self.WEIGHTS['epidemic'] * epidemic_score +
            self.WEIGHTS['festival'] * festival_score +
            self.WEIGHTS['icu_pressure'] * icu_score +
            self.WEIGHTS['seasonal'] * seasonal_score
        )
        
        # Generate explanations
        factors = self._generate_factors(
            aqi, aqi_score, slope, epidemic, festival, icu_occ, temp, humidity
        )
        
        # Calculate department-specific risks
        dept_risks = self._calculate_department_risks(
            aqi_score, icu_score, epidemic_score, festival_score
        )
        
        # Determine risk level
        level = self._get_risk_level(composite_risk)
        
        # Calculate supply risks
        supply_risks = self._calculate_supply_risks(
            current_patients, aqi_score, epidemic_score
        )
        
        # Calculate burnout risk (mock data - in production, fetch from staff DB)
        burnout_high_count = self._calculate_burnout_count(current_patients, icu_occ)
        burnout_note = self._generate_burnout_note(burnout_high_count)
        
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'hospital_risk_index': int(composite_risk),
            'index': int(composite_risk), # Alias for frontend
            'level': level,
            'breakdown': {
                'aqi_risk': int(aqi_score),
                'icu_risk': int(icu_score),
                'respiratory_risk': int((aqi_score + weather_score) / 2),
                'epidemic_risk': int(epidemic_score),
                'surge_risk': int(slope_score),
                'seasonal_risk': int(seasonal_score)
            },
            'seasonal': seasonal_summary.dict(),
            'epidemic': epidemic_summary.dict(),
            'contributing_factors': factors,
            'department_risks': dept_risks,
            'supply_risks': supply_risks,
            'recommendations': self._generate_recommendations(composite_risk, factors),
            'burnout_high_count': burnout_high_count,
            'burnout_note': burnout_note,
            'explanations': self._generate_explanations(
                aqi, pm2_5, pm10, temp, slope, epidemic, festival, icu_occ
            )
        }

    def _generate_explanations(self, aqi, pm2_5, pm10, temp, slope, epidemic, festival, icu_occ):
        """Generate detailed AI explainability bullet points"""
        explanations = []
        
        # AQI Impact
        if aqi > 150:
            resp_cases = int((aqi - 100) * 0.2)
            explanations.append(f"AQI is {aqi} (+{resp_cases} respiratory cases estimated)")
        elif aqi > 100:
            explanations.append(f"AQI is {aqi} (Moderate respiratory impact)")

        # PM2.5 Spike
        if pm2_5 > 60:
            er_visits = int((pm2_5 - 60) * 0.3) + 5
            explanations.append(f"PM2.5 spike overnight (+{er_visits} ER visits)")

        # Festival
        if festival:
            explanations.append("Major Festival today (+15 trauma cases)")

        # Temperature
        if temp < 18:
            flu_cases = int((18 - temp) * 1.5)
            explanations.append(f"Temperature drop to {temp}°C (+{flu_cases} flu cases)")
        elif temp > 35:
            heat_cases = int((temp - 35) * 2)
            explanations.append(f"High temperature {temp}°C (+{heat_cases} heat stress cases)")

        # Epidemic
        if epidemic > 2:
            epi_cases = int(epidemic * 4)
            explanations.append(f"Epidemic multiplier increased (+{epi_cases} cases)")

        # ICU
        if icu_occ > 0.7:
            explanations.append(f"ICU occupancy {int(icu_occ*100)}% (resource pressure)")

        # Fallback
        if not explanations:
            explanations.append("Risk factors are within normal limits")

        return explanations
    
    def _calculate_aqi_risk(self, aqi: int, pm2_5: float, pm10: float) -> float:
        """Calculate air quality risk score"""
        if aqi >= self.AQI_CRITICAL:
            return 100
        elif aqi >= self.AQI_HIGH:
            return 60 + ((aqi - self.AQI_HIGH) / (self.AQI_CRITICAL - self.AQI_HIGH)) * 40
        else:
            return (aqi / self.AQI_HIGH) * 60
    
    def _calculate_slope_risk(self, slope: float) -> float:
        """Calculate patient inflow trend risk"""
        if slope >= 1.5:
            return 100
        elif slope >= 1.2:
            return 70
        elif slope >= 1.1:
            return 40
        elif slope <= 0.9:
            return 0
        else:
            return 20
    
    def _calculate_epidemic_risk(self, index: float) -> float:
        """Calculate epidemic risk (0-10 scale to 0-100)"""
        return min(100, index * 10)
    
    def _calculate_icu_risk(self, occupancy: float) -> float:
        """Calculate ICU pressure risk"""
        if occupancy >= self.ICU_CRITICAL:
            return 100
        elif occupancy >= self.ICU_HIGH:
            return 60 + ((occupancy - self.ICU_HIGH) / (self.ICU_CRITICAL - self.ICU_HIGH)) * 40
        else:
            return (occupancy / self.ICU_HIGH) * 60
    
    def _calculate_weather_risk(self, temp: float, humidity: float) -> float:
        """Calculate weather-related health risk"""
        risk = 0
        
        # Extreme temperatures
        if temp < 15 or temp > 38:
            risk += 50
        elif temp < 18 or temp > 35:
            risk += 30
        
        # Extreme humidity
        if humidity > 85 or humidity < 25:
            risk += 50
        elif humidity > 75 or humidity < 35:
            risk += 20
        
        return min(100, risk)
    
    def _calculate_department_risks(self, aqi: float, icu: float, 
                                    epidemic: float, festival: float) -> Dict[str, int]:
        """Calculate risk for each department"""
        return {
            'Emergency': int((aqi * 0.3 + festival * 0.4 + epidemic * 0.3)),
            'ICU': int(icu),
            'Pulmonology': int((aqi * 0.7 + epidemic * 0.3)),
            'Pediatrics': int((epidemic * 0.5 + festival * 0.3 + aqi * 0.2)),
            'General_Ward': int((festival * 0.4 + epidemic * 0.4 + aqi * 0.2))
        }
    
    def _calculate_supply_risks(self, patients: int, aqi: float, 
                                epidemic: float) -> Dict[str, str]:
        """Estimate supply risk levels"""
        oxygen_risk = 'HIGH' if aqi > 70 else 'MEDIUM' if aqi > 40 else 'LOW'
        mask_risk = 'HIGH' if (aqi > 60 or epidemic > 50) else 'MEDIUM' if aqi > 30 else 'LOW'
        bed_risk = 'HIGH' if patients > 200 else 'MEDIUM' if patients > 150 else 'LOW'
        
        return {
            'oxygen_cylinders': oxygen_risk,
            'n95_masks': mask_risk,
            'icu_beds': bed_risk,
            'ventilators': 'HIGH' if (aqi > 80 and epidemic > 60) else 'MEDIUM'
        }
    
    def _generate_factors(self, aqi: int, aqi_score: float, slope: float,
                         epidemic: float, festival: bool, icu_occ: float,
                         temp: float, humidity: float) -> list:
        """Generate human-readable contributing factors"""
        factors = []
        
        if aqi >= self.AQI_CRITICAL:
            factors.append(f"Critical AQI ({aqi}) - Severe Air Pollution")
        elif aqi >= self.AQI_HIGH:
            factors.append(f"High AQI ({aqi}) - Poor Air Quality")
        
        if slope >= 1.2:
            factors.append(f"Patient Surge Detected (+{int((slope-1)*100)}% in 6h)")
        
        if festival:
            factors.append("Major Festival Period - Increased Trauma/Burn Cases")
        
        if icu_occ >= self.ICU_CRITICAL:
            factors.append(f"ICU Critical ({int(icu_occ*100)}% Occupancy)")
        elif icu_occ >= self.ICU_HIGH:
            factors.append(f"ICU High Pressure ({int(icu_occ*100)}% Occupancy)")
        
        if epidemic >= 7:
            factors.append(f"Active Epidemic Alert (Severity: {epidemic}/10)")
        elif epidemic >= 4:
            factors.append(f"Elevated Disease Activity (Severity: {epidemic}/10)")
        
        if temp > 38:
            factors.append(f"Extreme Heat ({temp}°C) - Heat-related Cases Expected")
        elif temp < 15:
            factors.append(f"Cold Wave ({temp}°C) - Respiratory Cases Rising")
        
        if not factors:
            factors.append("Normal Operating Conditions")
        
        return factors
    
    def _generate_recommendations(self, risk: float, factors: list) -> list:
        """Generate actionable recommendations"""
        recs = []
        
        if risk >= 80:
            recs.append("ACTIVATE LEVEL 3 EMERGENCY PROTOCOL")
            recs.append("Request additional staff from partner hospitals")
            recs.append("Defer all non-urgent procedures")
        elif risk >= 60:
            recs.append("Activate Level 2 Surge Protocol")
            recs.append("Increase staff on next shift")
            recs.append("Expedite supply orders")
        elif risk >= 40:
            recs.append("Monitor situation closely")
            recs.append("Prepare surge capacity")
        else:
            recs.append("Maintain standard operations")
        
        return recs
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MODERATE"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _calculate_seasonal_risk(self) -> SeasonalDiseaseSummary:
        current_month = datetime.now().month
        active_diseases = []
        total_risk = 0.0
        
        for disease in self.seasonal_config.get("disease_factors", []):
            if current_month in disease["months"]:
                active_diseases.append(disease["name"])
                total_risk += disease["base_risk"]
        
        # Cap at 1.0
        total_risk = min(1.0, total_risk)
        
        commentary = "No major seasonal risks."
        if active_diseases:
            commentary = f"Active seasonal risks: {', '.join(active_diseases)}"
            
        return SeasonalDiseaseSummary(
            active_diseases=active_diseases,
            seasonal_risk_index=total_risk,
            commentary=commentary
        )

    def _generate_epidemic_summary(self, index: float) -> EpidemicSummary:
        # index is 0-10 usually from input, let's normalize or use as is
        # If input is 0-10, we map to levels
        level = "LOW"
        if index >= 8:
            level = "CRITICAL"
        elif index >= 6:
            level = "HIGH"
        elif index >= 4:
            level = "MODERATE"
            
        return EpidemicSummary(
            epidemic_index=index/10.0 if index > 1 else index, # Normalize if needed, assuming input might be 0-10
            level=level,
            reason=f"Epidemic index at {index}"
        )

    def _calculate_burnout_count(self, patients: int, icu_occ: float) -> int:
        """
        Calculate number of staff at high burnout risk.
        Based on patient load and ICU pressure.
        In production, this would query actual staff shift data.
        """
        # Simple heuristic: high load + high ICU = more burnout
        if patients > 200 and icu_occ > 0.8:
            return 5
        elif patients > 180 and icu_occ > 0.7:
            return 3
        elif patients > 160 or icu_occ > 0.75:
            return 2
        elif patients > 140:
            return 1
        else:
            return 0
    
    def _generate_burnout_note(self, count: int) -> str:
        """Generate human-readable burnout note"""
        if count == 0:
            return "All staff within normal workload limits"
        elif count == 1:
            return "1 staff member showing signs of burnout based on shift load"
        else:
            return f"{count} staff members showing signs of burnout based on shift load"

