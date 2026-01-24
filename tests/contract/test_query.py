"""
Contract tests for Query API endpoint

Validates that the unified query endpoint follows expected API contract:
- Returns correct HTTP status codes
- Processes natural language queries correctly
- Routes to appropriate data sources
- Returns consistent data structures
"""
import pytest
from fastapi.testclient import TestClient


class TestQueryEndpointContract:
    """Test that query endpoint follows expected contract"""
    
    def test_query_endpoint_exists(self, client: TestClient):
        """POST /api/query endpoint is accessible"""
        response = client.post("/api/query", json={"query": "test"})
        # Should return 200 or 400, but not 404
        assert response.status_code != 404
    
    def test_query_requires_json_body(self, client: TestClient):
        """Query endpoint requires JSON request body"""
        response = client.post("/api/query")
        assert response.status_code == 422  # Validation error
    
    def test_query_requires_query_field(self, client: TestClient):
        """Query endpoint requires 'query' field in JSON"""
        response = client.post("/api/query", json={})
        assert response.status_code == 422  # Validation error
    
    def test_empty_query_returns_400(self, client: TestClient):
        """Empty query string returns 400 Bad Request"""
        response = client.post("/api/query", json={"query": ""})
        assert response.status_code == 400
    
    def test_whitespace_only_query_returns_400(self, client: TestClient):
        """Whitespace-only query returns 400 Bad Request"""
        response = client.post("/api/query", json={"query": "   "})
        assert response.status_code == 400
    
    def test_query_response_structure(self, client: TestClient):
        """Query response has required fields"""
        response = client.post("/api/query", json={
            "query": "Who won the 2023 championship?"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "dataType" in data
            assert "query" in data
            assert data["success"] is True
            assert data["query"] == "Who won the 2023 championship?"


class TestChampionshipQueries:
    """Test championship-related queries"""
    
    def test_championship_query_returns_200(self, client: TestClient):
        """Championship query returns 200 OK"""
        response = client.post("/api/query", json={
            "query": "Who won the 2023 championship?"
        })
        assert response.status_code == 200
    
    def test_championship_query_returns_standings_data(self, client: TestClient):
        """Championship query returns standings data"""
        response = client.post("/api/query", json={
            "query": "Who won the 2023 championship?"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["dataType"] == "championship_standings"
        assert "driverStandings" in data["data"]
        assert "constructorStandings" in data["data"]
    
    def test_championship_query_variations(self, client: TestClient):
        """Different phrasings of championship queries work"""
        queries = [
            "who won the 2023 championship",
            "2023 champion",
            "2023 title winner",
            "who was 2023 champion"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for query: {query}"
            data = response.json()
            assert data["dataType"] == "championship_standings"


class TestDriverStatsQueries:
    """Test driver statistics queries"""
    
    def test_driver_stats_query_returns_200(self, client: TestClient):
        """Driver stats query returns 200 OK"""
        response = client.post("/api/query", json={
            "query": "How many wins does Hamilton have?"
        })
        assert response.status_code == 200
    
    def test_driver_stats_query_returns_stats_data(self, client: TestClient):
        """Driver stats query returns statistics data"""
        response = client.post("/api/query", json={
            "query": "lewis hamilton stats"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["dataType"] == "driver_stats"
        
        # Check required stats fields - stats are nested under "statistics" key
        stats = data["data"].get("statistics", data["data"])
        required_fields = ["wins", "podiums", "totalRaces"]
        for field in required_fields:
            assert field in stats, f"Missing required field: {field}"
    
    def test_driver_stats_query_variations(self, client: TestClient):
        """Different phrasings of driver stats queries work"""
        queries = [
            "hamilton stats",
            "how many wins hamilton",
            "hamilton career stats",
            "tell me about hamilton"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for query: {query}"
            data = response.json()
            assert data["dataType"] == "driver_stats"


class TestStandingsQueries:
    """Test standings queries"""
    
    def test_standings_query_returns_200(self, client: TestClient):
        """Standings query returns 200 OK"""
        response = client.post("/api/query", json={
            "query": "2023 standings"
        })
        assert response.status_code == 200
    
    def test_standings_query_returns_standings_data(self, client: TestClient):
        """Standings query returns championship standings"""
        response = client.post("/api/query", json={
            "query": "2023 standings"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["dataType"] == "championship_standings"
        assert "season" in data["data"]
        assert data["data"]["season"] == 2023
    
    def test_standings_query_variations(self, client: TestClient):
        """Different phrasings of standings queries work"""
        queries = [
            "2023 standings",
            "2023 points table",
            "2023 leaderboard"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for query: {query}"


class TestWinnersQueries:
    """Test race winners queries"""
    
    def test_winners_query_returns_200(self, client: TestClient):
        """Winners query returns 200 OK"""
        response = client.post("/api/query", json={
            "query": "who won the most races in 2023"
        })
        assert response.status_code == 200
    
    def test_winners_query_returns_winners_data(self, client: TestClient):
        """Winners query returns race winners data"""
        response = client.post("/api/query", json={
            "query": "who won the most races in 2023"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["dataType"] == "season_winners"
        assert "winners" in data["data"]
        assert "count" in data["data"]


class TestErrorHandling:
    """Test error handling for query endpoint"""
    
    def test_unrecognized_query_returns_400(self, client: TestClient):
        """Unrecognized query pattern returns 400"""
        response = client.post("/api/query", json={
            "query": "blah blah random nonsense xyz123"
        })
        assert response.status_code == 400
    
    def test_invalid_year_in_query_returns_404(self, client: TestClient):
        """Invalid year in query returns 404 or 400"""
        response = client.post("/api/query", json={
            "query": "who won the 1950 championship"
        })
        # Year outside range: parser may not extract it (400) or endpoint rejects it (404)
        assert response.status_code in [400, 404]
    
    def test_invalid_driver_name_returns_400_or_404(self, client: TestClient):
        """Invalid driver name returns error"""
        response = client.post("/api/query", json={
            "query": "stats for nonexistentdriver12345"
        })
        # Should return either 400 (couldn't parse) or 404 (driver not found)
        assert response.status_code in [400, 404]
    
    def test_error_response_has_detail(self, client: TestClient):
        """Error responses include helpful detail message"""
        response = client.post("/api/query", json={
            "query": ""
        })
        assert response.status_code == 400
        error = response.json()
        assert "detail" in error
        assert len(error["detail"]) > 0


class TestQueryPerformance:
    """Test performance characteristics of query endpoint"""
    
    def test_query_response_time(self, client: TestClient):
        """Query endpoint responds quickly"""
        import time
        
        start = time.time()
        response = client.post("/api/query", json={
            "query": "2023 standings"
        })
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 100, f"Query took {elapsed:.2f}ms, expected < 100ms"
    
    def test_cached_query_response_time(self, client: TestClient):
        """Repeated queries benefit from caching"""
        # First request
        client.post("/api/query", json={"query": "hamilton stats"})
        
        # Second request (should be cached)
        import time
        start = time.time()
        response = client.post("/api/query", json={"query": "hamilton stats"})
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 50, f"Cached query took {elapsed:.2f}ms, expected < 50ms"
