class BurnoutAgent:
    """
    Burnout & Wellbeing Agent
    Monitors staff fatigue levels.
    """
    
    def calculate_burnout_risk(self, staff_history):
        """
        staff_history: list of {staff_id, shift_type, hours}
        """
        high_risk_staff = []
        
        for staff in staff_history:
            risk_score = 0
            reasons = []
            
            # 1. Consecutive Night Shifts
            consecutive_nights = staff.get('consecutive_nights', 0)
            if consecutive_nights >= 3:
                risk_score += 50
                reasons.append(f"{consecutive_nights} consecutive night shifts")
                
            # 2. Weekly Hours
            weekly_hours = staff.get('weekly_hours', 0)
            if weekly_hours > 60:
                risk_score += 40
                reasons.append(f"Overworked ({weekly_hours}h/week)")
                
            if risk_score > 40:
                high_risk_staff.append({
                    "id": staff['id'],
                    "risk_score": risk_score,
                    "reasons": reasons,
                    "recommendation": "Mandatory Rest Day"
                })
                
        return {
            "overall_risk": "HIGH" if len(high_risk_staff) > 5 else "LOW",
            "at_risk_count": len(high_risk_staff),
            "details": high_risk_staff
        }
