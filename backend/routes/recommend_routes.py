from flask import Blueprint, request, jsonify
from agents.planning_agent import PlanningAgent
from db_config import supabase
import uuid

recommend_bp = Blueprint('recommend', __name__)
planning_agent = PlanningAgent()

@recommend_bp.route('/recommend-plan', methods=['POST'])
def recommend_plan():
    """Generate recommendations for hospital resources."""
    data = request.get_json()
    prediction_id = data.get('prediction_id')
    predicted_patients = data.get('predicted_patients', 0)
    aqi = data.get('aqi', 100)

    # Generate recommendations using planning agent
    recommendations = planning_agent.generate_recommendations(predicted_patients)

    # Save to Supabase
    try:
        supabase.table("recommendations").insert({
            "id": str(uuid.uuid4()),
            "prediction_id": prediction_id,
            "recommended_staff": recommendations.get('staff', 0),
            "supplies_needed": recommendations.get('supplies', 0)
        }).execute()
    except Exception as e:
        print(f"Failed to save recommendations to Supabase: {e}")

    return jsonify(recommendations)

@recommend_bp.route('/optimize-staffing', methods=['POST'])
def optimize_staffing():
    """Optimize staffing based on predictions."""
    data = request.get_json()
    predictions = data.get('predictions', [])
    current_staff = data.get('current_staff', {})

    staffing_plan = planning_agent.create_staffing_plan(predictions, current_staff)

    # Save staffing recommendations to Supabase
    try:
        for day_plan in staffing_plan:
            supabase.table("recommendations").insert({
                "id": str(uuid.uuid4()),
                "prediction_id": day_plan.get('prediction_id'),
                "recommended_staff": day_plan.get('extra_doctors', 0) + day_plan.get('extra_nurses', 0),
                "supplies_needed": 0  # Staff optimization doesn't affect supplies directly
            }).execute()
    except Exception as e:
        print(f"Failed to save staffing plan to Supabase: {e}")

    return jsonify({"staffing_plan": staffing_plan})

@recommend_bp.route('/predict-consumption', methods=['POST'])
def predict_consumption():
    """Predict resource consumption."""
    data = request.get_json()
    predictions = data.get('predictions', [])

    consumption_plan = planning_agent.create_supply_plan(predictions)

    # Save supply recommendations to Supabase
    try:
        for day_plan in consumption_plan:
            total_supplies = sum(day_plan.get('procurement', {}).values())
            supabase.table("recommendations").insert({
                "id": str(uuid.uuid4()),
                "prediction_id": day_plan.get('prediction_id'),
                "recommended_staff": 0,  # Supply planning doesn't affect staff
                "supplies_needed": total_supplies
            }).execute()
    except Exception as e:
        print(f"Failed to save consumption plan to Supabase: {e}")

    return jsonify({"consumption_plan": consumption_plan})
