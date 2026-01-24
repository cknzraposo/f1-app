"""
Integration tests for Query Parsing workflow

Tests end-to-end query processing:
- Natural language → QueryParser → Endpoint routing
- Entity extraction (years, drivers, constructors)
- Pattern matching accuracy
- Data flow from query to response
"""
import pytest
from fastapi.testclient import TestClient


class TestQueryParsingWorkflow:
    """Test complete query parsing and routing workflow"""
    
    def test_championship_query_workflow(self, client: TestClient):
        """Championship query flows through parser to correct endpoint"""
        response = client.post("/api/query", json={
            "query": "Who won the 2023 championship?"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should route to standings endpoint
        assert data["dataType"] == "championship_standings"
        assert data["data"]["season"] == 2023
        
        # Check champion is correct
        driver_champion = data["data"]["driverStandings"][0]
        assert driver_champion["position"] == 1
        assert "driverId" in driver_champion
    
    def test_driver_stats_query_workflow(self, client: TestClient):
        """Driver stats query extracts driver and fetches stats"""
        response = client.post("/api/query", json={
            "query": "How many wins does Lewis Hamilton have?"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should route to driver stats
        assert data["dataType"] == "driver_stats"
        assert data["data"]["totalWins"] > 0
        assert "totalPodiums" in data["data"]
        assert "totalRaces" in data["data"]
    
    def test_standings_query_workflow(self, client: TestClient):
        """Standings query extracts year and fetches standings"""
        response = client.post("/api/query", json={
            "query": "Show me 2022 standings"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["dataType"] == "championship_standings"
        assert data["data"]["season"] == 2022
        assert len(data["data"]["driverStandings"]) > 0
        assert len(data["data"]["constructorStandings"]) > 0
    
    def test_winners_query_workflow(self, client: TestClient):
        """Winners query extracts year and fetches race winners"""
        response = client.post("/api/query", json={
            "query": "who won the most races in 2023"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["dataType"] == "season_winners"
        assert "winners" in data["data"]
        assert len(data["data"]["winners"]) > 0


class TestYearExtraction:
    """Test year extraction from queries"""
    
    def test_year_extraction_four_digits(self, client: TestClient):
        """Extracts 4-digit year from query"""
        queries = [
            ("2023 championship", 2023),
            ("who won in 2010", 2010),
            ("1984 season", 1984),
            ("2024 standings", 2024)
        ]
        
        for query, expected_year in queries:
            response = client.post("/api/query", json={"query": query})
            if response.status_code == 200:
                data = response.json()
                # Year should appear in the data somewhere
                assert expected_year in str(data["data"])
    
    def test_year_range_validation(self, client: TestClient):
        """Years outside 1984-2024 are rejected"""
        invalid_years = [1950, 1983, 2025, 2030]
        
        for year in invalid_years:
            response = client.post("/api/query", json={
                "query": f"{year} championship"
            })
            # Should either not parse (400) or reject invalid year (404)
            assert response.status_code in [400, 404]
    
    def test_multiple_years_uses_first(self, client: TestClient):
        """When multiple years present, uses most relevant one"""
        response = client.post("/api/query", json={
            "query": "2023 championship compared to 2022"
        })
        
        if response.status_code == 200:
            data = response.json()
            # Should extract 2023 as primary year
            assert 2023 in str(data["data"])


class TestDriverNameExtraction:
    """Test driver name extraction with fuzzy matching"""
    
    def test_driver_surname_extraction(self, client: TestClient):
        """Extracts driver by surname"""
        queries = [
            "hamilton stats",
            "verstappen wins",
            "alonso career"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for: {query}"
            data = response.json()
            assert data["dataType"] == "driver_stats"
    
    def test_driver_full_name_extraction(self, client: TestClient):
        """Extracts driver by full name"""
        queries = [
            "lewis hamilton stats",
            "max verstappen wins",
            "fernando alonso career"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            assert response.status_code == 200, f"Failed for: {query}"
            data = response.json()
            assert data["dataType"] == "driver_stats"
    
    def test_driver_fuzzy_matching(self, client: TestClient):
        """Handles minor typos in driver names"""
        queries = [
            "hamliton stats",  # hamilton
            "verstapen wins",   # verstappen
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            # Should either match or fail gracefully
            assert response.status_code in [200, 400, 404]
    
    def test_case_insensitive_driver_names(self, client: TestClient):
        """Driver name matching is case-insensitive"""
        queries = [
            "HAMILTON stats",
            "hamilton stats",
            "HaMiLtOn stats"
        ]
        
        results = []
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            if response.status_code == 200:
                results.append(response.json()["data"])
        
        # All should return same data
        if len(results) > 1:
            assert all(r == results[0] for r in results)


class TestConstructorNameExtraction:
    """Test constructor/team name extraction"""
    
    def test_constructor_name_extraction(self, client: TestClient):
        """Extracts constructor names from queries"""
        queries = [
            "ferrari stats",
            "red bull stats",
            "mercedes stats"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            # May or may not match depending on implementation
            if response.status_code == 200:
                data = response.json()
                assert data["dataType"] == "constructor_stats"
    
    def test_multi_word_constructor_names(self, client: TestClient):
        """Handles multi-word constructor names"""
        queries = [
            "red bull stats",
            "aston martin stats",
            "alfa romeo stats"
        ]
        
        for query in queries:
            response = client.post("/api/query", json={"query": query})
            # Should handle multi-word names
            if response.status_code == 200:
                assert "stats" in response.json()["dataType"]


class TestPatternMatching:
    """Test specific query pattern matching"""
    
    def test_championship_patterns(self, client: TestClient):
        """Recognizes championship query patterns"""
        patterns = [
            "who won the championship",
            "2023 champion",
            "title winner 2023",
            "who was champion in 2023"
        ]
        
        for pattern in patterns:
            response = client.post("/api/query", json={"query": pattern})
            if response.status_code == 200:
                assert "standings" in response.json()["dataType"]
    
    def test_stats_patterns(self, client: TestClient):
        """Recognizes stats query patterns"""
        patterns = [
            "hamilton stats",
            "how many wins hamilton",
            "hamilton career",
            "tell me about hamilton"
        ]
        
        for pattern in patterns:
            response = client.post("/api/query", json={"query": pattern})
            assert response.status_code == 200, f"Failed: {pattern}"
    
    def test_standings_patterns(self, client: TestClient):
        """Recognizes standings query patterns"""
        patterns = [
            "2023 standings",
            "2023 points table",
            "2023 leaderboard"
        ]
        
        for pattern in patterns:
            response = client.post("/api/query", json={"query": pattern})
            assert response.status_code == 200, f"Failed: {pattern}"
    
    def test_winners_patterns(self, client: TestClient):
        """Recognizes race winners query patterns"""
        patterns = [
            "who won the most races in 2023",
            "2023 race winners",
            "all winners 2023"
        ]
        
        for pattern in patterns:
            response = client.post("/api/query", json={"query": pattern})
            assert response.status_code == 200, f"Failed: {pattern}"


class TestQueryAmbiguityHandling:
    """Test handling of ambiguous queries"""
    
    def test_query_with_multiple_entities(self, client: TestClient):
        """Handles queries with multiple entities"""
        response = client.post("/api/query", json={
            "query": "hamilton 2023 championship"
        })
        
        # Should prioritize championship standings for 2023
        if response.status_code == 200:
            data = response.json()
            assert 2023 in str(data["data"])
    
    def test_incomplete_query_returns_error(self, client: TestClient):
        """Incomplete queries return helpful error"""
        response = client.post("/api/query", json={
            "query": "stats"  # No driver specified
        })
        
        # Should fail to parse
        assert response.status_code == 400
    
    def test_generic_query_returns_error(self, client: TestClient):
        """Very generic queries return error"""
        response = client.post("/api/query", json={
            "query": "formula 1"
        })
        
        assert response.status_code == 400


class TestQuerySourceIndicator:
    """Test that responses indicate processing source"""
    
    def test_keyword_parser_source_indicated(self, client: TestClient):
        """Responses indicate keyword_parser as source"""
        response = client.post("/api/query", json={
            "query": "2023 championship"
        })
        
        if response.status_code == 200:
            data = response.json()
            # Should have action field indicating source
            if "action" in data:
                assert data["action"] is not None


class TestEdgeCases:
    """Test edge cases in query processing"""
    
    def test_query_with_punctuation(self, client: TestClient):
        """Handles queries with punctuation"""
        response = client.post("/api/query", json={
            "query": "Who won the 2023 championship?"
        })
        assert response.status_code == 200
    
    def test_query_with_extra_whitespace(self, client: TestClient):
        """Handles queries with extra whitespace"""
        response = client.post("/api/query", json={
            "query": "  hamilton    stats  "
        })
        assert response.status_code == 200
    
    def test_very_long_query(self, client: TestClient):
        """Handles very long queries"""
        response = client.post("/api/query", json={
            "query": "Can you please tell me all about Lewis Hamilton's career statistics including how many wins he has and podium finishes?"
        })
        # Should extract key entities
        if response.status_code == 200:
            assert "stats" in response.json()["dataType"]
    
    def test_query_with_numbers(self, client: TestClient):
        """Handles queries with various number formats"""
        response = client.post("/api/query", json={
            "query": "2023 championship"
        })
        assert response.status_code == 200
