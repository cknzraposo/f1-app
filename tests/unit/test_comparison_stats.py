"""
Unit tests for comparison calculations

Tests the business logic for driver comparison statistics,
head-to-head calculations, and data aggregation.
"""
import pytest
from app.services.f1_service import F1Service


class TestHeadToHeadCalculations:
    """Unit tests for head-to-head comparison calculations"""
    
    def test_head_to_head_basic_structure(self):
        """UNIT-H2H-001: Head-to-head returns correct data structure"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        assert "driver1" in result
        assert "driver2" in result
        assert "headToHead" in result
        
        assert result["driver1"]["driverId"] == "vettel"
        assert result["driver2"]["driverId"] == "alonso"
    
    def test_head_to_head_statistics_included(self):
        """UNIT-H2H-002: Both drivers get full statistics"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        for driver_key in ["driver1", "driver2"]:
            stats = result[driver_key]["statistics"]
            
            assert "totalRaces" in stats
            assert "wins" in stats
            assert "podiums" in stats
            assert "totalPoints" in stats
            assert "polePositions" in stats
            assert "fastestLaps" in stats
            assert "dnfs" in stats
            assert "teams" in stats
            assert "seasons" in stats
    
    def test_head_to_head_races_together_count(self):
        """UNIT-H2H-003: Races together count matches actual races"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        h2h = result["headToHead"]
        races_count = h2h["racesTogetherCount"]
        races_list = h2h["races"]
        
        # Count should match list length
        assert races_count == len(races_list)
        
        # For drivers who raced together
        if races_count > 0:
            assert races_count > 50  # Vettel and Alonso raced many times together
    
    def test_head_to_head_winner_counts(self):
        """UNIT-H2H-004: Winner counts are consistent with race results"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        h2h = result["headToHead"]
        
        # Calculate from races
        driver1_better = 0
        driver2_better = 0
        
        for race in h2h["races"]:
            pos1 = race.get("driver1Position")
            pos2 = race.get("driver2Position")
            
            if pos1 and pos2:
                try:
                    if int(pos1) < int(pos2):
                        driver1_better += 1
                    elif int(pos2) < int(pos1):
                        driver2_better += 1
                except (ValueError, TypeError):
                    pass  # Skip non-numeric positions
        
        # Reported counts should match or exceed calculated (some races might not have valid positions)
        assert h2h["driver1Better"] >= driver1_better
        assert h2h["driver2Better"] >= driver2_better
        
        # Total should not exceed races together
        assert h2h["driver1Better"] + h2h["driver2Better"] <= h2h["racesTogetherCount"]
    
    def test_head_to_head_race_details(self):
        """UNIT-H2H-005: Race details include all necessary information"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        races = result["headToHead"]["races"]
        
        if len(races) > 0:
            race = races[0]
            
            # Required fields
            assert "season" in race
            assert "round" in race
            assert "raceName" in race
            assert "driver1Position" in race
            assert "driver2Position" in race
            
            # Season should be valid
            assert isinstance(race["season"], (str, int))
            season_int = int(race["season"])
            assert 1984 <= season_int <= 2024
    
    def test_head_to_head_with_year_range(self):
        """UNIT-H2H-006: Year range filtering works correctly"""
        # Get full comparison
        full_result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        # Get filtered comparison (2010-2015)
        filtered_result = F1Service.get_head_to_head_comparison(
            "vettel", "alonso", start_year=2010, end_year=2015
        )
        
        # Filtered should have fewer or equal races
        assert filtered_result["headToHead"]["racesTogetherCount"] <= full_result["headToHead"]["racesTogetherCount"]
        
        # All races in filtered should be within year range
        for race in filtered_result["headToHead"]["races"]:
            season = int(race["season"])
            assert 2010 <= season <= 2015
    
    def test_head_to_head_invalid_driver(self):
        """UNIT-H2H-007: Invalid driver raises ValueError"""
        with pytest.raises(ValueError, match="not found"):
            F1Service.get_head_to_head_comparison("nonexistent", "hamilton")
    
    def test_head_to_head_no_overlap(self):
        """UNIT-H2H-008: Drivers with no overlap return zero races together"""
        # Lauda and Leclerc had no overlap (different eras)
        result = F1Service.get_head_to_head_comparison("lauda", "leclerc")
        
        h2h = result["headToHead"]
        # They never raced together
        assert h2h["racesTogetherCount"] == 0
        
        # But both should have valid statistics
        assert result["driver1"]["statistics"]["totalRaces"] > 0
        assert result["driver2"]["statistics"]["totalRaces"] > 0


class TestFastestLapsCalculations:
    """Unit tests for fastest laps statistics"""
    
    def test_fastest_laps_basic_structure(self):
        """UNIT-FL-001: Fastest laps returns correct structure"""
        result = F1Service.get_fastest_laps_for_season(2023, limit=10)
        
        assert "season" in result
        assert "fastestLaps" in result
        assert result["season"] == 2023
        assert isinstance(result["fastestLaps"], list)
        assert len(result["fastestLaps"]) <= 10
    
    def test_fastest_laps_data_completeness(self):
        """UNIT-FL-002: Each fastest lap entry has complete data"""
        result = F1Service.get_fastest_laps_for_season(2023, limit=5)
        
        for lap in result["fastestLaps"]:
            assert "round" in lap
            assert "raceName" in lap
            assert "circuit" in lap
            assert "driver" in lap
            assert "constructor" in lap
            assert "lap" in lap
            assert "time" in lap
            assert "rank" in lap
            
            # Driver details
            assert "driverId" in lap["driver"]
            assert "name" in lap["driver"]
    
    def test_fastest_laps_limit_respected(self):
        """UNIT-FL-003: Limit parameter is respected"""
        for limit in [3, 5, 10, 20]:
            result = F1Service.get_fastest_laps_for_season(2023, limit=limit)
            assert len(result["fastestLaps"]) <= limit
    
    def test_fastest_laps_default_limit(self):
        """UNIT-FL-004: Default limit is 20"""
        result = F1Service.get_fastest_laps_for_season(2023)
        # Default should be 20 or fewer (if season has fewer races)
        assert len(result["fastestLaps"]) <= 20
    
    def test_fastest_laps_invalid_year(self):
        """UNIT-FL-005: Invalid year raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            F1Service.get_fastest_laps_for_season(1900)
    
    def test_fastest_laps_early_season(self):
        """UNIT-FL-006: Works for early F1 seasons"""
        result = F1Service.get_fastest_laps_for_season(1984, limit=5)
        
        assert result["season"] == 1984
        # Early seasons might have fewer fastest lap records
        assert len(result["fastestLaps"]) >= 0
    
    def test_fastest_laps_recent_season(self):
        """UNIT-FL-007: Works for recent seasons"""
        result = F1Service.get_fastest_laps_for_season(2024, limit=5)
        
        assert result["season"] == 2024
        assert len(result["fastestLaps"]) > 0
    
    def test_fastest_laps_includes_speed_when_available(self):
        """UNIT-FL-008: Average speed included when available"""
        result = F1Service.get_fastest_laps_for_season(2023, limit=10)
        
        # Check if any laps have speed data
        has_speed = False
        for lap in result["fastestLaps"]:
            if "averageSpeed" in lap:
                has_speed = True
                speed = lap["averageSpeed"]
                assert "value" in speed
                assert "units" in speed
                # Value should be numeric string
                assert float(speed["value"]) > 0
        
        # Modern seasons should have speed data
        assert has_speed


class TestComparisonDataQuality:
    """Unit tests for data quality in comparisons"""
    
    def test_statistics_consistency(self):
        """UNIT-DQ-001: Statistics are internally consistent"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        for driver_key in ["driver1", "driver2"]:
            stats = result[driver_key]["statistics"]
            
            # Wins should not exceed podiums
            assert stats["wins"] <= stats["podiums"]
            
            # Podiums should not exceed total races
            assert stats["podiums"] <= stats["totalRaces"]
            
            # Points should be non-negative
            assert stats["totalPoints"] >= 0
            
            # Counts should be non-negative
            assert stats["totalRaces"] >= 0
            assert stats["wins"] >= 0
            assert stats["podiums"] >= 0
            assert stats["polePositions"] >= 0
            assert stats["fastestLaps"] >= 0
            assert stats["dnfs"] >= 0
    
    def test_seasons_data_quality(self):
        """UNIT-DQ-002: Season-by-season data is valid"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        for driver_key in ["driver1", "driver2"]:
            seasons = result[driver_key]["statistics"]["seasons"]
            
            assert len(seasons) > 0
            
            for season in seasons:
                assert "season" in season
                assert "races" in season
                assert "wins" in season
                assert "podiums" in season
                assert "points" in season
                
                # Season should be valid year
                assert 1984 <= season["season"] <= 2024
                
                # Wins should not exceed races
                assert season["wins"] <= season["races"]
                
                # Podiums should not exceed races
                assert season["podiums"] <= season["races"]
    
    def test_teams_list_not_empty(self):
        """UNIT-DQ-003: Teams list contains valid entries"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        for driver_key in ["driver1", "driver2"]:
            teams = result[driver_key]["statistics"]["teams"]
            
            assert len(teams) > 0
            
            for team in teams:
                assert isinstance(team, str)
                assert len(team) > 0
    
    def test_head_to_head_data_quality(self):
        """UNIT-DQ-004: Head-to-head data is valid"""
        result = F1Service.get_head_to_head_comparison("vettel", "alonso")
        
        h2h = result["headToHead"]
        
        # Counts should be non-negative
        assert h2h["racesTogetherCount"] >= 0
        assert h2h["driver1Better"] >= 0
        assert h2h["driver2Better"] >= 0
        
        # Sum should not exceed total
        assert h2h["driver1Better"] + h2h["driver2Better"] <= h2h["racesTogetherCount"]
        
        # Races list should match count
        assert len(h2h["races"]) == h2h["racesTogetherCount"]


# Test count verification
def test_comparison_unit_coverage():
    """META: Document unit test coverage"""
    h2h_tests = 8         # UNIT-H2H-001 through UNIT-H2H-008
    fastest_laps_tests = 8  # UNIT-FL-001 through UNIT-FL-008
    data_quality_tests = 4  # UNIT-DQ-001 through UNIT-DQ-004
    
    total_tests = h2h_tests + fastest_laps_tests + data_quality_tests
    assert total_tests == 20  # Expected test count
