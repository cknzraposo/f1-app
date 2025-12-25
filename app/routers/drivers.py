"""
Driver-related API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from ..json_loader import load_drivers, load_season_results, get_available_seasons

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
    """
    drivers_data = load_drivers()
    drivers_list = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
    
    for driver in drivers_list:
        if driver.get("driverId") == driver_id:
            return {"MRData": {"DriverTable": {"Drivers": [driver]}}}
    
    raise HTTPException(status_code=404, detail=f"Driver '{driver_id}' not found")


@router.get("/{driver_id}/seasons/{year}")
def get_driver_season_results(driver_id: str, year: int) -> Dict[str, Any]:
    """
    Get all race results for a specific driver in a specific season.
    
    Args:
        driver_id: The driver's unique identifier
        year: Season year (e.g., 2024)
    """
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
    
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
    
    Args:
        driver_id: The driver's unique identifier
        start_year: Optional start year (default: all available)
        end_year: Optional end year (default: all available)
    
    Returns:
        Statistics including races, wins, podiums, points, and teams
    """
    # Try to get driver info from drivers database (may not exist for recent drivers)
    drivers_data = load_drivers()
    drivers_list = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
    
    driver_info = None
    for driver in drivers_list:
        if driver.get("driverId") == driver_id:
            driver_info = driver
            break
    
    available_seasons = get_available_seasons()
    
    if start_year:
        available_seasons = [y for y in available_seasons if y >= start_year]
    if end_year:
        available_seasons = [y for y in available_seasons if y <= end_year]
    
    stats = {
        "driverId": driver_id,
        "totalRaces": 0,
        "wins": 0,
        "podiums": 0,
        "totalPoints": 0.0,
        "polePositions": 0,
        "fastestLaps": 0,
        "dnfs": 0,
        "teams": set(),
        "seasons": [],
        "firstRace": None,
        "lastRace": None
    }
    
    for year in available_seasons:
        try:
            season_data = load_season_results(year)
            races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            
            year_races = 0
            year_wins = 0
            year_podiums = 0
            year_points = 0.0
            
            for race in races:
                results = race.get("Results", [])
                for result in results:
                    if result.get("Driver", {}).get("driverId") == driver_id:
                        year_races += 1
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
                                stats["wins"] += 1
                                year_wins += 1
                            if pos_int <= 3:
                                stats["podiums"] += 1
                                year_podiums += 1
                        
                        # Grid position (pole)
                        grid = result.get("grid")
                        if grid and int(grid) == 1:
                            stats["polePositions"] += 1
                        
                        # Fastest lap
                        fastest_lap = result.get("FastestLap", {})
                        if fastest_lap.get("rank") == "1":
                            stats["fastestLaps"] += 1
                        
                        # DNF detection
                        status = result.get("status", "")
                        if status != "Finished" and not status.startswith("+"):
                            stats["dnfs"] += 1
                        
                        # Points
                        points = float(result.get("points", 0))
                        stats["totalPoints"] += points
                        year_points += points
                        
                        # Teams
                        constructor = result.get("Constructor", {}).get("name")
                        if constructor:
                            stats["teams"].add(constructor)
                        
                        break
            
            if year_races > 0:
                stats["seasons"].append({
                    "season": year,
                    "races": year_races,
                    "wins": year_wins,
                    "podiums": year_podiums,
                    "points": year_points
                })
        
        except FileNotFoundError:
            continue
    
    # If driver has no race data at all, return 404
    if stats["totalRaces"] == 0 and not driver_info:
        raise HTTPException(
            status_code=404,
            detail=f"Driver '{driver_id}' not found and has no race data"
        )
    
    # Convert set to sorted list
    stats["teams"] = sorted(list(stats["teams"]))
    
    # Build response
    response = {
        "driverId": driver_id,
        "statistics": stats
    }
    
    # Add driver info if available
    if driver_info:
        response["driverInfo"] = {
            "givenName": driver_info.get("givenName"),
            "familyName": driver_info.get("familyName"),
            "dateOfBirth": driver_info.get("dateOfBirth"),
            "nationality": driver_info.get("nationality"),
            "url": driver_info.get("url")
        }
        if stats["totalRaces"] == 0:
            response["note"] = "No race results found in available seasons (1984-2024)"
    
    return response
