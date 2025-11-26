"""
Forecast Engine - Patient load prediction
Generates 3/7/14 day forecasts using rule-based model (upgradeable to ML)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import math

class ForecastEngine:
    """
    Patient load forecasting engine.
    Uses algorithmic approach with upgrade path to ML models.
    """
    
    def __init__(self):
        self.BASE_DAILY_LOAD = 150  # Base patient count
        
        # Day-of-week multipliers
        self.DOW_FACTORS = {
            0: 1.15,  # Monday - Post-weekend surge
            1: 1.05,  # Tuesday
            2: 1.00,  # Wednesday
            3: 1.00,  # Thursday
            4: 1.10,  # Friday
            5: 0.85,  # Saturday
            6: 0.80   # Sunday
        }
    
    def generate_forecast(self, days: int, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate patient load forecast for next N days.
        
        Args:
            days: Number of days to forecast (3, 7, or 14)
            context: {
                'aqi': int,
                'temperature': float,
                'humidity': float,
                'epidemic_severity': float (0-10),
                'patient_slope_24h': float,
                'festivals': List[dict],  # Upcoming festivals
                'current_load': int
            }
        
        Returns:
            List of daily forecasts with breakdowns
        """
        
        # Extract context
        aqi = context.get('aqi', 100)
        temp = context.get('temperature', 25)
        humidity = context.get('humidity', 50)
        epidemic = context.get('epidemic_severity', 0)
        slope = context.get('patient_slope_24h', 1.0)
        festivals = context.get('festivals', [])
        current_load = context.get('current_load', self.BASE_DAILY_LOAD)
        
        forecasts = []
        
        for day_offset in range(days):
            target_date = datetime.now() + timedelta(days=day_offset)
            date_str = target_date.strftime('%Y-%m-%d')
            dow = target_date.weekday()
            
            # Calculate factors
            dow_factor = self.DOW_FACTORS[dow]
            aqi_factor = self._calculate_aqi_factor(aqi)
            weather_factor = self._calculate_weather_factor(temp, humidity)
            epidemic_factor = self._calculate_epidemic_factor(epidemic)
            festival_factor = self._calculate_festival_factor(target_date, festivals)
            momentum_factor = self._calculate_momentum_factor(slope, day_offset)
            
            # Composite prediction
            predicted_total = int(
                self.BASE_DAILY_LOAD * 
                dow_factor * 
                aqi_factor * 
                weather_factor * 
                epidemic_factor * 
                festival_factor * 
                momentum_factor
            )
            
            # Add realistic variance
            variance = int(predicted_total * 0.05)  # ±5%
            predicted_total += (hash(date_str) % (2 * variance)) - variance
            
            # Calculate departmental breakdown
            breakdown = self._calculate_breakdown(
                predicted_total, aqi, epidemic, festival_factor > 1.0
            )
            
            # Calculate staff requirements
            staff_demand = self._calculate_staff_demand(predicted_total, breakdown)
            
            # Calculate confidence
            confidence = self._calculate_confidence(day_offset, epidemic, festival_factor)
            
            forecasts.append({
                'date': date_str,
                'day_of_week': target_date.strftime('%A'),
                'total_patients': predicted_total,
                'confidence': confidence,
                'breakdown': breakdown,
                'staff_demand': staff_demand,
                'factors': {
                    'day_of_week_impact': round(dow_factor, 2),
                    'aqi_impact': round(aqi_factor, 2),
                    'weather_impact': round(weather_factor, 2),
                    'epidemic_impact': round(epidemic_factor, 2),
                    'festival_impact': round(festival_factor, 2)
                },
                'alerts': self._generate_alerts(predicted_total, breakdown, festival_factor)
            })
        
        return forecasts
    
    def _calculate_aqi_factor(self, aqi: int) -> float:
        """Calculate AQI impact on patient load"""
        if aqi >= 300:
            return 1.5  # +50% respiratory cases
        elif aqi >= 200:
            return 1.3
        elif aqi >= 150:
            return 1.15
        elif aqi >= 100:
            return 1.05
        else:
            return 1.0
    
    def _calculate_weather_factor(self, temp: float, humidity: float) -> float:
        """Calculate weather impact"""
        factor = 1.0
        
        # Temperature extremes
        if temp > 38 or temp < 15:
            factor *= 1.2
        elif temp > 35 or temp < 18:
            factor *= 1.1
        
        # Humidity extremes
        if humidity > 85 or humidity < 25:
            factor *= 1.1
        
        return factor
    
    def _calculate_epidemic_factor(self, severity: float) -> float:
        """Calculate epidemic impact (0-10 scale)"""
        return 1.0 + (severity * 0.08)  # +8% per severity point
    
    def _calculate_festival_factor(self, target_date: datetime, 
                                   festivals: List[dict]) -> float:
        """Calculate festival proximity impact"""
        for festival in festivals:
            try:
                fest_date = datetime.fromisoformat(festival['date'].replace('Z', '+00:00'))
                days_diff = abs((fest_date.date() - target_date.date()).days)
                
                if festival.get('high_risk', False):
                    if days_diff == 0:
                        return 1.8  # Festival day
                    elif days_diff == 1:
                        return 1.4  # Day before/after
                    elif days_diff <= 3:
                        return 1.2  # Within 3 days
            except:
                continue
        
        return 1.0
    
    def _calculate_momentum_factor(self, slope: float, day_offset: int) -> float:
        """Calculate momentum/trend continuation"""
        # Momentum decays over time
        decay = 0.85 ** day_offset
        return 1.0 + ((slope - 1.0) * decay)
    
    def _calculate_breakdown(self, total: int, aqi: int, 
                            epidemic: float, is_festival: bool) -> Dict[str, int]:
        """Calculate patient distribution by category"""
        
        # Base percentages
        respiratory_pct = 0.15
        trauma_pct = 0.10
        viral_pct = 0.12
        cardiac_pct = 0.08
        pediatric_pct = 0.20
        icu_candidates_pct = 0.05
        
        # Adjust based on conditions
        if aqi > 200:
            respiratory_pct += 0.15
        elif aqi > 150:
            respiratory_pct += 0.08
        
        if epidemic > 5:
            viral_pct += 0.15
            icu_candidates_pct += 0.03
        
        if is_festival:
            trauma_pct += 0.15  # Burns, accidents
            cardiac_pct += 0.05  # Stress-related
        
        # Normalize to ensure total = 100%
        total_pct = (respiratory_pct + trauma_pct + viral_pct + 
                    cardiac_pct + pediatric_pct + icu_candidates_pct)
        
        return {
            'respiratory': int(total * (respiratory_pct / total_pct)),
            'trauma': int(total * (trauma_pct / total_pct)),
            'viral_infectious': int(total * (viral_pct / total_pct)),
            'cardiac': int(total * (cardiac_pct / total_pct)),
            'pediatric': int(total * (pediatric_pct / total_pct)),
            'icu_candidates': int(total * (icu_candidates_pct / total_pct)),
            'other': total - int(total * (
                (respiratory_pct + trauma_pct + viral_pct + 
                 cardiac_pct + pediatric_pct + icu_candidates_pct) / total_pct
            ))
        }
    
    def _calculate_staff_demand(self, total: int, 
                                breakdown: Dict[str, int]) -> Dict[str, int]:
        """Calculate required staff based on patient load"""
        
        # Ratios
        PATIENTS_PER_DOCTOR = 15
        PATIENTS_PER_NURSE = 6
        PATIENTS_PER_SUPPORT = 20
        
        # ICU requires more intensive staffing
        icu_patients = breakdown.get('icu_candidates', 0)
        icu_doctors = math.ceil(icu_patients / 3)
        icu_nurses = math.ceil(icu_patients / 2)
        
        # General ward
        general_patients = total - icu_patients
        general_doctors = math.ceil(general_patients / PATIENTS_PER_DOCTOR)
        general_nurses = math.ceil(general_patients / PATIENTS_PER_NURSE)
        
        return {
            'doctors': general_doctors + icu_doctors,
            'nurses': general_nurses + icu_nurses,
            'support_staff': math.ceil(total / PATIENTS_PER_SUPPORT),
            'icu_specialists': icu_doctors
        }
    
    def _calculate_confidence(self, day_offset: int, epidemic: float, 
                             festival_factor: float) -> float:
        """Calculate forecast confidence (0-100)"""
        
        # Base confidence decreases with time
        base_confidence = 95 - (day_offset * 3)
        
        # Reduce confidence during uncertain conditions
        if epidemic > 7:
            base_confidence -= 10
        elif epidemic > 4:
            base_confidence -= 5
        
        if festival_factor > 1.5:
            base_confidence -= 8
        elif festival_factor > 1.2:
            base_confidence -= 4
        
        return max(60, min(95, base_confidence))
    
    def _generate_alerts(self, total: int, breakdown: Dict[str, int], 
                        festival_factor: float) -> List[str]:
        """Generate alerts for high-risk forecasts"""
        alerts = []
        
        if total > 250:
            alerts.append("SURGE ALERT: Predicted load exceeds capacity")
        
        if breakdown.get('respiratory', 0) > 60:
            alerts.append("High respiratory case volume - Check oxygen supply")
        
        if breakdown.get('icu_candidates', 0) > 15:
            alerts.append("ICU capacity warning - Prepare additional beds")
        
        if festival_factor > 1.5:
            alerts.append("Festival surge - Trauma team on standby")
        
        return alerts
