from flask import Blueprint, jsonify
import json
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

def load_hms_data():
    try:
        with open('data/hms_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data from HMS data."""
    try:
        hms_data = load_hms_data()
        status = hms_data.get('current_status', {})
        info = hms_data.get('hospital_info', {})
        staff = hms_data.get('staff_on_duty', {})

        # Calculate metrics
        total_beds = info.get('total_beds', 500)
        occupied_beds = status.get('occupied_beds', 387)
        available_beds = total_beds - occupied_beds
        icu_occupancy = status.get('icu_occupancy', 28)
        total_staff = sum(staff.values()) if staff else 142

        # Department status (mock data for now - can be enhanced with real data)
        department_status = {
            "Emergency": 85,
            "General Ward": 67,
            "ICU": 92,
            "Pediatrics": 54,
            "Surgery": 71,
        }

        # Calculate ICU percentage
        icu_percentage = f"{round((icu_occupancy / 30) * 100, 1)}%" if icu_occupancy else "93.3%"

        dashboard_data = {
            "total_patients": occupied_beds,  # Using occupied beds as proxy for patients
            "available_beds": available_beds,
            "icu_occupancy": icu_percentage,
            "staff_on_duty": total_staff,
            "department_status": department_status,
            "last_updated": datetime.now().isoformat()
        }

        return jsonify(dashboard_data)

    except Exception as e:
        # Fallback to static data if everything fails
        return jsonify({
            "total_patients": 487,
            "available_beds": 63,
            "icu_occupancy": "89%",
            "staff_on_duty": 142,
            "department_status": {
                "Emergency": 85,
                "General Ward": 67,
                "ICU": 92,
                "Pediatrics": 54,
                "Surgery": 71,
            },
            "error": f"Data loading failed: {str(e)}",
            "last_updated": datetime.now().isoformat()
        })
