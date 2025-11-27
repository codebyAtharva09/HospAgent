import pandas as pd
import os
from typing import Dict, Any, List
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

class DataLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Loads CSV data into memory."""
        try:
            self.hospital_data = pd.read_csv(os.path.join(DATA_DIR, 'hospital_data.csv'))
        except FileNotFoundError:
            self.hospital_data = pd.DataFrame([{
                'total_beds': 120, 'icu_beds': 18, 'ventilators': 10, 'ambulances': 3,
                'total_doctors': 25, 'total_nurses': 70
            }]) # Fallback

        try:
            self.doctors = pd.read_csv(os.path.join(DATA_DIR, 'doctors.csv'))
        except FileNotFoundError:
            self.doctors = pd.DataFrame(columns=['id', 'name', 'specialization'])

        try:
            self.supplies = pd.read_csv(os.path.join(DATA_DIR, 'supplies.csv'))
        except FileNotFoundError:
            self.supplies = pd.DataFrame([
                {'item': 'Oxygen Cylinders', 'status': 'OK'},
                {'item': 'N95 Masks', 'status': 'OK'},
                {'item': 'IV Fluids', 'status': 'OK'},
                {'item': 'PPE Kits', 'status': 'OK'}
            ])

    def get_hospital_overview(self) -> Dict[str, int]:
        """Returns hospital capacity overview."""
        # Prefer hospital_data.csv for totals if available, otherwise count rows
        row = self.hospital_data.iloc[0] if not self.hospital_data.empty else {}
        
        total_doctors = len(self.doctors) if not self.doctors.empty else row.get('total_doctors', 25)
        # If doctors.csv is empty or missing, fallback to hospital_data count
        if total_doctors == 0:
             total_doctors = int(row.get('total_doctors', 25))

        return {
            "total_doctors": int(total_doctors),
            "total_nurses": int(row.get('total_nurses', 70)),
            "total_beds": int(row.get('total_beds', 120)),
            "icu_beds": int(row.get('icu_beds', 18)),
            "ventilators": int(row.get('ventilators', 10)),
            "ambulances": int(row.get('ambulances', 3))
        }

    def get_doctor_specializations(self) -> List[Dict[str, Any]]:
        """Returns doctor specializations count."""
        if self.doctors.empty:
            return []
        
        # Check if specialization column exists
        if 'specialization' not in self.doctors.columns:
            return []
            
        counts = self.doctors['specialization'].value_counts().reset_index()
        counts.columns = ['name', 'count']
        return counts.to_dict('records')

    def get_default_supplies(self) -> List[Dict[str, str]]:
        """Returns default supply status."""
        if self.supplies.empty:
            return []
        # Normalize column names
        df = self.supplies.copy()
        if 'name' not in df.columns and 'item' in df.columns:
            df.rename(columns={'item': 'name'}, inplace=True)
        
        return df[['name', 'status']].to_dict('records')

data_loader = DataLoader()
