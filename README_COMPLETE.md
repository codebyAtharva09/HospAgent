# HospAgent SurgeOps - Complete Production System

## 🏥 Overview

**HospAgent SurgeOps** is a real-time hospital surge prediction system designed for Indian hospitals. It uses live environmental data, festival calendars, and epidemic surveillance to predict patient loads and optimize hospital operations.

### Key Features

✅ **Live Environmental Data**
- Real-time AQI from OpenWeather API
- Live weather conditions (temperature, humidity, wind)
- PM2.5, PM10, and pollutant tracking

✅ **Multi-Factor Risk Engine**
- Composite risk scoring (0-100)
- Department-specific risk assessment
- Supply risk prediction
- Actionable recommendations

✅ **7-Day Patient Forecasting**
- Day-by-day patient load prediction
- Departmental breakdown (Respiratory, Trauma, ICU, etc.)
- Confidence intervals
- Staff demand calculation

✅ **Google Calendar Integration**
- Automatic festival tracking
- High-risk event flagging (Diwali, Holi, etc.)
- Surge multiplier calculation

✅ **Resource Optimization**
- Staffing recommendations per shift
- Supply requirements (Oxygen, Masks, Beds)
- Burnout risk monitoring

✅ **Modern SaaS UI**
- Full-screen dashboard layout
- Live/Simulation mode toggle
- Real-time updates
- Interactive controls

---

## 📁 Project Structure

```
HospAgent/
├── backend/
│   ├── main.py                          # FastAPI application
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── engines/
│   │   ├── risk_engine.py              # Risk calculation
│   │   └── forecast_engine.py          # Patient forecasting
│   │
│   ├── services/
│   │   ├── env_client.py               # OpenWeather API client
│   │   ├── festival_sync.py            # Google Calendar sync
│   │   └── data_store.py               # Data persistence
│   │
│   ├── routers/
│   │   ├── predict.py                  # Prediction endpoints
│   │   ├── ingest.py                   # Data ingestion
│   │   └── festivals.py                # Festival management
│   │
│   └── models/
│       └── schemas.py                   # Pydantic models
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   │
│   │   └── components/
│   │       ├── layout/
│   │       │   ├── Sidebar.jsx
│   │       │   ├── Topbar.jsx
│   │       │   └── SimulationStrip.jsx
│   │       │
│   │       └── cards/
│   │           ├── RiskCard.jsx
│   │           ├── ForecastCard.jsx
│   │           ├── StaffCard.jsx
│   │           ├── SupplyCard.jsx
│   │           └── FestivalCard.jsx
│   │
│   └── package.json
│
└── n8n/
    └── workflow.json                    # Automation workflow
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **OpenWeather API Key** (free tier works)
- **Google Calendar API** (optional, uses mock data as fallback)

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Edit `backend/.env`:
```env
# OpenWeather API (REQUIRED for live data)
OPENWEATHER_API_KEY=your_api_key_here

# Hospital Location (Mumbai - Goregaon)
HOSP_LAT=19.155
HOSP_LON=72.849

# Google Calendar (OPTIONAL - uses mock data if not provided)
GOOGLE_CALENDAR_CREDENTIALS=credentials.json

# Database (Optional)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_key
```

5. **Run backend server**
```bash
python main.py
```

Backend will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run development server**
```bash
npm run dev
```

Frontend will start on `http://localhost:5173` or `http://localhost:8080`

---

## 🔑 Getting API Keys

### OpenWeather API (Required)

1. Go to https://openweathermap.org/api
2. Sign up for free account
3. Navigate to API Keys section
4. Copy your API key
5. Add to `backend/.env` as `OPENWEATHER_API_KEY`

**Free tier includes:**
- 1,000 calls/day
- Current weather data
- Air pollution data
- Perfect for demo/development

### Google Calendar API (Optional)

See `docs/SETUP_GOOGLE_CALENDAR.md` for detailed instructions.

**Quick version:**
1. Create project in Google Cloud Console
2. Enable Google Calendar API
3. Create Service Account
4. Download credentials JSON
5. Save as `backend/credentials.json`

**Note:** System works with mock festival data if Google Calendar is not configured.

---

## 📡 API Endpoints

### Live Data

**GET /env/live**
- Fetches real-time AQI and weather
- Returns merged environmental data

**GET /api/predict/live**
- Complete prediction pipeline
- Uses live environmental data
- Returns risk, forecast, staffing, supplies

### Simulation Mode

**GET /risk/now**
- Manual risk calculation
- Query params: `aqi`, `slope`, `epidemic`, `icu`

**GET /forecast/patients**
- Patient load forecast
- Query params: `days`, `aqi`

**GET /plan/staffing**
- Staffing recommendations

**GET /plan/supplies**
- Supply requirements

### Festivals

**GET /api/festivals/upcoming**
- Upcoming high-risk festivals
- Query params: `days`

**POST /api/festivals/sync**
- Sync from Google Calendar

### AI Command

**POST /api/ai/command**
- AI Chat and Command interface
- Generates reports and answers queries

### Data Ingestion

**POST /ingest/aqi** (Legacy)
- Ingest AQI data point

**POST /ingest/weather** (Legacy)
- Ingest weather data

---

## 🎨 UI Features

### Color Palette

- **Background:** `#CDDBE5` (Pale Sky)
- **Primary:** `#769DD7` (Wisteria Blue)
- **Surface:** `#FFFFFF` (White)
- **Text:** `#111827` (Dark Gray)
- **Muted:** `#6B7280` (Medium Gray)

### Layout

- **Full-screen dashboard** (no centered boxes)
- **Permanent sidebar** with navigation
- **Top bar** with location, mode toggle, status
- **Simulation strip** for manual controls
- **Grid layout** for cards
- **Smooth animations** and transitions

### Components

1. **Risk Card** - Live risk gauge with breakdown
2. **Forecast Card** - 7-day bar chart
3. **Staff Card** - Staffing requirements
4. **Supply Card** - Critical supplies table
5. **Festival Card** - Upcoming high-risk events
6. **Wellbeing Card** - Staff burnout alerts

---

## 🤖 N8N Automation

### Workflow Schedule

**Every 10 minutes:**
1. Trigger `/api/predict/live`
   - Fetches live AQI & Weather internally
   - Updates risk and forecast models

**Daily at 00:15:**
1. POST to `/api/festivals/sync` (Sync Google Calendar)
2. GET `/forecast/patients` (Refresh forecast)
3. POST to `/api/ai/command` (Generate AI Daily Report)
4. Send Slack Alert with AI Report

### Setup

1. Import `n8n/workflow.json` into N8N
2. Configure credentials:
   - OpenWeather API key
   - Backend URL
   - Slack Webhook
3. Activate workflow

---

## 📊 Sample Responses

### /env/live

```json
{
  "location": {
    "lat": 19.155,
    "lon": 72.849,
    "name": "Mumbai"
  },
  "temperature": 29.6,
  "humidity": 70,
  "pressure": 1011,
  "weather_desc": "smoke",
  "wind_speed": 2.5,
  "aqi": 250,
  "aqi_level": 4,
  "pollutants": {
    "pm2_5": 108.5,
    "pm10": 192.3,
    "no2": 45.2,
    "so2": 12.1,
    "co": 890.5,
    "o3": 35.6
  },
  "timestamp": "2025-11-25T00:15:00Z",
  "is_live": true
}
```

### /predict/live

```json
{
  "env": { /* environmental data */ },
  "risk": {
    "timestamp": "2025-11-25T00:15:00Z",
    "hospital_risk_index": 75,
    "level": "HIGH",
    "breakdown": {
      "aqi_risk": 85,
      "icu_risk": 70,
      "respiratory_risk": 80,
      "epidemic_risk": 40,
      "surge_risk": 60
    },
    "contributing_factors": [
      "High AQI (250) - Poor Air Quality",
      "Patient Surge Detected (+15% in 6h)",
      "ICU High Pressure (72% Occupancy)"
    ],
    "department_risks": {
      "Emergency": 78,
      "ICU": 70,
      "Pulmonology": 88,
      "Pediatrics": 55,
      "General_Ward": 60
    },
    "supply_risks": {
      "oxygen_cylinders": "HIGH",
      "n95_masks": "HIGH",
      "icu_beds": "MEDIUM",
      "ventilators": "MEDIUM"
    },
    "recommendations": [
      "Activate Level 2 Surge Protocol",
      "Increase staff on next shift",
      "Expedite supply orders"
    ]
  },
  "forecast": [
    {
      "date": "2025-11-25",
      "day_of_week": "Monday",
      "total_patients": 245,
      "confidence": 92,
      "breakdown": {
        "respiratory": 85,
        "trauma": 25,
        "viral_infectious": 35,
        "cardiac": 20,
        "pediatric": 50,
        "icu_candidates": 15,
        "other": 15
      },
      "staff_demand": {
        "doctors": 21,
        "nurses": 46,
        "support_staff": 13,
        "icu_specialists": 5
      },
      "factors": {
        "day_of_week_impact": 1.15,
        "aqi_impact": 1.3,
        "weather_impact": 1.1,
        "epidemic_impact": 1.16,
        "festival_impact": 1.0
      },
      "alerts": [
        "High respiratory case volume - Check oxygen supply"
      ]
    }
    /* ... 6 more days */
  ],
  "staffing": [ /* staffing plan */ ],
  "supplies": [ /* supply requirements */ ]
}
```

---

## 🔧 Configuration

### Environment Variables

```env
# Required
OPENWEATHER_API_KEY=your_key_here

# Hospital Location
HOSP_LAT=19.155
HOSP_LON=72.849
HOSP_NAME=Mumbai Central Hospital

# Optional
GOOGLE_CALENDAR_CREDENTIALS=credentials.json
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

# Server
PORT=8000
DEBUG=false
```

### Customization

**Risk Weights** (`backend/engines/risk_engine.py`):
```python
self.WEIGHTS = {
    'aqi': 0.25,
    'patient_slope': 0.20,
    'epidemic': 0.15,
    'festival': 0.15,
    'icu_pressure': 0.15,
    'weather': 0.10
}
```

**Base Load** (`backend/engines/forecast_engine.py`):
```python
self.BASE_DAILY_LOAD = 150  # Adjust for your hospital
```

---

## 🧪 Testing

### Test Live API
```bash
curl http://localhost:8000/env/live
```

### Test Prediction
```bash
curl http://localhost:8000/predict/live
```

### Test with Parameters
```bash
curl "http://localhost:8000/risk/now?aqi=300&epidemic=5&override_festival=true"
```

---

## 🚢 Deployment

### Backend (FastAPI)

**Option 1: Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 2: Railway/Render**
- Connect GitHub repo
- Set environment variables
- Deploy

### Frontend (React)

**Build for production:**
```bash
npm run build
```

**Deploy to:**
- Vercel
- Netlify
- Cloudflare Pages

---

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Live AQI & Weather integration
- ✅ Risk calculation engine
- ✅ 7-day forecasting
- ✅ Google Calendar festivals
- ✅ Modern UI dashboard

### Phase 2 (Next)
- [ ] ML model training (Prophet/LSTM)
- [ ] Database integration (TimescaleDB)
- [ ] Historical data analysis
- [ ] SMS/WhatsApp notifications
- [ ] Multi-hospital support

### Phase 3 (Future)
- [ ] Mobile app (React Native)
- [ ] Predictive analytics dashboard
- [ ] Integration with HMS systems
- [ ] Real-time bed management
- [ ] Staff scheduling automation

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **OpenWeather** for environmental data API
- **Google Calendar** for festival tracking
- **FastAPI** for backend framework
- **React** for frontend library

---

## 📞 Support

For issues or questions:
- Create GitHub issue
- Email: support@hospagent.com
- Documentation: https://docs.hospagent.com

---

**Built for Mumbai Hacks 2025**  
**Solving India's Healthcare Surge Problem with Agentic AI**
