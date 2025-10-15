import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import numpy as np

class PredictiveAgent:
    def __init__(self, model_path='backend/models/surge_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        """Load pre-trained model."""
        try:
            self.model = joblib.load(self.model_path)
        except FileNotFoundError:
            # Create and train a simple model if not exists
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def train_model(self, X, y):
        """Train the predictive model."""
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)
        return {"status": "success", "message": "Model trained and saved"}

    def predict_surge(self, event_type, aqi=100):
        """
        Predict patient surge based on event type.
        event_type: 'festival', 'pollution', 'epidemic', 'normal'
        """
        # Map event types to features
        if event_type == 'festival':
            features = [aqi, 1, 0]
        elif event_type == 'epidemic':
            features = [aqi, 0, 1]
        elif event_type == 'pollution':
            features = [aqi, 0, 0]  # High AQI indicates pollution
        else:
            features = [50, 0, 0]  # Normal conditions

        if self.model is None:
            return {"status": "error", "message": "Model not loaded"}

        prediction = self.model.predict([features])[0]
        return {
            "status": "success",
            "predicted_patients": max(0, int(prediction)),
            "event_type": event_type,
            "aqi": aqi
        }

    def predict_next_7_days(self, event_type='normal', aqi=100):
        """
        Predict patient inflow for next 7 days.
        Returns list of dicts with date and predicted_patients.
        """
        from datetime import datetime, timedelta

        predictions = []
        for i in range(7):
            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            pred = self.predict_surge(event_type, aqi)
            predictions.append({
                "date": date,
                "predicted_patients": pred['predicted_patients'],
                "aqi": aqi
            })
        return predictions

    def predict_demand(self, dataset_type):
        """Predict demand for different hospital resources."""
        # This would use more sophisticated models for different datasets
        # For now, return basic predictions based on historical data
        predictions = {
            "appointments": {"next_week": 150, "trend": "increasing"},
            "treatments": {"next_week": 120, "trend": "stable"},
            "staffing": {"doctors_needed": 25, "nurses_needed": 40},
            "inventory": {"supplies_needed": 500, "trend": "increasing"}
        }
        return predictions
