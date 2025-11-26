"""
Enhanced API Routes for HospAgent
Exposes data integration, agentic coordination, and patient advisory features
"""
from flask import Blueprint, jsonify, request
from services.data_integration_service import data_integration_service
from services.agentic_coordinator import coordinator, AgentEvent, EventType
from services.patient_advisory_system import patient_advisory_system
from datetime import datetime

enhanced_bp = Blueprint('enhanced', __name__)

@enhanced_bp.route('/risk-assessment', methods=['GET'])
def get_risk_assessment():
    """
    Get comprehensive risk assessment from all data sources
    Combines AQI, weather, festivals, and epidemic data
    """
    try:
        risk_assessment = data_integration_service.get_integrated_risk_assessment()
        return jsonify({
            'status': 'success',
            'data': risk_assessment
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/aqi/current', methods=['GET'])
def get_current_aqi():
    """Get current Air Quality Index for a city"""
    city = request.args.get('city', 'Mumbai')
    
    try:
        aqi_data = data_integration_service.get_current_aqi(city)
        return jsonify({
            'status': 'success',
            'data': aqi_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/weather/forecast', methods=['GET'])
def get_weather_forecast():
    """Get weather forecast for next N days"""
    city = request.args.get('city', 'Mumbai')
    days = int(request.args.get('days', 7))
    
    try:
        forecast = data_integration_service.get_weather_forecast(city, days)
        return jsonify({
            'status': 'success',
            'data': forecast
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/festivals/upcoming', methods=['GET'])
def get_upcoming_festivals():
    """Get upcoming festivals with health impact data"""
    days_ahead = int(request.args.get('days_ahead', 30))
    
    try:
        festivals = data_integration_service.get_upcoming_festivals(days_ahead)
        return jsonify({
            'status': 'success',
            'data': festivals
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/epidemics/trends', methods=['GET'])
def get_epidemic_trends():
    """Get current epidemic and disease surveillance data"""
    try:
        trends = data_integration_service.get_epidemic_trends()
        return jsonify({
            'status': 'success',
            'data': trends
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/advisories/generate', methods=['POST'])
def generate_advisory():
    """Generate a patient advisory for a specific scenario"""
    data = request.get_json()
    scenario = data.get('scenario')
    context = data.get('context', {})
    target_audience = data.get('target_audience')
    
    try:
        advisory = patient_advisory_system.generate_advisory(
            scenario,
            context,
            target_audience
        )
        return jsonify({
            'status': 'success',
            'data': advisory
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/advisories/auto-generate', methods=['GET'])
def auto_generate_advisories():
    """
    Auto-generate advisories based on current risk assessment
    This is the main endpoint for the advisory system
    """
    try:
        # Get risk assessment
        risk_assessment = data_integration_service.get_integrated_risk_assessment()
        
        # Generate advisories
        advisories = patient_advisory_system.generate_multi_source_advisory(risk_assessment)
        
        # Simulate delivery for each advisory
        delivery_results = []
        for advisory in advisories:
            delivery = patient_advisory_system.simulate_delivery(advisory)
            delivery_results.append(delivery)
        
        return jsonify({
            'status': 'success',
            'data': {
                'advisories': advisories,
                'delivery_results': delivery_results,
                'total_advisories': len(advisories),
                'risk_level': risk_assessment['risk_level']
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/advisories/effectiveness', methods=['GET'])
def get_advisory_effectiveness():
    """Get advisory system effectiveness metrics"""
    try:
        effectiveness = patient_advisory_system.get_advisory_effectiveness()
        return jsonify({
            'status': 'success',
            'data': effectiveness
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/coordination/status', methods=['GET'])
def get_coordination_status():
    """Get agentic coordination system status"""
    try:
        status = coordinator.get_coordination_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/coordination/trigger-event', methods=['POST'])
def trigger_coordination_event():
    """
    Manually trigger a coordination event
    Useful for testing and demonstrations
    """
    data = request.get_json()
    event_type_str = data.get('event_type')
    event_data = data.get('data', {})
    priority = data.get('priority', 5)
    
    try:
        # Convert string to EventType enum
        event_type = EventType[event_type_str.upper()]
        
        # Create and publish event
        event = AgentEvent(
            event_type=event_type,
            data=event_data,
            priority=priority,
            source_agent='API'
        )
        
        response = coordinator.publish_event(event)
        
        return jsonify({
            'status': 'success',
            'data': {
                'event': event.to_dict(),
                'coordination_response': response
            }
        })
    except KeyError:
        return jsonify({
            'status': 'error',
            'message': f'Invalid event type: {event_type_str}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@enhanced_bp.route('/dashboard/enhanced', methods=['GET'])
def get_enhanced_dashboard():
    """
    Get comprehensive dashboard data with all enhanced features
    This is the main endpoint for the enhanced dashboard
    """
    try:
        # Get risk assessment
        risk_assessment = data_integration_service.get_integrated_risk_assessment()
        
        # Get auto-generated advisories
        advisories = patient_advisory_system.generate_multi_source_advisory(risk_assessment)
        
        # Get coordination status
        coordination = coordinator.get_coordination_status()
        
        # Get advisory effectiveness
        effectiveness = patient_advisory_system.get_advisory_effectiveness()
        
        return jsonify({
            'status': 'success',
            'data': {
                'risk_assessment': risk_assessment,
                'active_advisories': advisories[:5],  # Top 5
                'coordination_status': {
                    'active_agents': len(coordination['registered_agents']),
                    'recent_events': len(coordination['recent_events'])
                },
                'advisory_effectiveness': effectiveness,
                'system_health': {
                    'data_sources_active': 4,  # AQI, Weather, Festivals, Epidemics
                    'agents_coordinating': True,
                    'advisories_generated': len(advisories),
                    'last_updated': datetime.now().isoformat()
                }
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
