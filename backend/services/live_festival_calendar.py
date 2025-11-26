"""
Live Festival Calendar Client - Google Calendar API Integration
Fetches festival and holiday events from Google Calendar using service account
"""

from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import calendar

class LiveFestivalCalendar:
    """
    Client for fetching festival events from Google Calendar.
    Uses service account authentication with gen.json.
    """
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.service = None
        
        # High-risk festival keywords
        self.HIGH_RISK_KEYWORDS = [
            'diwali', 'deepavali', 'holi', 'ganesh', 'chaturthi', 
            'ganapati', 'navratri', 'durga puja', 'eid', 'dussehra',
            'dasara'
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
            service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', './gen.json')
            
            if not os.path.exists(service_account_file):
                print(f"⚠️  Service account file not found: {service_account_file}")
                print("   Calendar will use mock data")
                return
            
            # Create credentials from service account
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=self.SCOPES
            )
            
            # Build Calendar API service
            self.service = build('calendar', 'v3', credentials=credentials)
            print("✓ Google Calendar API service initialized")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize Google Calendar API: {e}")
            print("   Calendar will use mock data")
            self.service = None
    
    def fetch_festivals_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Fetch all festival events between start_date and end_date.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        
        Returns:
            List of normalized festival events:
            [{
                "id": str,
                "summary": str,
                "date": "YYYY-MM-DD",
                "source": "india_holidays" | "hospital_calendar",
                "high_risk": bool
            }]
        """
        
        if not self.service:
            return self._get_mock_festivals_range(start_date, end_date)
        
        try:
            all_festivals = []
            
            # Fetch from India Holidays calendar
            india_festivals = self._fetch_from_calendar(
                self.india_calendar_id,
                start_date,
                end_date,
                source='india_holidays'
            )
            all_festivals.extend(india_festivals)
            
            # Fetch from hospital calendar if configured
            if self.hospital_calendar_id:
                hospital_festivals = self._fetch_from_calendar(
                    self.hospital_calendar_id,
                    start_date,
                    end_date,
                    source='hospital_calendar'
                )
                all_festivals.extend(hospital_festivals)
            
            # Remove duplicates and sort by date
            unique_festivals = self._deduplicate_festivals(all_festivals)
            unique_festivals.sort(key=lambda x: x['date'])
            
            return unique_festivals
            
        except HttpError as e:
            print(f"⚠️  Google Calendar API error: {e}")
            return self._get_mock_festivals_range(start_date, end_date)
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
            return self._get_mock_festivals_range(start_date, end_date)
    
    def fetch_upcoming_festivals(self, days_ahead: int = 180) -> List[Dict[str, Any]]:
        """
        Convenience wrapper to fetch upcoming festivals.
        
        Args:
            days_ahead: Number of days to look ahead (default 180)
        
        Returns:
            List of upcoming festival events
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        return self.fetch_festivals_range(today, end_date)
    
    def fetch_month_festivals(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        Fetch all festivals for a specific month.
        
        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
        
        Returns:
            List of festival events for that month
        """
        # Get first and last day of month
        first_day = date(year, month, 1)
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = date(year, month, last_day_num)
        
        return self.fetch_festivals_range(first_day, last_day)
    
    def _fetch_from_calendar(
        self,
        calendar_id: str,
        start_date: date,
        end_date: date,
        source: str
    ) -> List[Dict[str, Any]]:
        """Fetch events from a specific calendar"""
        
        # Convert dates to RFC3339 format
        time_min = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc).isoformat()
        time_max = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc).isoformat()
        
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
                    # All-day event (YYYY-MM-DD format) - IMPORTANT for holidays
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
        """Determine if a festival is high-risk based on keywords"""
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
    
    def _get_mock_festivals_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Generate mock festival data for demo/fallback"""
        
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
            
            # Only include events within the date range
            if start_date <= event_date <= end_date:
                festivals.append({
                    'id': f"mock_{event['name'].lower().replace(' ', '_')}",
                    'summary': event['name'],
                    'date': event['date'],
                    'source': 'mock_data',
                    'high_risk': event['risk']
                })
        
        return festivals
