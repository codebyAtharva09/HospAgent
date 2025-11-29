import json
import os
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

DATA_FILE = os.path.join("data", "supply_reorders.json")

class ReorderRequest(BaseModel):
    id: str
    supply_id: str
    supply_name: str
    requested_by: str
    requested_qty: int
    status: str  # "PENDING" | "APPROVED" | "REJECTED"
    approved_by: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None

def _load_data() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def _save_data(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def list_reorders(status: Optional[str] = None) -> List[ReorderRequest]:
    data = _load_data()
    reqs = [ReorderRequest(**r) for r in data]
    if status:
        reqs = [r for r in reqs if r.status == status]
    return reqs

def create_reorder(supply_id: str, supply_name: str, qty: int, requested_by: str) -> ReorderRequest:
    data = _load_data()
    new_id = f"REQ-{len(data) + 1:03d}"
    
    new_req = {
        "id": new_id,
        "supply_id": supply_id,
        "supply_name": supply_name,
        "requested_by": requested_by,
        "requested_qty": qty,
        "status": "PENDING",
        "approved_by": None,
        "created_at": datetime.utcnow().isoformat(),
        "resolved_at": None
    }
    
    data.append(new_req)
    _save_data(data)
    return ReorderRequest(**new_req)

def update_reorder_status(req_id: str, status: str, approved_by: Optional[str] = None) -> Optional[ReorderRequest]:
    data = _load_data()
    for r in data:
        if r["id"] == req_id:
            r["status"] = status
            r["resolved_at"] = datetime.utcnow().isoformat()
            if approved_by:
                r["approved_by"] = approved_by
            _save_data(data)
            return ReorderRequest(**r)
    return None
