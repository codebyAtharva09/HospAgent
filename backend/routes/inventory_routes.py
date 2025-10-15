from flask import Blueprint, request, jsonify
from agents.supply_inventory_agent import SupplyInventoryAgent
from db_config import supabase
import uuid
from datetime import datetime

inventory_bp = Blueprint('inventory', __name__)
inventory_agent = SupplyInventoryAgent()

@inventory_bp.route('/predict-consumption', methods=['POST'])
def predict_consumption():
    """Predict supply consumption based on patient forecasts."""
    data = request.get_json()
    prediction_id = data.get('prediction_id')
    patient_forecast = data.get('patient_forecast', {})
    current_inventory = data.get('current_inventory', {})

    consumption = inventory_agent.predict_consumption(patient_forecast, current_inventory)

    # Save inventory recommendations to Supabase
    try:
        supabase.table("recommendations").insert({
            "id": str(uuid.uuid4()),
            "prediction_id": prediction_id,
            "recommended_staff": 0,  # Inventory doesn't affect staff
            "supplies_needed": consumption.get('total_supplies_needed', 0)
        }).execute()
    except Exception as e:
        print(f"Failed to save inventory recommendations to Supabase: {e}")

    return jsonify({
        'status': 'success',
        'consumption': consumption,
        'recommendations': consumption.get('recommendations', [])
    })

@inventory_bp.route('/inventory-status', methods=['GET'])
def get_inventory_status():
    """Get current inventory status."""
    status = inventory_agent.get_inventory_status()

    return jsonify({
        'status': 'success',
        'inventory': status,
        'critical_items': [item for item in status if item.get('status') == 'critical']
    })

@inventory_bp.route('/reorder-alerts', methods=['GET'])
def get_reorder_alerts():
    """Get items that need reordering."""
    alerts = inventory_agent.get_reorder_alerts()

    return jsonify({
        'status': 'success',
        'alerts': alerts,
        'urgent_count': len([a for a in alerts if a.get('priority') == 'urgent'])
    })

@inventory_bp.route('/inventory-dashboard', methods=['GET'])
def get_inventory_dashboard():
    """Get inventory dashboard data."""
    status = inventory_agent.get_inventory_status()
    alerts = inventory_agent.get_reorder_alerts()

    return jsonify({
        'status': 'success',
        'current_inventory': status,
        'reorder_alerts': alerts,
        'summary': {
            'total_items': len(status),
            'critical_items': len([item for item in status if item.get('status') == 'critical']),
            'low_stock_items': len([item for item in status if item.get('status') == 'low']),
            'urgent_reorders': len([a for a in alerts if a.get('priority') == 'urgent'])
        }
    })
