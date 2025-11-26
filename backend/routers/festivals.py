"""
Festival Routes - API endpoints for festival management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel
from datetime import datetime

from services.festival_client import FestivalClient
from services.festival_repository import FestivalRepository

router = APIRouter(prefix="/festivals", tags=["festivals"])

# Initialize services
festival_client = FestivalClient()
festival_repo = FestivalRepository()

# Pydantic Models
class FestivalEvent(BaseModel):
    """Festival event model"""
    id: str
    summary: str
    date: str  # YYYY-MM-DD format
    source: str
    high_risk: bool

class FestivalSyncResponse(BaseModel):
    """Response for festival sync operation"""
    success: bool
    festivals_synced: int
    message: str

@router.get("/upcoming", response_model=List[FestivalEvent])
async def get_upcoming_festivals(
    days_ahead: int = Query(default=180, ge=1, le=365, description="Days to look ahead")
):
    """
    Get upcoming festivals from Google Calendar.
    
    This endpoint:
    1. Fetches festivals from Google Calendar (or uses cached data)
    2. Returns normalized festival list
    3. Marks high-risk festivals based on keywords
    
    Args:
        days_ahead: Number of days to look ahead (1-365)
    
    Returns:
        List of festival events with high_risk flag
    
    Example:
        GET /festivals/upcoming?days_ahead=30
    """
    
    try:
        # Try to get from cache first
        cached_festivals = festival_repo.get_upcoming_festivals(days_ahead)
        
        # If cache is empty or stale, fetch from Google Calendar
        if not cached_festivals:
            print("Cache miss - fetching from Google Calendar")
            festivals = festival_client.fetch_festivals(days_ahead)
            
            # Cache the results
            if festivals:
                festival_repo.upsert_festivals(festivals)
            
            return festivals
        
        return cached_festivals
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch festivals: {str(e)}"
        )

@router.post("/sync", response_model=FestivalSyncResponse)
async def sync_festivals(
    days_ahead: int = Query(default=180, ge=1, le=365)
):
    """
    Manually sync festivals from Google Calendar.
    
    This endpoint:
    1. Fetches latest festivals from Google Calendar
    2. Updates local cache/database
    3. Returns sync status
    
    Use this to refresh festival data on-demand.
    
    Args:
        days_ahead: Number of days to look ahead
    
    Returns:
        Sync status with count of festivals synced
    
    Example:
        POST /festivals/sync?days_ahead=180
    """
    
    try:
        # Fetch from Google Calendar
        festivals = festival_client.fetch_festivals(days_ahead)
        
        if not festivals:
            return FestivalSyncResponse(
                success=False,
                festivals_synced=0,
                message="No festivals fetched from Google Calendar"
            )
        
        # Upsert to repository
        count = festival_repo.upsert_festivals(festivals)
        
        # Clean up old festivals
        deleted = festival_repo.clear_old_festivals(days_past=30)
        
        return FestivalSyncResponse(
            success=True,
            festivals_synced=len(festivals),
            message=f"Synced {len(festivals)} festivals, removed {deleted} old entries"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync festivals: {str(e)}"
        )

@router.get("/high-risk", response_model=List[FestivalEvent])
async def get_high_risk_festivals(
    days_ahead: int = Query(default=30, ge=1, le=90)
):
    """
    Get only high-risk festivals.
    
    High-risk festivals include:
    - Diwali, Holi, Ganesh Chaturthi, Navratri, Eid
    - Events that typically cause hospital surges
    
    Args:
        days_ahead: Number of days to look ahead (1-90)
    
    Returns:
        List of high-risk festival events
    """
    
    try:
        festivals = festival_repo.get_high_risk_festivals(days_ahead)
        return festivals
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch high-risk festivals: {str(e)}"
        )

@router.get("/features")
async def get_festival_features():
    """
    Get festival-related features for ML models.
    
    Returns calculated features:
    - is_festival_today
    - days_to_next_festival
    - is_high_risk_festival_window
    - festivals_next_7_days
    - high_risk_festivals_next_7_days
    
    These features can be used in risk/forecast models.
    """
    
    try:
        # Get upcoming festivals
        festivals = festival_repo.get_upcoming_festivals(days_ahead=30)
        
        # Calculate features
        features = festival_client.calculate_festival_features(festivals)
        
        return {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "features": features,
            "upcoming_festivals": festivals[:5]  # Next 5 festivals
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate festival features: {str(e)}"
        )
