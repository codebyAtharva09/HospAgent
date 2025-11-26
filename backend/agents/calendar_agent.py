import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class CalendarAgent:
    """
    Calendar Agent
    Fetches upcoming festivals and holidays from Google Calendar.
    Identifies high-risk days based on keywords (Diwali, Holi, etc.).
    """

    def __init__(self):
        self.creds = None
        self.service = None
        self.high_risk_keywords = [
            "Diwali", "Deepavali", "Holi", "Ganesh", "Navratri", "Eid", 
            "Dussehra", "Christmas", "New Year"
        ]
        # self._authenticate() # Commented out for now to avoid blocking on auth during dev without token

    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # In a real server, this flow needs to be handled differently (service account)
                # For hackathon local demo, this is fine if token.json exists
                pass

        if self.creds:
            self.service = build("calendar", "v3", credentials=self.creds)

    def get_upcoming_festivals(self, days=30):
        """
        Get upcoming festivals for the next N days.
        Returns a list of dicts: {date, name, is_high_risk}
        """
        # Mock data if no credentials (fallback for demo)
        if not self.service:
            return self._get_mock_festivals(days)

        try:
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            events_result = (
                self.service.events()
                .list(
                    calendarId="en.indian#holiday@group.v.calendar.google.com",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            
            festivals = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                name = event["summary"]
                
                is_high_risk = any(k.lower() in name.lower() for k in self.high_risk_keywords)
                
                festivals.append({
                    "date": start,
                    "name": name,
                    "is_high_risk": is_high_risk
                })
                
            return festivals

        except HttpError as error:
            print(f"An error occurred: {error}")
            return self._get_mock_festivals(days)

    def _get_mock_festivals(self, days):
        """Return mock festival data for demo purposes."""
        today = datetime.date.today()
        mock_events = [
            {"name": "Ganesh Chaturthi", "offset": 2, "risk": True},
            {"name": "Navratri Start", "offset": 15, "risk": True},
            {"name": "Gandhi Jayanti", "offset": 20, "risk": False},
            {"name": "Diwali", "offset": 28, "risk": True},
        ]
        
        festivals = []
        for event in mock_events:
            if event["offset"] <= days:
                evt_date = (today + datetime.timedelta(days=event["offset"])).isoformat()
                festivals.append({
                    "date": evt_date,
                    "name": event["name"],
                    "is_high_risk": event["risk"]
                })
        return festivals

if __name__ == "__main__":
    agent = CalendarAgent()
    print(agent.get_upcoming_festivals())
