"""
Constructor-related API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from ..json_loader import load_constructors, load_season_results, get_available_seasons

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
    
    Args:
        constructor_id: The constructor's unique identifier
        start_year: Optional start year (default: all available)
        end_year: Optional end year (default: all available)
    """
    # Try to get constructor info from constructors database
    constructors_data = load_constructors()
    constructors_list = constructors_data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])
    
    constructor_info = None
    for constructor in constructors_list:
        if constructor.get("constructorId") == constructor_id:
            constructor_info = constructor
            break
    
    available_seasons = get_available_seasons()
    
    if start_year:
        available_seasons = [y for y in available_seasons if y >= start_year]
    if end_year:
        available_seasons = [y for y in available_seasons if y <= end_year]
    
    stats = {
        "constructorId": constructor_id,
        "totalRaces": 0,
        "wins": 0,
        "podiums": 0,
        "totalPoints": 0.0,
        "polePositions": 0,
        "fastestLaps": 0,
        "drivers": set(),
        "seasons": [],
        "firstRace": None,
        "lastRace": None
    }
    
    for year in available_seasons:
        try:
            season_data = load_season_results(year)
            races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            
            year_races = set()
            year_wins = 0
            year_podiums = 0
            year_points = 0.0
            
            for race in races:
                results = race.get("Results", [])
                race_participated = False
                
                for result in results:
                    if result.get("Constructor", {}).get("constructorId") == constructor_id:
                        if not race_participated:
                            race_participated = True
                            year_races.add(race.get("round"))
                            stats["totalRaces"] += 1
                            
                            # Track first and last race
                            race_date = race.get("date", "")
                            if not stats["firstRace"] or race_date < stats["firstRace"]["date"]:
                                stats["firstRace"] = {
                                    "date": race_date,
                                    "raceName": race.get("raceName"),
                                    "season": year
                                }
                            if not stats["lastRace"] or race_date > stats["lastRace"]["date"]:
                                stats["lastRace"] = {
                                    "date": race_date,
                                    "raceName": race.get("raceName"),
                                    "season": year
                                }
                        
                        # Position stats
                        position = result.get("position")
                        if position:
                            pos_int = int(position)
                            if pos_int == 1:
                                year_wins += 1
                                stats["wins"] += 1
                            if pos_int <= 3:
                                year_podiums += 1
                                stats["podiums"] += 1
                        
                        # Grid position (pole)
                        grid = result.get("grid")
                        if grid and int(grid) == 1:
                            stats["polePositions"] += 1
                        
                        # Fastest lap
                        fastest_lap = result.get("FastestLap", {})
                        if fastest_lap.get("rank") == "1":
                            stats["fastestLaps"] += 1
                        
                        # Points
                        points = float(result.get("points", 0))
                        stats["totalPoints"] += points
                        year_points += points
                        
                        # Drivers
                        driver_id = result.get("Driver", {}).get("driverId")
                        if driver_id:
                            stats["drivers"].add(driver_id)
            
            if len(year_races) > 0:
                stats["seasons"].append({
                    "season": year,
                    "races": len(year_races),
                    "wins": year_wins,
                    "podiums": year_podiums,
                    "points": year_points
                })
        
        except FileNotFoundError:
            continue
    
    # If constructor has no race data at all, return 404
    if stats["totalRaces"] == 0 and not constructor_info:
        raise HTTPException(
            status_code=404,
            detail=f"Constructor '{constructor_id}' not found and has no race data"
        )
    
    # Convert set to sorted list
    stats["drivers"] = sorted(list(stats["drivers"]))
    
    # Build response
    response = {
        "constructorId": constructor_id,
        "statistics": stats
    }
    
    # Add constructor info if available
    if constructor_info:
        response["constructorInfo"] = {
            "name": constructor_info.get("name"),
            "nationality": constructor_info.get("nationality"),
            "url": constructor_info.get("url")
        }
        if stats["totalRaces"] == 0:
            response["note"] = "No race results found in available seasons (1984-2024)"
    
    return response
