from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
from routes.data_routes import data_bp
from routes.prediction_routes import prediction_bp
from routes.planning_routes import planning_bp
from routes.recommend_routes import recommend_bp
from routes.staff_routes import staff_bp
from routes.inventory_routes import inventory_bp
from routes.advisory_routes import advisory_bp
from routes.hms_routes import hms_bp
from routes.dashboard_routes import dashboard_bp
from routes.agent_routes import agent_bp
from routes.enhanced_routes import enhanced_bp

from agents.data_agent import DataAgent
from agents.predictive_agent import PredictiveAgent
from agents.planning_agent import PlanningAgent
from agents.staff_allocation_agent import StaffAllocationAgent
from agents.supply_inventory_agent import SupplyInventoryAgent
from agents.patient_advisory_agent import PatientAdvisoryAgent
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Register blueprints
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(prediction_bp, url_prefix='/api')
app.register_blueprint(planning_bp, url_prefix='/api')
app.register_blueprint(recommend_bp, url_prefix='/api')
app.register_blueprint(staff_bp, url_prefix='/api')
app.register_blueprint(inventory_bp, url_prefix='/api')
app.register_blueprint(advisory_bp, url_prefix='/api')
app.register_blueprint(hms_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(agent_bp, url_prefix='/api/agents')
app.register_blueprint(enhanced_bp, url_prefix='/api/enhanced')

from routes.surge_routes import surge_bp
app.register_blueprint(surge_bp, url_prefix='/api')

# Initialize agents
data_agent = DataAgent()
predictive_agent = PredictiveAgent()
planning_agent = PlanningAgent()

@app.route('/api')
def home():
    """Home endpoint with API information."""
    return {
        "message": "HospAgent Backend API",
        "version": "2.0",
        "endpoints": {
            "upload-data": "POST /api/upload-data",
            "analyze-trends": "GET /api/analyze-trends",
            "predict-surge": "POST /api/predict-surge",
            "recommend-plan": "POST /api/recommend-plan",
            "recommendations": "POST /api/recommendations",
            "generate-advisory": "POST /api/generate-advisory",

            "optimize-staffing": "POST /api/optimize-staffing",
            "staff-schedule": "GET /api/staff-schedule",
            "predict-consumption": "POST /api/predict-consumption",
            "inventory-status": "GET /api/inventory-status",
            "assess-risks": "GET /api/assess-risks",
            "hospital-status": "GET /api/hospital-status",
            "bed-occupancy": "GET /api/bed-occupancy"
        }
    }

# Sample data pipeline demonstrating agent communication
@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """Run the complete agent pipeline for a given event type."""
    data = request.get_json()
    event_type = data.get('event_type', 'festival')
    aqi = data.get('aqi', 150)

    # Step 1: Data Agent loads and analyzes data
    data_result = data_agent.load_data('data/hospital_data.csv')
    if data_result['status'] == 'error':
        return data_result, 500

    trends = data_agent.analyze_trends()

    # Step 2: Predictive Agent makes prediction
    prediction = predictive_agent.predict_surge(event_type, aqi)

    # Step 3: Planning Agent generates recommendations
    recommendations = planning_agent.generate_recommendations(prediction['predicted_patients'])

    # Return combined results
    return {
        "data_insights": trends,
        "prediction": prediction,
        "recommendations": recommendations,
        "pipeline_status": "completed"
    }

# New endpoints for real-time dashboard integration
@app.route('/api/patient-forecast', methods=['GET'])
def patient_forecast():
    """Returns daily/weekly patient inflow predictions."""
    try:
        # Get forecast data from predictive agent
        forecasts = predictive_agent.predict_next_7_days('normal', 100)

        # Format for frontend consumption
        forecast_data = {
            "daily": [
                {
                    "date": item['date'],
                    "predicted_inflow": item['predicted_patients'],
                    "confidence": round(random.uniform(0.85, 0.95), 2),
                    "trend": "increasing" if random.random() > 0.5 else "stable"
                } for item in forecasts
            ],
            "weekly": {
                "total_predicted": sum(item['predicted_patients'] for item in forecasts),
                "average_daily": round(sum(item['predicted_patients'] for item in forecasts) / len(forecasts), 1),
                "peak_day": max(forecasts, key=lambda x: x['predicted_patients'])['date'],
                "confidence_score": round(random.uniform(0.88, 0.96), 2)
            }
        }
        return jsonify(forecast_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/resource-status', methods=['GET'])
def resource_status():
    """Returns bed, oxygen, staff availability."""
    try:
        # Simulate real-time resource status
        status = {
            "beds": {
                "total": random.randint(400, 600),
                "occupied": random.randint(320, 480),
                "available": random.randint(80, 120),
                "utilization_rate": round(random.uniform(0.75, 0.85), 2),
                "icu_available": random.randint(15, 25)
            },
            "oxygen": {
                "cylinders_available": random.randint(80, 150),
                "critical_threshold": 50,
                "status": "adequate" if random.random() > 0.3 else "low",
                "consumption_rate": round(random.uniform(20, 40), 1)
            },
            "staff": {
                "doctors_on_duty": random.randint(45, 65),
                "nurses_on_duty": random.randint(120, 150),
                "absent_percent": round(random.uniform(5, 15), 1),
                "shift_coverage": round(random.uniform(0.85, 0.95), 2)
            },
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def alerts():
    """Returns communication or emergency advisories."""
    try:
        # Generate dynamic alerts based on simulated conditions
        alerts_list = []

        # Check for high patient volume
        if random.random() > 0.6:
            alerts_list.append({
                "id": f"alert_{random.randint(1000, 9999)}",
                "type": "Patient Surge",
                "priority": "high",
                "title": "High Patient Volume Alert",
                "message": "Emergency Department experiencing increased patient inflow. Wait times may be longer than usual.",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 30))).strftime('%Y-%m-%d %H:%M:%S'),
                "affected_departments": ["Emergency", "OPD"],
                "channel": "Dashboard"
            })

        # Check for staff shortages
        if random.random() > 0.7:
            alerts_list.append({
                "id": f"alert_{random.randint(1000, 9999)}",
                "type": "Staff Shortage",
                "priority": "medium",
                "title": "Staffing Alert",
                "message": "Reduced staffing levels detected. Some services may have limited availability.",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(10, 45))).strftime('%Y-%m-%d %H:%M:%S'),
                "affected_departments": ["General Ward", "ICU"],
                "channel": "SMS"
            })

        # Environmental alerts
        if random.random() > 0.8:
            alerts_list.append({
                "id": f"alert_{random.randint(1000, 9999)}",
                "type": "Weather Warning",
                "priority": "low",
                "title": "Air Quality Advisory",
                "message": "Poor air quality detected. Respiratory patients advised to take precautions.",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 3))).strftime('%Y-%m-%d %H:%M:%S'),
                "affected_departments": ["Pulmonology", "Emergency"],
                "channel": "Public Announcement"
            })

        # Always include at least one advisory
        if not alerts_list:
            alerts_list.append({
                "id": f"alert_{random.randint(1000, 9999)}",
                "type": "General Advisory",
                "priority": "low",
                "title": "Hospital Operations Normal",
                "message": "All hospital services operating within normal parameters.",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "affected_departments": [],
                "channel": "Dashboard"
            })

        return jsonify({
            "alerts": alerts_list,
            "total_count": len(alerts_list),
            "critical_count": len([a for a in alerts_list if a['priority'] == 'high'])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/learning-update', methods=['GET'])
def learning_update():
    """Shows model improvement or retraining progress."""
    try:
        # Simulate learning agent updates
        update_data = {
            "model_status": {
                "current_version": f"v{random.randint(3, 5)}.{random.randint(0, 9)}",
                "last_trained": (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S'),
                "training_status": "completed" if random.random() > 0.1 else "in_progress",
                "accuracy_score": round(random.uniform(0.85, 0.95), 3)
            },
            "performance_metrics": {
                "prediction_accuracy": round(random.uniform(0.88, 0.96), 2),
                "false_positive_rate": round(random.uniform(0.02, 0.08), 2),
                "model_confidence": round(random.uniform(0.82, 0.94), 2),
                "data_drift_detected": random.choice([True, False])
            },
            "recent_improvements": [
                {
                    "type": "accuracy_improvement",
                    "description": "Improved prediction accuracy by 2.3%",
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(2, 12))).strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    "type": "feature_added",
                    "description": "Added weather correlation features",
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d %H:%M:%S')
                }
            ] if random.random() > 0.5 else [],
            "next_retraining": (datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M:%S'),
            "data_quality_score": round(random.uniform(0.85, 0.98), 2)
        }
        return jsonify(update_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('../frontend/build', path)):
        return send_from_directory('../frontend/build', path)
    else:
        return send_from_directory('../frontend/build', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
