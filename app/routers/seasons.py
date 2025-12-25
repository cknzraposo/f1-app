"""
Season-related API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ..json_loader import load_season_results, get_available_seasons

router = APIRouter(prefix="/api/seasons", tags=["Seasons"])


@router.get("")
def get_seasons() -> Dict[str, Any]:
    """
    Get list of available seasons.
    """
    seasons = get_available_seasons()
    return {
        "seasons": seasons,
        "count": len(seasons),
        "firstSeason": min(seasons) if seasons else None,
        "lastSeason": max(seasons) if seasons else None
    }


@router.get("/{year}")
def get_season(year: int) -> Dict[str, Any]:
    """
    Get all race data for a specific season.
    Returns the complete season JSON structure unchanged.
    
    Args:
        year: Season year (e.g., 2024)
    """
    try:
        return load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")


@router.get("/{year}/races/{round}")
def get_race(year: int, round: int) -> Dict[str, Any]:
    """
    Get results for a specific race in a season.
    
    Args:
        year: Season year
        round: Race round number (1-based)
    """
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
    
    races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    
    for race in races:
        if int(race.get("round", 0)) == round:
            return {"MRData": {"RaceTable": {"Races": [race]}}}
    
    raise HTTPException(
        status_code=404,
        detail=f"Round {round} not found in season {year}"
    )


@router.get("/{year}/standings")
def get_season_standings(year: int) -> Dict[str, Any]:
    """
    Calculate driver and constructor championship standings for a season.
    Aggregates points from all races.
    
    Args:
        year: Season year
    """
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
    
    races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    
    driver_points = {}
    constructor_points = {}
    driver_constructors = {}  # Track primary constructor for each driver
    
    for race in races:
        results = race.get("Results", [])
        for result in results:
            # Driver standings
            driver_id = result.get("Driver", {}).get("driverId")
            driver_name = f"{result.get('Driver', {}).get('givenName', '')} {result.get('Driver', {}).get('familyName', '')}"
            points = float(result.get("points", 0))
            constructor_id = result.get("Constructor", {}).get("constructorId")
            constructor_name = result.get("Constructor", {}).get("name")
            
            if driver_id:
                if driver_id not in driver_points:
                    driver_points[driver_id] = {
                        "driverId": driver_id,
                        "name": driver_name,
                        "nationality": result.get("Driver", {}).get("nationality"),
                        "points": 0.0,
                        "wins": 0,
                        "podiums": 0
                    }
                    # Track first constructor as primary
                    driver_constructors[driver_id] = {
                        "constructorId": constructor_id,
                        "name": constructor_name
                    }
                
                driver_points[driver_id]["points"] += points
                
                position = result.get("position")
                if position:
                    pos_int = int(position)
                    if pos_int == 1:
                        driver_points[driver_id]["wins"] += 1
                    if pos_int <= 3:
                        driver_points[driver_id]["podiums"] += 1
            
            # Constructor standings
            constructor_id = result.get("Constructor", {}).get("constructorId")
            constructor_name = result.get("Constructor", {}).get("name")
            
            if constructor_id:
                if constructor_id not in constructor_points:
                    constructor_points[constructor_id] = {
                        "constructorId": constructor_id,
                        "name": constructor_name,
                        "nationality": result.get("Constructor", {}).get("nationality"),
                        "points": 0.0,
                        "wins": 0
                    }
                
                constructor_points[constructor_id]["points"] += points
                
                position = result.get("position")
                if position and int(position) == 1:
                    constructor_points[constructor_id]["wins"] += 1
    
    # Sort by points (descending)
    driver_standings = sorted(
        driver_points.values(),
        key=lambda x: (-x["points"], -x["wins"])
    )
    
    constructor_standings = sorted(
        constructor_points.values(),
        key=lambda x: (-x["points"], -x["wins"])
    )
    
    # Add positions
    for i, driver in enumerate(driver_standings, 1):
        driver["position"] = i
        # Add constructor info
        if driver["driverId"] in driver_constructors:
            driver["constructor"] = driver_constructors[driver["driverId"]]["name"]
            driver["constructorId"] = driver_constructors[driver["driverId"]]["constructorId"]
    
    for i, constructor in enumerate(constructor_standings, 1):
        constructor["position"] = i
    
    return {
        "season": year,
        "driverStandings": driver_standings,
        "constructorStandings": constructor_standings
    }


@router.get("/{year}/winners")
def get_season_winners(year: int) -> Dict[str, Any]:
    """
    Get list of race winners for a season.
    
    Args:
        year: Season year
    """
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
    
    races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    winners = []
    
    for race in races:
        results = race.get("Results", [])
        for result in results:
            if result.get("position") == "1":
                winners.append({
                    "round": race.get("round"),
                    "raceName": race.get("raceName"),
                    "circuit": race.get("Circuit", {}).get("circuitName"),
                    "date": race.get("date"),
                    "driver": {
                        "driverId": result.get("Driver", {}).get("driverId"),
                        "name": f"{result.get('Driver', {}).get('givenName', '')} {result.get('Driver', {}).get('familyName', '')}",
                        "nationality": result.get("Driver", {}).get("nationality")
                    },
                    "constructor": {
                        "constructorId": result.get("Constructor", {}).get("constructorId"),
                        "name": result.get("Constructor", {}).get("name")
                    },
                    "grid": result.get("grid"),
                    "time": result.get("Time", {}).get("time") if "Time" in result else None
                })
                break
    
    return {
        "season": year,
        "winners": winners,
        "count": len(winners)
    }
