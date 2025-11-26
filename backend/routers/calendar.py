"""
Calendar Routes - Live festival calendar endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel
from datetime import datetime, date

from services.live_festival_calendar import LiveFestivalCalendar

router = APIRouter(prefix="/calendar", tags=["calendar"])

# Initialize calendar client
calendar_client = LiveFestivalCalendar()

# Pydantic Models
class FestivalEvent(BaseModel):
    """Festival event model"""
    id: str
    summary: str
    date: str  # YYYY-MM-DD format
    source: str
    high_risk: bool

@router.get("/month", response_model=List[FestivalEvent])
async def get_month_festivals(
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)")
):
    """
    Get all festivals for a specific month.
    
    Args:
        year: Year (2020-2030)
        month: Month (1-12)
    
    Returns:
        List of festival events for that month
    
    Example:
        GET /calendar/month?year=2025&month=11
    """
    
    try:
        festivals = calendar_client.fetch_month_festivals(year, month)
        return festivals
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch month festivals: {str(e)}"
        )

@router.get("/upcoming", response_model=List[FestivalEvent])
async def get_upcoming_festivals(
    days_ahead: int = Query(default=180, ge=1, le=365, description="Days to look ahead")
):
    """
    Get upcoming festivals.
    
    Args:
        days_ahead: Number of days to look ahead (1-365)
    
    Returns:
        List of upcoming festival events
    
    Example:
        GET /calendar/upcoming?days_ahead=180
    """
    
    try:
        festivals = calendar_client.fetch_upcoming_festivals(days_ahead)
        return festivals
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch upcoming festivals: {str(e)}"
        )

@router.get("/range", response_model=List[FestivalEvent])
async def get_festivals_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get festivals within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        List of festival events in the range
    
    Example:
        GET /calendar/range?start_date=2025-11-01&end_date=2025-11-30
    """
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start > end:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before or equal to end_date"
            )
        
        festivals = calendar_client.fetch_festivals_range(start, end)
        return festivals
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch festivals: {str(e)}"
        )
