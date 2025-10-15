from flask import Blueprint, request, jsonify
from agents.predictive_agent import PredictiveAgent
from agents.data_agent import DataAgent
from datetime import datetime, timedelta
from db_config import supabase
import uuid

prediction_bp = Blueprint('prediction', __name__)
predictive_agent = PredictiveAgent()
data_agent = DataAgent()

@prediction_bp.route('/predict-surge', methods=['POST'])
def predict_surge():
    """Predict patient surge based on event type."""
    data = request.get_json()
    event_type = data.get('event_type', 'normal')
    aqi = data.get('aqi', 100)

    # Train model if not exists
    if predictive_agent.model is None or not hasattr(predictive_agent.model, 'feature_importances_'):
        result = data_agent.load_all_datasets()
        if result['status'] == 'error':
            return jsonify({"error": "Failed to load data", "details": result['message']}), 500
        # For now, use appointments as proxy for patient count
        # TODO: Implement proper feature preparation from multiple datasets
        features = data_agent.prepare_features_from_appointments()
        if features is None:
            return jsonify({"error": "Failed to prepare features"}), 500
        X, y = features
        predictive_agent.train_model(X, y)

    prediction = predictive_agent.predict_surge(event_type, aqi)

    # Save prediction to Supabase
    try:
        prediction_date = datetime.now().date()
        supabase.table("predictions").insert({
            "id": str(uuid.uuid4()),
            "date": prediction_date.isoformat(),
            "predicted_patients": prediction.get('predicted_patients', 0),
            "aqi": aqi,
            "event_type": event_type
        }).execute()
    except Exception as e:
        print(f"Failed to save prediction to Supabase: {e}")

    return jsonify(prediction)

@prediction_bp.route('/forecast', methods=['GET'])
def forecast():
    """Predict patient inflow for next 7 days."""
    # Load and train model if needed
    if predictive_agent.model is None or not hasattr(predictive_agent.model, 'feature_importances_'):
        result = data_agent.load_all_datasets()
        if result['status'] == 'error':
            return jsonify({"error": "Failed to load data", "details": result['message']}), 500
        # For now, use appointments as proxy for patient count
        # TODO: Implement proper feature preparation from multiple datasets
        features = data_agent.prepare_features_from_appointments()
        if features is None:
            return jsonify({"error": "Failed to prepare features"}), 500
        X, y = features
        predictive_agent.train_model(X, y)

    forecasts = predictive_agent.predict_next_7_days('normal', 100)

    # Save forecasts to Supabase
    try:
        for forecast_item in forecasts:
            supabase.table("predictions").insert({
                "id": str(uuid.uuid4()),
                "date": forecast_item['date'],
                "predicted_patients": forecast_item['predicted_patients'],
                "aqi": 100,  # Default AQI for forecasts
                "event_type": "forecast"
            }).execute()
    except Exception as e:
        print(f"Failed to save forecasts to Supabase: {e}")

    return jsonify(forecasts)

@prediction_bp.route('/demand', methods=['GET'])
def predict_demand():
    """Predict demand for hospital resources."""
    dataset_type = request.args.get('dataset_type', 'general')
    demand = predictive_agent.predict_demand(dataset_type)
    return jsonify(demand)
