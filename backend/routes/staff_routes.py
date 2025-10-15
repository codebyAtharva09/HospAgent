from flask import Blueprint, request, jsonify
from agents.staff_allocation_agent import StaffAllocationAgent
from db_config import supabase
import uuid
from datetime import datetime

staff_bp = Blueprint('staff', __name__)
staff_agent = StaffAllocationAgent()

@staff_bp.route('/optimize-staffing', methods=['POST'])
def optimize_staffing():
    """Optimize staff allocation based on predictions."""
    data = request.get_json()
    prediction_id = data.get('prediction_id')
    current_staff = data.get('current_staff', {})
    predicted_demand = data.get('predicted_demand', {})

    optimization = staff_agent.optimize_staff_allocation(current_staff, predicted_demand)

    # Save staff recommendations to Supabase
    try:
        supabase.table("recommendations").insert({
            "id": str(uuid.uuid4()),
            "prediction_id": prediction_id,
            "recommended_staff": optimization.get('total_recommended', 0),
            "supplies_needed": 0  # Staff optimization doesn't affect supplies
        }).execute()
    except Exception as e:
        print(f"Failed to save staff recommendations to Supabase: {e}")

    return jsonify({
        'status': 'success',
        'optimization': optimization,
        'recommendations': optimization.get('recommendations', [])
    })

@staff_bp.route('/staff-schedule', methods=['GET'])
def get_staff_schedule():
    """Get current staff schedule and availability."""
    schedule = staff_agent.get_staff_schedule()

    return jsonify({
        'status': 'success',
        'schedule': schedule,
        'total_on_duty': sum([s.get('count', 0) for s in schedule.values()])
    })

@staff_bp.route('/shift-coverage', methods=['GET'])
def get_shift_coverage():
    """Get shift coverage analysis."""
    coverage = staff_agent.analyze_shift_coverage()

    return jsonify({
        'status': 'success',
        'coverage': coverage,
        'gaps': coverage.get('gaps', [])
    })

@staff_bp.route('/staff-dashboard', methods=['GET'])
def get_staff_dashboard():
    """Get staff dashboard data."""
    schedule = staff_agent.get_staff_schedule()
    coverage = staff_agent.analyze_shift_coverage()

    return jsonify({
        'status': 'success',
        'current_schedule': schedule,
        'shift_coverage': coverage,
        'alerts': coverage.get('alerts', [])
    })
