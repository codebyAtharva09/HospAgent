"""
Enhanced Data Integration Service
Integrates real-time data from multiple sources for HospAgent
"""
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DataIntegrationService:
    """
    Integrates data from multiple real-time sources:
    - AQI (OpenAQ API)
    - Weather (OpenWeather API)
    - Festival calendars
    - Epidemiological trends
    """
    
    def __init__(self):
        self.openaq_base_url = "https://api.openaq.org/v2"
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY', '')
        
        # Festival calendar for India (2025)
        self.festival_calendar = self._load_festival_calendar()
        
    def _load_festival_calendar(self) -> List[Dict]:
        """Load Indian festival calendar with health impact predictions"""
        return [
            {
                'name': 'Diwali',
                'date': '2025-10-20',
                'duration_days': 5,
                'health_impact': 'high',
                'risk_factors': ['respiratory', 'burns', 'accidents', 'pollution'],
                'expected_surge': 1.8,  # 80% increase in patients
                'departments_affected': ['ER', 'Burns', 'Respiratory', 'Pediatrics']
            },
            {
                'name': 'Holi',
                'date': '2025-03-14',
                'duration_days': 2,
                'health_impact': 'medium',
                'risk_factors': ['skin_allergies', 'eye_injuries', 'accidents'],
                'expected_surge': 1.4,
                'departments_affected': ['ER', 'Dermatology', 'Ophthalmology']
            },
            {
                'name': 'Eid al-Fitr',
                'date': '2025-03-31',
                'duration_days': 3,
                'health_impact': 'medium',
                'risk_factors': ['food_poisoning', 'accidents', 'crowd_injuries'],
                'expected_surge': 1.3,
                'departments_affected': ['ER', 'Gastroenterology']
            },
            {
                'name': 'Ganesh Chaturthi',
                'date': '2025-08-27',
                'duration_days': 10,
                'health_impact': 'high',
                'risk_factors': ['drowning', 'accidents', 'crowd_crush'],
                'expected_surge': 1.6,
                'departments_affected': ['ER', 'Trauma', 'ICU']
            },
            {
                'name': 'Durga Puja',
                'date': '2025-09-30',
                'duration_days': 5,
                'health_impact': 'medium',
                'risk_factors': ['accidents', 'crowd_injuries', 'food_poisoning'],
                'expected_surge': 1.4,
                'departments_affected': ['ER', 'Gastroenterology']
            }
        ]
    
    def get_current_aqi(self, city: str = "Mumbai") -> Dict:
        """
        Fetch current AQI data from OpenAQ
        Falls back to mock data if API unavailable
        """
        try:
            # Try real API first
            params = {
                'city': city,
                'limit': 1,
                'order_by': 'datetime',
                'sort': 'desc'
            }
            response = requests.get(
                f"{self.openaq_base_url}/latest",
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    measurements = result.get('measurements', [])
                    
                    aqi_data = {
                        'city': city,
                        'aqi': self._calculate_aqi(measurements),
                        'pm25': next((m['value'] for m in measurements if m['parameter'] == 'pm25'), None),
                        'pm10': next((m['value'] for m in measurements if m['parameter'] == 'pm10'), None),
                        'timestamp': result.get('lastUpdated'),
                        'source': 'openaq'
                    }
                    return aqi_data
        except Exception as e:
            logger.warning(f"OpenAQ API failed: {e}, using fallback data")
        
        # Fallback to mock data
        return self._get_mock_aqi(city)
    
    def _calculate_aqi(self, measurements: List[Dict]) -> int:
        """Calculate AQI from pollutant measurements"""
        # Simplified AQI calculation based on PM2.5
        pm25 = next((m['value'] for m in measurements if m['parameter'] == 'pm25'), None)
        if pm25:
            # US EPA AQI breakpoints for PM2.5
            if pm25 <= 12: return int((50/12) * pm25)
            elif pm25 <= 35.4: return int(50 + ((100-50)/(35.4-12)) * (pm25-12))
            elif pm25 <= 55.4: return int(100 + ((150-100)/(55.4-35.4)) * (pm25-35.4))
            elif pm25 <= 150.4: return int(150 + ((200-150)/(150.4-55.4)) * (pm25-55.4))
            elif pm25 <= 250.4: return int(200 + ((300-200)/(250.4-150.4)) * (pm25-150.4))
            else: return int(300 + ((500-300)/(500.4-250.4)) * (pm25-250.4))
        return 100  # Default moderate
    
    def _get_mock_aqi(self, city: str) -> Dict:
        """Mock AQI data for development"""
        import random
        return {
            'city': city,
            'aqi': random.randint(80, 350),
            'pm25': random.uniform(20, 150),
            'pm10': random.uniform(40, 200),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock'
        }
    
    def get_weather_forecast(self, city: str = "Mumbai", days: int = 7) -> List[Dict]:
        """
        Fetch weather forecast from OpenWeather
        Falls back to mock data if API unavailable
        """
        try:
            if self.openweather_api_key:
                # Try real API
                params = {
                    'q': city,
                    'appid': self.openweather_api_key,
                    'units': 'metric',
                    'cnt': days
                }
                response = requests.get(
                    f"{self.openweather_base_url}/forecast/daily",
                    params=params,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    forecast = []
                    for day in data.get('list', []):
                        forecast.append({
                            'date': datetime.fromtimestamp(day['dt']).date().isoformat(),
                            'temperature': day['temp']['day'],
                            'humidity': day['humidity'],
                            'description': day['weather'][0]['description'],
                            'source': 'openweather'
                        })
                    return forecast
        except Exception as e:
            logger.warning(f"OpenWeather API failed: {e}, using fallback data")
        
        # Fallback to mock data
        return self._get_mock_weather(days)
    
    def _get_mock_weather(self, days: int) -> List[Dict]:
        """Mock weather data for development"""
        import random
        forecast = []
        base_temp = 28  # Mumbai average
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i+1)).date()
            forecast.append({
                'date': date.isoformat(),
                'temperature': round(base_temp + random.uniform(-3, 5), 1),
                'humidity': random.randint(40, 85),
                'description': random.choice(['clear sky', 'few clouds', 'scattered clouds', 'light rain']),
                'source': 'mock'
            })
        return forecast
    
    def get_upcoming_festivals(self, days_ahead: int = 30) -> List[Dict]:
        """Get festivals in the next N days with health impact data"""
        today = datetime.now().date()
        upcoming = []
        
        for festival in self.festival_calendar:
            festival_date = datetime.strptime(festival['date'], '%Y-%m-%d').date()
            days_until = (festival_date - today).days
            
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    **festival,
                    'days_until': days_until,
                    'alert_level': 'critical' if days_until <= 7 else 'high' if days_until <= 14 else 'medium'
                })
        
        return sorted(upcoming, key=lambda x: x['days_until'])
    
    def get_epidemic_trends(self) -> Dict:
        """
        Get current epidemic/disease surveillance data
        In production, this would integrate with government health APIs
        """
        # Mock epidemic data - in production, integrate with IDSP, WHO, etc.
        import random
        
        diseases = [
            {
                'name': 'Seasonal Influenza',
                'cases_this_week': random.randint(50, 200),
                'trend': random.choice(['increasing', 'stable', 'decreasing']),
                'severity': random.choice(['low', 'medium', 'high']),
                'affected_age_groups': ['children', 'elderly'],
                'departments_impacted': ['ER', 'Pediatrics', 'General Medicine']
            },
            {
                'name': 'Dengue',
                'cases_this_week': random.randint(20, 100),
                'trend': 'increasing' if datetime.now().month in [7, 8, 9, 10] else 'stable',
                'severity': 'medium',
                'affected_age_groups': ['all'],
                'departments_impacted': ['ER', 'ICU', 'General Medicine']
            }
        ]
        
        return {
            'active_outbreaks': diseases,
            'total_cases': sum(d['cases_this_week'] for d in diseases),
            'high_risk_diseases': [d['name'] for d in diseases if d['severity'] == 'high'],
            'last_updated': datetime.now().isoformat()
        }
    
    def get_integrated_risk_assessment(self) -> Dict:
        """
        Combine all data sources for comprehensive risk assessment
        This is the core data fusion function
        """
        aqi_data = self.get_current_aqi()
        weather = self.get_weather_forecast(days=7)
        festivals = self.get_upcoming_festivals(days_ahead=30)
        epidemics = self.get_epidemic_trends()
        
        # Calculate composite risk score
        risk_score = 0
        risk_factors = []
        
        # AQI contribution
        if aqi_data['aqi'] > 300:
            risk_score += 40
            risk_factors.append('critical_pollution')
        elif aqi_data['aqi'] > 200:
            risk_score += 25
            risk_factors.append('high_pollution')
        elif aqi_data['aqi'] > 150:
            risk_score += 10
            risk_factors.append('moderate_pollution')
        
        # Festival contribution
        if festivals:
            nearest_festival = festivals[0]
            if nearest_festival['days_until'] <= 7:
                risk_score += 30 * nearest_festival['expected_surge']
                risk_factors.append(f"festival_{nearest_festival['name']}")
        
        # Epidemic contribution
        high_risk_diseases = epidemics.get('high_risk_diseases', [])
        if high_risk_diseases:
            risk_score += 20 * len(high_risk_diseases)
            risk_factors.extend([f"epidemic_{d}" for d in high_risk_diseases])
        
        # Weather contribution (extreme heat/cold)
        avg_temp = sum(d['temperature'] for d in weather) / len(weather)
        if avg_temp > 38:
            risk_score += 15
            risk_factors.append('extreme_heat')
        elif avg_temp < 15:
            risk_score += 10
            risk_factors.append('extreme_cold')
        
        return {
            'composite_risk_score': min(100, int(risk_score)),
            'risk_level': 'critical' if risk_score > 70 else 'high' if risk_score > 40 else 'medium' if risk_score > 20 else 'low',
            'risk_factors': risk_factors,
            'data_sources': {
                'aqi': aqi_data,
                'weather': weather[:3],  # Next 3 days
                'upcoming_festivals': festivals,
                'epidemics': epidemics
            },
            'predicted_surge_multiplier': 1 + (risk_score / 100),
            'timestamp': datetime.now().isoformat()
        }

# Singleton instance
data_integration_service = DataIntegrationService()
