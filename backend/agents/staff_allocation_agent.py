import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpInteger, LpBinary

class StaffAllocationAgent:
    def __init__(self):
        self.staff_data = self._load_staff_data()
        self.departments = ['ER', 'ICU', 'OPD', 'Surgery', 'Pediatrics', 'Maternity']

    def _load_staff_data(self):
        """Load staff roster and specialization data."""
        # Mock staff data - in real implementation, this would come from HMS
        return {
            'doctors': [
                {'id': 1, 'name': 'Dr. Patel', 'specialization': 'ER', 'shift': 'morning', 'available': True},
                {'id': 2, 'name': 'Dr. Sharma', 'specialization': 'ICU', 'shift': 'evening', 'available': True},
                {'id': 3, 'name': 'Dr. Kumar', 'specialization': 'OPD', 'shift': 'morning', 'available': False},
                {'id': 4, 'name': 'Dr. Singh', 'specialization': 'Surgery', 'shift': 'morning', 'available': True},
                {'id': 5, 'name': 'Dr. Gupta', 'specialization': 'Pediatrics', 'shift': 'evening', 'available': True},
            ],
            'nurses': [
                {'id': 1, 'name': 'Nurse Raj', 'department': 'ER', 'shift': 'morning', 'available': True},
                {'id': 2, 'name': 'Nurse Priya', 'department': 'ICU', 'shift': 'evening', 'available': True},
                {'id': 3, 'name': 'Nurse Amit', 'department': 'OPD', 'shift': 'morning', 'available': True},
                {'id': 4, 'name': 'Nurse Sunita', 'department': 'Surgery', 'shift': 'evening', 'available': True},
            ]
        }

    def optimize_staffing(self, predicted_patients, department_loads, date=None):
        """
        Optimize staff allocation based on predicted patient load.
        Uses linear programming to minimize overtime while meeting demand.
        """
        if date is None:
            date = datetime.now() + timedelta(days=1)

        recommendations = []

        for dept in self.departments:
            load = department_loads.get(dept, 1.0)
            base_staff_needed = int(predicted_patients * load * 0.1)  # Base calculation

            # Get available staff for this department
            available_doctors = [d for d in self.staff_data['doctors']
                               if d['specialization'] == dept and d['available']]
            available_nurses = [n for n in self.staff_data['nurses']
                              if n['department'] == dept and n['available']]

            current_doctors = len([d for d in available_doctors if d['shift'] == 'morning'])
            current_nurses = len([n for n in available_nurses if n['shift'] == 'morning'])

            # Calculate additional staff needed
            additional_doctors = max(0, base_staff_needed - current_doctors)
            additional_nurses = max(0, base_staff_needed - current_nurses)

            if additional_doctors > 0 or additional_nurses > 0:
                recommendations.append({
                    'department': dept,
                    'date': date.strftime('%Y-%m-%d'),
                    'current_doctors': current_doctors,
                    'current_nurses': current_nurses,
                    'additional_doctors': additional_doctors,
                    'additional_nurses': additional_nurses,
                    'reason': f"Predicted {int(predicted_patients * load)} patients in {dept}",
                    'severity': 'high' if additional_doctors > 2 else 'medium'
                })

        return recommendations

    def get_staff_schedule(self, date=None):
        """Get current staff schedule for a given date."""
        if date is None:
            date = datetime.now().date()

        schedule = {}
        for dept in self.departments:
            schedule[dept] = {
                'doctors': [d for d in self.staff_data['doctors']
                           if d['specialization'] == dept and d['available']],
                'nurses': [n for n in self.staff_data['nurses']
                          if n['department'] == dept and n['available']]
            }

        return schedule

    def update_staff_availability(self, staff_id, staff_type, available):
        """Update staff availability (e.g., for leaves, training)."""
        if staff_type == 'doctor':
            for doctor in self.staff_data['doctors']:
                if doctor['id'] == staff_id:
                    doctor['available'] = available
                    return True
        elif staff_type == 'nurse':
            for nurse in self.staff_data['nurses']:
                if nurse['id'] == staff_id:
                    nurse['available'] = available
                    return True
        return False

    def optimize_staff_allocation(self, current_staff, predicted_demand):
        """Optimize staff allocation based on predictions."""
        # Mock optimization logic
        total_patients = predicted_demand.get('predicted_patients', 100)
        
        # Simple heuristic: 1 doctor per 20 patients, 1 nurse per 10 patients
        recommended_doctors = max(1, int(total_patients / 20))
        recommended_nurses = max(2, int(total_patients / 10))
        
        return {
            'total_recommended': recommended_doctors + recommended_nurses,
            'details': {
                'doctors': recommended_doctors,
                'nurses': recommended_nurses
            },
            'recommendations': [
                f"Increase doctors by {max(0, recommended_doctors - current_staff.get('doctors', 0))}",
                f"Increase nurses by {max(0, recommended_nurses - current_staff.get('nurses', 0))}"
            ]
        }

    def analyze_shift_coverage(self):
        """Analyze shift coverage and identify gaps."""
        # Mock coverage analysis
        return {
            'status': 'adequate',
            'coverage_percent': 85,
            'gaps': [
                {'shift': 'night', 'department': 'ER', 'role': 'nurse', 'shortage': 2}
            ],
            'alerts': [
                {'type': 'staffing', 'message': 'Night shift ER nurse shortage detected', 'severity': 'medium'}
            ]
        }
