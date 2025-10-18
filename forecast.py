#!/usr/bin/env python3
"""
AI Forecast Script for Patient Surge Prediction
Simulates 7-day forecast data and inserts it into Supabase
"""

from supabase import create_client
import datetime
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def insert_forecast():
    """
    Generate and insert 7-day forecast data into Supabase
    """
    today = datetime.date.today()

    # Clear existing forecast data for today onwards
    try:
        supabase.table("forecast_logs").delete().gte("date", today.isoformat()).execute()
        print("🧹 Cleared existing forecast data")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear existing data: {e}")

    # Generate new forecast data
    forecast_entries = []
    for i in range(7):
        forecast_date = today + datetime.timedelta(days=i)

        # Simulate realistic patient inflow based on day of week
        # Weekends typically have lower patient counts
        base_inflow = 45 if forecast_date.weekday() >= 5 else 65  # Mon-Fri higher
        variation = random.randint(-15, 15)
        predicted_inflow = max(10, min(100, base_inflow + variation))

        # Confidence decreases slightly for future dates
        confidence = max(75, 95 - (i * 2) + random.randint(-5, 5))

        entry = {
            "date": forecast_date.isoformat(),
            "predicted_inflow": predicted_inflow,
            "confidence": round(confidence, 2)
        }
        forecast_entries.append(entry)

    # Insert forecast data
    try:
        result = supabase.table("forecast_logs").insert(forecast_entries).execute()
        print(f"✅ Successfully inserted {len(forecast_entries)} forecast entries for the next 7 days")

        # Print summary
        print("\n📊 Forecast Summary:")
        for entry in forecast_entries:
            print(f"  {entry['date']}: {entry['predicted_inflow']} patients (Confidence: {entry['confidence']}%)")

    except Exception as e:
        print(f"❌ Error inserting forecast data: {e}")

if __name__ == "__main__":
    print("🤖 Starting AI Forecast Generation...")
    insert_forecast()
    print("🎉 Forecast generation complete!")
