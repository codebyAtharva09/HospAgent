# Google Calendar Integration - Complete Setup Guide

## 📋 Overview

This guide will help you set up **live Google Calendar integration** for HospAgent SurgeOps to automatically fetch Indian festivals and holidays.

**Time Required:** 15 minutes  
**Cost:** Free  
**Difficulty:** Beginner-friendly

---

## 🎯 What You'll Achieve

After completing this setup:
- ✅ Automatic festival tracking from Google Calendar
- ✅ High-risk festival flagging (Diwali, Holi, etc.)
- ✅ Real-time risk assessment with festival factors
- ✅ Patient surge predictions around festivals

---

## 📝 Prerequisites

- Google Account
- Access to Google Cloud Console
- HospAgent backend running locally

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a project" dropdown (top bar)
   - Click "NEW PROJECT"
   - Enter project name: `HospAgent-Calendar`
   - Click "CREATE"
   - Wait ~30 seconds for project creation

3. **Select Your Project**
   - Click "Select a project" again
   - Choose `HospAgent-Calendar`

---

### Step 2: Enable Google Calendar API

1. **Navigate to APIs & Services**
   - In left sidebar: "APIs & Services" → "Library"

2. **Search for Calendar API**
   - Search box: Type "Google Calendar API"
   - Click on "Google Calendar API"

3. **Enable the API**
   - Click blue "ENABLE" button
   - Wait for confirmation

---

### Step 3: Create Service Account

1. **Go to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"

2. **Create Service Account**
   - Click "CREATE CREDENTIALS" → "Service account"

3. **Fill Service Account Details**
   ```
   Service account name: hospagent-calendar-reader
   Service account ID: (auto-generated)
   Description: Service account for reading festival calendar
   ```
   - Click "CREATE AND CONTINUE"

4. **Grant Permissions (Optional)**
   - Role: `Project > Viewer`
   - Click "CONTINUE"
   - Click "DONE"

---

### Step 4: Create Service Account Key

1. **Find Your Service Account**
   - In "Credentials" page, scroll to "Service Accounts"
   - Click on `hospagent-calendar-reader@...`

2. **Create JSON Key**
   - Go to "KEYS" tab
   - Click "ADD KEY" → "Create new key"
   - Select "JSON" format
   - Click "CREATE"

3. **Download Key File**
   - A JSON file will download automatically
   - **Filename:** `hospagent-calendar-xxxxx.json`
   - **IMPORTANT:** Keep this file secure!

---

### Step 5: Configure Backend

1. **Rename Downloaded File**
   ```bash
   # Rename to service-account.json
   mv hospagent-calendar-xxxxx.json service-account.json
   ```

2. **Move to Backend Directory**
   ```bash
   # Move to backend folder
   mv service-account.json backend/service-account.json
   ```

3. **Update .env File**
   
   Edit `backend/.env` and add:
   ```env
   # Google Calendar Configuration
   GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
   INDIA_HOLIDAY_CALENDAR_ID=en.indian#holiday@group.v.calendar.google.com
   # HOSPITAL_CALENDAR_ID=your-custom-calendar@group.calendar.google.com  # Optional
   ```

4. **Verify File Structure**
   ```
   backend/
   ├── service-account.json  ← Should be here
   ├── .env                  ← Updated with path
   ├── main.py
   └── services/
       └── festival_client.py
   ```

---

### Step 6: Test Integration

1. **Start Backend Server**
   ```bash
   cd backend
   python main.py
   ```

2. **Check Logs**
   Look for this message:
   ```
   ✓ Google Calendar API service initialized successfully
   ```

3. **Test Festival Endpoint**
   ```bash
   curl http://localhost:8000/festivals/upcoming
   ```

4. **Expected Response**
   ```json
   [
     {
       "id": "...",
       "summary": "Ganesh Chaturthi",
       "date": "2025-08-27",
       "source": "india_holidays",
       "high_risk": true
     },
     {
       "id": "...",
       "summary": "Diwali",
       "date": "2025-10-20",
       "source": "india_holidays",
       "high_risk": true
     }
   ]
   ```

---

## 🔧 Optional: Custom Hospital Calendar

If you want to add custom hospital events:

### Create Custom Calendar

1. **Go to Google Calendar**
   - Visit: https://calendar.google.com

2. **Create New Calendar**
   - Left sidebar: Click "+" next to "Other calendars"
   - Select "Create new calendar"
   - Name: `Hospital Events`
   - Click "Create calendar"

3. **Get Calendar ID**
   - Settings → Select your calendar
   - Scroll to "Integrate calendar"
   - Copy "Calendar ID" (looks like: `abc123@group.calendar.google.com`)

### Share with Service Account

1. **Add Service Account**
   - In calendar settings: "Share with specific people"
   - Click "Add people"
   - Paste service account email from `service-account.json`:
     ```
     hospagent-calendar-reader@hospagent-calendar.iam.gserviceaccount.com
     ```

2. **Grant Permissions**
   - Permission: "See all event details"
   - Click "Send"

3. **Update .env**
   ```env
   HOSPITAL_CALENDAR_ID=abc123@group.calendar.google.com
   ```

---

## 📊 API Endpoints

### GET /festivals/upcoming

Fetch upcoming festivals:
```bash
curl "http://localhost:8000/festivals/upcoming?days_ahead=30"
```

### POST /festivals/sync

Manually sync festivals:
```bash
curl -X POST "http://localhost:8000/festivals/sync?days_ahead=180"
```

### GET /festivals/high-risk

Get only high-risk festivals:
```bash
curl "http://localhost:8000/festivals/high-risk?days_ahead=30"
```

### GET /predict/live

Get prediction with festivals:
```bash
curl "http://localhost:8000/predict/live?days=7"
```

---

## 🐛 Troubleshooting

### Error: "Service account file not found"

**Solution:**
```bash
# Verify file exists
ls backend/service-account.json

# Check .env has correct path
cat backend/.env | grep GOOGLE_SERVICE_ACCOUNT_FILE
```

### Error: "Permission denied"

**Solution:**
- Ensure Calendar API is enabled in Google Cloud Console
- Verify service account has "Viewer" role
- For custom calendars, ensure service account is shared

### Error: "Calendar not found"

**Solution:**
- Verify calendar ID is correct
- For India Holidays: `en.indian#holiday@group.v.calendar.google.com`
- For custom calendar: Check "Integrate calendar" section

### Using Mock Data

If you see:
```
⚠️  GOOGLE_SERVICE_ACCOUNT_FILE not set in environment
   Using mock festival data
```

This is **normal** if credentials aren't configured. The system will use predefined 2025 festival dates.

---

## 🔐 Security Best Practices

### 1. Never Commit Credentials

Add to `.gitignore`:
```
service-account.json
*.json
!package.json
```

### 2. Restrict Permissions

- Only grant "Viewer" role to service account
- Only enable Calendar API (no other APIs)

### 3. Rotate Keys Periodically

- Delete old keys in Google Cloud Console
- Generate new keys every 90 days

### 4. Use Environment Variables

- Never hardcode paths
- Use `.env` for configuration
- Different credentials for dev/prod

---

## 📈 Festival Data Format

### Input (Google Calendar)

```
Event: Diwali
Date: October 20, 2025
Type: All-day event
```

### Output (API Response)

```json
{
  "id": "abc123",
  "summary": "Diwali",
  "date": "2025-10-20",
  "source": "india_holidays",
  "high_risk": true
}
```

### High-Risk Keywords

Events containing these keywords are flagged as `high_risk: true`:
- diwali, deepavali
- holi
- ganesh, chaturthi, ganapati
- navratri, durga puja
- eid
- dussehra, dasara
- pongal, makar sankranti
- christmas, new year

---

## 🎯 Integration with Risk Model

Festivals are automatically used in risk calculations:

### Festival Features

```python
{
  'is_festival_today': bool,
  'days_to_next_festival': int,
  'is_high_risk_festival_window': bool,
  'festivals_next_7_days': int,
  'high_risk_festivals_next_7_days': int
}
```

### Festival Factor Calculation

```python
def compute_festival_factor(features):
    if features['is_festival_today']:
        return 40  # High risk
    elif features['is_high_risk_festival_window']:
        return 25  # Moderate-high risk
    elif features['days_to_next_festival'] <= 7:
        return 10  # Low-moderate risk
    else:
        return 0   # No risk
```

### Overall Risk Formula

```python
overall_risk = (
    0.25 * aqi_risk +
    0.25 * patient_inflow_risk +
    0.20 * icu_pressure +
    0.20 * festival_factor +  # ← Festival contribution
    0.10 * epidemic_risk
)
```

---

## 📚 Additional Resources

- [Google Calendar API Docs](https://developers.google.com/calendar)
- [Service Account Guide](https://cloud.google.com/iam/docs/service-accounts)
- [Python Client Library](https://github.com/googleapis/google-api-python-client)

---

## ✅ Verification Checklist

- [ ] Google Cloud project created
- [ ] Calendar API enabled
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] File placed in `backend/service-account.json`
- [ ] `.env` updated with path
- [ ] Backend server started successfully
- [ ] `/festivals/upcoming` endpoint returns data
- [ ] Logs show "✓ Google Calendar API service initialized"

---

## 🎉 Success!

You now have live Google Calendar integration! The system will:
- ✅ Automatically fetch Indian festivals
- ✅ Flag high-risk events (Diwali, Holi, etc.)
- ✅ Use festivals in risk calculations
- ✅ Predict patient surges around festivals

**Next Steps:**
1. Test `/predict/live` endpoint
2. View festivals in frontend dashboard
3. Set up N8N workflow for daily sync

---

**Setup Time:** ~15 minutes  
**Maintenance:** Minimal (auto-syncs daily)  
**Cost:** Free (within API limits)
