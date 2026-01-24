"""Contract tests for driver endpoints (T016)

Validates that driver API endpoints conform to the OpenAPI specification
and return data in the correct Ergast API format.
"""
import pytest
from fastapi.testclient import TestClient
from app.api_server import app

client = TestClient(app)


class TestDriverEndpointsContract:
    """Contract tests for /api/drivers endpoints"""
    
    def test_get_all_drivers_returns_200(self):
        """GET /api/drivers should return 200 OK"""
        response = client.get("/api/drivers")
        assert response.status_code == 200
    
    def test_get_all_drivers_returns_ergast_structure(self):
        """GET /api/drivers should return Ergast API format"""
        response = client.get("/api/drivers")
        data = response.json()
        
        # Verify Ergast structure
        assert "MRData" in data
        assert "DriverTable" in data["MRData"]
        assert "Drivers" in data["MRData"]["DriverTable"]
        assert isinstance(data["MRData"]["DriverTable"]["Drivers"], list)
    
    def test_get_all_drivers_contains_required_fields(self):
        """Each driver should have required Ergast fields"""
        response = client.get("/api/drivers")
        drivers = response.json()["MRData"]["DriverTable"]["Drivers"]
        
        assert len(drivers) > 0, "Should return at least one driver"
        
        # Check first driver has required fields
        driver = drivers[0]
        required_fields = ["driverId", "givenName", "familyName", "nationality"]
        for field in required_fields:
            assert field in driver, f"Driver missing required field: {field}"
    
    def test_get_driver_by_id_returns_200_for_valid_driver(self):
        """GET /api/drivers/{id} should return 200 for valid driver"""
        # Get a valid driver ID first
        all_drivers_response = client.get("/api/drivers")
        drivers = all_drivers_response.json()["MRData"]["DriverTable"]["Drivers"]
        valid_driver_id = drivers[0]["driverId"]
        
        response = client.get(f"/api/drivers/{valid_driver_id}")
        assert response.status_code == 200
    
    def test_get_driver_by_id_returns_404_for_invalid_driver(self):
        """GET /api/drivers/{id} should return 404 for non-existent driver"""
        response = client.get("/api/drivers/nonexistent_driver_id_12345")
        assert response.status_code == 404
    
    def test_get_driver_by_id_returns_ergast_structure(self):
        """GET /api/drivers/{id} should return Ergast format"""
        # Get a valid driver ID
        all_drivers_response = client.get("/api/drivers")
        drivers = all_drivers_response.json()["MRData"]["DriverTable"]["Drivers"]
        valid_driver_id = drivers[0]["driverId"]
        
        response = client.get(f"/api/drivers/{valid_driver_id}")
        data = response.json()
        
        assert "MRData" in data
        assert "DriverTable" in data["MRData"]
        assert "Drivers" in data["MRData"]["DriverTable"]
        assert len(data["MRData"]["DriverTable"]["Drivers"]) == 1
    
    def test_get_driver_stats_returns_200_for_valid_driver(self):
        """GET /api/drivers/{id}/stats should return 200 for valid driver"""
        # Get a driver ID that has actual race data
        response = client.get("/api/drivers/abate/stats")
        assert response.status_code == 200
    
    def test_get_driver_stats_returns_statistics_structure(self):
        """GET /api/drivers/{id}/stats should return statistics data"""
        response = client.get("/api/drivers/abate/stats")
        data = response.json()
        
        # Should have driverId and statistics
        assert "driverId" in data
        assert "statistics" in data
        
        stats = data["statistics"]
        # Check for expected statistics fields
        expected_fields = ["totalRaces", "wins", "podiums", "polePositions", "fastestLaps"]
        for field in expected_fields:
            assert field in stats, f"Statistics missing field: {field}"
    
    def test_search_drivers_returns_200(self):
        """GET /api/drivers/search should return 200"""
        response = client.get("/api/drivers/search?name=verstappen")
        assert response.status_code == 200
    
    def test_search_drivers_filters_by_name(self):
        """GET /api/drivers/search should filter by name parameter"""
        response = client.get("/api/drivers/search?name=verstappen")
        data = response.json()
        drivers = data["MRData"]["DriverTable"]["Drivers"]
        
        # All returned drivers should match search term
        for driver in drivers:
            full_name = f"{driver['givenName']} {driver['familyName']}".lower()
            assert "verstappen" in full_name
    
    def test_search_drivers_returns_ergast_structure(self):
        """GET /api/drivers/search should return Ergast format"""
        response = client.get("/api/drivers/search?nationality=British")
        data = response.json()
        
        assert "MRData" in data
        assert "DriverTable" in data["MRData"]
        assert "Drivers" in data["MRData"]["DriverTable"]


class TestDriverEndpointsPerformance:
    """Performance validation for driver endpoints"""
    
    def test_get_all_drivers_response_time(self):
        """GET /api/drivers should respond quickly (cached)"""
        # Warm up cache
        client.get("/api/drivers")
        
        # Measure cached response time
        import time
        start = time.perf_counter()
        response = client.get("/api/drivers")
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed_ms < 100, f"Response took {elapsed_ms:.2f}ms, expected <100ms"
    
    def test_get_driver_stats_completes_within_timeout(self):
        """GET /api/drivers/{id}/stats should complete within reasonable time"""
        import time
        start = time.perf_counter()
        response = client.get("/api/drivers/abate/stats")
        elapsed_s = time.perf_counter() - start
        
        assert response.status_code == 200
        assert elapsed_s < 2.0, f"Stats computation took {elapsed_s:.2f}s, expected <2s"
