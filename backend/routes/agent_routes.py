from flask import Blueprint, request, jsonify
from agents.perception_agent import PerceptionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.planning_agent import PlanningAgent
from agents.communication_agent import CommunicationAgent
from agents.learning_agent import LearningAgent
from datetime import datetime

agent_bp = Blueprint('agents', __name__)

# Initialize agents
perception_agent = PerceptionAgent()
reasoning_agent = ReasoningAgent()
planning_agent = PlanningAgent()
communication_agent = CommunicationAgent()
learning_agent = LearningAgent()

@agent_bp.route('/perception/collect', methods=['POST'])
def collect_data():
    """Trigger data collection cycle"""
    try:
        data = perception_agent.run_collection_cycle()
        return jsonify({
            'status': 'success',
            'message': 'Data collection completed',
            'data_points': len(data),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/perception/latest', methods=['GET'])
def get_latest_data():
    """Get latest collected data"""
    source = request.args.get('source')
    data = perception_agent.get_latest_data(source)
    if data:
        return jsonify({'status': 'success', 'data': data})
    return jsonify({'status': 'error', 'message': 'No data found'}), 404

@agent_bp.route('/reasoning/analyze', methods=['POST'])
def run_reasoning():
    """Run reasoning analysis on collected data"""
    try:
        # Get latest data from perception agent
        his_data = perception_agent.get_latest_data('his')
        aqi_data = perception_agent.get_latest_data('aqi')
        festival_data = perception_agent.get_latest_data('festivals')

        if not all([his_data, aqi_data, festival_data]):
            return jsonify({'status': 'error', 'message': 'Insufficient data for analysis'}), 400

        data_bundle = {
            'his': his_data.get('data', {}),
            'aqi': aqi_data.get('data', {}),
            'festivals': festival_data.get('data', {})
        }

        insights = reasoning_agent.generate_insights(data_bundle)

        return jsonify({
            'status': 'success',
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/planning/optimize', methods=['POST'])
def run_planning():
    """Generate operational plans based on reasoning insights"""
    try:
        # Get reasoning insights (assuming they're passed or we run reasoning first)
        data = request.get_json()
        insights = data.get('insights')

        if not insights:
            return jsonify({'status': 'error', 'message': 'No insights provided'}), 400

        master_plan = planning_agent.optimize_overall_plan(insights)

        return jsonify({
            'status': 'success',
            'plan': master_plan,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/communication/notify', methods=['POST'])
def send_notifications():
    """Send notifications based on plans"""
    try:
        data = request.get_json()
        plan = data.get('plan')

        if not plan:
            return jsonify({'status': 'error', 'message': 'No plan provided'}), 400

        # Generate tasks from plan
        tasks = planning_agent.dispatch_tasks(plan)

        # Send notifications
        results = []
        for task in tasks:
            result = communication_agent.send_notification(task)
            results.append(result)

        return jsonify({
            'status': 'success',
            'notifications_sent': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/communication/advisory', methods=['POST'])
def send_advisory():
    """Send patient advisories"""
    try:
        data = request.get_json()
        risk_data = data.get('risk_data')

        if not risk_data:
            return jsonify({'status': 'error', 'message': 'No risk data provided'}), 400

        advisories = communication_agent.create_patient_advisory(risk_data)

        return jsonify({
            'status': 'success',
            'advisories_sent': len(advisories),
            'advisories': advisories,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/learning/evaluate', methods=['POST'])
def evaluate_performance():
    """Evaluate prediction performance"""
    try:
        data = request.get_json()
        predictions = data.get('predictions')
        actuals = data.get('actuals')

        if not predictions or not actuals:
            return jsonify({'status': 'error', 'message': 'Predictions and actuals required'}), 400

        # Collect feedback
        learning_agent.collect_feedback(predictions, actuals)

        # Evaluate performance
        evaluation = learning_agent.evaluate_predictions(predictions, actuals)

        # Update performance history
        learning_agent.update_performance_history(evaluation)

        return jsonify({
            'status': 'success',
            'evaluation': evaluation,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/learning/retrain', methods=['POST'])
def retrain_model():
    """Retrain ML model"""
    try:
        result = learning_agent.retrain_model()

        return jsonify({
            'status': 'success',
            'retraining_result': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/learning/insights', methods=['GET'])
def get_learning_insights():
    """Get learning insights"""
    try:
        insights = learning_agent.get_learning_insights()

        return jsonify({
            'status': 'success',
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@agent_bp.route('/pipeline/run', methods=['POST'])
def run_full_pipeline():
    """Run the complete agent pipeline"""
    try:
        pipeline_steps = []

        # Step 1: Data Collection
        perception_data = perception_agent.run_collection_cycle()
        pipeline_steps.append({
            'step': 'perception',
            'status': 'completed',
            'data_points': len(perception_data)
        })

        # Step 2: Reasoning/Analysis
        his_data = perception_agent.get_latest_data('his')
        aqi_data = perception_agent.get_latest_data('aqi')
        festival_data = perception_agent.get_latest_data('festivals')

        data_bundle = {
            'his': his_data.get('data', {}),
            'aqi': aqi_data.get('data', {}),
            'festivals': festival_data.get('data', {})
        }

        insights = reasoning_agent.generate_insights(data_bundle)
        pipeline_steps.append({
            'step': 'reasoning',
            'status': 'completed',
            'forecasts': len(insights.get('patient_forecasts', []))
        })

        # Step 3: Planning
        master_plan = planning_agent.optimize_overall_plan(insights)
        pipeline_steps.append({
            'step': 'planning',
            'status': 'completed',
            'risks_identified': len(master_plan.get('risk_assessment', []))
        })

        # Step 4: Communication
        tasks = planning_agent.dispatch_tasks(master_plan)
        notification_results = []
        for task in tasks:
            result = communication_agent.send_notification(task)
            notification_results.append(result)

        pipeline_steps.append({
            'step': 'communication',
            'status': 'completed',
            'notifications_sent': len(notification_results)
        })

        # Step 5: Learning (evaluation)
        learning_insights = learning_agent.get_learning_insights()
        pipeline_steps.append({
            'step': 'learning',
            'status': 'completed',
            'model_versions': len(learning_insights.get('model_versions', []))
        })

        return jsonify({
            'status': 'success',
            'pipeline_status': 'completed',
            'steps': pipeline_steps,
            'results': {
                'insights': insights,
                'plan': master_plan,
                'notifications': notification_results,
                'learning_insights': learning_insights
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'pipeline_status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@agent_bp.route('/status', methods=['GET'])
def get_agent_status():
    """Get status of all agents"""
    try:
        status = {
            'perception': {
                'active': True,
                'last_collection': perception_agent.get_latest_data() is not None,
                'data_sources': ['his', 'aqi', 'festivals']
            },
            'reasoning': {
                'active': True,
                'model_loaded': reasoning_agent.model is not None,
                'last_analysis': datetime.now().isoformat()
            },
            'planning': {
                'active': True,
                'optimization_ready': True,
                'last_plan': datetime.now().isoformat()
            },
            'communication': {
                'active': True,
                'channels': ['email', 'sms', 'api', 'websocket'],
                'last_notification': datetime.now().isoformat()
            },
            'learning': {
                'active': True,
                'model_versions': len(learning_agent.model_versions),
                'feedback_entries': len(learning_agent.feedback_data),
                'last_evaluation': datetime.now().isoformat()
            }
        }

        return jsonify({
            'status': 'success',
            'agents': status,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500
