"""
Analytics and statistical API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional

from ..json_loader import load_season_results, get_available_seasons

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
    Shows their career stats and races where they competed against each other.
    
    Args:
        driver1: First driver ID
        driver2: Second driver ID
        start_year: Optional start year
        end_year: Optional end year
    """
    # Import here to avoid circular dependency
    from .drivers import get_driver_stats
    
    # Get stats for both drivers
    driver1_stats_response = get_driver_stats(driver1, start_year, end_year)
    driver2_stats_response = get_driver_stats(driver2, start_year, end_year)
    
    driver1_stats = driver1_stats_response["statistics"]
    driver2_stats = driver2_stats_response["statistics"]
    
    # Find races where they competed together
    available_seasons = get_available_seasons()
    
    if start_year:
        available_seasons = [y for y in available_seasons if y >= start_year]
    if end_year:
        available_seasons = [y for y in available_seasons if y <= end_year]
    
    head_to_head_races = []
    driver1_better = 0
    driver2_better = 0
    
    for year in available_seasons:
        try:
            season_data = load_season_results(year)
            races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            
            for race in races:
                results = race.get("Results", [])
                driver1_result = None
                driver2_result = None
                
                for result in results:
                    driver_id = result.get("Driver", {}).get("driverId")
                    if driver_id == driver1:
                        driver1_result = result
                    elif driver_id == driver2:
                        driver2_result = result
                
                if driver1_result and driver2_result:
                    # Both competed in this race
                    pos1 = driver1_result.get("positionText", "")
                    pos2 = driver2_result.get("positionText", "")
                    
                    # Compare positions (lower is better)
                    try:
                        pos1_int = int(driver1_result.get("position", 999))
                        pos2_int = int(driver2_result.get("position", 999))
                        
                        if pos1_int < pos2_int:
                            driver1_better += 1
                            better = driver1
                        elif pos2_int < pos1_int:
                            driver2_better += 1
                            better = driver2
                        else:
                            better = "tie"
                    except (ValueError, TypeError):
                        better = "unknown"
                    
                    head_to_head_races.append({
                        "season": year,
                        "round": race.get("round"),
                        "raceName": race.get("raceName"),
                        "date": race.get("date"),
                        "driver1Position": pos1,
                        "driver2Position": pos2,
                        "better": better
                    })
        
        except FileNotFoundError:
            continue
    
    return {
        "driver1": {
            "driverId": driver1,
            "statistics": driver1_stats
        },
        "driver2": {
            "driverId": driver2,
            "statistics": driver2_stats
        },
        "headToHead": {
            "racesTogetherCount": len(head_to_head_races),
            "driver1Better": driver1_better,
            "driver2Better": driver2_better,
            "races": head_to_head_races
        }
    }


@router.get("/fastest-laps/{year}")
def get_fastest_laps(year: int, limit: int = Query(20, description="Number of results to return")) -> Dict[str, Any]:
    """
    Get fastest laps for a season.
    Lists drivers with fastest laps and their average speeds.
    
    Args:
        year: Season year
        limit: Maximum number of results to return
    """
    try:
        season_data = load_season_results(year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Season {year} data not found")
    
    races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    fastest_laps = []
    
    for race in races:
        results = race.get("Results", [])
        for result in results:
            fastest_lap = result.get("FastestLap", {})
            if fastest_lap:
                avg_speed = fastest_lap.get("AverageSpeed", {})
                fastest_laps.append({
                    "round": race.get("round"),
                    "raceName": race.get("raceName"),
                    "circuit": race.get("Circuit", {}).get("circuitName"),
                    "driver": {
                        "driverId": result.get("Driver", {}).get("driverId"),
                        "name": f"{result.get('Driver', {}).get('givenName', '')} {result.get('Driver', {}).get('familyName', '')}",
                    },
                    "constructor": result.get("Constructor", {}).get("name"),
                    "lap": fastest_lap.get("lap"),
                    "time": fastest_lap.get("Time", {}).get("time"),
                    "rank": fastest_lap.get("rank"),
                    "averageSpeed": {
                        "value": avg_speed.get("speed"),
                        "units": avg_speed.get("units")
                    } if avg_speed else None
                })
    
    # Sort by rank (fastest lap award winners first, then by time if needed)
    fastest_laps.sort(key=lambda x: (int(x["rank"]) if x["rank"] else 999, x["time"] or ""))
    
    return {
        "season": year,
        "fastestLaps": fastest_laps[:limit],
        "count": len(fastest_laps)
    }
