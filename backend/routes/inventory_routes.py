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

@inventory_bp.route('/inventory', methods=['GET'])
def get_inventory_adapter():
    """Adapter endpoint for frontend inventory data."""
    # Get real data from agent
    status = inventory_agent.get_inventory_status()
    alerts = inventory_agent.get_reorder_alerts()
    
    # Transform to frontend format
    # If agent returns list, we need to map it to the object structure expected
    
    # Mock structure populated with real data where possible
    inventory_data = {
      "oxygen": {
        "current_stock": 120,
        "daily_consumption": 35,
        "reorder_point": 80,
        "status": "adequate",
        "supplier": "Medical Gases Ltd"
      },
      "masks": {
        "current_stock": 2500,
        "daily_consumption": 180,
        "reorder_point": 1000,
        "status": "adequate",
        "supplier": "Health Supplies Co"
      },
      "gloves": {
        "current_stock": 800,
        "daily_consumption": 120,
        "reorder_point": 500,
        "status": "low",
        "supplier": "MediEquip"
      },
      "syringes": {
        "current_stock": 1500,
        "daily_consumption": 95,
        "reorder_point": 800,
        "status": "adequate",
        "supplier": "PharmaCorp"
      },
      "medications": {
        "current_stock": 95,
        "daily_consumption": 25,
        "reorder_point": 60,
        "status": "adequate",
        "supplier": "MediPharm"
      },
      "alerts": [
        {
          "item": a.get('supply', 'Unknown'),
          "message": a.get('reason', 'Stock alert'),
          "priority": a.get('urgency', 'medium'),
          "action_required": "Reorder"
        } for a in alerts
      ]
    }
    
    # Try to update with real values if available in status
    if isinstance(status, dict):
        for name, item in status.items():
            # Map agent supply names to frontend keys if needed, or just use them
            # For now, we'll try to match keys
            if name in inventory_data:
                inventory_data[name]['current_stock'] = item.get('current_stock', inventory_data[name]['current_stock'])
                inventory_data[name]['status'] = item.get('stock_level', inventory_data[name]['status'])
                
    return jsonify(inventory_data)
