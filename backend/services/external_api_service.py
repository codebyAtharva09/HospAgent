import requests
import json
from datetime import datetime, timedelta
import random

class ExternalAPIService:
    def __init__(self):
        self.base_urls = {
            'pollution': 'https://api.openaq.org/v2/latest',
            'weather': 'https://api.openweathermap.org/data/2.5/weather',
            'festival': 'https://api.indianfestivalapi.com',
            'epidemic': 'https://api.epidemictracking.com'
        }
        # Mock API keys - in production, use environment variables
        self.api_keys = {
            'weather': 'mock_weather_key',
            'pollution': 'mock_pollution_key'
        }

    def get_pollution_data(self, city='Mumbai'):
        """Get current AQI data for a city."""
        # Mock implementation - in real scenario, call actual API
        return {
            'city': city,
            'aqi': random.randint(50, 350),
            'pm25': random.uniform(10, 150),
            'pm10': random.uniform(20, 200),
            'no2': random.uniform(10, 80),
            'so2': random.uniform(5, 40),
            'co': random.uniform(0.5, 2.0),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_api'
        }

    def get_weather_data(self, city='Mumbai'):
        """Get current weather data."""
        # Mock implementation
        return {
            'city': city,
            'temperature': random.uniform(20, 40),
            'humidity': random.randint(30, 90),
            'pressure': random.randint(1000, 1020),
            'wind_speed': random.uniform(5, 25),
            'description': random.choice(['clear sky', 'few clouds', 'scattered clouds', 'broken clouds', 'shower rain', 'rain', 'thunderstorm']),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_api'
        }

    def get_festival_data(self, days_ahead=30):
        """Get upcoming festival data."""
        # Mock festival data for India
        festivals = [
            {'name': 'Diwali', 'date': '2024-11-12', 'type': 'religious', 'expected_crowd': 'high'},
            {'name': 'Holi', 'date': '2024-03-25', 'type': 'religious', 'expected_crowd': 'high'},
            {'name': 'Eid', 'date': '2024-04-10', 'type': 'religious', 'expected_crowd': 'medium'},
            {'name': 'Christmas', 'date': '2024-12-25', 'type': 'religious', 'expected_crowd': 'low'},
            {'name': 'New Year', 'date': '2025-01-01', 'type': 'cultural', 'expected_crowd': 'medium'}
        ]

        upcoming = []
        for festival in festivals:
            festival_date = datetime.strptime(festival['date'], '%Y-%m-%d').date()
            days_until = (festival_date - datetime.now().date()).days
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    **festival,
                    'days_until': days_until,
                    'health_impact': 'high' if festival['expected_crowd'] == 'high' else 'medium'
                })

        return upcoming

    def get_epidemic_data(self):
        """Get current epidemic/surveillance data."""
        # Mock epidemic data
        diseases = ['Influenza', 'Dengue', 'COVID-19', 'Chikungunya']
        return {
            'active_outbreaks': [
                {
                    'disease': random.choice(diseases),
                    'cases_this_week': random.randint(50, 500),
                    'severity': random.choice(['low', 'medium', 'high']),
                    'regions_affected': ['Mumbai', 'Delhi', 'Bangalore'],
                    'trend': random.choice(['increasing', 'stable', 'decreasing'])
                }
            ],
            'surveillance_alerts': [
                {
                    'type': 'respiratory_symptoms',
                    'level': random.choice(['normal', 'elevated', 'high']),
                    'locations': ['City Hospital', 'Regional Clinic']
                }
            ],
            'last_updated': datetime.now().isoformat(),
            'source': 'mock_api'
        }

    def get_forecast_weather(self, days=7):
        """Get weather forecast for next few days."""
        forecast = []
        base_temp = 28  # Base temperature for Mumbai

        for i in range(days):
            date = (datetime.now() + timedelta(days=i+1)).date()
            # Add some seasonal variation
            temp_variation = random.uniform(-3, 3)
            temp = base_temp + temp_variation

            forecast.append({
                'date': date.isoformat(),
                'temperature': round(temp, 1),
                'humidity': random.randint(40, 85),
                'aqi': random.randint(80, 250),
                'weather_condition': random.choice(['sunny', 'cloudy', 'rainy', 'partly_cloudy'])
            })

        return forecast

    def get_pollution_forecast(self, days=7):
        """Get pollution forecast for next few days."""
        forecast = []

        for i in range(days):
            date = (datetime.now() + timedelta(days=i+1)).date()
            # Pollution tends to be higher on certain days
            base_aqi = 120
            if date.weekday() >= 5:  # Weekend
                base_aqi += 30
            if random.random() < 0.3:  # Random pollution events
                base_aqi += 50

            forecast.append({
                'date': date.isoformat(),
                'aqi': min(400, base_aqi + random.randint(-20, 40)),
                'pm25': random.uniform(20, 120),
                'pm10': random.uniform(40, 180),
                'dominant_pollutant': random.choice(['PM2.5', 'PM10', 'NO2', 'CO'])
            })

        return forecast

    def get_combined_environmental_data(self):
        """Get combined environmental data for risk assessment."""
        return {
            'pollution': self.get_pollution_data(),
            'weather': self.get_weather_data(),
            'festivals': self.get_festival_data(14),  # Next 2 weeks
            'epidemic': self.get_epidemic_data(),
            'forecasts': {
                'weather': self.get_forecast_weather(7),
                'pollution': self.get_pollution_forecast(7)
            },
            'timestamp': datetime.now().isoformat()
        }
