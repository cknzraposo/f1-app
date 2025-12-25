"""
Constructor-related API endpoints

Thin HTTP handlers that delegate to service layer for business logic.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from ..json_loader import load_constructors, load_season_results, get_available_seasons
from ..services import F1Service

router = APIRouter(prefix="/api/constructors", tags=["Constructors"])


@router.get("")
def get_all_constructors() -> Dict[str, Any]:
    """
    Get all F1 constructors.
    Returns the complete constructors.json structure unchanged.
    """
    return load_constructors()


@router.get("/{constructor_id}")
def get_constructor(constructor_id: str) -> Dict[str, Any]:
    """
    Get a specific constructor by constructorId.
    
    Args:
        constructor_id: The constructor's unique identifier (e.g., 'red_bull')
    """
    constructors_data = load_constructors()
    constructors_list = constructors_data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])
    
    for constructor in constructors_list:
        if constructor.get("constructorId") == constructor_id:
            return {"MRData": {"ConstructorTable": {"Constructors": [constructor]}}}
    
    raise HTTPException(status_code=404, detail=f"Constructor '{constructor_id}' not found")


@router.get("/{constructor_id}/seasons/{year}")
def get_constructor_season_results(constructor_id: str, year: int) -> Dict[str, Any]:
    """
    Get all race results for a specific constructor in a specific season.
    
    Args:
        constructor_id: The constructor's unique identifier
        year: Season year (e.g., 2024)
    """
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
    
    races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    constructor_results = []
    
    for race in races:
        results = race.get("Results", [])
        race_results = []
        
        for result in results:
            if result.get("Constructor", {}).get("constructorId") == constructor_id:
                race_results.append(result)
        
        if race_results:
            race_copy = race.copy()
            race_copy["Results"] = race_results
            constructor_results.append(race_copy)
    
    # Return empty results with note instead of 404
    response = {
        "MRData": {
            "RaceTable": {
                "season": str(year),
                "constructorId": constructor_id,
                "Races": constructor_results
            }
        }
    }
    
    if not constructor_results:
        response["note"] = f"No results found for constructor '{constructor_id}' in season {year}"
    
    return response


@router.get("/{constructor_id}/stats")
def get_constructor_stats(
    constructor_id: str,
    start_year: Optional[int] = Query(None, description="Start year for stats calculation"),
    end_year: Optional[int] = Query(None, description="End year for stats calculation")
) -> Dict[str, Any]:
    """
    Calculate career statistics for a constructor.
    
    Thin HTTP handler that delegates to service layer.
    
    Args:
        constructor_id: The constructor's unique identifier
        start_year: Optional start year (default: all available)
        end_year: Optional end year (default: all available)
    """
    try:
        return F1Service.get_constructor_statistics(constructor_id, start_year, end_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
