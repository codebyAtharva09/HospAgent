# HospAgent Supabase Integration Guide

## Overview
This guide explains how to integrate Supabase with your HospAgent project for storing and retrieving prediction data, recommendations, and advisories.

## Architecture
```
Frontend (React) ←→ Flask Backend ←→ Supabase PostgreSQL
     ↑                                       ↑
   Axios HTTP                           PostgREST API
```

## Prerequisites
1. Create a Supabase project at https://supabase.com
2. Get your project URL and anon key from the project settings

## Setup Instructions

### 1. Backend Configuration

#### Install Dependencies
```bash
cd backend
pip install supabase python-dotenv
```

#### Environment Variables
Create `backend/.env`:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

#### Database Configuration
Create `backend/db_config.py`:
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

### 2. Supabase Database Setup

#### Create Tables
Run the SQL in `supabase_schema.sql` in your Supabase SQL Editor:

```sql
-- Creates predictions, recommendations, and advisories tables
-- with proper relationships and RLS policies
```

#### Tables Structure
- **predictions**: Stores AI predictions with date, patient count, AQI, event type
- **recommendations**: Links to predictions, stores staff and supply recommendations
- **advisories**: Links to predictions, stores advisory messages

### 3. Backend Route Updates

#### Prediction Routes (`backend/routes/prediction_routes.py`)
- `/predict-surge` now saves predictions to Supabase
- `/forecast` saves 7-day forecasts to Supabase

#### Recommendation Routes (`backend/routes/recommend_routes.py`)
- `/recommend-plan` saves staffing and supply recommendations
- `/optimize-staffing` and `/predict-consumption` save optimization results

#### Advisory Routes (`backend/routes/advisory_routes.py`)
- `/generate-advisory` saves advisory messages to Supabase

### 4. Frontend Integration

#### Install Supabase Client
```bash
cd frontend
npm install @supabase/supabase-js
```

#### Environment Variables
Create `frontend/.env`:
```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

#### Supabase Service (`frontend/src/services/supabase.js`)
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// Functions for fetching historical data
export const getPredictionsHistory = async () => { /* ... */ }
export const getRecommendationsHistory = async () => { /* ... */ }
export const getAdvisoriesHistory = async () => { /* ... */ }

// Real-time subscriptions
export const subscribeToPredictions = (callback) => { /* ... */ }
```

#### Update Components
- **PredictionPanel**: Now shows historical predictions from Supabase
- **StaffPanel**: Shows historical staffing recommendations
- **InventoryPanel**: Shows historical supply recommendations
- **AdvisoryPanel**: Shows historical advisories

## API Endpoints

### Backend Endpoints
- `POST /api/predict-surge` - Generate and save predictions
- `GET /api/forecast` - Generate and save forecasts
- `POST /api/recommend-plan` - Generate and save recommendations
- `POST /api/generate-advisory` - Generate and save advisories

### Supabase Direct Access (Frontend)
```javascript
// Get prediction history
const predictions = await supabase
  .from('predictions')
  .select('*')
  .order('created_at', { ascending: false })

// Get recommendations with prediction details
const recommendations = await supabase
  .from('recommendations')
  .select(`
    *,
    predictions (
      date,
      predicted_patients,
      aqi,
      event_type
    )
  `)
```

## Real-time Features

### Enable Real-time
```javascript
// Subscribe to new predictions
const subscription = supabase
  .channel('predictions_changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'predictions'
  }, (payload) => {
    console.log('New prediction:', payload.new)
    // Update UI with new data
  })
  .subscribe()
```

## Security Considerations

### Row Level Security (RLS)
- Currently set to allow anonymous access for demo purposes
- For production, implement proper authentication:
  - Use Supabase Auth for user management
  - Create policies based on user roles
  - Restrict data access based on hospital/organization

### Environment Variables
- Never commit actual Supabase keys to version control
- Use different keys for development and production
- Rotate keys regularly

## Testing the Integration

### 1. Start Backend
```bash
cd backend
python app.py
```

### 2. Start Frontend
```bash
cd frontend
npm start
```

### 3. Test Data Flow
1. Make a prediction request
2. Check Supabase dashboard - data should appear
3. Refresh frontend - historical data should load
4. Test real-time updates

### 4. Verify Tables
Check your Supabase dashboard to ensure data is being inserted correctly into:
- `predictions` table
- `recommendations` table
- `advisories` table

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check SUPABASE_URL and SUPABASE_KEY in .env files
   - Ensure Supabase project is active

2. **Data Not Appearing**
   - Check Supabase table policies (RLS)
   - Verify table names match exactly
   - Check browser console for errors

3. **Real-time Not Working**
   - Ensure real-time is enabled in Supabase dashboard
   - Check subscription setup in frontend

### Debug Commands
```bash
# Test backend connection
cd backend
python -c "from db_config import supabase; print('Connected:', supabase.table('predictions').select('*').limit(1).execute())"

# Test frontend connection
cd frontend
npm run dev
# Check browser console for Supabase errors
```

## Next Steps

1. **Authentication**: Implement Supabase Auth for secure access
2. **Advanced Queries**: Add filtering, pagination, and search
3. **Analytics**: Build dashboards with historical trend analysis
4. **Notifications**: Add push notifications for critical alerts
5. **Backup**: Set up automated data backups

## Support

For issues with this integration:
1. Check Supabase documentation: https://supabase.com/docs
2. Review Flask-Supabase integration docs
3. Check browser developer tools for frontend errors
4. Verify backend logs for server-side errors
