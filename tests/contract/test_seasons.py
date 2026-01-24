"""
Contract tests for Season API endpoints

Validates that endpoints follow the expected API contract:
- Return correct HTTP status codes
- Include required fields in responses
- Maintain consistent data structures
- Handle errors gracefully
"""
import pytest
from fastapi.testclient import TestClient


class TestSeasonEndpointsContract:
    """Test that season endpoints follow expected contract"""
    
    def test_get_seasons_returns_200(self, client: TestClient):
        """GET /api/seasons returns 200 OK"""
        response = client.get("/api/seasons")
        assert response.status_code == 200
    
    def test_get_seasons_returns_list_structure(self, client: TestClient):
        """GET /api/seasons returns seasons list with metadata"""
        response = client.get("/api/seasons")
        data = response.json()
        
        assert "seasons" in data
        assert "count" in data
        assert "firstSeason" in data
        assert "lastSeason" in data
        assert isinstance(data["seasons"], list)
        assert len(data["seasons"]) > 0
    
    def test_get_seasons_returns_valid_year_range(self, client: TestClient):
        """GET /api/seasons returns years between 1984-2024"""
        response = client.get("/api/seasons")
        data = response.json()
        
        assert data["firstSeason"] >= 1984
        assert data["lastSeason"] <= 2024
        assert data["count"] == len(data["seasons"])
    
    def test_get_season_returns_200_for_valid_year(self, client: TestClient):
        """GET /api/seasons/{year} returns 200 for valid season"""
        response = client.get("/api/seasons/2023")
        assert response.status_code == 200
    
    def test_get_season_returns_ergast_structure(self, client: TestClient):
        """GET /api/seasons/{year} follows Ergast API structure"""
        response = client.get("/api/seasons/2023")
        data = response.json()
        
        assert "MRData" in data
        assert "RaceTable" in data["MRData"]
        assert "Races" in data["MRData"]["RaceTable"]
        assert isinstance(data["MRData"]["RaceTable"]["Races"], list)
    
    def test_get_season_returns_404_for_invalid_year(self, client: TestClient):
        """GET /api/seasons/{year} returns 404 for unavailable year"""
        response = client.get("/api/seasons/1950")
        assert response.status_code == 404
    
    def test_get_season_includes_year_range_in_error(self, client: TestClient):
        """GET /api/seasons/{year} includes available year range in error"""
        response = client.get("/api/seasons/2030")
        assert response.status_code == 404
        error = response.json()["detail"]
        assert "1984" in error or "Available" in error
        assert "2024" in error or "Available" in error
    
    def test_get_season_standings_returns_200(self, client: TestClient):
        """GET /api/seasons/{year}/standings returns 200 OK"""
        response = client.get("/api/seasons/2023/standings")
        assert response.status_code == 200
    
    def test_get_season_standings_structure(self, client: TestClient):
        """GET /api/seasons/{year}/standings returns driver and constructor standings"""
        response = client.get("/api/seasons/2023/standings")
        data = response.json()
        
        assert "season" in data
        assert "driverStandings" in data
        assert "constructorStandings" in data
        assert isinstance(data["driverStandings"], list)
        assert isinstance(data["constructorStandings"], list)
    
    def test_get_season_standings_driver_fields(self, client: TestClient):
        """Driver standings include required fields"""
        response = client.get("/api/seasons/2023/standings")
        standings = response.json()["driverStandings"]
        
        assert len(standings) > 0
        driver = standings[0]
        required_fields = ["position", "driverId", "name", "points", "wins", "constructor"]
        for field in required_fields:
            assert field in driver, f"Missing required field: {field}"
    
    def test_get_season_standings_constructor_fields(self, client: TestClient):
        """Constructor standings include required fields"""
        response = client.get("/api/seasons/2023/standings")
        standings = response.json()["constructorStandings"]
        
        assert len(standings) > 0
        constructor = standings[0]
        required_fields = ["position", "constructorId", "name", "points", "wins"]
        for field in required_fields:
            assert field in constructor, f"Missing required field: {field}"
    
    def test_get_season_winners_returns_200(self, client: TestClient):
        """GET /api/seasons/{year}/winners returns 200 OK"""
        response = client.get("/api/seasons/2023/winners")
        assert response.status_code == 200
    
    def test_get_season_winners_structure(self, client: TestClient):
        """GET /api/seasons/{year}/winners returns winners list"""
        response = client.get("/api/seasons/2023/winners")
        data = response.json()
        
        assert "season" in data
        assert "winners" in data
        assert "count" in data
        assert isinstance(data["winners"], list)
        assert data["count"] == len(data["winners"])
    
    def test_get_season_winners_includes_race_details(self, client: TestClient):
        """Winners list includes race and driver details"""
        response = client.get("/api/seasons/2023/winners")
        winners = response.json()["winners"]
        
        assert len(winners) > 0
        winner = winners[0]
        required_fields = ["round", "raceName", "circuit", "date", "driver", "constructor"]
        for field in required_fields:
            assert field in winner, f"Missing required field: {field}"
        
        # Check nested driver structure
        assert "driverId" in winner["driver"]
        assert "name" in winner["driver"]
        
        # Check nested constructor structure
        assert "constructorId" in winner["constructor"]
        assert "name" in winner["constructor"]
    
    def test_get_season_returns_404_for_future_year(self, client: TestClient):
        """GET /api/seasons/{year} returns 404 for future year"""
        response = client.get("/api/seasons/2030")
        assert response.status_code == 404


class TestSeasonEndpointsPerformance:
    """Test performance characteristics of season endpoints"""
    
    def test_get_seasons_response_time(self, client: TestClient):
        """GET /api/seasons responds quickly"""
        import time
        
        # Warmup
        client.get("/api/seasons")
        
        # Timed request
        start = time.time()
        response = client.get("/api/seasons")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 50, f"Response took {elapsed:.2f}ms, expected < 50ms"
    
    def test_get_season_cached_response_time(self, client: TestClient):
        """GET /api/seasons/{year} responds quickly after caching"""
        # First request (cache miss)
        client.get("/api/seasons/2023")
        
        # Cached request
        import time
        start = time.time()
        response = client.get("/api/seasons/2023")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 10, f"Cached response took {elapsed:.2f}ms, expected < 10ms"
    
    def test_get_season_standings_computation_time(self, client: TestClient):
        """GET /api/seasons/{year}/standings computes quickly"""
        import time
        
        start = time.time()
        response = client.get("/api/seasons/2023/standings")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"Standings computation took {elapsed:.2f}ms, expected < 500ms"
