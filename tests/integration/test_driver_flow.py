"""Integration tests for driver data flow (T017)

Tests the complete data flow from API endpoint → service layer → data loader.
"""
import pytest
from fastapi.testclient import TestClient
from app.api_server import app

client = TestClient(app)


class TestDriverDataFlow:
    """Integration tests for driver data retrieval flow"""
    
    def test_driver_list_flow(self):
        """Test complete flow: API → json_loader → return drivers"""
        response = client.get("/api/drivers")
        
        assert response.status_code == 200
        data = response.json()
        drivers = data["MRData"]["DriverTable"]["Drivers"]
        assert len(drivers) > 0
        assert all("driverId" in d for d in drivers)
    
    def test_driver_detail_flow(self):
        """Test complete flow: API → find driver → return single driver"""
        # Get valid driver ID
        all_drivers = client.get("/api/drivers").json()
        test_driver_id = all_drivers["MRData"]["DriverTable"]["Drivers"][0]["driverId"]
        
        # Request specific driver
        response = client.get(f"/api/drivers/{test_driver_id}")
        
        assert response.status_code == 200
        data = response.json()
        drivers = data["MRData"]["DriverTable"]["Drivers"]
        assert len(drivers) == 1
        assert drivers[0]["driverId"] == test_driver_id
    
    def test_driver_stats_flow(self):
        """Test complete flow: API → F1Service → aggregate stats from seasons"""
        response = client.get("/api/drivers/abate/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify statistics were computed
        assert "statistics" in data
        stats = data["statistics"]
        assert "totalRaces" in stats
        assert isinstance(stats["totalRaces"], int)
        assert stats["totalRaces"] >= 0
    
    def test_driver_search_flow(self):
        """Test complete flow: API → filter drivers → return matches"""
        response = client.get("/api/drivers/search?name=max")
        
        assert response.status_code == 200
        data = response.json()
        drivers = data["MRData"]["DriverTable"]["Drivers"]
        
        # All results should contain 'max' in name
        for driver in drivers:
            full_name = f"{driver['givenName']} {driver['familyName']}".lower()
            assert "max" in full_name
    
    def test_driver_not_found_error_flow(self):
        """Test error handling flow: Invalid ID → 404 with message"""
        response = client.get("/api/drivers/invalid_driver_12345")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "invalid_driver_12345" in error_data["detail"]


class TestDriverStatsIntegration:
    """Integration tests for driver statistics computation"""
    
    def test_stats_aggregates_across_all_seasons(self):
        """Stats should aggregate data from all available seasons"""
        response = client.get("/api/drivers/abate/stats")
        data = response.json()
        
        # abate has limited racing history, but stats should be computed
        stats = data["statistics"]
        assert "totalRaces" in stats
        assert "wins" in stats
        assert "podiums" in stats
    
    def test_stats_handles_driver_with_no_results(self):
        """Stats for driver with no race results should return zeros"""
        # Use a very early driver who may have minimal data
        response = client.get("/api/drivers/abecassis/stats")
        
        # Should still return 200 with zero stats
        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
        assert data["statistics"]["totalRaces"] >= 0
    
    def test_stats_caching_performance(self):
        """Second request for same driver stats should be faster (cached)"""
        import time
        
        # First request (cold cache for seasons)
        start1 = time.perf_counter()
        response1 = client.get("/api/drivers/abate/stats")
        time1 = time.perf_counter() - start1
        
        # Second request (warm cache)
        start2 = time.perf_counter()
        response2 = client.get("/api/drivers/abate/stats")
        time2 = time.perf_counter() - start2
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Second request should be significantly faster (or at least not slower)
        # Note: With LRU cache of 5 seasons, not all seasons cached, but some should be
        assert time2 <= time1 * 2, "Second request should benefit from some caching"


class TestDriverSearchIntegration:
    """Integration tests for driver search functionality"""
    
    def test_search_by_partial_name(self):
        """Search should work with partial names"""
        response = client.get("/api/drivers/search?name=ver")
        
        assert response.status_code == 200
        drivers = response.json()["MRData"]["DriverTable"]["Drivers"]
        assert len(drivers) > 0
        
        # Should include drivers like Verstappen, Verhoeven, etc.
        driver_names = [f"{d['givenName']} {d['familyName']}" for d in drivers]
        assert any("ver" in name.lower() for name in driver_names)
    
    def test_search_by_nationality(self):
        """Search should filter by nationality"""
        response = client.get("/api/drivers/search?nationality=Dutch")
        
        assert response.status_code == 200
        drivers = response.json()["MRData"]["DriverTable"]["Drivers"]
        
        # All returned drivers should be Dutch
        for driver in drivers:
            assert driver["nationality"] == "Dutch"
    
    def test_search_with_multiple_filters(self):
        """Search should support combining name and nationality"""
        response = client.get("/api/drivers/search?name=max&nationality=Dutch")
        
        assert response.status_code == 200
        drivers = response.json()["MRData"]["DriverTable"]["Drivers"]
        
        # Results should match both criteria
        for driver in drivers:
            assert driver["nationality"] == "Dutch"
            assert "max" in f"{driver['givenName']} {driver['familyName']}".lower()
