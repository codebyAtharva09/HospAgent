from flask import Blueprint, request, jsonify
from agents.planning_agent import PlanningAgent

planning_bp = Blueprint('planning', __name__)
planning_agent = PlanningAgent()

@planning_bp.route('/recommend-plan', methods=['POST'])
def recommend_plan():
    """Generate staffing and supply recommendations."""
    data = request.get_json()
    predicted_patients = data.get('predicted_patients', 200)

    recommendations = planning_agent.generate_recommendations(predicted_patients)
    return jsonify(recommendations)

@planning_bp.route('/recommendations', methods=['POST'])
def recommendations():
    """Generate recommendations for multiple forecasts."""
    data = request.get_json()
    forecasts = data.get('forecasts', [])

    recommendations = []
    for forecast in forecasts:
        rec = planning_agent.generate_recommendations(forecast['predicted_patients'])
        rec['date'] = forecast['date']
        rec['predicted_patients'] = forecast['predicted_patients']
        recommendations.append(rec)

    return jsonify(recommendations)

@planning_bp.route('/generate-advisory', methods=['GET'])
def generate_advisory():
    """Generate advisory messages based on current situation."""
    query = request.args.get('query', '')
    advisory = planning_agent.generate_advisory(query)
    return jsonify(advisory)
