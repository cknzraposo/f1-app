"""
Analytics and statistical API endpoints

Thin HTTP handlers that delegate to service layer for business logic.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from ..services import F1Service

router = APIRouter(prefix="/api/stats", tags=["Analytics"])


@router.get("/head-to-head")
def get_head_to_head(
    driver1: str = Query(..., description="First driver ID"),
    driver2: str = Query(..., description="Second driver ID"),
    start_year: Optional[int] = Query(None, description="Start year"),
    end_year: Optional[int] = Query(None, description="End year")
) -> Dict[str, Any]:
    """
    Compare two drivers head-to-head.
    
    Thin HTTP handler that delegates to service layer.
    
    Args:
        driver1: First driver ID
        driver2: Second driver ID
        start_year: Optional start year
        end_year: Optional end year
    """
    try:
        return F1Service.get_head_to_head_comparison(driver1, driver2, start_year, end_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/fastest-laps/{year}")
def get_fastest_laps(year: int, limit: int = Query(20, description="Number of results to return")) -> Dict[str, Any]:
    """
    Get fastest laps for a season.
    
    Thin HTTP handler that delegates to service layer.
    
    Args:
        year: Season year
        limit: Maximum number of results to return
    """
    try:
        return F1Service.get_fastest_laps_for_season(year, limit)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
