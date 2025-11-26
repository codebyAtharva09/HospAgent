"""
Festival Repository - Database persistence for festival events
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json

class FestivalRepository:
    """
    Repository for storing and retrieving festival events.
    Uses simple file-based storage for demo (can be upgraded to PostgreSQL).
    """
    
    def __init__(self, storage_path: str = 'data/festivals.json'):
        self.storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
    
    def upsert_festivals(self, festivals: List[Dict[str, Any]]) -> int:
        """
        Insert or update festival events.
        
        Args:
            festivals: List of festival dicts
        
        Returns:
            Number of festivals upserted
        """
        
        # Load existing festivals
        existing = self._load_all()
        existing_map = {(f['id'], f['date']): f for f in existing}
        
        # Upsert new festivals
        upserted_count = 0
        for fest in festivals:
            key = (fest['id'], fest['date'])
            
            # Add metadata
            fest_with_meta = {
                **fest,
                'created_at': datetime.utcnow().isoformat() + 'Z',
                'updated_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            if key in existing_map:
                # Update existing
                existing_map[key].update(fest_with_meta)
            else:
                # Insert new
                existing_map[key] = fest_with_meta
                upserted_count += 1
        
        # Save back to storage
        all_festivals = list(existing_map.values())
        self._save_all(all_festivals)
        
        return upserted_count
    
    def get_upcoming_festivals(self, days_ahead: int = 180) -> List[Dict[str, Any]]:
        """
        Get upcoming festivals within specified time window.
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            List of upcoming festivals sorted by date
        """
        
        all_festivals = self._load_all()
        today = date.today()
        
        # Filter upcoming festivals
        upcoming = []
        for fest in all_festivals:
            try:
                fest_date = datetime.strptime(fest['date'], '%Y-%m-%d').date()
                days_until = (fest_date - today).days
                
                if 0 <= days_until <= days_ahead:
                    upcoming.append(fest)
            except:
                continue
        
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        
        return upcoming
    
    def get_high_risk_festivals(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get only high-risk festivals"""
        upcoming = self.get_upcoming_festivals(days_ahead)
        return [f for f in upcoming if f.get('high_risk', False)]
    
    def clear_old_festivals(self, days_past: int = 30):
        """Remove festivals older than specified days"""
        all_festivals = self._load_all()
        today = date.today()
        
        # Keep only recent/upcoming festivals
        filtered = []
        for fest in all_festivals:
            try:
                fest_date = datetime.strptime(fest['date'], '%Y-%m-%d').date()
                days_diff = (today - fest_date).days
                
                if days_diff < days_past:
                    filtered.append(fest)
            except:
                continue
        
        self._save_all(filtered)
        return len(all_festivals) - len(filtered)
    
    def _load_all(self) -> List[Dict]:
        """Load all festivals from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_all(self, festivals: List[Dict]):
        """Save all festivals to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(festivals, f, indent=2)


# PostgreSQL Schema (for production upgrade)
"""
CREATE TABLE festival_events (
    id TEXT PRIMARY KEY,
    summary TEXT NOT NULL,
    date DATE NOT NULL,
    source TEXT NOT NULL,
    high_risk BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_festival_date ON festival_events(date);
CREATE INDEX idx_festival_high_risk ON festival_events(high_risk, date);

-- Upsert query
INSERT INTO festival_events (id, summary, date, source, high_risk, updated_at)
VALUES ($1, $2, $3, $4, $5, NOW())
ON CONFLICT (id) 
DO UPDATE SET 
    summary = EXCLUDED.summary,
    date = EXCLUDED.date,
    source = EXCLUDED.source,
    high_risk = EXCLUDED.high_risk,
    updated_at = NOW();

-- Query upcoming festivals
SELECT * FROM festival_events
WHERE date >= CURRENT_DATE
  AND date <= CURRENT_DATE + INTERVAL '180 days'
ORDER BY date ASC;

-- Query high-risk festivals
SELECT * FROM festival_events
WHERE date >= CURRENT_DATE
  AND date <= CURRENT_DATE + INTERVAL '30 days'
  AND high_risk = TRUE
ORDER BY date ASC;
"""
