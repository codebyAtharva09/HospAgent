import json
import os
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

DATA_FILE = os.path.join("data", "supplies.json")
LOG_FILE = os.path.join("data", "supplies_log.json")

class Supply(BaseModel):
    id: str
    name: str
    current_stock: int
    reorder_threshold: int
    unit: str
    status: Optional[str] = None # Computed

class SupplyLog(BaseModel):
    supply_id: str
    supply_name: str
    quantity_change: int
    role: str
    timestamp: str

def _load_data() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def _save_data(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _append_log(log: SupplyLog):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                pass
    logs.append(log.dict())
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def list_supplies() -> List[Supply]:
    data = _load_data()
    supplies = []
    for item in data:
        s = Supply(**item)
        # Compute status
        if s.current_stock <= s.reorder_threshold * 0.5: # Critical threshold assumption
            s.status = "CRITICAL"
        elif s.current_stock <= s.reorder_threshold:
            s.status = "LOW"
        else:
            s.status = "OK"
        supplies.append(s)
    return supplies

def restock_supply(supply_id: str, quantity: int, role: str = "pharmacist") -> Optional[Supply]:
    data = _load_data()
    for item in data:
        if item["id"] == supply_id:
            item["current_stock"] += quantity
            _save_data(data)
            
            # Log
            log = SupplyLog(
                supply_id=supply_id,
                supply_name=item["name"],
                quantity_change=quantity,
                role=role,
                timestamp=datetime.utcnow().isoformat()
            )
            _append_log(log)
            
            # Return updated supply
            s = Supply(**item)
            if s.current_stock <= s.reorder_threshold * 0.5:
                s.status = "CRITICAL"
            elif s.current_stock <= s.reorder_threshold:
                s.status = "LOW"
            else:
                s.status = "OK"
            return s
    return None
