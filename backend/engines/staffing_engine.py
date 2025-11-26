"""
Staffing Engine - Calculate staffing requirements based on predicted load
"""

from typing import List, Dict, Any
from datetime import datetime

class StaffingEngine:
    """
    Rule-based staffing recommendation engine.
    Calculates required doctors, nurses, and support staff based on:
    - Predicted patient load
    - ICU/ER pressure
    - AQI level (respiratory cases)
    - Epidemic severity
    """
    
    def __init__(self):
        # Base ratios (patients per staff member)
        self.PATIENTS_PER_DOCTOR = 15
        self.PATIENTS_PER_NURSE = 6
        self.PATIENTS_PER_SUPPORT = 20
        
        # ICU ratios (more intensive)
        self.ICU_PATIENTS_PER_DOCTOR = 3
        self.ICU_PATIENTS_PER_NURSE = 2
    
    def recommend_staffing(
        self,
        predicted_patients_today: int,
        icu_risk: float,  # 0-100
        epidemic_index: float,  # 0-10
        aqi_level: int,  # 0-500
        respiratory_cases: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Calculate staffing requirements for today.
        
        Args:
            predicted_patients_today: Total predicted patients
            icu_risk: ICU pressure score (0-100)
            epidemic_index: Epidemic severity (0-10)
            aqi_level: Air quality index (0-500)
            respiratory_cases: Predicted respiratory cases
        
        Returns:
            List of staffing plans by shift/department
        """
        
        # Estimate ICU patients based on ICU risk
        icu_patients = int(predicted_patients_today * (icu_risk / 100) * 0.15)
        
        # Estimate ER patients (higher during high AQI or epidemics)
        er_multiplier = 1.0
        if aqi_level > 300:
            er_multiplier = 1.5
        elif aqi_level > 200:
            er_multiplier = 1.3
        
        if epidemic_index > 7:
            er_multiplier *= 1.3
        elif epidemic_index > 4:
            er_multiplier *= 1.15
        
        er_patients = int(predicted_patients_today * 0.3 * er_multiplier)
        
        # General ward patients
        general_patients = predicted_patients_today - icu_patients - er_patients
        
        # Calculate staff requirements
        
        # ICU Staff
        icu_doctors = max(2, int(icu_patients / self.ICU_PATIENTS_PER_DOCTOR) + 1)
        icu_nurses = max(3, int(icu_patients / self.ICU_PATIENTS_PER_NURSE) + 1)
        
        # ER Staff
        er_doctors = max(3, int(er_patients / 10) + 1)
        er_nurses = max(5, int(er_patients / 5) + 1)
        
        # General Ward Staff
        general_doctors = max(4, int(general_patients / self.PATIENTS_PER_DOCTOR))
        general_nurses = max(8, int(general_patients / self.PATIENTS_PER_NURSE))
        
        # Total requirements
        total_doctors = icu_doctors + er_doctors + general_doctors
        total_nurses = icu_nurses + er_nurses + general_nurses
        total_support = max(10, int(predicted_patients_today / self.PATIENTS_PER_SUPPORT))
        
        # Calculate overall risk score
        risk_score = self._calculate_staffing_risk(
            predicted_patients_today,
            icu_risk,
            epidemic_index,
            aqi_level
        )
        
        # Generate staffing plan
        staffing_plan = [
            {
                "shift_label": "Today (24h)",
                "department": "Hospital Wide",
                "doctors": total_doctors,
                "nurses": total_nurses,
                "support": total_support,
                "risk": risk_score,
                "breakdown": {
                    "icu": {"doctors": icu_doctors, "nurses": icu_nurses},
                    "er": {"doctors": er_doctors, "nurses": er_nurses},
                    "general": {"doctors": general_doctors, "nurses": general_nurses}
                },
                "notes": self._generate_staffing_notes(
                    risk_score,
                    predicted_patients_today,
                    icu_patients,
                    er_patients
                )
            }
        ]
        
        return staffing_plan
    
    def _calculate_staffing_risk(
        self,
        patients: int,
        icu_risk: float,
        epidemic: float,
        aqi: int
    ) -> int:
        """
        Calculate staffing pressure risk (0-100).
        Higher = more pressure on staff.
        """
        
        # Base risk from patient volume
        if patients > 250:
            base_risk = 90
        elif patients > 200:
            base_risk = 70
        elif patients > 150:
            base_risk = 50
        else:
            base_risk = 30
        
        # Adjust for ICU pressure
        icu_adjustment = (icu_risk - 50) * 0.3
        
        # Adjust for epidemic
        epidemic_adjustment = epidemic * 2
        
        # Adjust for AQI (respiratory cases need more care)
        aqi_adjustment = 0
        if aqi > 300:
            aqi_adjustment = 15
        elif aqi > 200:
            aqi_adjustment = 10
        
        total_risk = base_risk + icu_adjustment + epidemic_adjustment + aqi_adjustment
        
        return int(min(100, max(0, total_risk)))
    
    def _generate_staffing_notes(
        self,
        risk: int,
        total_patients: int,
        icu_patients: int,
        er_patients: int
    ) -> List[str]:
        """Generate actionable staffing notes"""
        
        notes = []
        
        if risk >= 80:
            notes.append("CRITICAL: Call in additional staff immediately")
            notes.append("Consider activating disaster protocol")
        elif risk >= 60:
            notes.append("HIGH PRESSURE: Increase staff on next shift")
            notes.append("Prepare for potential surge")
        elif risk >= 40:
            notes.append("MODERATE: Monitor staffing levels closely")
        else:
            notes.append("Normal staffing levels adequate")
        
        if icu_patients > 15:
            notes.append(f"ICU at capacity ({icu_patients} patients) - prioritize critical care staff")
        
        if er_patients > 50:
            notes.append(f"ER surge expected ({er_patients} patients) - reinforce ER team")
        
        return notes
