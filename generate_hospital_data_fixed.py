import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import json

# Initialize Faker for realistic data generation
fake = Faker('en_IN')  # Indian locale

# Constants
NUM_ROWS = 10000
CITIES = ['Mumbai', 'Pune', 'Delhi', 'Chennai', 'Bengaluru', 'Kolkata', 'Ahmedabad', 'Hyderabad', 'Lucknow', 'Indore']
REGIONS = ['West India', 'North India', 'South India', 'East India', 'Central India']
HOSPITAL_NAMES = [
    'City General Hospital', 'Metro Health Center', 'Regional Medical Institute',
    'Apollo Healthcare', 'Max Super Speciality', 'Fortis Hospital', 'AIIMS Branch',
    'Tata Memorial', 'CMC Hospital', 'KEM Hospital'
]

# Agent-related constants
AGENTS = ['communication_agent', 'data_agent', 'learning_agent', 'patient_advisory_agent',
          'perception_agent', 'planning_agent', 'predictive_agent', 'reasoning_agent',
          'staff_allocation_agent', 'supply_inventory_agent']

def generate_timestamp(start_date='2023-01-01', end_date='2024-12-31'):
    """Generate random timestamp between start and end dates."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    random_date = start + timedelta(days=random.randint(0, (end - start).days))
    random_time = timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    return (random_date + random_time).strftime('%Y-%m-%d %H:%M:%S')

def get_aqi_category(aqi):
    """Categorize AQI levels."""
    if aqi <= 50: return 'Good'
    elif aqi <= 100: return 'Moderate'
    elif aqi <= 150: return 'Unhealthy for Sensitive Groups'
    elif aqi <= 200: return 'Unhealthy'
    elif aqi <= 300: return 'Very Unhealthy'
    else: return 'Hazardous'

def get_epidemic_alert_level():
    """Random epidemic alert levels."""
    return random.choice(['Low Risk', 'Moderate Risk', 'High Risk', 'Critical'])

def generate_festival_event(timestamp):
    """Determine if there's a festival event based on date."""
    dt = datetime.strptime(timestamp.split()[0], '%Y-%m-%d')
    month_day = (dt.month, dt.day)

    festivals = {
        (11, 12): 'Diwali', (3, 25): 'Holi', (10, 2): 'Gandhi Jayanti',
        (1, 26): 'Republic Day', (8, 15): 'Independence Day', (5, 1): 'Labour Day'
    }

    return festivals.get(month_day, False)

def calculate_correlations(row):
    """Apply realistic correlations between variables."""
    # High AQI increases respiratory cases and ICU usage
    if row['aqi_category'] in ['Unhealthy', 'Very Unhealthy', 'Hazardous']:
        row['airborne_cases'] += random.randint(5, 15)
        row['icu_beds_available'] -= random.randint(1, 3)
        row['oxygen_cylinders_available'] -= random.randint(10, 30)

    # Festival increases patient inflow and staff shortage
    if row['festival_event']:
        row['predicted_patient_inflow'] += random.randint(20, 50)
        row['actual_patient_inflow'] += random.randint(15, 45)
        row['predicted_staff_shortage_risk'] += random.uniform(0.1, 0.3)
        row['staff_absent_percent'] += random.uniform(5, 15)

    # Epidemic alert affects medicine stock and absenteeism
    if row['epidemic_alert_level'] in ['High Risk', 'Critical']:
        row['critical_medicines_stock'] -= random.randint(20, 50)
        row['supply_shortage_risk'] += random.uniform(0.2, 0.4)
        row['staff_absent_percent'] += random.uniform(10, 25)

    # Calculate prediction error
    row['prediction_error'] = abs(row['predicted_patient_inflow'] - row['actual_patient_inflow'])

    return row

def generate_row(record_id):
    """Generate a single row of hospital data."""
    timestamp = generate_timestamp()
    city = random.choice(CITIES)
    region = REGIONS[CITIES.index(city) // 2]  # Group cities into regions

    # Base values
    base_patients = random.randint(50, 200)
    base_staff = random.randint(20, 80)

    row = {
        # Identifiers
        'record_id': f'R{record_id:05d}',
        'timestamp': timestamp,
        'hospital_id': f'H{random.randint(100, 999)}',
        'hospital_name': random.choice(HOSPITAL_NAMES),
        'city': city,
        'region': region,

        # External Conditions (Perception Agent)
        'festival_event': generate_festival_event(timestamp),
        'pollution_index': random.randint(50, 500),
        'aqi_category': '',  # Will be set after AQI calculation
        'temperature_celsius': random.randint(15, 40),
        'humidity_percent': random.randint(30, 90),
        'epidemic_alert_level': get_epidemic_alert_level(),

        # Hospital Operations (Predictive + Reasoning Agents)
        'total_beds': random.randint(200, 1000),
        'beds_occupied': 0,  # Will be calculated
        'icu_beds_available': random.randint(10, 50),
        'ambulance_requests': random.randint(0, 20),
        'staff_absent_percent': random.uniform(0, 20),
        'doctors_on_duty': 0,  # Will be calculated
        'nurses_on_duty': 0,  # Will be calculated

        # Patients (Predictive + Reasoning)
        'viral_cases_reported': random.randint(0, 30),
        'airborne_cases': random.randint(0, 25),
        'waterborne_cases': random.randint(0, 15),
        'predicted_patient_inflow': base_patients + random.randint(-20, 20),
        'actual_patient_inflow': base_patients + random.randint(-30, 30),
        'prediction_error': 0,  # Will be calculated

        # Inventory (Supply Inventory Agent)
        'oxygen_cylinders_available': random.randint(50, 200),
        'critical_medicines_stock': random.randint(100, 500),
        'supply_shortage_risk': random.uniform(0, 0.5),
        'auto_restock_flag': random.choice([True, False]),

        # Staffing (Staff Allocation Agent)
        'predicted_staff_shortage_risk': random.uniform(0, 0.8),
        'recommended_nurses_to_add': random.randint(0, 10),
        'recommended_doctors_to_add': random.randint(0, 5),
        'shift_rearrangement_flag': random.choice([True, False]),

        # Planning (Planning Agent)
        'optimal_plan_id': f'P{random.randint(1000, 9999)}',
        'plan_confidence_score': random.uniform(0.5, 0.95),
        'plan_accepted': random.choice([True, False]),

        # Advisories (Communication + Patient Advisory Agents)
        'alert_type': random.choice(['Patient Surge', 'Staff Shortage', 'Supply Alert', 'Weather Warning', 'Epidemic Alert']),
        'alert_priority': random.choice(['Low', 'Medium', 'High', 'Critical']),
        'advisory_message': fake.sentence(),
        'channel': random.choice(['SMS', 'Email', 'Dashboard', 'Mobile App', 'Public Announcement']),
        'affected_departments': random.sample(['ER', 'ICU', 'OPD', 'Surgery', 'Pediatrics'], random.randint(1, 3)),

        # Learning (Learning Agent)
        'system_confidence_score': random.uniform(0.6, 0.95),
        'model_version': f'v{random.randint(1, 5)}.0',
        'feedback_flag': random.choice([True, False]),
        'retrain_required': random.choice([True, False]),
        'data_drift_detected': random.choice([True, False]),

        # Contextual Environment (Perception Agent)
        'traffic_delay_minutes': random.randint(0, 60),
        'festival_crowd_density': random.choice(['Low', 'Medium', 'High', 'Very High']),
        'public_transport_status': random.choice(['Normal', 'Delayed', 'Disrupted']),
        'power_supply_status': random.choice(['Stable', 'Intermittent', 'Outage']),
        'pharma_stock_level': random.choice(['Adequate', 'Low', 'Critical'])
    }

    # Set AQI and category
    row['aqi_category'] = get_aqi_category(row['pollution_index'])

    # Calculate derived values
    row['beds_occupied'] = int(row['total_beds'] * random.uniform(0.6, 0.95))
    row['doctors_on_duty'] = base_staff - int(base_staff * row['staff_absent_percent'] / 100)
    row['nurses_on_duty'] = (base_staff * 2) - int((base_staff * 2) * row['staff_absent_percent'] / 100)

    # Apply correlations
    row = calculate_correlations(row)

    # Convert affected_departments to string for CSV
    row['affected_departments'] = ', '.join(row['affected_departments'])

    return row

def add_missing_values(df, missing_rate=0.08):
    """Add random missing values to simulate real-world data issues."""
    df_copy = df.copy()
    total_cells = df_copy.size
    num_missing = int(total_cells * missing_rate)

    for _ in range(num_missing):
        row_idx = random.randint(0, len(df_copy) - 1)
        col_idx = random.randint(0, len(df_copy.columns) - 1)
        df_copy.iloc[row_idx, col_idx] = np.nan

    return df_copy

def main():
    print(f"Generating {NUM_ROWS} rows of synthetic hospital data...")

    # Generate data
    data = []
    for i in range(1, NUM_ROWS + 1):
        row = generate_row(i)
        data.append(row)

        if i % 1000 == 0:
            print(f"Generated {i} rows...")

    # Create DataFrame
    df = pd.DataFrame(data)

    # Add missing values
    df = add_missing_values(df)

    # Save as CSV
    df.to_csv('backend/data/hospital_data.csv', index=False)
    print("Saved hospital_data.csv")

    # Save as JSON
    df.to_json('backend/data/hospital_data.json', orient='records', indent=2)
    print("Saved hospital_data.json")

    # Print summary statistics
    print("\nData Generation Summary:")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(".2%")

    print("\nSample of generated data:")
    print(df.head())

    print("\nColumn info:")
    print(df.info())

if __name__ == '__main__':
    main()
