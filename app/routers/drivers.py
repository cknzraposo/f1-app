"""
Driver-related API endpoints

Thin HTTP handlers that delegate to service layer for business logic.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional
from difflib import get_close_matches

from ..json_loader import load_drivers, load_season_results, get_available_seasons
from ..services import F1Service
from ..services.validation import validate_driver_id, get_available_driver_ids

router = APIRouter(prefix="/api/drivers", tags=["Drivers"])


@router.get("")
def get_all_drivers() -> Dict[str, Any]:
    """
    Get all F1 drivers.
    Returns the complete drivers.json structure unchanged.
    """
    return load_drivers()


@router.get("/search")
def search_drivers(
    name: Optional[str] = Query(None, description="Search by driver name (case-insensitive)"),
    nationality: Optional[str] = Query(None, description="Filter by nationality")
) -> Dict[str, Any]:
    """
    Search for drivers by name or nationality.
    
    Args:
        name: Search term for driver name (searches givenName and familyName)
        nationality: Filter by exact nationality
    """
    drivers_data = load_drivers()
    drivers_list = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
    
    filtered_drivers = drivers_list
    
    if name:
        name_lower = name.lower()
        filtered_drivers = [
            d for d in filtered_drivers
            if name_lower in d.get("givenName", "").lower() or
               name_lower in d.get("familyName", "").lower() or
               name_lower in f"{d.get('givenName', '')} {d.get('familyName', '')}".lower()
        ]
    
    if nationality:
        filtered_drivers = [
            d for d in filtered_drivers
            if d.get("nationality", "").lower() == nationality.lower()
        ]
    
    return {
        "MRData": {
            "DriverTable": {
                "Drivers": filtered_drivers
            }
        }
    }


@router.get("/{driver_id}")
def get_driver(driver_id: str) -> Dict[str, Any]:
    """
    Get a specific driver by driverId.
    
    Args:
        driver_id: The driver's unique identifier (e.g., 'max_verstappen')
        
    Raises:
        HTTPException 404: If driver not found, with suggestions for similar drivers
    """
    drivers_data = load_drivers()
    drivers_list = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
    
    for driver in drivers_list:
        if driver.get("driverId") == driver_id:
            return {"MRData": {"DriverTable": {"Drivers": [driver]}}}
    
    # Driver not found - provide helpful suggestions
    all_driver_ids = [d.get("driverId") for d in drivers_list if d.get("driverId")]
    suggestions = get_close_matches(driver_id, all_driver_ids, n=5, cutoff=0.6)
    
    error_message = f"Driver '{driver_id}' not found."
    if suggestions:
        error_message += f" Did you mean: {', '.join(suggestions)}?"
    
    raise HTTPException(status_code=404, detail=error_message)


@router.get("/{driver_id}/seasons/{year}")
def get_driver_season_results(driver_id: str, year: int) -> Dict[str, Any]:
    """
    Get all race results for a specific driver in a specific season.
    
    Args:
        driver_id: The driver's unique identifier
        year: Season year (e.g., 2024)
        
    Raises:
        HTTPException 404: If season data not found or driver not recognized
    """
    # Check if driver exists first
    drivers_data = load_drivers()
    drivers_list = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
    driver_exists = any(d.get("driverId") == driver_id for d in drivers_list)
    
    if not driver_exists:
        all_driver_ids = [d.get("driverId") for d in drivers_list if d.get("driverId")]
        suggestions = get_close_matches(driver_id, all_driver_ids, n=3, cutoff=0.6)
        error_message = f"Driver '{driver_id}' not found."
        if suggestions:
            error_message += f" Did you mean: {', '.join(suggestions)}?"
        raise HTTPException(status_code=404, detail=error_message)
    
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        available_years = get_available_seasons()
        error_message = f"Season {year} data not found. Available years: {min(available_years)}-{max(available_years)}"
        raise HTTPException(status_code=404, detail=error_message)
    
    # Filter results for specific driver
    races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    driver_results = []
    
    for race in races:
        results = race.get("Results", [])
        for result in results:
            if result.get("Driver", {}).get("driverId") == driver_id:
                # Create a copy of the race with only this driver's result
                race_copy = race.copy()
                race_copy["Results"] = [result]
                driver_results.append(race_copy)
                break
    
    # Return empty results with note instead of 404
    response = {
        "MRData": {
            "RaceTable": {
                "season": str(year),
                "driverId": driver_id,
                "Races": driver_results
            }
        }
    }
    
    if not driver_results:
        response["note"] = f"No race results found for driver '{driver_id}' in season {year}"
    
    return response


@router.get("/{driver_id}/stats")
def get_driver_stats(
    driver_id: str,
    start_year: Optional[int] = Query(None, description="Start year for stats calculation"),
    end_year: Optional[int] = Query(None, description="End year for stats calculation")
) -> Dict[str, Any]:
    """
    Calculate career statistics for a driver.
    
    Thin HTTP handler that delegates to service layer.
    
    Args:
        driver_id: The driver's unique identifier
        start_year: Optional start year (default: all available)
        end_year: Optional end year (default: all available)
    
    Returns:
        Statistics including races, wins, podiums, points, and teams
    """
    try:
        return F1Service.get_driver_statistics(driver_id, start_year, end_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
