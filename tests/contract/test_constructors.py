"""
Contract tests for Constructor API endpoints

Validates that endpoints follow the expected API contract:
- Return correct HTTP status codes
- Include required fields in responses
- Follow Ergast API data structure
- Maintain backwards compatibility
"""
import pytest
from fastapi.testclient import TestClient


class TestConstructorEndpointsContract:
    """Test that constructor endpoints follow expected contract"""
    
    def test_get_all_constructors_returns_200(self, client: TestClient):
        """GET /api/constructors returns 200 OK"""
        response = client.get("/api/constructors")
        assert response.status_code == 200
    
    def test_get_all_constructors_returns_ergast_structure(self, client: TestClient):
        """GET /api/constructors follows Ergast API structure"""
        response = client.get("/api/constructors")
        data = response.json()
        
        # Ergast structure: MRData → ConstructorTable → Constructors
        assert "MRData" in data
        assert "ConstructorTable" in data["MRData"]
        assert "Constructors" in data["MRData"]["ConstructorTable"]
        assert isinstance(data["MRData"]["ConstructorTable"]["Constructors"], list)
    
    def test_constructor_object_has_required_fields(self, client: TestClient):
        """Each constructor object contains required fields"""
        response = client.get("/api/constructors")
        constructors = response.json()["MRData"]["ConstructorTable"]["Constructors"]
        
        assert len(constructors) > 0, "Should return at least one constructor"
        
        required_fields = ["constructorId", "name", "nationality", "url"]
        for constructor in constructors[:5]:  # Check first 5
            for field in required_fields:
                assert field in constructor, f"Constructor missing required field: {field}"
                assert constructor[field], f"Constructor {field} should not be empty"
    
    def test_get_constructor_by_id_returns_200_for_valid_id(self, client: TestClient):
        """GET /api/constructors/{id} returns 200 for valid constructor"""
        response = client.get("/api/constructors/red_bull")
        assert response.status_code == 200
    
    def test_get_constructor_by_id_returns_ergast_structure(self, client: TestClient):
        """GET /api/constructors/{id} follows Ergast structure"""
        response = client.get("/api/constructors/ferrari")
        data = response.json()
        
        assert "MRData" in data
        assert "ConstructorTable" in data["MRData"]
        assert "Constructors" in data["MRData"]["ConstructorTable"]
        constructors = data["MRData"]["ConstructorTable"]["Constructors"]
        assert isinstance(constructors, list)
        assert len(constructors) == 1  # Single constructor
    
    def test_get_constructor_by_id_returns_404_for_invalid_id(self, client: TestClient):
        """GET /api/constructors/{id} returns 404 for unknown constructor"""
        response = client.get("/api/constructors/nonexistent_team_xyz")
        assert response.status_code == 404
    
    def test_get_constructor_by_id_includes_suggestions_on_404(self, client: TestClient):
        """GET /api/constructors/{id} includes helpful suggestions when not found"""
        response = client.get("/api/constructors/ferarri")  # Typo
        assert response.status_code == 404
        assert "detail" in response.json()
        error_message = response.json()["detail"]
        assert "ferrari" in error_message.lower()  # Should suggest correct spelling
    
    def test_get_constructor_stats_returns_200(self, client: TestClient):
        """GET /api/constructors/{id}/stats returns 200 OK"""
        response = client.get("/api/constructors/mercedes/stats")
        assert response.status_code == 200
    
    def test_get_constructor_stats_includes_key_metrics(self, client: TestClient):
        """GET /api/constructors/{id}/stats includes championships, wins, poles"""
        response = client.get("/api/constructors/ferrari/stats")
        stats = response.json()
        
        required_metrics = ["totalChampionships", "totalWins", "totalPodiums", "totalPoles"]
        for metric in required_metrics:
            assert metric in stats, f"Stats missing required metric: {metric}"
            assert isinstance(stats[metric], int), f"{metric} should be an integer"
    
    def test_get_constructor_season_results_returns_200(self, client: TestClient):
        """GET /api/constructors/{id}/seasons/{year} returns 200 OK"""
        response = client.get("/api/constructors/ferrari/seasons/2023")
        assert response.status_code == 200
    
    def test_get_constructor_season_results_returns_404_for_invalid_year(self, client: TestClient):
        """GET /api/constructors/{id}/seasons/{year} returns 404 for unavailable year"""
        response = client.get("/api/constructors/ferrari/seasons/1950")
        assert response.status_code == 404
        error_message = response.json()["detail"]
        assert "1984" in error_message  # Should mention earliest available year
        assert "2024" in error_message  # Should mention latest available year
    
    def test_get_constructor_season_results_validates_constructor_first(self, client: TestClient):
        """GET /api/constructors/{id}/seasons/{year} validates constructor before year"""
        response = client.get("/api/constructors/fake_team/seasons/2023")
        assert response.status_code == 404
        error_message = response.json()["detail"]
        assert "not found" in error_message.lower()


class TestConstructorEndpointsPerformance:
    """Test performance characteristics of constructor endpoints"""
    
    def test_get_all_constructors_response_time(self, client: TestClient):
        """GET /api/constructors responds quickly (under 100ms after warmup)"""
        # Warmup request
        client.get("/api/constructors")
        
        # Timed request
        import time
        start = time.time()
        response = client.get("/api/constructors")
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert response.status_code == 200
        assert elapsed < 100, f"Response took {elapsed:.2f}ms, expected < 100ms"
    
    def test_get_constructor_stats_response_time(self, client: TestClient):
        """GET /api/constructors/{id}/stats responds quickly"""
        # Warmup
        client.get("/api/constructors/ferrari/stats")
        
        # Timed request
        import time
        start = time.time()
        response = client.get("/api/constructors/ferrari/stats")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 200, f"Stats computation took {elapsed:.2f}ms, expected < 200ms"
