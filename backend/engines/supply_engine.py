"""
Supply Engine - Calculate critical supply requirements
"""

from typing import List, Dict, Any
from datetime import datetime

class SupplyEngine:
    """
    Rule-based supply recommendation engine.
    Calculates required medical supplies based on:
    - Forecasted patient load
    - Respiratory case volume (AQI-driven)
    - Epidemic severity
    - Festival proximity
    """
    
    def __init__(self):
        # Base consumption rates (per patient per day)
        self.OXYGEN_PER_RESPIRATORY = 2.5  # Cylinders
        self.MASKS_PER_PATIENT = 3  # N95 masks
        self.IV_FLUIDS_PER_PATIENT = 0.8  # Units
        self.NEBULIZERS_PER_RESPIRATORY = 0.5
        
        # Safety stock multipliers
        self.SAFETY_MULTIPLIER = 1.2  # 20% buffer
        self.FESTIVAL_MULTIPLIER = 1.5  # 50% extra during festivals
    
    def recommend_supplies(
        self,
        forecast: List[Dict],
        current_stock: Dict[str, int] = None,
        festival_window: bool = False,
        aqi_level: int = 100,
        epidemic_index: float = 0
    ) -> List[Dict[str, Any]]:
        """
        Calculate supply requirements based on forecast.
        
        Args:
            forecast: List of daily forecasts with patient counts
            current_stock: Current inventory levels (optional)
            festival_window: Whether in high-risk festival period
            aqi_level: Current AQI (affects respiratory supplies)
            epidemic_index: Epidemic severity (0-10)
        
        Returns:
            List of supply requirements with status
        """
        
        if not forecast or len(forecast) == 0:
            return self._get_default_supplies()
        
        # Get today's forecast
        today = forecast[0]
        total_patients = today.get('total_patients', 150)
        respiratory = today.get('breakdown', {}).get('respiratory', 0)
        
        # Calculate multipliers
        multiplier = self.SAFETY_MULTIPLIER
        if festival_window:
            multiplier *= self.FESTIVAL_MULTIPLIER
        
        # AQI adjustment for respiratory supplies
        aqi_multiplier = 1.0
        if aqi_level > 300:
            aqi_multiplier = 1.8
        elif aqi_level > 200:
            aqi_multiplier = 1.4
        elif aqi_level > 150:
            aqi_multiplier = 1.2
        
        # Epidemic adjustment
        epidemic_multiplier = 1.0 + (epidemic_index * 0.05)
        
        # Calculate requirements
        
        # Oxygen Cylinders (respiratory cases)
        oxygen_required = int(
            respiratory * self.OXYGEN_PER_RESPIRATORY * multiplier * aqi_multiplier
        )
        
        # N95 Masks (all patients + staff)
        masks_required = int(
            total_patients * self.MASKS_PER_PATIENT * multiplier * aqi_multiplier
        )
        
        # IV Fluids
        iv_fluids_required = int(
            total_patients * self.IV_FLUIDS_PER_PATIENT * multiplier * epidemic_multiplier
        )
        
        # Nebulizers (respiratory cases)
        nebulizers_required = int(
            respiratory * self.NEBULIZERS_PER_RESPIRATORY * multiplier * aqi_multiplier
        )
        
        # PPE Kits (based on epidemic severity)
        ppe_required = int(
            total_patients * 0.5 * epidemic_multiplier
        )
        
        # Determine status based on current stock (if provided)
        supplies = [
            {
                "item": "Oxygen Cylinders",
                "required": oxygen_required,
                "status": self._get_status("oxygen", oxygen_required, current_stock),
                "priority": "HIGH" if aqi_level > 200 else "MEDIUM"
            },
            {
                "item": "N95 Masks",
                "required": masks_required,
                "status": self._get_status("masks", masks_required, current_stock),
                "priority": "HIGH" if aqi_level > 200 or epidemic_index > 5 else "MEDIUM"
            },
            {
                "item": "IV Fluids",
                "required": iv_fluids_required,
                "status": self._get_status("iv_fluids", iv_fluids_required, current_stock),
                "priority": "MEDIUM"
            },
            {
                "item": "Nebulizers",
                "required": nebulizers_required,
                "status": self._get_status("nebulizers", nebulizers_required, current_stock),
                "priority": "HIGH" if respiratory > 50 else "MEDIUM"
            },
            {
                "item": "PPE Kits",
                "required": ppe_required,
                "status": self._get_status("ppe", ppe_required, current_stock),
                "priority": "HIGH" if epidemic_index > 7 else "LOW"
            }
        ]
        
        # Add notes
        for supply in supplies:
            supply['notes'] = self._generate_supply_notes(
                supply['item'],
                supply['status'],
                supply['priority'],
                festival_window
            )
        
        return supplies
    
    def _get_status(
        self,
        item_key: str,
        required: int,
        current_stock: Dict[str, int] = None
    ) -> str:
        """
        Determine supply status based on current stock.
        If no stock data, assume OK for demo.
        """
        
        if not current_stock:
            # Default status for demo
            if required > 300:
                return "LOW"
            elif required > 200:
                return "MEDIUM"
            else:
                return "OK"
        
        current = current_stock.get(item_key, 0)
        
        if current >= required * 1.5:
            return "OK"
        elif current >= required:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_supply_notes(
        self,
        item: str,
        status: str,
        priority: str,
        festival: bool
    ) -> str:
        """Generate actionable supply notes"""
        
        if status == "LOW":
            if priority == "HIGH":
                return f"URGENT: Order {item} immediately"
            else:
                return f"Order {item} within 24 hours"
        elif status == "MEDIUM":
            if festival:
                return f"Restock {item} before festival surge"
            else:
                return f"Monitor {item} levels"
        else:
            return "Stock adequate"
    
    def _get_default_supplies(self) -> List[Dict[str, Any]]:
        """Return default supply list when no forecast available"""
        
        return [
            {"item": "Oxygen Cylinders", "required": 30, "status": "OK", "priority": "MEDIUM"},
            {"item": "N95 Masks", "required": 200, "status": "OK", "priority": "MEDIUM"},
            {"item": "IV Fluids", "required": 100, "status": "OK", "priority": "MEDIUM"},
            {"item": "Nebulizers", "required": 15, "status": "OK", "priority": "LOW"},
            {"item": "PPE Kits", "required": 50, "status": "OK", "priority": "LOW"}
        ]
