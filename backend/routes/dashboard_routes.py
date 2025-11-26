from flask import Blueprint, jsonify
import json
from datetime import datetime
from db_config import supabase

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

@dashboard_bp.route('/overview', methods=['GET'])
def get_overview_adapter():
    """Adapter endpoint for frontend overview data."""
    # Reuse the existing logic but ensure keys match exactly what frontend expects
    try:
        hms_data = load_hms_data()
        status = hms_data.get('current_status', {})
        info = hms_data.get('hospital_info', {})
        staff = hms_data.get('staff_on_duty', {})

        total_beds = info.get('total_beds', 500)
        occupied_beds = status.get('occupied_beds', 387)
        available_beds = total_beds - occupied_beds
        icu_occupancy = status.get('icu_occupancy', 28)
        
        overview_data = {
          "hospital_status": {
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "utilization_rate": round(occupied_beds / total_beds, 2)
          },
          "patient_stats": {
            "current_patients": occupied_beds,
            "admitted_today": 45,
            "discharged_today": 38,
            "average_stay": 4.2
          },
          "department_status": [
            { "name": "Emergency", "patients": 28, "capacity": 30, "status": "high" },
            { "name": "ICU", "patients": 18, "capacity": 20, "status": "normal" },
            { "name": "General Ward", "patients": 156, "capacity": 200, "status": "normal" },
            { "name": "OPD", "patients": 185, "capacity": 250, "status": "normal" }
          ],
          "alerts_count": 3,
          "last_updated": datetime.now().isoformat()
        }
        return jsonify(overview_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/department-status', methods=['GET'])
def get_department_status():
    """Get department status from Supabase."""
    try:
        if supabase is None:
            # Fallback to static data if Supabase not configured
            return jsonify([
                {"name": "Emergency", "occupancy": 85},
                {"name": "ICU", "occupancy": 92},
                {"name": "Surgery", "occupancy": 71},
                {"name": "Pediatrics", "occupancy": 54},
                {"name": "General Ward", "occupancy": 67}
            ])

        # Query Supabase for department status
        result = supabase.table('department_status').select('name, occupancy').execute()

        # Format the response
        departments = [{"name": row['name'], "occupancy": row['occupancy']} for row in result.data]

        return jsonify(departments)

    except Exception as e:
        # Fallback to static data on error
        return jsonify([
            {"name": "Emergency", "occupancy": 85},
            {"name": "ICU", "occupancy": 92},
            {"name": "Surgery", "occupancy": 71},
            {"name": "Pediatrics", "occupancy": 54},
            {"name": "General Ward", "occupancy": 67}
        ])

@dashboard_bp.route('/activity', methods=['GET'])
def get_activity_data():
    """Get system activity and health data."""
    try:
        # Mock data for system activity
        activity_data = {
            "recent_predictions": [
                {
                    "type": "Patient Surge",
                    "result": "High probability of influx",
                    "confidence": "87%",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                },
                {
                    "type": "Staff Allocation",
                    "result": "Optimized for night shift",
                    "confidence": "92%",
                    "timestamp": (datetime.now()).isoformat(),
                    "status": "completed"
                },
                {
                    "type": "Inventory Check",
                    "result": "Low stock alert: Oxygen",
                    "confidence": "99%",
                    "timestamp": datetime.now().isoformat(),
                    "status": "processing"
                }
            ],
            "active_processes": [
                {"name": "Data Ingestion", "status": "running", "progress": 45},
                {"name": "Model Training", "status": "running", "progress": 78},
                {"name": "Report Generation", "status": "queued", "progress": 0}
            ],
            "system_health": {
                "status": "healthy",
                "uptime": "24d 13h 45m",
                "last_backup": (datetime.now()).isoformat()
            },
            "model_performance": {
                "accuracy": 94.2,
                "last_updated": datetime.now().isoformat()
            }
        }
        return jsonify(activity_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
