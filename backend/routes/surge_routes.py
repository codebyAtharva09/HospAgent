from flask import Blueprint, request, jsonify
from agents.risk_agent import RiskAssessmentAgent
from agents.surge_forecast_agent import SurgeForecastAgent
from agents.resource_optimizer_agent import ResourceOptimizerAgent
from agents.wellbeing_agent import WellbeingAgent
from agents.simulation_agent import SimulationAgent
from agents.communication_agent import CommunicationAgent # Using existing one

surge_bp = Blueprint('surge_bp', __name__)

# Initialize Agents
risk_agent = RiskAssessmentAgent()
forecast_agent = SurgeForecastAgent()
resource_agent = ResourceOptimizerAgent()
wellbeing_agent = WellbeingAgent()
simulation_agent = SimulationAgent()
comm_agent = CommunicationAgent()

# --- Data Ingestion (Mock) ---
@surge_bp.route('/ingest/events/patient', methods=['POST'])
def ingest_patient_event():
    data = request.json
    # In real app, save to DB
    return jsonify({"status": "success", "message": "Event ingested", "id": data.get('patient_id')})

@surge_bp.route('/ingest/context/external', methods=['POST'])
def ingest_external_context():
    data = request.json
    # In real app, save to DB
    return jsonify({"status": "success", "message": "Context updated"})

# --- Risk Assessment ---
@surge_bp.route('/risk/now', methods=['GET'])
def get_risk_now():
    # Mock data fetching
    hospital_data = {"er_occupancy": 0.85, "icu_occupancy": 0.6}
    external_data = {"aqi": 320, "festival_nearby": True}
    
    risk = risk_agent.calculate_risk(hospital_data, external_data)
    return jsonify(risk)

@surge_bp.route('/risk/forecast', methods=['GET'])
def get_risk_forecast():
    days = int(request.args.get('days', 7))
    forecast = risk_agent.get_risk_forecast(days)
    return jsonify({"forecast": forecast})

# --- Surge Forecast ---
@surge_bp.route('/forecast/patients', methods=['GET'])
def get_patient_forecast():
    days = int(request.args.get('days', 7))
    # Mock context
    context = {"aqi": 320, "is_festival": True}
    forecast = forecast_agent.predict_load(days, context)
    return jsonify({"forecast": forecast})

# --- Resource Planning ---
@surge_bp.route('/plan/staffing', methods=['GET'])
def get_staffing_plan():
    # Get forecast first
    context = {"aqi": 320}
    forecast = forecast_agent.predict_load(7, context)
    plan = resource_agent.optimize_staffing(forecast)
    return jsonify({"staffing_plan": plan})

@surge_bp.route('/plan/supplies', methods=['GET'])
def get_supply_plan():
    context = {"aqi": 320}
    forecast = forecast_agent.predict_load(7, context)
    # Mock inventory
    inventory = {"oxygen_cylinders": 80, "n95_masks": 200}
    plan = resource_agent.optimize_supplies(forecast, inventory)
    return jsonify({"supply_plan": plan})

# --- Simulation ---
@surge_bp.route('/simulation/run', methods=['POST'])
def run_simulation():
    scenario = request.json
    result = simulation_agent.run_simulation(scenario)
    return jsonify(result)

# --- Wellbeing ---
@surge_bp.route('/wellbeing/burnout-risk', methods=['GET'])
def get_burnout_risk():
    # Mock staff data
    staff_roster = [{"id": "D1", "name": "Dr. A"}, {"id": "N1", "name": "Nurse B"}]
    past_shifts = {"D1": ["S1", "S2", "S3", "S4"], "N1": ["S1"]} # D1 has 4 shifts
    
    report = wellbeing_agent.analyze_burnout_risk(staff_roster, past_shifts)
    return jsonify(report)

# --- Advisory ---
@surge_bp.route('/advisory/generate', methods=['POST'])
def generate_advisory():
    # Use existing CommunicationAgent logic or enhance it
    data = request.json
    # Mock risk data for advisory
    risk_data = {
        "risks": ["pollution_high"] if data.get('aqi', 0) > 200 else [],
        "environmental_data": {"pollution": {"aqi": data.get('aqi', 100)}}
    }
    advisories = comm_agent.create_patient_advisory(risk_data)
    return jsonify({"advisories": advisories})
