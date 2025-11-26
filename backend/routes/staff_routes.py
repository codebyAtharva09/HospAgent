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

@staff_bp.route('/staff', methods=['GET'])
def get_staff_adapter():
    """Adapter endpoint for frontend staff data."""
    # Get real data from agent
    schedule = staff_agent.get_staff_schedule()
    
    # Calculate totals
    # Calculate totals
    doctors_on_duty = 0
    nurses_on_duty = 0
    
    for dept_data in schedule.values():
        doctors_on_duty += len(dept_data.get('doctors', []))
        nurses_on_duty += len(dept_data.get('nurses', []))
        
    techs_on_duty = 0 # Technicians not currently tracked in agent
    
    # Mock some data that isn't fully implemented in agent yet to satisfy frontend
    staff_data = {
      "doctors": {
        "total": 85,
        "on_duty": doctors_on_duty if doctors_on_duty > 0 else 62,
        "available": 23,
        "recommended": 68
      },
      "nurses": {
        "total": 150,
        "on_duty": nurses_on_duty if nurses_on_duty > 0 else 125,
        "available": 25,
        "recommended": 135
      },
      "technicians": {
        "total": 45,
        "on_duty": techs_on_duty if techs_on_duty > 0 else 38,
        "available": 7,
        "recommended": 42
      },
      "allocation": [
        { "department": "Emergency", "doctors": 12, "nurses": 25, "technicians": 8 },
        { "department": "ICU", "doctors": 8, "nurses": 18, "technicians": 6 },
        { "department": "General Ward", "doctors": 15, "nurses": 35, "technicians": 10 },
        { "department": "OPD", "doctors": 18, "nurses": 30, "technicians": 12 },
        { "department": "Surgery", "doctors": 15, "nurses": 27, "technicians": 6 }
      ]
    }
    return jsonify(staff_data)
