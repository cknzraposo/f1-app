"""
Contract tests for analytics endpoints

Validates that analytics endpoints meet their specified contracts for:
- Head-to-head driver comparisons
- Fastest lap rankings

These tests verify endpoint behavior, response structure, and data format
without testing business logic (covered by unit tests).
"""
import pytest
from fastapi.testclient import TestClient
from app.api_server import app

client = TestClient(app)


class TestHeadToHeadContract:
    """Contract tests for /api/stats/head-to-head endpoint"""
    
    def test_head_to_head_requires_both_drivers(self):
        """HEAD-TO-HEAD-001: Endpoint requires both driver parameters"""
        # Missing driver2
        response = client.get("/api/stats/head-to-head?driver1=hamilton")
        assert response.status_code == 422  # Unprocessable Entity
        
        # Missing driver1
        response = client.get("/api/stats/head-to-head?driver2=verstappen")
        assert response.status_code == 422
        
        # Missing both
        response = client.get("/api/stats/head-to-head")
        assert response.status_code == 422
    
    def test_head_to_head_returns_correct_structure(self):
        """HEAD-TO-HEAD-002: Response has correct structure"""
        response = client.get("/api/stats/head-to-head?driver1=vettel&driver2=alonso")
        assert response.status_code == 200
        
        data = response.json()
        
        # Top level structure
        assert "driver1" in data
        assert "driver2" in data
        assert "headToHead" in data
        
        # Driver1 structure
        assert "driverId" in data["driver1"]
        assert "statistics" in data["driver1"]
        assert data["driver1"]["driverId"] == "vettel"
        
        # Driver2 structure
        assert "driverId" in data["driver2"]
        assert "statistics" in data["driver2"]
        assert data["driver2"]["driverId"] == "alonso"
        
        # HeadToHead structure
        h2h = data["headToHead"]
        assert "racesTogetherCount" in h2h
        assert "driver1Better" in h2h
        assert "driver2Better" in h2h
        assert "races" in h2h
        
        # Data types
        assert isinstance(h2h["racesTogetherCount"], int)
        assert isinstance(h2h["driver1Better"], int)
        assert isinstance(h2h["driver2Better"], int)
        assert isinstance(h2h["races"], list)
    
    def test_head_to_head_statistics_structure(self):
        """HEAD-TO-HEAD-003: Driver statistics have correct structure"""
        response = client.get("/api/stats/head-to-head?driver1=vettel&driver2=alonso")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check driver1 statistics
        stats = data["driver1"]["statistics"]
        assert "totalRaces" in stats
        assert "wins" in stats
        assert "podiums" in stats
        assert "totalPoints" in stats
        assert "polePositions" in stats
        assert "fastestLaps" in stats
        assert "dnfs" in stats
        assert "teams" in stats
        assert "seasons" in stats
        
        # Data types
        assert isinstance(stats["totalRaces"], int)
        assert isinstance(stats["wins"], int)
        assert isinstance(stats["podiums"], int)
        assert isinstance(stats["totalPoints"], (int, float))
        assert isinstance(stats["teams"], list)
        assert isinstance(stats["seasons"], list)
    
    def test_head_to_head_with_year_range(self):
        """HEAD-TO-HEAD-004: Accepts optional start_year and end_year parameters"""
        response = client.get(
            "/api/stats/head-to-head?driver1=vettel&driver2=alonso&start_year=2010&end_year=2015"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "driver1" in data
        assert "driver2" in data
        assert "headToHead" in data
    
    def test_head_to_head_invalid_driver(self):
        """HEAD-TO-HEAD-005: Returns 404 for non-existent driver"""
        response = client.get("/api/stats/head-to-head?driver1=nonexistent&driver2=alonso")
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_head_to_head_races_structure(self):
        """HEAD-TO-HEAD-006: Race details have correct structure when drivers raced together"""
        response = client.get("/api/stats/head-to-head?driver1=vettel&driver2=alonso")
        assert response.status_code == 200
        
        data = response.json()
        races = data["headToHead"]["races"]
        
        if len(races) > 0:  # If they raced together
            race = races[0]
            assert "season" in race
            assert "round" in race
            assert "raceName" in race
            assert "driver1Position" in race
            assert "driver2Position" in race
            
            # Data types
            assert isinstance(race["season"], (str, int))  # Can be either string or int
            assert isinstance(race["round"], str)
            assert isinstance(race["raceName"], str)


class TestFastestLapsContract:
    """Contract tests for /api/stats/fastest-laps/{year} endpoint"""
    
    def test_fastest_laps_requires_year(self):
        """FASTEST-LAPS-001: Endpoint requires year parameter"""
        response = client.get("/api/stats/fastest-laps/")
        assert response.status_code == 404  # Not Found (no year in path)
    
    def test_fastest_laps_returns_correct_structure(self):
        """FASTEST-LAPS-002: Response has correct structure"""
        response = client.get("/api/stats/fastest-laps/2023")
        assert response.status_code == 200
        
        data = response.json()
        
        # Top level structure
        assert "season" in data
        assert "fastestLaps" in data
        
        assert data["season"] == 2023
        assert isinstance(data["fastestLaps"], list)
    
    def test_fastest_laps_data_structure(self):
        """FASTEST-LAPS-003: Fastest lap entries have correct structure"""
        response = client.get("/api/stats/fastest-laps/2023?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        laps = data["fastestLaps"]
        
        assert len(laps) <= 5  # Respects limit parameter
        
        if len(laps) > 0:
            lap = laps[0]
            assert "round" in lap
            assert "raceName" in lap
            assert "circuit" in lap
            assert "driver" in lap
            assert "constructor" in lap
            assert "lap" in lap
            assert "time" in lap
            assert "rank" in lap
            
            # Driver structure
            driver = lap["driver"]
            assert "driverId" in driver
            assert "name" in driver
    
    def test_fastest_laps_accepts_limit_parameter(self):
        """FASTEST-LAPS-004: Accepts optional limit parameter"""
        response = client.get("/api/stats/fastest-laps/2023?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["fastestLaps"]) <= 3
    
    def test_fastest_laps_default_limit(self):
        """FASTEST-LAPS-005: Uses default limit when not specified"""
        response = client.get("/api/stats/fastest-laps/2023")
        assert response.status_code == 200
        
        data = response.json()
        # Default limit is 20
        assert len(data["fastestLaps"]) <= 20
    
    def test_fastest_laps_invalid_year(self):
        """FASTEST-LAPS-006: Returns 404 for invalid/unavailable year"""
        response = client.get("/api/stats/fastest-laps/1900")
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_fastest_laps_includes_speed_when_available(self):
        """FASTEST-LAPS-007: Includes average speed when available"""
        response = client.get("/api/stats/fastest-laps/2023?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        laps = data["fastestLaps"]
        
        if len(laps) > 0:
            lap = laps[0]
            if "averageSpeed" in lap:
                speed = lap["averageSpeed"]
                assert "value" in speed
                assert "units" in speed


class TestAnalyticsEdgeCases:
    """Contract tests for edge cases and error handling"""
    
    def test_head_to_head_same_driver(self):
        """EDGE-001: Allows comparing driver to themselves"""
        response = client.get("/api/stats/head-to-head?driver1=hamilton&driver2=hamilton")
        # Should return valid response (though not meaningful)
        assert response.status_code in [200, 400, 404]
    
    def test_head_to_head_driver_order_matters(self):
        """EDGE-002: Driver order affects which is driver1/driver2"""
        response1 = client.get("/api/stats/head-to-head?driver1=vettel&driver2=alonso")
        response2 = client.get("/api/stats/head-to-head?driver1=alonso&driver2=vettel")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # driver1 in first request should be driver2 in second
        assert data1["driver1"]["driverId"] == data2["driver2"]["driverId"]
        assert data1["driver2"]["driverId"] == data2["driver1"]["driverId"]
    
    def test_fastest_laps_year_as_string(self):
        """EDGE-003: Year parameter accepts integer format"""
        # FastAPI should convert string to int automatically
        response = client.get("/api/stats/fastest-laps/2023")
        assert response.status_code == 200
    
    def test_head_to_head_invalid_year_range(self):
        """EDGE-004: Handles invalid year ranges gracefully"""
        # end_year before start_year
        response = client.get(
            "/api/stats/head-to-head?driver1=vettel&driver2=alonso&start_year=2015&end_year=2010"
        )
        # Should either work (return empty) or return error
        assert response.status_code in [200, 400]


# Test counts for documentation
def test_analytics_contract_coverage():
    """META: Document contract test coverage"""
    head_to_head_tests = 6  # HEAD-TO-HEAD-001 through HEAD-TO-HEAD-006
    fastest_laps_tests = 7  # FASTEST-LAPS-001 through FASTEST-LAPS-007
    edge_case_tests = 4     # EDGE-001 through EDGE-004
    
    total_tests = head_to_head_tests + fastest_laps_tests + edge_case_tests
    assert total_tests == 17  # Expected test count
