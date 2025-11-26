import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.risk_agent import RiskAssessmentAgent
from agents.surge_forecast_agent import SurgeForecastAgent
from agents.resource_optimizer_agent import ResourceOptimizerAgent
from agents.wellbeing_agent import WellbeingAgent
from agents.simulation_agent import SimulationAgent

def test_risk_agent():
    print("\n--- Testing Risk Agent ---")
    agent = RiskAssessmentAgent()
    risk = agent.calculate_risk(
        hospital_data={"er_occupancy": 0.95, "icu_occupancy": 0.5},
        external_data={"aqi": 350, "festival_nearby": True}
    )
    print("Risk Score:", risk['hospital_risk_index'])
    print("Level:", risk['level'])
    print("Factors:", risk['contributing_factors'])
    assert risk['hospital_risk_index'] > 70

def test_forecast_agent():
    print("\n--- Testing Forecast Agent ---")
    agent = SurgeForecastAgent()
    forecast = agent.predict_load(days=3, current_context={"aqi": 300, "is_festival": True})
    print("Day 1 Prediction:", forecast[0]['predicted_total'])
    print("Breakdown:", forecast[0]['breakdown'])
    assert forecast[0]['predicted_total'] > 150 # Base is 150, factors should increase it

def test_resource_agent():
    print("\n--- Testing Resource Agent ---")
    f_agent = SurgeForecastAgent()
    r_agent = ResourceOptimizerAgent()
    forecast = f_agent.predict_load(days=1, current_context={"aqi": 300})
    
    staffing = r_agent.optimize_staffing(forecast)
    print("Staffing Summary:", staffing[0]['summary'])
    
    supplies = r_agent.optimize_supplies(forecast, {"oxygen_cylinders": 10})
    print("Supply Alerts:", supplies[0]['alerts'])
    assert len(supplies[0]['alerts']) > 0 # Should have oxygen shortage

def test_simulation_agent():
    print("\n--- Testing Simulation Agent ---")
    agent = SimulationAgent()
    result = agent.run_simulation({
        "name": "Test Scenario",
        "modifications": {"aqi": 500},
        "duration_days": 3
    })
    print("Scenario Impact:", result['summary'])
    assert result['summary']['total_patients_predicted'] > 0

if __name__ == "__main__":
    test_risk_agent()
    test_forecast_agent()
    test_resource_agent()
    test_simulation_agent()
    print("\nAll Tests Passed!")
