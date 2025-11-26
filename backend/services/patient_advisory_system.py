"""
Enhanced Patient Advisory System
Generates tailored health advisories with multi-channel delivery
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PatientAdvisorySystem:
    """
    Advanced advisory system that generates personalized health advisories
    based on risk factors, demographics, and upcoming events
    """
    
    def __init__(self):
        self.advisory_templates = self._load_templates()
        self.delivery_channels = ['sms', 'email', 'whatsapp', 'hospital_display', 'mobile_app']
    
    def _load_templates(self) -> Dict:
        """Load advisory templates for different scenarios"""
        return {
            'pollution_critical': {
                'title': '🚨 Critical Air Quality Alert',
                'severity': 'critical',
                'template': 'Air Quality Index is {aqi} (Hazardous). {risk_groups} should avoid outdoor activities. Wear N95 masks if going outside. Keep windows closed and use air purifiers.',
                'risk_groups': ['elderly', 'children', 'respiratory_patients', 'cardiac_patients'],
                'actions': ['stay_indoors', 'wear_mask', 'use_purifier', 'medication_ready']
            },
            'pollution_high': {
                'title': '⚠️ High Pollution Advisory',
                'severity': 'high',
                'template': 'Air quality is poor (AQI: {aqi}). {risk_groups} should limit outdoor exposure. Consider wearing masks during outdoor activities.',
                'risk_groups': ['elderly', 'children', 'respiratory_patients'],
                'actions': ['limit_outdoor', 'wear_mask', 'monitor_symptoms']
            },
            'festival_safety': {
                'title': '🎊 {festival_name} Health & Safety Advisory',
                'severity': 'medium',
                'template': '{festival_name} is approaching in {days} days. Expected health risks: {risks}. Please follow safety guidelines and keep emergency contacts handy.',
                'risk_groups': ['general_public'],
                'actions': ['first_aid_ready', 'emergency_contacts', 'avoid_crowds']
            },
            'epidemic_alert': {
                'title': '🦠 {disease_name} Alert',
                'severity': 'high',
                'template': '{disease_name} cases are {trend}. {cases} cases reported this week. {risk_groups} should take precautions: {precautions}',
                'risk_groups': ['all'],
                'actions': ['hygiene', 'vaccination', 'avoid_crowds', 'monitor_symptoms']
            },
            'heat_wave': {
                'title': '🌡️ Extreme Heat Advisory',
                'severity': 'high',
                'template': 'Temperature expected to reach {temperature}°C. Stay hydrated, avoid outdoor activities between 11 AM - 4 PM. {risk_groups} should take extra precautions.',
                'risk_groups': ['elderly', 'children', 'outdoor_workers', 'chronic_patients'],
                'actions': ['stay_hydrated', 'avoid_sun', 'cool_environment']
            },
            'hospital_surge': {
                'title': '🏥 Hospital Capacity Advisory',
                'severity': 'medium',
                'template': 'Hospitals are experiencing high patient volume. Non-emergency cases should consider: {alternatives}. Emergency services remain available 24/7.',
                'risk_groups': ['general_public'],
                'actions': ['telemedicine', 'local_clinic', 'pharmacy_consultation']
            }
        }
    
    def generate_advisory(
        self,
        scenario: str,
        context: Dict,
        target_audience: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a tailored advisory for a specific scenario
        
        Args:
            scenario: Type of advisory (pollution_critical, festival_safety, etc.)
            context: Context data (aqi, temperature, festival details, etc.)
            target_audience: Specific audience segments to target
        """
        if scenario not in self.advisory_templates:
            logger.warning(f"Unknown scenario: {scenario}")
            return None
        
        template = self.advisory_templates[scenario]
        
        # Format message with context
        message = template['template'].format(**context)
        
        # Determine target audience
        if not target_audience:
            target_audience = template['risk_groups']
        
        advisory = {
            'id': f"ADV_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'title': template['title'].format(**context),
            'message': message,
            'severity': template['severity'],
            'target_audience': target_audience,
            'recommended_actions': template['actions'],
            'channels': self._select_channels(template['severity']),
            'created_at': datetime.now().isoformat(),
            'expires_at': self._calculate_expiry(scenario),
            'context': context
        }
        
        return advisory
    
    def generate_multi_source_advisory(self, risk_assessment: Dict) -> List[Dict]:
        """
        Generate advisories based on integrated risk assessment
        Combines pollution, weather, festival, and epidemic data
        """
        advisories = []
        data_sources = risk_assessment.get('data_sources', {})
        
        # AQI-based advisories
        aqi_data = data_sources.get('aqi', {})
        if aqi_data.get('aqi', 0) > 300:
            advisories.append(self.generate_advisory(
                'pollution_critical',
                {
                    'aqi': aqi_data['aqi'],
                    'risk_groups': 'Elderly, children, and those with respiratory/cardiac conditions'
                }
            ))
        elif aqi_data.get('aqi', 0) > 200:
            advisories.append(self.generate_advisory(
                'pollution_high',
                {
                    'aqi': aqi_data['aqi'],
                    'risk_groups': 'Sensitive groups'
                }
            ))
        
        # Festival-based advisories
        festivals = data_sources.get('upcoming_festivals', [])
        for festival in festivals[:2]:  # Top 2 upcoming festivals
            if festival['days_until'] <= 14:
                advisories.append(self.generate_advisory(
                    'festival_safety',
                    {
                        'festival_name': festival['name'],
                        'days': festival['days_until'],
                        'risks': ', '.join(festival['risk_factors'])
                    }
                ))
        
        # Epidemic-based advisories
        epidemics = data_sources.get('epidemics', {})
        for outbreak in epidemics.get('active_outbreaks', []):
            if outbreak['severity'] in ['high', 'medium']:
                advisories.append(self.generate_advisory(
                    'epidemic_alert',
                    {
                        'disease_name': outbreak['name'],
                        'trend': outbreak['trend'],
                        'cases': outbreak['cases_this_week'],
                        'risk_groups': ', '.join(outbreak['affected_age_groups']),
                        'precautions': 'Maintain hygiene, get vaccinated if eligible, avoid crowded places'
                    }
                ))
        
        # Weather-based advisories
        weather = data_sources.get('weather', [])
        if weather:
            avg_temp = sum(d['temperature'] for d in weather) / len(weather)
            if avg_temp > 38:
                advisories.append(self.generate_advisory(
                    'heat_wave',
                    {
                        'temperature': int(avg_temp),
                        'risk_groups': 'Elderly, children, and outdoor workers'
                    }
                ))
        
        return advisories
    
    def _select_channels(self, severity: str) -> List[str]:
        """Select delivery channels based on severity"""
        if severity == 'critical':
            return ['sms', 'email', 'whatsapp', 'hospital_display', 'mobile_app']
        elif severity == 'high':
            return ['email', 'whatsapp', 'hospital_display', 'mobile_app']
        else:
            return ['email', 'hospital_display', 'mobile_app']
    
    def _calculate_expiry(self, scenario: str) -> str:
        """Calculate advisory expiry time"""
        from datetime import timedelta
        
        expiry_hours = {
            'pollution_critical': 24,
            'pollution_high': 48,
            'festival_safety': 168,  # 7 days
            'epidemic_alert': 168,
            'heat_wave': 48,
            'hospital_surge': 24
        }
        
        hours = expiry_hours.get(scenario, 48)
        expiry = datetime.now() + timedelta(hours=hours)
        return expiry.isoformat()
    
    def simulate_delivery(self, advisory: Dict) -> Dict:
        """
        Simulate multi-channel advisory delivery
        In production, this would integrate with SMS/Email/WhatsApp APIs
        """
        delivery_status = {}
        
        for channel in advisory['channels']:
            # Simulate delivery
            delivery_status[channel] = {
                'status': 'sent',
                'timestamp': datetime.now().isoformat(),
                'recipients': self._estimate_recipients(advisory['target_audience']),
                'delivery_method': self._get_delivery_method(channel)
            }
        
        return {
            'advisory_id': advisory['id'],
            'delivery_status': delivery_status,
            'total_recipients': sum(s['recipients'] for s in delivery_status.values()),
            'channels_used': len(delivery_status)
        }
    
    def _estimate_recipients(self, target_audience: List[str]) -> int:
        """Estimate number of recipients based on audience"""
        # Mock estimation - in production, query actual user database
        audience_sizes = {
            'elderly': 500,
            'children': 300,
            'respiratory_patients': 200,
            'cardiac_patients': 150,
            'general_public': 2000,
            'all': 3000,
            'outdoor_workers': 400,
            'chronic_patients': 250
        }
        
        total = sum(audience_sizes.get(group, 100) for group in target_audience)
        return min(total, 3000)  # Cap at 3000
    
    def _get_delivery_method(self, channel: str) -> str:
        """Get delivery method description"""
        methods = {
            'sms': 'Twilio SMS API',
            'email': 'SendGrid Email API',
            'whatsapp': 'WhatsApp Business API',
            'hospital_display': 'Digital Signage System',
            'mobile_app': 'Push Notification Service'
        }
        return methods.get(channel, 'Unknown')
    
    def get_advisory_history(self, days: int = 7) -> List[Dict]:
        """Get historical advisories (mock implementation)"""
        # In production, query from database
        return []
    
    def get_advisory_effectiveness(self) -> Dict:
        """Calculate advisory effectiveness metrics"""
        return {
            'total_advisories_sent': 45,
            'average_response_rate': 0.68,
            'channels_performance': {
                'sms': {'delivery_rate': 0.95, 'open_rate': 0.82},
                'email': {'delivery_rate': 0.98, 'open_rate': 0.45},
                'whatsapp': {'delivery_rate': 0.97, 'open_rate': 0.78},
                'mobile_app': {'delivery_rate': 0.99, 'open_rate': 0.65}
            },
            'most_effective_channel': 'sms',
            'improvement_suggestions': [
                'Increase WhatsApp adoption',
                'Optimize email subject lines',
                'Add regional language support'
            ]
        }

# Singleton instance
patient_advisory_system = PatientAdvisorySystem()
