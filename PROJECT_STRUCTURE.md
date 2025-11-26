# HospAgent SurgeOps - Complete Project Structure

```
HospAgent/
│
├── backend/
│   ├── main.py                          # FastAPI entry point
│   ├── requirements.txt                 # Python dependencies
│   ├── .env                             # Environment variables
│   │
│   ├── agents/                          # AI Agents
│   │   ├── risk_agent.py
│   │   ├── forecast_agent.py
│   │   ├── resource_optimizer_agent.py
│   │   └── ... (other agents)
│   │
│   ├── services/
│   │   ├── env_client.py               # OpenWeather API client
│   │   ├── festival_sync.py            # Google Calendar integration
│   │   └── data_store.py               # Simple data persistence
│   │
│   ├── engines/
│   │   ├── risk_engine.py              # Risk calculation engine
│   │   └── forecast_engine.py          # Patient load forecasting
│   │
│   ├── routers/
│   │   ├── predict.py                  # Prediction endpoints
│   │   ├── ingest.py                   # Data ingestion endpoints
│   │   ├── festivals.py                # Festival management
│   │   └── ai_command.py               # AI Command Bot
│   │
│   └── models/
│       └── schemas.py                   # Pydantic models
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main application
│   │   ├── main.jsx                    # Entry point
│   │   ├── index.css                   # Global styles
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── Topbar.jsx
│   │   │   │   └── SimulationStrip.jsx
│   │   │   │
│   │   │   └── cards/
│   │   │       ├── RiskCard.jsx
│   │   │       ├── ForecastCard.jsx
│   │   │       ├── StaffCard.jsx
│   │   │       ├── SupplyCard.jsx
│   │   │       ├── FestivalCard.jsx
│   │   │       └── WellbeingCard.jsx
│   │   │
│   │   └── services/
│   │       └── api.js                  # API client
│   │
│   ├── package.json
│   └── vite.config.js
│
├── n8n/
│   ├── workflow.json                    # N8N automation workflow
│   └── alerts_workflow.json             # Automated alerts workflow
│
├── docs/
│   ├── SETUP_GOOGLE_CALENDAR.md
│   └── API_DOCUMENTATION.md
│
└── README.md
```

## Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **httpx** - Async HTTP client for API calls
- **python-dotenv** - Environment variable management
- **google-api-python-client** - Google Calendar integration
- **pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **CSS3** - Custom styling (no framework dependencies)

### External APIs
- **OpenWeather API** - Live AQI & Weather data
- **Google Calendar API** - Festival tracking

### Automation
- **N8N** - Workflow automation for scheduled tasks
