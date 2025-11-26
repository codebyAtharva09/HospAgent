class AdvisoryAgent:
    """
    Advisory & Communication Agent
    Generates text-based advisories.
    """
    
    def generate_advisories(self, risk_data, forecast_data):
        patient_advisories = []
        admin_advisories = []
        
        # Patient Advisories
        if risk_data['hospital_risk_index'] > 70:
            patient_advisories.append({
                "channel": "SMS/WhatsApp",
                "text": f"⚠️ High Wait Times Expected at City Hospital. ER Wait > 4 hours. For mild fever, please visit OPD clinics. AQI is {risk_data['breakdown']['aqi_risk']}."
            })
            
        if risk_data['breakdown']['respiratory_risk'] > 60:
             patient_advisories.append({
                "channel": "Public Display",
                "text": "😷 Air Quality Alert: Respiratory patients advised to stay indoors. ER seeing surge in asthma cases."
            })
            
        # Admin Advisories
        if forecast_data[0]['total_patients'] > 200:
             admin_advisories.append({
                "priority": "HIGH",
                "text": f"📈 Surge Alert: Expecting {forecast_data[0]['total_patients']} patients tomorrow. Activate Level 2 Staffing."
            })
            
        return {
            "patient": patient_advisories,
            "admin": admin_advisories
        }
