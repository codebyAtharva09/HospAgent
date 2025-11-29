import json
import os
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

DATA_FILE = os.path.join("data", "patients.json")

class Patient(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    contact: str
    address: str
    doctor_id: str
    doctor_name: str
    department: str
    reason: str
    status: str  # "ADMITTED" | "DISCHARGED"
    bed_type: Optional[str] = None
    admitted_at: str
    discharged_at: Optional[str] = None

def _load_data() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def _save_data(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def list_patients(status: Optional[str] = None) -> List[Patient]:
    data = _load_data()
    patients = [Patient(**p) for p in data]
    if status:
        patients = [p for p in patients if p.status == status]
    return patients

def create_patient(patient_data: dict) -> Patient:
    data = _load_data()
    
    # Generate ID
    new_id = f"PAT-{len(data) + 1:03d}"
    
    new_patient = {
        "id": new_id,
        **patient_data,
        "status": "ADMITTED",
        "admitted_at": datetime.utcnow().isoformat(),
        "discharged_at": None
    }
    
    data.append(new_patient)
    _save_data(data)
    return Patient(**new_patient)

def discharge_patient(patient_id: str) -> Optional[Patient]:
    data = _load_data()
    for p in data:
        if p["id"] == patient_id:
            p["status"] = "DISCHARGED"
            p["discharged_at"] = datetime.utcnow().isoformat()
            _save_data(data)
            return Patient(**p)
    return None

def get_patient_summary() -> dict:
    patients = list_patients()
    active = [p for p in patients if p.status == "ADMITTED"]
    
    # Discharged today
    today_str = datetime.utcnow().date().isoformat()
    discharged_today = [
        p for p in patients 
        if p.status == "DISCHARGED" and p.discharged_at and p.discharged_at.startswith(today_str)
    ]
    
    # By Department
    dept_counts = {}
    for p in active:
        dept_counts[p.department] = dept_counts.get(p.department, 0) + 1
    
    by_department = [{"department": k, "count": v} for k, v in dept_counts.items()]
    
    # By Doctor
    doc_counts = {}
    for p in active:
        if p.doctor_id not in doc_counts:
            doc_counts[p.doctor_id] = {"name": p.doctor_name, "count": 0}
        doc_counts[p.doctor_id]["count"] += 1
        
    by_doctor = [
        {"doctor_id": k, "doctor_name": v["name"], "active_patients": v["count"]}
        for k, v in doc_counts.items()
    ]
    
    return {
        "total_patients": len(patients),
        "active_inpatients": len(active),
        "discharged_today": len(discharged_today),
        "by_department": by_department,
        "by_doctor": by_doctor
    }
