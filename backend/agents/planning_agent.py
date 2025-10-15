from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpInteger, LpBinary
from datetime import datetime, timedelta
import json

class PlanningAgent:
    """
    Planning Agent: Creates actionable operational plans based on reasoning agent insights
    Uses optimization algorithms to allocate resources efficiently
    """

    def __init__(self):
        self.hospital_capacity = {
            'total_beds': 300,
            'icu_beds': 50,
            'doctors': 60,
            'nurses': 120,
            'technicians': 40
        }

    def create_staffing_plan(self, patient_forecasts, current_staff=None):
        """Create optimal staffing plan using linear programming"""
        if current_staff is None:
            current_staff = {'doctors': 30, 'nurses': 60, 'technicians': 20}

        plans = []

        for forecast in patient_forecasts:
            patients = forecast['predicted_patients']

            # Optimization problem
            prob = LpProblem("Staff_Planning", LpMinimize)

            # Decision variables
            extra_doctors = LpVariable("extra_doctors", lowBound=0, cat=LpInteger)
            extra_nurses = LpVariable("extra_nurses", lowBound=0, cat=LpInteger)
            extra_technicians = LpVariable("extra_technicians", lowBound=0, cat=LpInteger)

            # Overtime variables (binary)
            overtime_doctors = LpVariable("overtime_doctors", cat=LpBinary)
            overtime_nurses = LpVariable("overtime_nurses", cat=LpBinary)

            # Objective: minimize cost
            prob += (1000 * extra_doctors + 500 * extra_nurses + 300 * extra_technicians +
                    200 * overtime_doctors + 100 * overtime_nurses)

            # Constraints
            total_doctors = current_staff['doctors'] + extra_doctors + overtime_doctors * 5
            total_nurses = current_staff['nurses'] + extra_nurses + overtime_nurses * 10

            prob += total_doctors >= patients // 15  # Doctor-to-patient ratio
            prob += total_nurses >= patients // 8    # Nurse-to-patient ratio
            prob += extra_doctors <= 20  # Max additional staff
            prob += extra_nurses <= 40

            prob.solve()

            plan = {
                'date': forecast['date'],
                'extra_doctors': int(extra_doctors.varValue or 0),
                'extra_nurses': int(extra_nurses.varValue or 0),
                'extra_technicians': int(extra_technicians.varValue or 0),
                'overtime_doctors': bool(overtime_doctors.varValue),
                'overtime_nurses': bool(overtime_nurses.varValue),
                'total_cost': prob.objective.value() if prob.objective.value() else 0
            }

            plans.append(plan)

        return plans

    def create_supply_plan(self, resource_forecasts, current_inventory=None):
        """Create supply procurement and allocation plan"""
        if current_inventory is None:
            current_inventory = {
                'oxygen_cylinders': 100,
                'medicines': 500,
                'masks': 1000,
                'ventilators': 20
            }

        plans = []

        for forecast in resource_forecasts:
            plan = {
                'date': forecast['date'],
                'procurement': {},
                'allocation': {},
                'priorities': []
            }

            # Oxygen planning
            needed_oxygen = forecast['oxygen_cylinders']
            current_oxygen = current_inventory['oxygen_cylinders']
            if needed_oxygen > current_oxygen * 0.8:  # Keep 80% buffer
                to_procure = needed_oxygen - current_oxygen + 20  # Safety buffer
                plan['procurement']['oxygen_cylinders'] = to_procure
                plan['priorities'].append('oxygen')

            # Medicine planning
            needed_meds = forecast['medicines']
            current_meds = current_inventory['medicines']
            if needed_meds > current_meds * 0.7:
                to_procure = needed_meds - current_meds + 50
                plan['procurement']['medicines'] = to_procure
                plan['priorities'].append('medicines')

            # Mask planning
            needed_masks = forecast['masks']
            current_masks = current_inventory['masks']
            if needed_masks > current_masks * 0.6:
                to_procure = needed_masks - current_masks + 200
                plan['procurement']['masks'] = to_procure
                plan['priorities'].append('masks')

            plans.append(plan)

        return plans

    def create_bed_management_plan(self, bed_forecasts):
        """Create bed allocation and management plan"""
        plans = []

        for forecast in bed_forecasts:
            occupancy = forecast['predicted_occupancy']
            available_beds = forecast['available_beds']

            plan = {
                'date': forecast['date'],
                'occupancy_rate': occupancy,
                'available_beds': available_beds,
                'actions': []
            }

            if occupancy > 90:
                plan['actions'].append('Activate emergency bed protocol')
                plan['actions'].append('Contact nearby hospitals for transfer options')
                plan['actions'].append('Prioritize ICU admissions')

            elif occupancy > 80:
                plan['actions'].append('Increase discharge planning')
                plan['actions'].append('Optimize bed turnover')

            if available_beds < 30:
                plan['actions'].append('Convert non-ICU beds to ICU if needed')
                plan['actions'].append('Implement early discharge incentives')

            plans.append(plan)

        return plans

    def optimize_overall_plan(self, insights):
        """Create comprehensive operational plan combining all aspects"""
        patient_forecasts = insights.get('patient_forecasts', [])
        bed_forecasts = insights.get('bed_forecasts', [])
        resource_forecasts = insights.get('resource_forecasts', [])

        staffing_plan = self.create_staffing_plan(patient_forecasts)
        supply_plan = self.create_supply_plan(resource_forecasts)
        bed_plan = self.create_bed_management_plan(bed_forecasts)

        # Combine into master plan
        master_plan = {
            'timestamp': datetime.now().isoformat(),
            'planning_period': f"{patient_forecasts[0]['date']} to {patient_forecasts[-1]['date']}",
            'staffing_plan': staffing_plan,
            'supply_plan': supply_plan,
            'bed_management_plan': bed_plan,
            'risk_assessment': self.assess_plan_risks(staffing_plan, supply_plan, bed_plan),
            'contingency_plans': self.create_contingency_plans(staffing_plan, supply_plan, bed_plan)
        }

        return master_plan

    def assess_plan_risks(self, staffing, supply, bed):
        """Assess risks in the operational plan"""
        risks = []

        # Staffing risks
        for day in staffing:
            if day['extra_doctors'] > 15:
                risks.append({
                    'type': 'staffing_shortage',
                    'severity': 'high',
                    'date': day['date'],
                    'description': f'Major doctor shortage on {day["date"]}'
                })

        # Supply risks
        for day in supply:
            if 'oxygen_cylinders' in day['procurement'] and day['procurement']['oxygen_cylinders'] > 50:
                risks.append({
                    'type': 'supply_critical',
                    'severity': 'critical',
                    'date': day['date'],
                    'description': f'Oxygen shortage risk on {day["date"]}'
                })

        # Bed risks
        for day in bed:
            if day['occupancy_rate'] > 95:
                risks.append({
                    'type': 'capacity_critical',
                    'severity': 'critical',
                    'date': day['date'],
                    'description': f'Bed capacity critical on {day["date"]}'
                })

        return risks

    def create_contingency_plans(self, staffing, supply, bed):
        """Create contingency plans for high-risk scenarios"""
        contingencies = []

        # Check for critical staffing days
        critical_staffing_days = [day for day in staffing if day['extra_doctors'] > 10]

        if critical_staffing_days:
            contingencies.append({
                'trigger': 'staffing_crisis',
                'condition': 'Extra doctors needed > 10',
                'actions': [
                    'Activate staff recall protocol',
                    'Contact locum agencies',
                    'Implement staff shift extensions',
                    'Request assistance from nearby hospitals'
                ]
            })

        # Check for supply critical days
        critical_supply_days = [day for day in supply if len(day['priorities']) > 2]

        if critical_supply_days:
            contingencies.append({
                'trigger': 'supply_crisis',
                'condition': 'Multiple supply priorities',
                'actions': [
                    'Activate emergency procurement protocol',
                    'Contact alternative suppliers',
                    'Implement supply rationing',
                    'Request supplies from medical stockpiles'
                ]
            })

        # Check for capacity critical days
        critical_capacity_days = [day for day in bed if day['occupancy_rate'] > 90]

        if critical_capacity_days:
            contingencies.append({
                'trigger': 'capacity_crisis',
                'condition': 'Bed occupancy > 90%',
                'actions': [
                    'Activate hospital overflow protocol',
                    'Set up temporary beds in corridors',
                    'Implement patient transfer protocols',
                    'Contact disaster management authorities'
                ]
            })

        return contingencies

    def generate_recommendations(self, predicted_patients):
        """Generate staffing and supply recommendations based on patient forecast."""
        # Calculate staffing needs
        doctors_needed = max(1, predicted_patients // 15)  # 1 doctor per 15 patients
        nurses_needed = max(1, predicted_patients // 8)    # 1 nurse per 8 patients
        technicians_needed = max(1, predicted_patients // 20)  # 1 technician per 20 patients

        # Calculate supply needs (rough estimates)
        oxygen_cylinders = predicted_patients // 10  # 1 cylinder per 10 patients
        medicines = predicted_patients * 5  # 5 units per patient
        masks = predicted_patients * 2  # 2 masks per patient

        recommendations = {
            'staffing': {
                'doctors': doctors_needed,
                'nurses': nurses_needed,
                'technicians': technicians_needed
            },
            'supplies': {
                'oxygen_cylinders': oxygen_cylinders,
                'medicines': medicines,
                'masks': masks
            },
            'capacity_check': {
                'beds_needed': predicted_patients,
                'icu_beds_needed': predicted_patients // 10  # 10% need ICU
            },
            'risk_level': 'high' if predicted_patients > 250 else 'medium' if predicted_patients > 150 else 'low'
        }

        return recommendations

    def generate_advisory(self, query=""):
        """Generate advisory messages based on current situation."""
        # This would use more sophisticated logic based on the query
        # For now, return a generic advisory
        advisory = {
            "advisory": "Based on current predictions, prepare for potential patient surge. Ensure adequate staffing and resources are available. Monitor air quality and implement infection control measures.",
            "priority": "high",
            "actions": [
                "Increase staffing by 20%",
                "Stock up on essential medications",
                "Prepare additional beds",
                "Implement visitor restrictions if needed"
            ]
        }
        return advisory

    def dispatch_tasks(self, plan):
        """Dispatch tasks to communication agent"""
        tasks = []

        # Create tasks from staffing plan
        for day in plan['staffing_plan']:
            if day['extra_doctors'] > 0 or day['extra_nurses'] > 0:
                tasks.append({
                    'type': 'staff_notification',
                    'priority': 'high' if day['extra_doctors'] > 5 else 'medium',
                    'recipients': ['hr_manager', 'department_heads'],
                    'message': f"Staff augmentation needed for {day['date']}: {day['extra_doctors']} doctors, {day['extra_nurses']} nurses",
                    'actions_required': ['recall_staff', 'arrange_overtime' if day['overtime_doctors'] else None]
                })

        # Create tasks from supply plan
        for day in plan['supply_plan']:
            if day['procurement']:
                tasks.append({
                    'type': 'supply_procurement',
                    'priority': 'high' if 'oxygen_cylinders' in day['procurement'] else 'medium',
                    'recipients': ['procurement_team', 'inventory_manager'],
                    'message': f"Supply procurement needed for {day['date']}: {day['procurement']}",
                    'actions_required': ['contact_suppliers', 'arrange_emergency_delivery']
                })

        # Create tasks from bed management
        for day in plan['bed_management_plan']:
            if day['actions']:
                tasks.append({
                    'type': 'bed_management',
                    'priority': 'critical' if day['occupancy_rate'] > 90 else 'medium',
                    'recipients': ['nursing_supervisor', 'admin_team'],
                    'message': f"Bed management actions for {day['date']}: {day['actions']}",
                    'actions_required': day['actions']
                })

        return tasks
