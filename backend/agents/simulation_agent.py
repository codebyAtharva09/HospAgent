from .surge_forecast_agent import SurgeForecastAgent
from .resource_optimizer_agent import ResourceOptimizerAgent

class SimulationAgent:
    """
    What-if Simulation Agent
    Runs scenarios by modifying inputs and calling other agents.
    """

    def __init__(self):
        self.forecaster = SurgeForecastAgent()
        self.optimizer = ResourceOptimizerAgent()

    def run_simulation(self, scenario_config):
        """
        Run a simulation scenario.
        
        scenario_config: {
            "name": "High Pollution",
            "modifications": {
                "aqi": 400,
                "epidemic_level": 5
            },
            "duration_days": 7
        }
        """
        # 1. Prepare Context
        context = {
            "aqi": scenario_config['modifications'].get('aqi', 100),
            "epidemic_level": scenario_config['modifications'].get('epidemic_level', 0),
            "is_festival": scenario_config['modifications'].get('is_festival', False)
        }
        
        days = scenario_config.get('duration_days', 7)

        # 2. Run Forecast
        forecast = self.forecaster.predict_load(days=days, current_context=context)

        # 3. Run Resource Optimization
        # Mock current inventory
        current_inventory = {"oxygen_cylinders": 100, "n95_masks": 500}
        
        staffing_plan = self.optimizer.optimize_staffing(forecast)
        supply_plan = self.optimizer.optimize_supplies(forecast, current_inventory)

        # 4. Aggregate Results
        total_patients = sum(d['predicted_total'] for d in forecast)
        avg_daily = total_patients / days
        
        impact_summary = {
            "scenario": scenario_config['name'],
            "total_patients_predicted": total_patients,
            "average_daily_load": int(avg_daily),
            "critical_resource_gaps": [
                alert for day in supply_plan for alert in day['alerts']
            ]
        }

        return {
            "summary": impact_summary,
            "forecast": forecast,
            "staffing": staffing_plan,
            "supplies": supply_plan
        }
