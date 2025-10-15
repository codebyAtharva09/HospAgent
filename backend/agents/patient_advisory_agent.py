import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class PatientAdvisoryAgent:
    def __init__(self):
        self.advisory_templates = self._load_advisory_templates()
        self.risk_patterns = self._load_risk_patterns()
        self.nlp_model = self._train_nlp_model()

    def _load_advisory_templates(self):
        """Load predefined advisory templates."""
        return {
            'pollution_high': {
                'title': 'High Pollution Alert',
                'message': 'Air quality index is critically high. Elderly patients and those with respiratory conditions should avoid outdoor activities and wear N95 masks.',
                'severity': 'high',
                'target_groups': ['elderly', 'respiratory_patients', 'children']
            },
            'epidemic_risk': {
                'title': 'Epidemic Risk Advisory',
                'message': 'Increased risk of {disease} transmission detected. Please maintain hygiene protocols and consider vaccination if eligible.',
                'severity': 'high',
                'target_groups': ['general_public', 'healthcare_workers']
            },
            'seasonal_flu': {
                'title': 'Seasonal Flu Advisory',
                'message': 'Seasonal flu cases are rising. Annual flu vaccination is recommended, especially for high-risk groups.',
                'severity': 'medium',
                'target_groups': ['elderly', 'children', 'chronic_patients']
            },
            'festival_crowd': {
                'title': 'Festival Health Advisory',
                'message': 'Upcoming festival may cause healthcare facility congestion. Plan medical visits accordingly and stay hydrated.',
                'severity': 'medium',
                'target_groups': ['general_public', 'chronic_patients']
            },
            'heat_wave': {
                'title': 'Heat Wave Health Alert',
                'message': 'Extreme heat conditions detected. Stay hydrated, avoid outdoor activities during peak hours, and monitor for heat-related illnesses.',
                'severity': 'high',
                'target_groups': ['elderly', 'children', 'outdoor_workers']
            }
        }

    def _load_risk_patterns(self):
        """Load patterns for risk assessment."""
        return {
            'aqi_thresholds': {'low': 50, 'moderate': 100, 'high': 200, 'critical': 300},
            'temperature_thresholds': {'normal': 25, 'warm': 30, 'hot': 35, 'extreme': 40},
            'humidity_risks': {'low': 30, 'normal': 60, 'high': 80},
            'epidemic_indicators': ['fever_cluster', 'respiratory_symptoms', 'gastrointestinal_issues']
        }

    def _train_nlp_model(self):
        """Train NLP model for advisory classification."""
        # Mock training data - in real implementation, use actual advisory data
        training_data = [
            ("high pollution respiratory problems", "pollution_high"),
            ("flu season vaccination needed", "seasonal_flu"),
            ("festival crowd medical congestion", "festival_crowd"),
            ("extreme heat dehydration risk", "heat_wave"),
            ("virus outbreak hygiene protocols", "epidemic_risk")
        ]

        texts, labels = zip(*training_data)
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(texts)

        model = MultinomialNB()
        model.fit(X, labels)

        return {'model': model, 'vectorizer': vectorizer}

    def assess_health_risks(self, aqi, temperature, humidity, epidemic_data, festival_data):
        """Assess current health risks based on environmental factors."""
        risks = []

        # AQI-based risks
        if aqi >= self.risk_patterns['aqi_thresholds']['critical']:
            risks.append('pollution_high')
        elif aqi >= self.risk_patterns['aqi_thresholds']['high']:
            risks.append('pollution_moderate')

        # Temperature-based risks
        if temperature >= self.risk_patterns['temperature_thresholds']['extreme']:
            risks.append('heat_wave')
        elif temperature >= self.risk_patterns['temperature_thresholds']['hot']:
            risks.append('heat_alert')

        # Epidemic risks
        if epidemic_data.get('active_cases', 0) > 100:
            risks.append('epidemic_risk')

        # Festival-related risks
        if festival_data.get('crowd_expected', False):
            risks.append('festival_crowd')

        return list(set(risks))  # Remove duplicates

    def generate_advisory(self, risks, patient_demographics=None):
        """Generate personalized advisory based on identified risks."""
        advisories = []

        for risk in risks:
            if risk in self.advisory_templates:
                template = self.advisory_templates[risk].copy()

                # Personalize based on demographics
                if patient_demographics:
                    if 'elderly' in patient_demographics and 'elderly' in template['target_groups']:
                        template['message'] += " Special attention needed for elderly patients."
                    if 'children' in patient_demographics and 'children' in template['target_groups']:
                        template['message'] += " Children should be closely monitored."

                advisories.append(template)

        return advisories

    def create_public_announcement(self, advisory_data):
        """Create formatted public announcement from advisory data."""
        announcements = []

        for advisory in advisory_data:
            announcement = {
                'title': advisory['title'],
                'message': advisory['message'],
                'severity': advisory['severity'],
                'target_groups': advisory['target_groups'],
                'channels': ['hospital_website', 'sms', 'email', 'public_display'],
                'timestamp': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
            }
            announcements.append(announcement)

        return announcements

    def predict_advisory_needs(self, forecast_data, environmental_data):
        """Predict when advisories will be needed based on forecasts."""
        predictions = []

        for forecast in forecast_data:
            date = forecast['date']
            patients = forecast['predicted_patients']
            aqi = forecast.get('aqi', 100)

            # Predict advisory needs based on patient surge and AQI
            if patients > 250 and aqi > 200:
                predictions.append({
                    'date': date,
                    'advisory_type': 'pollution_high',
                    'confidence': 0.9,
                    'reason': f"High patient load ({patients}) combined with poor air quality (AQI: {aqi})"
                })
            elif patients > 200:
                predictions.append({
                    'date': date,
                    'advisory_type': 'general_surge',
                    'confidence': 0.7,
                    'reason': f"Expected patient surge ({patients} patients)"
                })

        return predictions

    def get_advisory_history(self, days=30):
        """Get historical advisory data for analytics."""
        # Mock historical data
        history = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            history.append({
                'date': date,
                'advisories_issued': np.random.randint(0, 3),
                'response_rate': np.random.uniform(0.1, 0.8),
                'effectiveness_score': np.random.uniform(0.5, 0.95)
            })

        return history

    def analyze_advisory_effectiveness(self, advisory_history):
        """Analyze the effectiveness of past advisories."""
        if not advisory_history:
            return {}

        total_advisories = sum(h['advisories_issued'] for h in advisory_history)
        avg_response_rate = np.mean([h['response_rate'] for h in advisory_history])
        avg_effectiveness = np.mean([h['effectiveness_score'] for h in advisory_history])

        return {
            'total_advisories': total_advisories,
            'average_response_rate': round(avg_response_rate, 2),
            'average_effectiveness': round(avg_effectiveness, 2),
            'trend': 'improving' if avg_effectiveness > 0.7 else 'needs_improvement'
        }
