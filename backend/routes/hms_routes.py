from flask import Blueprint, request, jsonify
import json
from datetime import datetime

hms_bp = Blueprint('hms', __name__)

# Mock HMS data - in real implementation, this would connect to actual HMS database
def load_hms_data():
    try:
        with open('data/hms_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_hms_data(data):
    with open('data/hms_data.json', 'w') as f:
        json.dump(data, f, indent=2)

@hms_bp.route('/hospital-status', methods=['GET'])
def get_hospital_status():
    """Get current hospital status."""
    hms_data = load_hms_data()
    return jsonify({
        'status': 'success',
        'data': hms_data.get('current_status', {}),
        'hospital_info': hms_data.get('hospital_info', {})
    })

@hms_bp.route('/bed-occupancy', methods=['GET'])
def get_bed_occupancy():
    """Get bed occupancy information."""
    hms_data = load_hms_data()
    status = hms_data.get('current_status', {})

    occupancy_rate = (status.get('occupied_beds', 0) / hms_data.get('hospital_info', {}).get('total_beds', 500)) * 100

    return jsonify({
        'status': 'success',
        'occupied_beds': status.get('occupied_beds', 0),
        'available_beds': status.get('available_beds', 0),
        'total_beds': hms_data.get('hospital_info', {}).get('total_beds', 500),
        'occupancy_rate': round(occupancy_rate, 1),
        'icu_occupancy': status.get('icu_occupancy', 0),
        'er_waiting': status.get('er_waiting', 0)
    })

@hms_bp.route('/appointments', methods=['GET'])
def get_appointments():
    """Get today's appointments by department."""
    hms_data = load_hms_data()
    appointments = hms_data.get('appointments_today', [])

    total_appointments = sum(apt['count'] for apt in appointments)

    return jsonify({
        'status': 'success',
        'appointments': appointments,
        'total_appointments': total_appointments,
        'date': datetime.now().strftime('%Y-%m-%d')
    })

@hms_bp.route('/staff-on-duty', methods=['GET'])
def get_staff_on_duty():
    """Get current staff on duty."""
    hms_data = load_hms_data()
    staff = hms_data.get('staff_on_duty', {})

    return jsonify({
        'status': 'success',
        'staff': staff,
        'total_staff': sum(staff.values())
    })

@hms_bp.route('/patient-demographics', methods=['GET'])
def get_patient_demographics():
    """Get patient demographics and trends."""
    hms_data = load_hms_data()
    demographics = hms_data.get('patient_demographics', {})

    return jsonify({
        'status': 'success',
        'demographics': demographics
    })

@hms_bp.route('/update-bed-occupancy', methods=['POST'])
def update_bed_occupancy():
    """Update bed occupancy (for real-time updates)."""
    data = request.get_json()
    occupied_beds = data.get('occupied_beds')
    icu_occupancy = data.get('icu_occupancy')
    er_waiting = data.get('er_waiting')

    hms_data = load_hms_data()
    if 'current_status' not in hms_data:
        hms_data['current_status'] = {}

    total_beds = hms_data.get('hospital_info', {}).get('total_beds', 500)

    if occupied_beds is not None:
        hms_data['current_status']['occupied_beds'] = occupied_beds
        hms_data['current_status']['available_beds'] = total_beds - occupied_beds

    if icu_occupancy is not None:
        hms_data['current_status']['icu_occupancy'] = icu_occupancy

    if er_waiting is not None:
        hms_data['current_status']['er_waiting'] = er_waiting

    hms_data['current_status']['last_updated'] = datetime.now().isoformat()

    save_hms_data(hms_data)

    return jsonify({
        'status': 'success',
        'message': 'Bed occupancy updated',
        'updated_data': hms_data['current_status']
    })

@hms_bp.route('/hms-dashboard', methods=['GET'])
def get_hms_dashboard():
    """Get comprehensive HMS dashboard data."""
    hms_data = load_hms_data()

    # Calculate key metrics
    status = hms_data.get('current_status', {})
    info = hms_data.get('hospital_info', {})
    appointments = hms_data.get('appointments_today', [])
    staff = hms_data.get('staff_on_duty', {})

    total_beds = info.get('total_beds', 500)
    occupied_beds = status.get('occupied_beds', 0)
    occupancy_rate = (occupied_beds / total_beds) * 100 if total_beds > 0 else 0

    total_appointments = sum(apt['count'] for apt in appointments)
    total_staff = sum(staff.values())

    # Department load analysis
    dept_load = {}
    for apt in appointments:
        dept = apt['department']
        count = apt['count']
        # Estimate bed requirements based on appointments
        estimated_load = count * 0.3  # Rough estimate: 30% of appointments need admission
        dept_load[dept] = {
            'appointments': count,
            'estimated_bed_needs': int(estimated_load)
        }

    return jsonify({
        'status': 'success',
        'summary': {
            'occupancy_rate': round(occupancy_rate, 1),
            'total_appointments': total_appointments,
            'total_staff': total_staff,
            'available_beds': status.get('available_beds', 0),
            'er_waiting': status.get('er_waiting', 0)
        },
        'departments': dept_load,
        'hospital_info': info,
        'last_updated': status.get('last_updated', datetime.now().isoformat())
    })
