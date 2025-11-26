class WellbeingAgent:
    """
    Staff Burnout & Wellbeing Agent
    Calculates burnout risk score and suggests rotations.
    """

    def __init__(self):
        self.MAX_CONSECUTIVE_SHIFTS = 3
        self.MAX_WEEKLY_HOURS = 60

    def analyze_burnout_risk(self, staff_roster, past_shifts):
        """
        Analyze staff roster for burnout risks.
        
        staff_roster: list of staff members
        past_shifts: dict mapping staff_id to list of recent shift dates/types
        """
        risk_report = {
            "overall_risk": "LOW",
            "high_risk_staff": [],
            "recommendations": []
        }

        high_risk_count = 0

        for staff in staff_roster:
            staff_id = staff['id']
            shifts = past_shifts.get(staff_id, [])
            
            # 1. Check consecutive shifts
            consecutive = self._count_consecutive(shifts)
            
            # 2. Check total hours (mock)
            total_hours = len(shifts) * 8 # Assuming 8hr shifts
            
            risk_score = 0
            reasons = []

            if consecutive > self.MAX_CONSECUTIVE_SHIFTS:
                risk_score += 50
                reasons.append(f"{consecutive} consecutive shifts")
            
            if total_hours > self.MAX_WEEKLY_HOURS:
                risk_score += 40
                reasons.append(f"{total_hours} hours this week")

            if risk_score >= 50:
                high_risk_count += 1
                risk_report['high_risk_staff'].append({
                    "id": staff_id,
                    "name": staff['name'],
                    "risk_score": risk_score,
                    "reasons": reasons
                })
                risk_report['recommendations'].append(
                    f"Rotate {staff['name']} immediately (Risk: {risk_score})"
                )

        if high_risk_count > len(staff_roster) * 0.2:
            risk_report['overall_risk'] = "HIGH"
        elif high_risk_count > 0:
            risk_report['overall_risk'] = "MODERATE"

        return risk_report

    def _count_consecutive(self, shifts):
        # Simplified consecutive logic
        return len(shifts) # Mock
