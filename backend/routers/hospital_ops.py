from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Literal
from pydantic import BaseModel

from services.auth_service import require_roles, UserRole, get_current_user
from models.auth import User
from repositories import patients_repo, supplies_repo

router = APIRouter(prefix="/hospital", tags=["hospital-ops"])

# --- Models ---

class PatientAdmissionRequest(BaseModel):
    name: str
    age: int
    gender: str
    contact: str
    address: str
    doctor_id: str
    doctor_name: str
    department: str
    reason: str
    bed_type: Literal["General Ward", "ICU", "Emergency"] = "General Ward"

class RestockRequest(BaseModel):
    supply_id: str
    quantity: int
    
    class Config:
        fields = {'supply_id': 'supplyId'} 
        allow_population_by_field_name = True

# --- Patient Endpoints (Receptionist Only) ---

@router.get("/patients/current", response_model=List[patients_repo.Patient])
def get_current_inpatients():
    return patients_repo.list_patients(status="ADMITTED")

@router.post("/patients/admit", response_model=patients_repo.Patient)
def admit_patient(
    request: PatientAdmissionRequest,
    current_user: User = Depends(require_roles(UserRole.RECEPTION))
):
    return patients_repo.create_patient(request.dict())

@router.post("/patients/discharge", response_model=patients_repo.Patient)
def discharge_patient(
    patient_id: str, # Passed as query param or body? User said POST with admission_id. Let's use body or query. Query is simpler for now or body.
    # Actually user said "Button calls POST /api/patients/discharge with admission_id". 
    # Usually POST takes body. Let's use a simple body or query param. 
    # To match REST, POST /patients/{id}/discharge is better, but user said POST /api/patients/discharge.
    # I will stick to the previous pattern /patients/{id}/discharge or use a body.
    # Let's use /patients/{id}/discharge for clarity and consistency with previous code, 
    # but the user prompt said "POST /api/patients/discharge". I will support that.
    current_user: User = Depends(require_roles(UserRole.RECEPTION))
):
    patient = patients_repo.discharge_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Also support the path param version for backward compat if needed, or just use this one.
@router.post("/patients/{patient_id}/discharge", response_model=patients_repo.Patient)
def discharge_patient_path(
    patient_id: str,
    current_user: User = Depends(require_roles(UserRole.RECEPTION))
):
    return discharge_patient(patient_id, current_user)


@router.get("/patients/stats/today")
def get_patient_stats_today():
    return patients_repo.get_patient_summary()

# --- Inventory Endpoints (Pharmacist Only) ---

# --- Inventory Endpoints (Pharmacist Only) ---

@router.get("/inventory/supplies", response_model=List[supplies_repo.Supply])
def get_inventory():
    return supplies_repo.list_supplies()

@router.post("/inventory/restock", response_model=supplies_repo.Supply)
def restock_inventory(
    request: RestockRequest,
    current_user: User = Depends(require_roles(UserRole.PHARMACIST))
):
    print(f"Restock request: {request.dict()} by {current_user.email}")
    try:
        supply = supplies_repo.restock_supply(request.supply_id, request.quantity, role=current_user.role)
        if not supply:
            print(f"Supply not found: {request.supply_id}")
            raise HTTPException(status_code=404, detail="Supply not found")
        return supply
    except Exception as e:
        print(f"Restock error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to restock: {str(e)}")
