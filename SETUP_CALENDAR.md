# Google Calendar Integration Setup

To enable the live festival tracking feature, follow these steps:

## 1. Create Google Cloud Project
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project named `HospAgent-SurgeOps`.
3.  Enable the **Google Calendar API**.

## 2. Configure Credentials
1.  Go to **APIs & Services > Credentials**.
2.  Click **Create Credentials > OAuth client ID**.
3.  Select **Desktop app**.
4.  Download the JSON file and rename it to `credentials.json`.
5.  Place `credentials.json` in the `backend/` directory.

## 3. Generate Token
Run the following script once to generate the `token.json` file (requires browser login):

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        'backend/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open('backend/token.json', 'w') as token:
        token.write(creds.to_json())
    print("Token generated successfully!")

if __name__ == '__main__':
    main()
```

## 4. Verify
Restart the backend. The `CalendarAgent` will now fetch live Indian holidays from Google Calendar.
