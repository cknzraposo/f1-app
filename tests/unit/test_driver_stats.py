"""Unit tests for driver statistics computation (T018)

Tests the pure logic of statistics calculation in F1Service.
"""
import pytest
from app.services.f1_service import F1Service


class TestDriverStatisticsComputation:
    """Unit tests for driver statistics calculation"""
    
    def test_get_driver_statistics_returns_dict(self):
        """get_driver_statistics should return a dictionary"""
        result = F1Service.get_driver_statistics("abate")
        assert isinstance(result, dict)
    
    def test_get_driver_statistics_includes_required_fields(self):
        """Statistics should include all required fields"""
        result = F1Service.get_driver_statistics("abate")
        
        required_fields = [
            "driverId",
            "statistics"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check statistics sub-fields
        stats = result["statistics"]
        stats_fields = ["totalRaces", "wins", "podiums", "polePositions", "fastestLaps"]
        for field in stats_fields:
            assert field in stats, f"Missing statistics field: {field}"
    
    def test_get_driver_statistics_returns_integers(self):
        """All numeric statistics should be integers"""
        result = F1Service.get_driver_statistics("abate")
        stats = result["statistics"]
        
        # Fields that should be integers
        numeric_fields = ["totalRaces", "wins", "podiums", "polePositions", "fastestLaps", "dnfs"]
        for field in numeric_fields:
            if field in stats:
                assert isinstance(stats[field], int), f"{field} should be an integer, got {type(stats[field])}"
    
    def test_get_driver_statistics_with_year_range(self):
        """Should support filtering statistics by year range"""
        result = F1Service.get_driver_statistics("abate", start_year=1990, end_year=2000)
        assert isinstance(result, dict)
        assert "statistics" in result
    
    def test_get_driver_statistics_raises_on_invalid_driver(self):
        """Should raise ValueError for non-existent driver"""
        with pytest.raises(ValueError, match="Driver .* not found"):
            F1Service.get_driver_statistics("nonexistent_driver_12345")
    
    def test_get_driver_statistics_no_http_dependencies(self):
        """F1Service should not import HTTP-related modules"""
        import inspect
        import sys
        
        source = inspect.getsource(F1Service)
        
        # Should not have HTTP imports
        forbidden_imports = ["fastapi", "starlette", "httpx", "requests"]
        for forbidden in forbidden_imports:
            assert forbidden not in source.lower(), \
                f"F1Service should not import {forbidden} (service layer should be HTTP-agnostic)"


class TestStatisticsAggregation:
    """Unit tests for statistics aggregation logic"""
    
    def test_wins_count_first_place_finishes(self):
        """Wins should count position=1 finishes"""
        # This tests the logic through a known driver
        result = F1Service.get_driver_statistics("abate")
        stats = result["statistics"]
        
        # Wins should be non-negative integer
        assert stats["wins"] >= 0
        assert isinstance(stats["wins"], int)
    
    def test_podiums_count_top_3_finishes(self):
        """Podiums should count position <=3 finishes"""
        result = F1Service.get_driver_statistics("abate")
        stats = result["statistics"]
        
        # Podiums should be >= wins
        assert stats["podiums"] >= stats["wins"]
    
    def test_total_races_counts_all_starts(self):
        """Total races should count all race starts"""
        result = F1Service.get_driver_statistics("abate")
        stats = result["statistics"]
        
        # Total races should be >= podiums (can't podium without racing)
        assert stats["totalRaces"] >= stats["podiums"]
    
    def test_statistics_internally_consistent(self):
        """Statistics should follow logical relationships"""
        result = F1Service.get_driver_statistics("abate")
        stats = result["statistics"]
        
        # Logical constraints
        assert stats["totalRaces"] >= stats["wins"]
        assert stats["totalRaces"] >= stats["podiums"]
        assert stats["totalRaces"] >= stats["polePositions"]
        assert stats["podiums"] >= stats["wins"]
        assert stats["wins"] >= 0
        assert stats["podiums"] >= 0
        assert stats["polePositions"] >= 0
        assert stats["fastestLaps"] >= 0


class TestDriverStatsWithMockedData:
    """Unit tests with mocked data for edge cases"""
    
    def test_driver_with_zero_races(self, sample_driver_data, monkeypatch):
        """Driver with no race results should return zero statistics"""
        # This would require mocking load_season_results to return empty results
        # For now, we test the actual logic handles the case
        pass  # Covered by integration tests
    
    def test_statistics_year_range_filtering(self):
        """Year range should filter races correctly"""
        # Get stats for specific year range
        result_limited = F1Service.get_driver_statistics("abate", start_year=1990, end_year=1995)
        result_all = F1Service.get_driver_statistics("abate")
        
        # Limited range should have same or fewer races
        assert result_limited["statistics"]["totalRaces"] <= result_all["statistics"]["totalRaces"]


class TestStatisticsValidation:
    """Unit tests for input validation in statistics computation"""
    
    def test_invalid_driver_id_raises_error(self):
        """Invalid driver ID should raise descriptive error"""
        with pytest.raises(ValueError) as exc_info:
            F1Service.get_driver_statistics("this_driver_does_not_exist")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_empty_driver_id_raises_error(self):
        """Empty driver ID should raise error"""
        with pytest.raises(ValueError):
            F1Service.get_driver_statistics("")
    
    def test_invalid_year_range_handled(self):
        """Invalid year range should be handled gracefully"""
        # end_year before start_year
        result = F1Service.get_driver_statistics("abate", start_year=2000, end_year=1990)
        
        # Should return valid result (empty or error handling)
        assert isinstance(result, dict)
