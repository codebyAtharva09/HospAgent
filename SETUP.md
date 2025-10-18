# Patient Surge Prediction Dashboard Setup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Supabase account and project

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
# SUPABASE_URL=your_project_url
# SUPABASE_ANON_KEY=your_anon_key
# SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 2. Database Setup
1. Create a new Supabase project
2. Run the SQL schema in `supabase_forecast_schema.sql` in your Supabase SQL editor
3. Copy your project URL and keys to `.env`

### 3. Backend Setup
```bash
cd backend
npm install
npm start
# Server will run on http://localhost:5000
```

### 4. AI Forecast Generation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate initial forecast data
python forecast.py
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Frontend will run on http://localhost:5173
```

## 📊 Testing the Dashboard

1. **Generate Forecast Data**: Run `python forecast.py` to populate the database
2. **Start Backend**: `cd backend && npm start`
3. **Start Frontend**: `cd frontend && npm run dev`
4. **View Dashboard**: Open http://localhost:5173 and click "AI Forecast"

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `GET /api/forecast` - Get 7-day forecast data
- `GET /api/forecast/summary` - Get forecast statistics

## 🗂️ Project Structure

```
├── backend/
│   ├── server.js          # Express API server
│   ├── package.json       # Backend dependencies
│   └── ...
├── frontend/
│   ├── src/components/ForecastChart.jsx  # Main dashboard component
│   └── ...
├── forecast.py            # AI forecast generation script
├── supabase_forecast_schema.sql  # Database schema
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

## 🚀 Deployment

### Backend (Render)
1. Connect your GitHub repo to Render
2. Set environment variables in Render dashboard
3. Deploy the `backend/` directory

### Frontend (Vercel)
1. Connect your GitHub repo to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`

### Database (Supabase)
- Already cloud-hosted, just update your production `.env` with production Supabase credentials

## 🔄 Daily Operations

Run `python forecast.py` daily to generate new forecast data. The dashboard will automatically display the latest 7 days of predictions.

## 🐛 Troubleshooting

- **Frontend not loading**: Check if backend is running on port 5000
- **No data showing**: Run `python forecast.py` to generate forecast data
- **Supabase errors**: Verify your `.env` credentials are correct

## 📈 Features

- ✅ Real-time 7-day patient inflow predictions
- ✅ Confidence percentage for each forecast
- ✅ Interactive charts with Recharts
- ✅ Smooth animations with Framer Motion
- ✅ Responsive design with Tailwind CSS
- ✅ Auto-refresh every 30 seconds
- ✅ Supabase integration for live data
