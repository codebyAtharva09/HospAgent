"""
Festival Client - Google Calendar API Integration
Fetches live festival and holiday events from Google Calendar
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class FestivalClient:
    """
    Client for fetching festival events from Google Calendar.
    Supports both India Holidays calendar and custom hospital calendars.
    """
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.service = None
        
        # High-risk festival keywords
        self.HIGH_RISK_KEYWORDS = [
            'diwali', 'deepavali', 'holi', 'ganesh', 'chaturthi', 
            'ganapati', 'navratri', 'durga puja', 'eid', 'dussehra',
            'dasara', 'pongal', 'makar sankranti', 'christmas', 'new year'
        ]
        
        # Calendar IDs from environment
        self.india_calendar_id = os.getenv(
            'INDIA_HOLIDAY_CALENDAR_ID',
            'en.indian#holiday@group.v.calendar.google.com'
        )
        self.hospital_calendar_id = os.getenv('HOSPITAL_CALENDAR_ID', None)
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar API service with service account"""
        try:
            service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
            
            if not service_account_file:
                print("⚠️  GOOGLE_SERVICE_ACCOUNT_FILE not set in environment")
                print("   Using mock festival data")
                return
            
            if not os.path.exists(service_account_file):
                print(f"⚠️  Service account file not found: {service_account_file}")
                print("   Using mock festival data")
                return
            
            # Create credentials from service account
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=self.SCOPES
            )
            
            # Build Calendar API service
            self.service = build('calendar', 'v3', credentials=credentials)
            print("✓ Google Calendar API service initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize Google Calendar API: {e}")
            print("   Using mock festival data")
            self.service = None
    
    def fetch_festivals(self, days_ahead: int = 180) -> List[Dict[str, Any]]:
        """
        Fetch festival events from Google Calendar.
        
        Args:
            days_ahead: Number of days to look ahead (default 180)
        
        Returns:
            List of festival events with normalized format:
            [{
                "id": str,
                "summary": str,
                "date": "YYYY-MM-DD",
                "source": "india_holidays" | "hospital_calendar",
                "high_risk": bool
            }]
        """
        
        if not self.service:
            print("Using mock festival data (Google Calendar not configured)")
            return self._get_mock_festivals(days_ahead)
        
        try:
            all_festivals = []
            
            # Fetch from India Holidays calendar
            india_festivals = self._fetch_from_calendar(
                self.india_calendar_id,
                days_ahead,
                source='india_holidays'
            )
            all_festivals.extend(india_festivals)
            
            # Fetch from hospital calendar if configured
            if self.hospital_calendar_id:
                hospital_festivals = self._fetch_from_calendar(
                    self.hospital_calendar_id,
                    days_ahead,
                    source='hospital_calendar'
                )
                all_festivals.extend(hospital_festivals)
            
            # Remove duplicates and sort by date
            unique_festivals = self._deduplicate_festivals(all_festivals)
            unique_festivals.sort(key=lambda x: x['date'])
            
            print(f"✓ Fetched {len(unique_festivals)} festivals from Google Calendar")
            return unique_festivals
            
        except HttpError as e:
            print(f"⚠️  Google Calendar API error: {e}")
            print("   Falling back to mock festival data")
            return self._get_mock_festivals(days_ahead)
        except Exception as e:
            print(f"⚠️  Unexpected error fetching festivals: {e}")
            print("   Falling back to mock festival data")
            return self._get_mock_festivals(days_ahead)
    
    def _fetch_from_calendar(
        self, 
        calendar_id: str, 
        days_ahead: int,
        source: str
    ) -> List[Dict[str, Any]]:
        """Fetch events from a specific calendar"""
        
        # Calculate time range
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days_ahead)).isoformat()
        
        # Fetch events
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Normalize events
        festivals = []
        for event in events:
            try:
                # Get event date (handle all-day events)
                start = event['start']
                if 'date' in start:
                    # All-day event (YYYY-MM-DD format)
                    event_date = start['date']
                elif 'dateTime' in start:
                    # Timed event - extract date
                    dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                    event_date = dt.strftime('%Y-%m-%d')
                else:
                    continue
                
                summary = event.get('summary', 'Unnamed Event')
                
                # Determine if high-risk
                high_risk = self._is_high_risk_festival(summary)
                
                festivals.append({
                    'id': event['id'],
                    'summary': summary,
                    'date': event_date,
                    'source': source,
                    'high_risk': high_risk
                })
                
            except Exception as e:
                print(f"⚠️  Error processing event: {e}")
                continue
        
        return festivals
    
    def _is_high_risk_festival(self, summary: str) -> bool:
        """
        Determine if a festival is high-risk based on keywords.
        
        High-risk festivals typically cause:
        - Increased trauma/burn cases
        - Respiratory issues (pollution)
        - Crowd-related incidents
        """
        summary_lower = summary.lower()
        return any(keyword in summary_lower for keyword in self.HIGH_RISK_KEYWORDS)
    
    def _deduplicate_festivals(self, festivals: List[Dict]) -> List[Dict]:
        """Remove duplicate festivals (same date + summary)"""
        seen = set()
        unique = []
        
        for fest in festivals:
            key = (fest['date'], fest['summary'].lower())
            if key not in seen:
                seen.add(key)
                unique.append(fest)
        
        return unique
    
    def _get_mock_festivals(self, days_ahead: int) -> List[Dict[str, Any]]:
        """
        Generate mock festival data for demo/fallback.
        Based on typical 2025 Indian festival calendar.
        """
        
        today = datetime.now().date()
        
        # Predefined 2025 festival dates
        mock_events = [
            {'name': 'Makar Sankranti', 'date': '2025-01-14', 'risk': True},
            {'name': 'Republic Day', 'date': '2025-01-26', 'risk': False},
            {'name': 'Maha Shivaratri', 'date': '2025-02-26', 'risk': True},
            {'name': 'Holi', 'date': '2025-03-14', 'risk': True},
            {'name': 'Ram Navami', 'date': '2025-04-06', 'risk': True},
            {'name': 'Good Friday', 'date': '2025-04-18', 'risk': False},
            {'name': 'Eid ul-Fitr', 'date': '2025-04-01', 'risk': True},
            {'name': 'Independence Day', 'date': '2025-08-15', 'risk': False},
            {'name': 'Ganesh Chaturthi', 'date': '2025-08-27', 'risk': True},
            {'name': 'Navratri Start', 'date': '2025-09-22', 'risk': True},
            {'name': 'Gandhi Jayanti', 'date': '2025-10-02', 'risk': False},
            {'name': 'Dussehra', 'date': '2025-10-02', 'risk': True},
            {'name': 'Diwali', 'date': '2025-10-20', 'risk': True},
            {'name': 'Guru Nanak Jayanti', 'date': '2025-11-05', 'risk': True},
            {'name': 'Christmas', 'date': '2025-12-25', 'risk': True},
        ]
        
        festivals = []
        for event in mock_events:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
            days_until = (event_date - today).days
            
            # Only include events within the time window
            if 0 <= days_until <= days_ahead:
                festivals.append({
                    'id': f"mock_{event['name'].lower().replace(' ', '_')}",
                    'summary': event['name'],
                    'date': event['date'],
                    'source': 'mock_data',
                    'high_risk': event['risk']
                })
        
        return festivals
    
    def get_next_high_risk_festival(self, festivals: List[Dict]) -> Optional[Dict]:
        """Get the next upcoming high-risk festival"""
        today = datetime.now().date()
        
        for fest in festivals:
            fest_date = datetime.strptime(fest['date'], '%Y-%m-%d').date()
            if fest_date >= today and fest.get('high_risk', False):
                return fest
        
        return None
    
    def calculate_festival_features(self, festivals: List[Dict]) -> Dict[str, Any]:
        """
        Calculate festival-related features for risk/forecast models.
        
        Returns:
            {
                'is_festival_today': bool,
                'days_to_next_festival': int,
                'is_high_risk_festival_window': bool,
                'next_festival_name': str | None,
                'festivals_next_7_days': int,
                'high_risk_festivals_next_7_days': int
            }
        """
        
        today = datetime.now().date()
        
        # Initialize features
        features = {
            'is_festival_today': False,
            'days_to_next_festival': 999,
            'is_high_risk_festival_window': False,
            'next_festival_name': None,
            'festivals_next_7_days': 0,
            'high_risk_festivals_next_7_days': 0
        }
        
        # Process festivals
        for fest in festivals:
            fest_date = datetime.strptime(fest['date'], '%Y-%m-%d').date()
            days_until = (fest_date - today).days
            
            # Check if festival is today
            if days_until == 0:
                features['is_festival_today'] = True
                if fest.get('high_risk', False):
                    features['is_high_risk_festival_window'] = True
            
            # Count festivals in next 7 days
            if 0 <= days_until <= 7:
                features['festivals_next_7_days'] += 1
                if fest.get('high_risk', False):
                    features['high_risk_festivals_next_7_days'] += 1
                    features['is_high_risk_festival_window'] = True
            
            # Track next festival
            if days_until >= 0 and days_until < features['days_to_next_festival']:
                features['days_to_next_festival'] = days_until
                features['next_festival_name'] = fest['summary']
        
        return features
