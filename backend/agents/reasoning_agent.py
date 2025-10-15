import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import json

class ReasoningAgent:
    """
    Reasoning Agent: Analyzes data and forecasts patient inflow, bed occupancy, and resource needs
    Uses ML models (Random Forest) for predictions
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()

    def load_model(self):
        """Load pre-trained ML model"""
        try:
            self.model = joblib.load('models/reasoning_model.pkl')
            print("Reasoning model loaded successfully")
        except FileNotFoundError:
            print("Model not found, using default logic")
            self.model = None

    def preprocess_data(self, data):
        """Preprocess input data for ML model"""
        features = []

        # Extract relevant features
        his_data = data.get('his', {})
        aqi_data = data.get('aqi', {})
        festival_data = data.get('festivals', {})

        # HIS features
        bed_occupancy = his_data.get('bed_occupancy', 0)
        patient_count = his_data.get('patient_count', 0)
        icu_occupancy = his_data.get('icu_occupancy', 0)
        er_waiting = his_data.get('er_waiting', 0)

        # AQI features
        aqi = aqi_data.get('aqi', 0)
        pm25 = aqi_data.get('pm25', 0)
        pm10 = aqi_data.get('pm10', 0)

        # Festival features
        festival_impact = 0
        upcoming_festivals = festival_data.get('events', [])
        for festival in upcoming_festivals:
            if festival.get('days_until', 30) <= 7:  # Within a week
                if festival.get('expected_crowd') == 'high':
                    festival_impact = 1
                elif festival.get('expected_crowd') == 'medium':
                    festival_impact = 0.5

        features = [bed_occupancy, patient_count, icu_occupancy, er_waiting,
                   aqi, pm25, pm10, festival_impact]

        return np.array(features).reshape(1, -1)

    def forecast_patient_inflow(self, data, days_ahead=7):
        """Forecast patient inflow for next N days"""
        forecasts = []

        for i in range(days_ahead):
            # Use ML model if available, otherwise use rule-based logic
            if self.model:
                features = self.preprocess_data(data)
                scaled_features = self.scaler.transform(features)
                predicted_patients = self.model.predict(scaled_features)[0]
            else:
                # Rule-based fallback
                base_patients = data.get('his', {}).get('patient_count', 200)
                aqi_multiplier = 1 + (data.get('aqi', {}).get('aqi', 50) / 500)
                festival_multiplier = 1.3 if any(f.get('days_until', 30) <= 7 for f in data.get('festivals', {}).get('events', [])) else 1.0
                predicted_patients = base_patients * aqi_multiplier * festival_multiplier

            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            forecasts.append({
                'date': date,
                'predicted_patients': int(predicted_patients),
                'confidence': 0.85 if self.model else 0.7
            })

        return forecasts

    def forecast_bed_occupancy(self, forecasts):
        """Forecast bed occupancy based on patient predictions"""
        bed_forecasts = []

        for forecast in forecasts:
            predicted_patients = forecast['predicted_patients']
            # Estimate bed occupancy (rough calculation)
            estimated_occupancy = min(95, (predicted_patients / 300) * 100)  # Assuming 300 bed capacity

            bed_forecasts.append({
                'date': forecast['date'],
                'predicted_occupancy': round(estimated_occupancy, 1),
                'available_beds': int(300 * (1 - estimated_occupancy/100))
            })

        return bed_forecasts

    def forecast_resource_needs(self, forecasts):
        """Forecast resource needs (oxygen, medicines, staff)"""
        resource_forecasts = []

        for forecast in forecasts:
            patients = forecast['predicted_patients']

            # Resource calculations based on patient load
            oxygen_cylinders = max(10, int(patients * 0.3))  # 30% may need oxygen
            medicines = int(patients * 1.5)  # Average medicines per patient
            masks = int(patients * 2)  # Surgical masks

            resource_forecasts.append({
                'date': forecast['date'],
                'oxygen_cylinders': oxygen_cylinders,
                'medicines': medicines,
                'masks': masks,
                'critical_threshold': patients > 250  # Flag for critical load
            })

        return resource_forecasts

    def analyze_trends(self, historical_data):
        """Analyze trends from historical data"""
        trends = {
            'patient_trend': 'increasing' if len(historical_data) > 1 else 'stable',
            'aqi_impact': 'high' if any(d.get('aqi', {}).get('aqi', 0) > 150 for d in historical_data) else 'moderate',
            'seasonal_pattern': self.detect_seasonal_pattern(historical_data)
        }

        return trends

    def detect_seasonal_pattern(self, data):
        """Detect seasonal patterns in the data"""
        # Simple pattern detection
        if any('festival' in str(d).lower() for d in data):
            return 'festival_season'
        elif any(d.get('aqi', {}).get('aqi', 0) > 200 for d in data):
            return 'pollution_season'
        else:
            return 'normal_season'

    def generate_insights(self, data):
        """Generate comprehensive insights from all analyses"""
        patient_forecasts = self.forecast_patient_inflow(data)
        bed_forecasts = self.forecast_bed_occupancy(patient_forecasts)
        resource_forecasts = self.forecast_resource_needs(patient_forecasts)

        insights = {
            'timestamp': datetime.now().isoformat(),
            'patient_forecasts': patient_forecasts,
            'bed_forecasts': bed_forecasts,
            'resource_forecasts': resource_forecasts,
            'alerts': self.generate_alerts(patient_forecasts, bed_forecasts, resource_forecasts),
            'recommendations': self.generate_recommendations(patient_forecasts)
        }

        return insights

    def generate_alerts(self, patient_forecasts, bed_forecasts, resource_forecasts):
        """Generate alerts based on forecasts"""
        alerts = []

        for pf, bf, rf in zip(patient_forecasts, bed_forecasts, resource_forecasts):
            if pf['predicted_patients'] > 250:
                alerts.append({
                    'type': 'patient_surge',
                    'severity': 'high',
                    'message': f'Patient surge expected on {pf["date"]}: {pf["predicted_patients"]} patients'
                })

            if bf['predicted_occupancy'] > 90:
                alerts.append({
                    'type': 'bed_shortage',
                    'severity': 'critical',
                    'message': f'Bed occupancy will exceed 90% on {bf["date"]}'
                })

            if rf['critical_threshold']:
                alerts.append({
                    'type': 'resource_critical',
                    'severity': 'high',
                    'message': f'Resource shortage expected on {rf["date"]}'
                })

        return alerts

    def generate_recommendations(self, forecasts):
        """Generate preliminary recommendations"""
        recommendations = []

        max_patients = max(f['predicted_patients'] for f in forecasts)
        if max_patients > 250:
            extra_staff = (max_patients - 200) // 20
            recommendations.append(f'Add {extra_staff} doctors and {extra_staff * 2} nurses')

        if any(f['predicted_patients'] > 200 for f in forecasts):
            recommendations.append('Increase oxygen cylinder stock by 50%')
            recommendations.append('Stock up on respiratory medicines')

        return recommendations
