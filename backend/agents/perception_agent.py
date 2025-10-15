import requests
import json
from datetime import datetime
import time

class PerceptionAgent:
    """
    Perception Agent: Collects and normalizes live data from multiple sources
    - Hospital Information System (HIS)
    - Air Quality Index APIs
    - Festival/Event Calendars
    """

    def __init__(self):
        self.data_sources = {
            'his': 'http://mock-his-api.com/status',
            'aqi': 'http://api.openweathermap.org/data/2.5/air_pollution',
            'festivals': 'http://mock-festival-api.com/events'
        }
        self.collection_interval = 300  # 5 minutes

    def collect_his_data(self):
        """Collect hospital information system data"""
        try:
            # Mock HIS data collection
            response = {
                'timestamp': datetime.now().isoformat(),
                'bed_occupancy': 85,
                'patient_count': 245,
                'icu_occupancy': 92,
                'er_waiting': 12,
                'staff_on_duty': 45
            }
            return response
        except Exception as e:
            return {'error': str(e)}

    def collect_aqi_data(self, city='Delhi'):
        """Collect air quality index data"""
        try:
            # Mock AQI API call
            mock_aqi = {
                'timestamp': datetime.now().isoformat(),
                'city': city,
                'aqi': 142,
                'pm25': 85,
                'pm10': 120,
                'no2': 45,
                'so2': 12,
                'co': 0.8
            }
            return mock_aqi
        except Exception as e:
            return {'error': str(e)}

    def collect_festival_data(self):
        """Collect festival and event calendar data"""
        try:
            # Mock festival data
            festivals = [
                {
                    'name': 'Diwali',
                    'date': '2024-11-12',
                    'days_until': 15,
                    'expected_crowd': 'high',
                    'regions': ['Delhi', 'Mumbai', 'Bangalore']
                },
                {
                    'name': 'Holi',
                    'date': '2024-03-25',
                    'days_until': 120,
                    'expected_crowd': 'medium',
                    'regions': ['North India']
                }
            ]
            return festivals
        except Exception as e:
            return {'error': str(e)}

    def normalize_data(self, raw_data):
        """Normalize data from different sources into standard format"""
        normalized = {
            'timestamp': datetime.now().isoformat(),
            'source': raw_data.get('source', 'unknown'),
            'data': raw_data
        }
        return normalized

    def store_data(self, data):
        """Store collected data in database"""
        # Mock storage - in real implementation, use MongoDB/PostgreSQL
        with open('data/perception_data.json', 'a') as f:
            json.dump(data, f)
            f.write('\n')
        return True

    def run_collection_cycle(self):
        """Run one complete data collection cycle"""
        collected_data = []

        # Collect from all sources
        his_data = self.collect_his_data()
        his_data['source'] = 'his'
        collected_data.append(self.normalize_data(his_data))

        aqi_data = self.collect_aqi_data()
        aqi_data['source'] = 'aqi'
        collected_data.append(self.normalize_data(aqi_data))

        festival_data = self.collect_festival_data()
        festival_data = {'events': festival_data, 'source': 'festivals'}
        collected_data.append(self.normalize_data(festival_data))

        # Store all collected data
        for data in collected_data:
            self.store_data(data)

        return collected_data

    def get_latest_data(self, source=None):
        """Retrieve latest collected data"""
        try:
            with open('data/perception_data.json', 'r') as f:
                lines = f.readlines()
                if lines:
                    latest = json.loads(lines[-1])
                    if source and latest.get('source') != source:
                        return None
                    return latest
        except FileNotFoundError:
            return None
        return None
