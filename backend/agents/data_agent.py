import pandas as pd
import json
import os

class DataAgent:
    def __init__(self):
        self.data = None
        self.appointments = None
        self.patients = None
        self.doctors = None
        self.treatments = None
        self.billing = None

    def load_data(self, filepath):
        """Load hospital data from CSV file."""
        try:
            self.data = pd.read_csv(filepath)
            self.data['date'] = pd.to_datetime(self.data['date'])
            return {"status": "success", "message": f"Loaded {len(self.data)} records"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_all_datasets(self):
        """Load all hospital datasets."""
        try:
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            self.appointments = pd.read_csv(os.path.join(base_path, 'appointments.csv'))
            self.patients = pd.read_csv(os.path.join(base_path, 'patients.csv'))
            self.doctors = pd.read_csv(os.path.join(base_path, 'doctors.csv'))
            self.treatments = pd.read_csv(os.path.join(base_path, 'treatments.csv'))
            self.billing = pd.read_csv(os.path.join(base_path, 'billing.csv'))

            # Convert date columns
            self.appointments['appointment_date'] = pd.to_datetime(self.appointments['appointment_date'])
            self.patients['registration_date'] = pd.to_datetime(self.patients['registration_date'])
            self.treatments['treatment_date'] = pd.to_datetime(self.treatments['treatment_date'])
            self.billing['bill_date'] = pd.to_datetime(self.billing['bill_date'])

            return {"status": "success", "message": "All datasets loaded successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def analyze_trends(self):
        """Analyze historical data for surge patterns."""
        if self.data is None:
            return {"status": "error", "message": "No data loaded"}

        # Group by month to find busiest periods
        monthly = self.data.groupby(self.data['date'].dt.month)['patient_count'].mean()
        busiest_month = monthly.idxmax()

        # Analyze event types
        event_impacts = self.data.groupby(['festival_flag', 'epidemic_flag'])['patient_count'].mean()

        insights = {
            "busiest_month": int(busiest_month),
            "average_patients": float(self.data['patient_count'].mean()),
            "event_impacts": {str(k): float(v) for k, v in event_impacts.to_dict().items()},
            "total_records": int(len(self.data))
        }

        return {"status": "success", "insights": insights}

    def analyze_comprehensive_trends(self):
        """Analyze trends from all datasets."""
        if self.appointments is None:
            result = self.load_all_datasets()
            if result['status'] == 'error':
                return result

        # Appointment trends
        appointment_trends = self.appointments.groupby(self.appointments['appointment_date'].dt.month)['appointment_id'].count()

        # Treatment costs
        treatment_costs = self.treatments.groupby('treatment_type')['cost'].mean()

        # Doctor specialization distribution
        doctor_specializations = self.doctors['specialization'].value_counts()

        # Patient demographics
        patient_age_groups = pd.cut(pd.to_datetime('today').year - pd.to_datetime(self.patients['date_of_birth']).dt.year,
                                   bins=[0, 18, 35, 50, 65, 100], labels=['0-18', '19-35', '36-50', '51-65', '65+'])
        age_distribution = patient_age_groups.value_counts()

        # Billing status
        billing_status = self.billing['payment_status'].value_counts()

        insights = {
            "appointment_trends": appointment_trends.to_dict(),
            "treatment_costs": treatment_costs.to_dict(),
            "doctor_specializations": doctor_specializations.to_dict(),
            "patient_age_distribution": age_distribution.to_dict(),
            "billing_status": billing_status.to_dict()
        }

        return {"status": "success", "insights": insights}

    def prepare_features(self):
        """Prepare features for prediction."""
        if self.data is None:
            return None

        features = self.data[['AQI', 'festival_flag', 'epidemic_flag']].values
        target = self.data['patient_count'].values
        return features, target

    def prepare_features_from_appointments(self):
        """Prepare features from appointments data for prediction."""
        if self.appointments is None:
            return None

        # Create synthetic features from appointments
        # Group by date to get daily appointment counts
        daily_appointments = self.appointments.groupby(self.appointments['appointment_date'].dt.date)['appointment_id'].count().reset_index()
        daily_appointments.columns = ['date', 'appointment_count']

        # Add synthetic AQI and flags (since we don't have real data)
        daily_appointments['AQI'] = 100  # Default AQI
        daily_appointments['festival_flag'] = 0  # Default no festival
        daily_appointments['epidemic_flag'] = 0  # Default no epidemic

        features = daily_appointments[['AQI', 'festival_flag', 'epidemic_flag']].values
        target = daily_appointments['appointment_count'].values
        return features, target
