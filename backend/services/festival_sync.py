"""
Festival Sync Service - Google Calendar Integration
Fetches and normalizes Indian festival data for risk assessment
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class FestivalSyncService:
    """
    Syncs festival data from Google Calendar.
    Identifies high-risk events for hospital surge prediction.
    """
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.service = None
        
        # High-risk festival keywords
        self.HIGH_RISK_KEYWORDS = [
            'diwali', 'deepavali', 'holi', 'ganesh', 'ganapati',
            'navratri', 'durga puja', 'eid', 'dussehra', 'dasara',
            'christmas', 'new year', 'pongal', 'makar sankranti',
            'pollution', 'smog', 'air quality'
        ]
        
        # Try to initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar API service"""
        try:
            creds_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS', 'credentials.json')
            
            if os.path.exists(creds_path):
                credentials = service_account.Credentials.from_service_account_file(
                    creds_path, scopes=self.SCOPES
                )
                self.service = build('calendar', 'v3', credentials=credentials)
                print("✓ Google Calendar service initialized")
            else:
                print(f"⚠ Google Calendar credentials not found at {creds_path}")
                print("  Using mock festival data")
        except Exception as e:
            print(f"⚠ Failed to initialize Google Calendar: {e}")
            print("  Using mock festival data")
    
    async def fetch_upcoming_festivals(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch upcoming festivals from Google Calendar.
        Falls back to mock data if API unavailable.
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            List of festival events with risk flags
        """
        
        if self.service:
            try:
                return await self._fetch_from_google(days_ahead)
            except Exception as e:
                print(f"Error fetching from Google Calendar: {e}")
                return self._get_mock_festivals(days_ahead)
        else:
            return self._get_mock_festivals(days_ahead)
    
    async def _fetch_from_google(self, days_ahead: int) -> List[Dict[str, Any]]:
        """Fetch from Google Calendar API"""
        
        # Use Indian Holiday calendar
        calendar_id = 'en.indian#holiday@group.v.calendar.google.com'
        
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        festivals = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '')
            
            # Determine if high-risk
            is_high_risk = any(
                keyword in summary.lower() 
                for keyword in self.HIGH_RISK_KEYWORDS
            )
            
            festivals.append({
                'id': event['id'],
                'name': summary,
                'date': start,
                'high_risk': is_high_risk,
                'source': 'google_calendar',
                'impact_score': self._calculate_impact_score(summary, start)
            })
        
        return festivals
    
    def _get_mock_festivals(self, days_ahead: int) -> List[Dict[str, Any]]:
        """Generate mock festival data for demo/fallback"""
        
        today = datetime.now()
        
        # Predefined festival schedule (2025)
        mock_events = [
            {'name': 'Makar Sankranti', 'offset': 2, 'risk': True, 'impact': 7},
            {'name': 'Republic Day', 'offset': 5, 'risk': False, 'impact': 3},
            {'name': 'Maha Shivaratri', 'offset': 12, 'risk': True, 'impact': 6},
            {'name': 'Holi', 'offset': 18, 'risk': True, 'impact': 9},
            {'name': 'Ram Navami', 'offset': 25, 'risk': True, 'impact': 5},
            {'name': 'Ganesh Chaturthi', 'offset': 35, 'risk': True, 'impact': 8},
            {'name': 'Navratri Start', 'offset': 45, 'risk': True, 'impact': 7},
            {'name': 'Dussehra', 'offset': 54, 'risk': True, 'impact': 8},
            {'name': 'Diwali', 'offset': 65, 'risk': True, 'impact': 10},
            {'name': 'Guru Nanak Jayanti', 'offset': 75, 'risk': True, 'impact': 6},
            {'name': 'Christmas', 'offset': 85, 'risk': True, 'impact': 7},
        ]
        
        festivals = []
        for event in mock_events:
            event_date = today + timedelta(days=event['offset'])
            
            if event['offset'] <= days_ahead:
                festivals.append({
                    'id': f"mock_{event['name'].lower().replace(' ', '_')}",
                    'name': event['name'],
                    'date': event_date.isoformat(),
                    'high_risk': event['risk'],
                    'source': 'mock_data',
                    'impact_score': event['impact']
                })
        
        return festivals
    
    def _calculate_impact_score(self, name: str, date_str: str) -> int:
        """
        Calculate festival impact score (1-10).
        Higher score = higher expected hospital surge.
        """
        
        score = 5  # Base score
        
        name_lower = name.lower()
        
        # Major festivals
        if 'diwali' in name_lower or 'deepavali' in name_lower:
            score = 10  # Highest - burns, respiratory, trauma
        elif 'holi' in name_lower:
            score = 9   # High - injuries, accidents
        elif 'ganesh' in name_lower or 'ganapati' in name_lower:
            score = 8   # High - crowd-related incidents
        elif 'navratri' in name_lower or 'durga' in name_lower:
            score = 7   # Moderate-high
        elif 'eid' in name_lower or 'christmas' in name_lower:
            score = 7
        elif 'dussehra' in name_lower or 'dasara' in name_lower:
            score = 8
        
        # Pollution/environmental events
        if 'pollution' in name_lower or 'smog' in name_lower:
            score = 9
        
        return score
    
    def normalize_festivals(self, raw_festivals: List[Dict]) -> List[Dict[str, Any]]:
        """
        Normalize festival data to standard format.
        
        Returns:
            [{
                'id': str,
                'name': str,
                'date': ISO8601,
                'high_risk': bool,
                'impact_score': int (1-10),
                'days_until': int,
                'surge_multiplier': float
            }]
        """
        
        normalized = []
        today = datetime.now()
        
        for fest in raw_festivals:
            try:
                # Parse date
                fest_date = datetime.fromisoformat(fest['date'].replace('Z', '+00:00'))
                days_until = (fest_date.date() - today.date()).days
                
                # Calculate surge multiplier based on proximity and impact
                surge_multiplier = self._calculate_surge_multiplier(
                    days_until, fest['impact_score']
                )
                
                normalized.append({
                    'id': fest['id'],
                    'name': fest['name'],
                    'date': fest['date'],
                    'high_risk': fest['high_risk'],
                    'impact_score': fest['impact_score'],
                    'days_until': days_until,
                    'surge_multiplier': surge_multiplier,
                    'source': fest.get('source', 'unknown')
                })
            except Exception as e:
                print(f"Error normalizing festival {fest.get('name')}: {e}")
                continue
        
        # Sort by date
        normalized.sort(key=lambda x: x['days_until'])
        
        return normalized
    
    def _calculate_surge_multiplier(self, days_until: int, impact: int) -> float:
        """
        Calculate expected patient surge multiplier.
        
        Args:
            days_until: Days until festival
            impact: Impact score (1-10)
        
        Returns:
            Multiplier (1.0 = normal, 2.0 = double load)
        """
        
        if days_until < 0:
            return 1.0  # Past event
        
        # Base multiplier from impact score
        base_multiplier = 1.0 + (impact / 20.0)  # Max 1.5x for impact 10
        
        # Proximity factor
        if days_until == 0:
            proximity_factor = 1.5  # Festival day
        elif days_until == 1:
            proximity_factor = 1.3  # Day before/after
        elif days_until <= 3:
            proximity_factor = 1.15  # Within 3 days
        elif days_until <= 7:
            proximity_factor = 1.05  # Within a week
        else:
            proximity_factor = 1.0
        
        return min(2.0, base_multiplier * proximity_factor)
