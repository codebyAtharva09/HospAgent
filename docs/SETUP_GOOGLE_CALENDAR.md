# Google Calendar Integration Setup Guide

## Overview

HospAgent SurgeOps integrates with Google Calendar to automatically track Indian festivals and high-risk events that may cause hospital surges.

**Note:** This integration is **optional**. The system will use mock festival data if Google Calendar is not configured.

---

## Prerequisites

- Google Account
- Google Cloud Console access
- Basic command-line knowledge

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Click **"Select a project"** → **"New Project"**

3. Enter project details:
   - **Project name:** `HospAgent-SurgeOps`
   - **Organization:** (leave default)
   - Click **"Create"**

4. Wait for project creation (takes ~30 seconds)

---

## Step 2: Enable Google Calendar API

1. In Google Cloud Console, ensure your project is selected

2. Navigate to **"APIs & Services"** → **"Library"**

3. Search for **"Google Calendar API"**

4. Click on **"Google Calendar API"**

5. Click **"Enable"**

6. Wait for API to be enabled

---

## Step 3: Create Service Account

1. Navigate to **"APIs & Services"** → **"Credentials"**

2. Click **"Create Credentials"** → **"Service Account"**

3. Fill in service account details:
   - **Service account name:** `hospagent-calendar-reader`
   - **Service account ID:** (auto-generated)
   - **Description:** `Service account for reading festival calendar`

4. Click **"Create and Continue"**

5. Grant role (optional):
   - **Role:** `Project > Viewer`
   - Click **"Continue"**

6. Click **"Done"**

---

## Step 4: Create Service Account Key

1. In **"Credentials"** page, find your service account under **"Service Accounts"**

2. Click on the service account email

3. Navigate to **"Keys"** tab

4. Click **"Add Key"** → **"Create new key"**

5. Select **"JSON"** format

6. Click **"Create"**

7. A JSON file will download automatically
   - **Filename:** `hospagent-surgeops-xxxxx.json`

8. **IMPORTANT:** Keep this file secure! It contains credentials.

---

## Step 5: Configure Backend

1. **Rename the downloaded JSON file:**
   ```bash
   mv hospagent-surgeops-xxxxx.json credentials.json
   ```

2. **Move to backend directory:**
   ```bash
   mv credentials.json backend/credentials.json
   ```

3. **Update .env file:**
   ```env
   GOOGLE_CALENDAR_CREDENTIALS=credentials.json
   ```

4. **Verify file location:**
   ```
   backend/
   ├── credentials.json  ← Should be here
   ├── .env
   └── main.py
   ```

---

## Step 6: Share Calendar (Optional)

If you want to use a custom calendar instead of the public Indian Holidays calendar:

1. Create a new calendar in Google Calendar

2. Add festival events with dates

3. Share calendar with service account:
   - Go to Calendar Settings
   - Find **"Share with specific people"**
   - Add service account email (from credentials.json)
   - Grant **"See all event details"** permission

4. Update `backend/services/festival_sync.py`:
   ```python
   # Replace this line:
   calendar_id = 'en.indian#holiday@group.v.calendar.google.com'
   
   # With your calendar ID:
   calendar_id = 'your-calendar-id@group.calendar.google.com'
   ```

---

## Step 7: Test Integration

1. **Start backend server:**
   ```bash
   cd backend
   python main.py
   ```

2. **Test festival endpoint:**
   ```bash
   curl http://localhost:8000/festivals/upcoming
   ```

3. **Expected response:**
   ```json
   [
     {
       "id": "...",
       "name": "Diwali",
       "date": "2025-11-12",
       "high_risk": true,
       "impact_score": 10,
       "days_until": 15,
       "surge_multiplier": 1.8,
       "source": "google_calendar"
     }
   ]
   ```

4. **Check logs for confirmation:**
   ```
   ✓ Google Calendar service initialized
   ```

---

## Troubleshooting

### Error: "Credentials not found"

**Solution:**
- Verify `credentials.json` is in `backend/` directory
- Check `.env` file has correct path
- Ensure file is valid JSON

### Error: "Permission denied"

**Solution:**
- Verify service account has Calendar API enabled
- Check calendar sharing permissions
- Ensure service account email is added to calendar

### Error: "API not enabled"

**Solution:**
- Go to Google Cloud Console
- Navigate to "APIs & Services" → "Library"
- Search "Google Calendar API"
- Click "Enable"

### Using Mock Data

If you see this message:
```
⚠ Google Calendar credentials not found
  Using mock festival data
```

This is **normal** and the system will work with predefined festival dates. No action needed unless you want live calendar sync.

---

## Security Best Practices

1. **Never commit credentials.json to Git**
   - Add to `.gitignore`:
     ```
     credentials.json
     *.json
     ```

2. **Restrict service account permissions**
   - Only grant "Viewer" role
   - Only enable Calendar API

3. **Rotate keys periodically**
   - Delete old keys in Google Cloud Console
   - Generate new keys every 90 days

4. **Use environment variables**
   - Store path in `.env`, not hardcoded
   - Use different credentials for dev/prod

---

## Alternative: Using OAuth 2.0 (Not Recommended for Server)

If you prefer OAuth instead of Service Account:

1. Create OAuth 2.0 Client ID
2. Download `client_secret.json`
3. Run authentication flow (requires browser)
4. Save `token.json`

**Note:** Service Account is recommended for server applications.

---

## Calendar Event Format

For custom calendars, use this format:

**Event Title:** `Diwali` (or any festival name)

**Date:** Single day or multi-day event

**Description (optional):**
```
High-risk festival
Expected surge: 80%
Categories: Trauma, Burns, Respiratory
```

The system will automatically flag events containing keywords:
- diwali, holi, ganesh, navratri, eid, christmas, etc.

---

## API Rate Limits

**Google Calendar API (Free Tier):**
- 1,000,000 queries per day
- 10 queries per second per user

**HospAgent Usage:**
- ~1 query per day (daily sync)
- Well within free tier limits

---

## Support

For issues with Google Calendar integration:

1. Check backend logs for error messages
2. Verify credentials.json is valid JSON
3. Test with mock data first
4. Consult [Google Calendar API Docs](https://developers.google.com/calendar)

---

## Summary

✅ **Required Steps:**
1. Create Google Cloud Project
2. Enable Calendar API
3. Create Service Account
4. Download credentials JSON
5. Place in `backend/credentials.json`
6. Update `.env`

✅ **Optional:**
- Custom calendar
- Calendar sharing
- Event customization

✅ **Fallback:**
- System works with mock data if not configured
- No functionality loss

---

**Setup Time:** ~10 minutes  
**Cost:** Free (within API limits)  
**Difficulty:** Beginner-friendly
