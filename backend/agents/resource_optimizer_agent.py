import math

class ResourceOptimizerAgent:
    """
    Resource & Supply Optimizer Agent
    """

    def __init__(self):
        self.OXYGEN_PER_PATIENT = 1.5
        self.MASK_PER_PATIENT = 2.5
        self.IV_PER_PATIENT = 0.8

    def optimize_resources(self, forecast_data, staff_roster, holiday_calendar=None):
        """
        Generate staffing and supply plans.
        """
        staffing_plan = []
        supply_plan = []
        
        for day in forecast_data:
            date = day['date']
            total = day['total_patients']
            resp = day['breakdown']['respiratory']
            
            # --- Staffing Logic ---
            required_docs = math.ceil(total / 15)
            required_nurses = math.ceil(total / 6)
            
            # Check holidays
            is_holiday = False
            if holiday_calendar:
                is_holiday = any(h['date'] == date for h in holiday_calendar)
            
            # Holiday adjustment (assume 20% staff absence on holidays)
            available_docs_pct = 0.8 if is_holiday else 0.95
            
            staffing_plan.append({
                "date": date,
                "requirements": {
                    "doctors": required_docs,
                    "nurses": required_nurses,
                    "support": math.ceil(total / 20)
                },
                "alerts": ["High Staff Absence Risk"] if is_holiday else []
            })
            
            # --- Supply Logic ---
            # Lead time adjustment: If festival nearby, order 3 days earlier
            lead_time_days = 3 if is_holiday else 1
            
            supply_plan.append({
                "date": date,
                "items": {
                    "oxygen_cylinders": math.ceil(resp * self.OXYGEN_PER_PATIENT),
                    "n95_masks": math.ceil(total * self.MASK_PER_PATIENT),
                    "iv_fluids": math.ceil(total * self.IV_PER_PATIENT)
                },
                "action": f"Order {lead_time_days} days in advance" if is_holiday else "Standard Restock"
            })
            
        return {"staffing": staffing_plan, "supplies": supply_plan}
