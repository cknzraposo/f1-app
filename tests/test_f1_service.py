"""
Tests for F1Service business logic layer.

These tests verify Constitution Principle VI compliance:
- Functions are independently testable without extensive mocking
- Business logic is separated from HTTP concerns
- Module has single, well-defined responsibility
"""
import pytest
from app.services.f1_service import F1Service


class TestDriverStatistics:
    """Test driver statistics calculation."""
    
    def test_get_driver_statistics_returns_correct_structure(self):
        """
        Test that get_driver_statistics returns expected data structure.
        
        Validates:
        - Returns dict with driverId and statistics keys
        - Statistics contains required fields
        """
        # Use a known driver (Lewis Hamilton)
        result = F1Service.get_driver_statistics("hamilton", start_year=2023, end_year=2023)
        
        # Verify structure
        assert "driverId" in result
        assert "statistics" in result
        assert result["driverId"] == "hamilton"
        
        # Verify statistics fields
        stats = result["statistics"]
        assert "totalRaces" in stats
        assert "wins" in stats
        assert "podiums" in stats
        assert "totalPoints" in stats
        assert "polePositions" in stats
        assert "fastestLaps" in stats
        assert "dnfs" in stats
        assert "teams" in stats
        assert "seasons" in stats
        
        # Verify 2023 had races
        assert stats["totalRaces"] > 0
    
    def test_get_driver_statistics_handles_year_range(self):
        """Test that year range filtering works correctly."""
        # Get stats for 2023 only
        result_2023 = F1Service.get_driver_statistics("hamilton", start_year=2023, end_year=2023)
        
        # Get stats for 2022-2023
        result_2022_2023 = F1Service.get_driver_statistics("hamilton", start_year=2022, end_year=2023)
        
        # 2022-2023 should have more races than 2023 alone
        assert result_2022_2023["statistics"]["totalRaces"] > result_2023["statistics"]["totalRaces"]
    
    def test_get_driver_statistics_raises_on_invalid_driver(self):
        """Test that invalid driver ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            F1Service.get_driver_statistics("invalid_driver_xyz_12345")
    
    def test_get_driver_statistics_has_no_http_dependencies(self):
        """
        Verify function is independently testable (Constitution Principle VI).
        
        Should not require:
        - HTTPException (FastAPI)
        - Request/Response objects
        - Mock HTTP context
        """
        # This test passes by successfully calling the function without HTTP context
        result = F1Service.get_driver_statistics("max_verstappen", start_year=2023, end_year=2023)
        assert result is not None
        assert isinstance(result, dict)


class TestHeadToHeadComparison:
    """Test head-to-head driver comparison."""
    
    def test_get_head_to_head_comparison_returns_correct_structure(self):
        """Test head-to-head comparison returns expected structure."""
        result = F1Service.get_head_to_head_comparison(
            "hamilton", 
            "max_verstappen", 
            start_year=2023, 
            end_year=2023
        )
        
        # Verify structure
        assert "driver1" in result
        assert "driver2" in result
        assert "headToHead" in result
        
        # Verify driver data
        assert result["driver1"]["driverId"] == "hamilton"
        assert result["driver2"]["driverId"] == "max_verstappen"
        
        # Verify head-to-head data
        h2h = result["headToHead"]
        assert "racesTogetherCount" in h2h
        assert "driver1Better" in h2h
        assert "driver2Better" in h2h
        assert "races" in h2h
        
        # Should have raced together in 2023
        assert h2h["racesTogetherCount"] > 0
    
    def test_head_to_head_uses_driver_statistics(self):
        """Test that head-to-head internally uses get_driver_statistics."""
        result = F1Service.get_head_to_head_comparison(
            "hamilton", 
            "alonso", 
            start_year=2023, 
            end_year=2023
        )
        
        # Both drivers should have statistics
        assert "statistics" in result["driver1"]
        assert "statistics" in result["driver2"]
        assert result["driver1"]["statistics"]["totalRaces"] > 0
        assert result["driver2"]["statistics"]["totalRaces"] > 0


class TestConstructorStatistics:
    """Test constructor statistics calculation."""
    
    def test_get_constructor_statistics_returns_correct_structure(self):
        """Test constructor statistics returns expected structure."""
        result = F1Service.get_constructor_statistics("red_bull", start_year=2023, end_year=2023)
        
        # Verify structure
        assert "constructorId" in result
        assert "statistics" in result
        assert result["constructorId"] == "red_bull"
        
        # Verify statistics fields
        stats = result["statistics"]
        assert "totalRaces" in stats
        assert "wins" in stats
        assert "podiums" in stats
        assert "totalPoints" in stats
        assert "polePositions" in stats
        assert "fastestLaps" in stats
        assert "drivers" in stats
        assert "seasons" in stats
        
        # Red Bull should have raced in 2023
        assert stats["totalRaces"] > 0
    
    def test_get_constructor_statistics_raises_on_invalid_constructor(self):
        """Test that invalid constructor ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            F1Service.get_constructor_statistics("invalid_constructor_xyz_12345")


class TestFastestLaps:
    """Test fastest laps retrieval."""
    
    def test_get_fastest_laps_for_season_returns_correct_structure(self):
        """Test fastest laps returns expected structure."""
        result = F1Service.get_fastest_laps_for_season(2023, limit=10)
        
        # Verify structure
        assert "season" in result
        assert "fastestLaps" in result
        assert "count" in result
        assert result["season"] == 2023
        
        # Should have fastest laps
        assert len(result["fastestLaps"]) > 0
        assert len(result["fastestLaps"]) <= 10
    
    def test_get_fastest_laps_respects_limit(self):
        """Test that limit parameter works correctly."""
        result_5 = F1Service.get_fastest_laps_for_season(2023, limit=5)
        result_10 = F1Service.get_fastest_laps_for_season(2023, limit=10)
        
        assert len(result_5["fastestLaps"]) <= 5
        assert len(result_10["fastestLaps"]) <= 10
    
    def test_get_fastest_laps_raises_on_invalid_season(self):
        """Test that invalid season raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            F1Service.get_fastest_laps_for_season(1900)


class TestServiceLayerDesignPrinciples:
    """Test adherence to Constitution Principle VI design principles."""
    
    def test_all_methods_are_static(self):
        """Verify all service methods are static (no instance state)."""
        # This ensures functions are independently testable
        assert callable(F1Service.get_driver_statistics)
        assert callable(F1Service.get_head_to_head_comparison)
        assert callable(F1Service.get_constructor_statistics)
        assert callable(F1Service.get_fastest_laps_for_season)
        
        # Verify they're static by calling without instance
        result = F1Service.get_driver_statistics("hamilton", start_year=2023, end_year=2023)
        assert result is not None
    
    def test_service_has_no_http_imports(self):
        """Verify service layer has no HTTP dependencies (FastAPI, etc.)."""
        import inspect
        import app.services.f1_service as service_module
        
        source = inspect.getsource(service_module)
        
        # Should not import FastAPI, HTTPException, etc.
        assert "from fastapi" not in source
        assert "HTTPException" not in source
        assert "APIRouter" not in source
        
        # Should only import data layer and typing
        assert "from ..json_loader import" in source
        assert "from typing import" in source
    
    def test_functions_return_plain_dicts(self):
        """Verify functions return plain Python dicts, not HTTP responses."""
        result = F1Service.get_driver_statistics("hamilton", start_year=2023, end_year=2023)
        
        # Should be plain dict, not Response object
        assert isinstance(result, dict)
        assert not hasattr(result, "status_code")
        assert not hasattr(result, "headers")
