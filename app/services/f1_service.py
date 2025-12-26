"""
F1 Business Logic Service Layer

Provides independently testable business logic for F1 data processing.
All methods are static and have no HTTP dependencies, making them easy to test.
"""
from typing import Dict, Any, Optional, List, Set
from functools import lru_cache
from ..json_loader import load_drivers, load_constructors, load_season_results, get_available_seasons


class F1Service:
    """
    Service layer for F1 business logic.
    
    Separates business logic from HTTP routing for better testability and
    module independence (Constitution Principle VI).
    """
    
    @staticmethod
    def get_driver_statistics(
        driver_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate career statistics for a driver.
        
        Args:
            driver_id: The driver's unique identifier
            start_year: Optional start year (default: all available)
            end_year: Optional end year (default: all available)
        
        Returns:
            Dictionary containing:
                - driverId: str
                - statistics: Dict with totalRaces, wins, podiums, points, etc.
                - driverInfo: Optional Dict with personal information
                - note: Optional str if no race results found
        
        Raises:
            ValueError: If driver not found and has no race data
        """
        # Try to get driver info from drivers database
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
        
        # If driver has no race data at all, raise error
        if stats["totalRaces"] == 0 and not driver_info:
            raise ValueError(f"Driver '{driver_id}' not found and has no race data")
        
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
    
    @staticmethod
    def get_head_to_head_comparison(
        driver1_id: str,
        driver2_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compare two drivers head-to-head.
        
        Args:
            driver1_id: First driver ID
            driver2_id: Second driver ID
            start_year: Optional start year
            end_year: Optional end year
        
        Returns:
            Dictionary containing:
                - driver1: Dict with driverId and statistics
                - driver2: Dict with driverId and statistics
                - headToHead: Dict with race comparison data
        """
        # Get stats for both drivers
        driver1_stats_response = F1Service.get_driver_statistics(driver1_id, start_year, end_year)
        driver2_stats_response = F1Service.get_driver_statistics(driver2_id, start_year, end_year)
        
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
                        if driver_id == driver1_id:
                            driver1_result = result
                        elif driver_id == driver2_id:
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
                                better = driver1_id
                            elif pos2_int < pos1_int:
                                driver2_better += 1
                                better = driver2_id
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
                "driverId": driver1_id,
                "statistics": driver1_stats
            },
            "driver2": {
                "driverId": driver2_id,
                "statistics": driver2_stats
            },
            "headToHead": {
                "racesTogetherCount": len(head_to_head_races),
                "driver1Better": driver1_better,
                "driver2Better": driver2_better,
                "races": head_to_head_races
            }
        }
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_constructor_statistics(
        constructor_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate career statistics for a constructor.
        
        Args:
            constructor_id: The constructor's unique identifier
            start_year: Optional start year (default: all available)
            end_year: Optional end year (default: all available)
        
        Returns:
            Dictionary containing:
                - constructorId: str
                - statistics: Dict with totalRaces, wins, podiums, points, etc.
                - constructorInfo: Optional Dict with team information
                - note: Optional str if no race results found
        
        Raises:
            ValueError: If constructor not found and has no race data
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
            "totalWins": 0,
            "totalPodiums": 0,
            "totalPoints": 0.0,
            "totalPoles": 0,
            "totalFastestLaps": 0,
            "totalChampionships": 0,
            "drivers": set(),
            "seasons": [],
            "firstRace": None,
            "lastRace": None,
            "bestSeasonPosition": None,
            "bestSeasonYear": None
        }
        
        for year in available_seasons:
            try:
                season_data = load_season_results(year)
                races = season_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
                
                year_races: Set[str] = set()
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
                                try:
                                    pos_int = int(position)
                                    if pos_int == 1:
                                        year_wins += 1
                                        stats["totalWins"] += 1
                                    if pos_int <= 3:
                                        year_podiums += 1
                                        stats["totalPodiums"] += 1
                                except (ValueError, TypeError):
                                    pass
                            
                            # Grid position (pole) - check qualifying results
                            grid = result.get("grid")
                            if grid:
                                try:
                                    if int(grid) == 1:
                                        stats["totalPoles"] += 1
                                except (ValueError, TypeError):
                                    pass
                            
                            # Fastest lap
                            fastest_lap = result.get("FastestLap", {})
                            if fastest_lap.get("rank") == "1":
                                stats["totalFastestLaps"] += 1
                            
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
        
        # Calculate championship wins from standings data
        for year in available_seasons:
            try:
                season_data = load_season_results(year)
                standings_table = season_data.get("MRData", {}).get("StandingsTable", {})
                standings_lists = standings_table.get("StandingsLists", [])
                
                if standings_lists:
                    # Get final standings (last element)
                    final_standings = standings_lists[-1]
                    constructor_standings = final_standings.get("ConstructorStandings", [])
                    
                    for standing in constructor_standings:
                        if standing.get("Constructor", {}).get("constructorId") == constructor_id:
                            position = standing.get("position")
                            try:
                                pos_int = int(position)
                                
                                # Track best season position
                                if stats["bestSeasonPosition"] is None or pos_int < stats["bestSeasonPosition"]:
                                    stats["bestSeasonPosition"] = pos_int
                                    stats["bestSeasonYear"] = year
                                
                                # Championship win
                                if pos_int == 1:
                                    stats["totalChampionships"] += 1
                            except (ValueError, TypeError):
                                pass
                            break
            except FileNotFoundError:
                continue
        
        # If constructor has no race data at all, raise error
        if stats["totalRaces"] == 0 and not constructor_info:
            raise ValueError(f"Constructor '{constructor_id}' not found and has no race data")
        
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
    
    @staticmethod
    def get_fastest_laps_for_season(year: int, limit: int = 20) -> Dict[str, Any]:
        """
        Get fastest laps for a season.
        
        Args:
            year: Season year
            limit: Maximum number of results to return
        
        Returns:
            Dictionary containing:
                - season: int
                - fastestLaps: List of fastest lap records
                - count: Total count of fastest laps
        
        Raises:
            FileNotFoundError: If season data not found
        """
        season_data = load_season_results(year)
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
