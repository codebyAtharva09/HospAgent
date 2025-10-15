from flask import Blueprint, request, jsonify
from agents.patient_advisory_agent import PatientAdvisoryAgent
from services.external_api_service import ExternalAPIService
from db_config import supabase
import uuid

advisory_bp = Blueprint('advisory', __name__)
advisory_agent = PatientAdvisoryAgent()
external_api = ExternalAPIService()

@advisory_bp.route('/assess-risks', methods=['GET'])
def assess_health_risks():
    """Assess current health risks based on environmental data."""
    # Get current environmental data
    env_data = external_api.get_combined_environmental_data()

    aqi = env_data['pollution']['aqi']
    temperature = env_data['weather']['temperature']
    humidity = env_data['weather']['humidity']
    epidemic_data = env_data['epidemic']
    festival_data = {'crowd_expected': len(env_data['festivals']) > 0}

    risks = advisory_agent.assess_health_risks(aqi, temperature, humidity, epidemic_data, festival_data)

    return jsonify({
        'status': 'success',
        'risks': risks,
        'environmental_data': env_data
    })

@advisory_bp.route('/generate-advisory', methods=['POST'])
def generate_advisory():
    """Generate advisories based on identified risks."""
    data = request.get_json()
    risks = data.get('risks', [])
    patient_demographics = data.get('patient_demographics', [])
    prediction_id = data.get('prediction_id')

    advisories = advisory_agent.generate_advisory(risks, patient_demographics)
    announcements = advisory_agent.create_public_announcement(advisories)

    # Save advisories to Supabase
    try:
        for advisory in advisories:
            supabase.table("advisories").insert({
                "id": str(uuid.uuid4()),
                "prediction_id": prediction_id,
                "advisory_text": advisory.get('message', advisory.get('content', 'Advisory generated'))
            }).execute()
    except Exception as e:
        print(f"Failed to save advisories to Supabase: {e}")

    return jsonify({
        'status': 'success',
        'advisories': advisories,
        'public_announcements': announcements
    })

@advisory_bp.route('/predict-advisory-needs', methods=['POST'])
def predict_advisory_needs():
    """Predict when advisories will be needed."""
    data = request.get_json()
    forecast_data = data.get('forecast_data', [])

    predictions = advisory_agent.predict_advisory_needs(forecast_data, {})

    return jsonify({
        'status': 'success',
        'predictions': predictions,
        'upcoming_alerts': len([p for p in predictions if p['confidence'] > 0.8])
    })

@advisory_bp.route('/advisory-history', methods=['GET'])
def get_advisory_history():
    """Get historical advisory data."""
    days = int(request.args.get('days', 30))
    history = advisory_agent.get_advisory_history(days)

    return jsonify({
        'status': 'success',
        'history': history
    })

@advisory_bp.route('/advisory-analytics', methods=['GET'])
def get_advisory_analytics():
    """Get advisory effectiveness analytics."""
    days = int(request.args.get('days', 30))
    history = advisory_agent.get_advisory_history(days)
    analytics = advisory_agent.analyze_advisory_effectiveness(history)

    return jsonify({
        'status': 'success',
        'analytics': analytics,
        'period_days': days
    })

@advisory_bp.route('/publish-advisory', methods=['POST'])
def publish_advisory():
    """Publish advisory through various channels."""
    data = request.get_json()
    advisory_id = data.get('advisory_id')
    channels = data.get('channels', ['hospital_website'])

    # Mock publishing - in real implementation, integrate with email/SMS services
    published_channels = []
    for channel in channels:
        if channel in ['hospital_website', 'sms', 'email', 'public_display']:
            published_channels.append(channel)

    return jsonify({
        'status': 'success',
        'advisory_id': advisory_id,
        'published_channels': published_channels,
        'timestamp': '2024-01-15T10:30:00Z'
    })

@advisory_bp.route('/advisory-dashboard', methods=['GET'])
def get_advisory_dashboard():
    """Get advisory dashboard data."""
    # Get current risks
    env_data = external_api.get_combined_environmental_data()
    risks = advisory_agent.assess_health_risks(
        env_data['pollution']['aqi'],
        env_data['weather']['temperature'],
        env_data['weather']['humidity'],
        env_data['epidemic'],
        {'crowd_expected': len(env_data['festivals']) > 0}
    )

    # Get recent history
    history = advisory_agent.get_advisory_history(7)
    analytics = advisory_agent.analyze_advisory_effectiveness(history)

    # Get upcoming festivals
    upcoming_festivals = env_data['festivals']

    return jsonify({
        'status': 'success',
        'current_risks': risks,
        'active_advisories': len(risks),
        'upcoming_festivals': upcoming_festivals,
        'analytics': analytics,
        'environmental_summary': {
            'aqi': env_data['pollution']['aqi'],
            'temperature': env_data['weather']['temperature'],
            'festivals_next_week': len([f for f in upcoming_festivals if f['days_until'] <= 7])
        }
    })
