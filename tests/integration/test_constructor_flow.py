"""
Integration tests for Constructor data flow

Tests the complete flow from API endpoint → service layer → data loader.
Validates that data flows correctly through all layers and business logic works end-to-end.
"""
import pytest
from fastapi.testclient import TestClient


class TestConstructorDataFlow:
    """Test complete constructor data flow through all layers"""
    
    def test_constructor_list_flow_from_api_to_data(self, client: TestClient):
        """Constructor list flows correctly from API → service → loader"""
        response = client.get("/api/constructors")
        assert response.status_code == 200
        
        data = response.json()
        constructors = data["MRData"]["ConstructorTable"]["Constructors"]
        
        # Should return all constructors from data file
        assert len(constructors) > 100, "Should have 100+ constructors in database"
        
        # Verify data integrity
        constructor_ids = [c["constructorId"] for c in constructors]
        assert "ferrari" in constructor_ids
        assert "mclaren" in constructor_ids
        assert "mercedes" in constructor_ids
    
    def test_single_constructor_flow(self, client: TestClient):
        """Single constructor retrieval flows through all layers correctly"""
        response = client.get("/api/constructors/red_bull")
        assert response.status_code == 200
        
        data = response.json()
        constructors = data["MRData"]["ConstructorTable"]["Constructors"]
        assert len(constructors) == 1
        
        constructor = constructors[0]
        assert constructor["constructorId"] == "red_bull"
        assert constructor["name"] == "Red Bull"
        assert "nationality" in constructor
    
    def test_constructor_stats_computation_flow(self, client: TestClient):
        """Constructor stats computation flows through service layer"""
        response = client.get("/api/constructors/ferrari/stats")
        assert response.status_code == 200
        
        stats = response.json()
        
        # Ferrari should have significant statistics
        assert stats["totalWins"] > 200, "Ferrari should have 200+ wins"
        assert stats["totalChampionships"] > 0, "Ferrari should have championships"
        assert stats["totalPoles"] > 0, "Ferrari should have pole positions"
    
    def test_constructor_season_results_flow(self, client: TestClient):
        """Season results filtered by constructor flow correctly"""
        response = client.get("/api/constructors/mercedes/seasons/2020")
        assert response.status_code == 200
        
        data = response.json()
        races = data["MRData"]["RaceTable"]["Races"]
        
        # Should have results for all 2020 races
        assert len(races) > 10, "2020 season had multiple races"
        
        # Verify Mercedes drivers in results
        for race in races[:3]:  # Check first 3 races
            results = race["Results"]
            mercedes_results = [r for r in results if r.get("Constructor", {}).get("constructorId") == "mercedes"]
            assert len(mercedes_results) > 0, "Each race should have Mercedes results"


class TestConstructorStatsIntegration:
    """Test constructor statistics computation integration"""
    
    def test_championship_count_accuracy(self, client: TestClient):
        """Championship count matches historical records"""
        # Ferrari - most successful team
        response = client.get("/api/constructors/ferrari/stats")
        stats = response.json()
        assert stats["totalChampionships"] >= 16, "Ferrari has won 16+ championships"
        
        # Mercedes - dominant 2010s-2020s
        response = client.get("/api/constructors/mercedes/stats")
        stats = response.json()
        assert stats["totalChampionships"] >= 8, "Mercedes has won 8+ championships"
    
    def test_win_count_computation(self, client: TestClient):
        """Win count computation includes all seasons"""
        response = client.get("/api/constructors/mclaren/stats")
        stats = response.json()
        
        # McLaren is a historically successful team
        assert stats["totalWins"] > 100, "McLaren should have 100+ wins"
        assert stats["totalPodiums"] > stats["totalWins"], "Podiums > wins"
    
    def test_pole_position_computation(self, client: TestClient):
        """Pole position count computed correctly"""
        response = client.get("/api/constructors/williams/stats")
        stats = response.json()
        
        # Williams was dominant in 1990s
        assert stats["totalPoles"] > 100, "Williams should have 100+ poles"
    
    def test_stats_for_newer_teams(self, client: TestClient):
        """Stats work correctly for newer teams with less history"""
        response = client.get("/api/constructors/haas/stats")
        stats = response.json()
        
        # Haas entered F1 in 2016, limited success
        assert stats["totalWins"] == 0, "Haas has no wins yet"
        assert stats["totalChampionships"] == 0, "Haas has no championships"
        assert stats["totalPodiums"] == 0, "Haas has no podiums yet"
    
    def test_stats_include_best_season(self, client: TestClient):
        """Stats include best season information"""
        response = client.get("/api/constructors/red_bull/stats")
        stats = response.json()
        
        assert "bestSeasonPosition" in stats
        assert "bestSeasonYear" in stats
        assert stats["bestSeasonPosition"] == 1, "Red Bull has been champion"


class TestConstructorSearchIntegration:
    """Test constructor search and fuzzy matching"""
    
    def test_exact_match_works(self, client: TestClient):
        """Exact constructor ID match returns correct constructor"""
        response = client.get("/api/constructors/ferrari")
        assert response.status_code == 200
        
        constructor = response.json()["MRData"]["ConstructorTable"]["Constructors"][0]
        assert constructor["constructorId"] == "ferrari"
    
    def test_typo_provides_suggestions(self, client: TestClient):
        """Typo in constructor name provides helpful suggestions"""
        response = client.get("/api/constructors/ferarri")  # Missing 'r'
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "ferrari" in error.lower(), "Should suggest 'ferrari'"
    
    def test_partial_match_suggests_similar(self, client: TestClient):
        """Partial match suggests similar constructor names"""
        response = client.get("/api/constructors/red_bul")  # Missing 'l'
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "red_bull" in error.lower(), "Should suggest 'red_bull'"
    
    def test_invalid_constructor_year_combo(self, client: TestClient):
        """Invalid constructor shows helpful message even with valid year"""
        response = client.get("/api/constructors/fake_team/seasons/2023")
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "fake_team" in error.lower()
        assert "not found" in error.lower()


class TestConstructorSeasonDataIntegration:
    """Test constructor season data integration"""
    
    def test_season_data_includes_all_races(self, client: TestClient):
        """Season data includes all races for the year"""
        response = client.get("/api/constructors/ferrari/seasons/2023")
        assert response.status_code == 200
        
        races = response.json()["MRData"]["RaceTable"]["Races"]
        assert len(races) >= 20, "2023 season had 20+ races"
    
    def test_season_data_filters_by_constructor(self, client: TestClient):
        """Season results only include specified constructor"""
        response = client.get("/api/constructors/alpine/seasons/2022")
        assert response.status_code == 200
        
        races = response.json()["MRData"]["RaceTable"]["Races"]
        
        for race in races[:5]:  # Check first 5 races
            results = race["Results"]
            alpine_results = [r for r in results if r.get("Constructor", {}).get("constructorId") == "alpine"]
            assert len(alpine_results) > 0, f"Race {race['raceName']} should have Alpine results"
    
    def test_invalid_year_shows_available_range(self, client: TestClient):
        """Invalid year shows user what years are available"""
        response = client.get("/api/constructors/ferrari/seasons/1960")
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "1984" in error, "Should mention earliest year"
        assert "2024" in error, "Should mention latest year"
    
    def test_future_year_handled_gracefully(self, client: TestClient):
        """Future year request handled with helpful message"""
        response = client.get("/api/constructors/ferrari/seasons/2030")
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "2024" in error or "not found" in error.lower()


class TestConstructorErrorHandling:
    """Test constructor error handling and user feedback"""
    
    def test_nonexistent_constructor_provides_context(self, client: TestClient):
        """Nonexistent constructor provides helpful context"""
        response = client.get("/api/constructors/team_xyz_never_existed")
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "not found" in error.lower()
    
    def test_constructor_validation_before_year(self, client: TestClient):
        """Constructor validated before checking year data"""
        response = client.get("/api/constructors/nonexistent/seasons/2023")
        assert response.status_code == 404
        
        error = response.json()["detail"]
        # Should mention constructor issue, not year issue
        assert "nonexistent" in error.lower() or "not found" in error.lower()
    
    def test_case_sensitive_constructor_id(self, client: TestClient):
        """Constructor ID is case-sensitive, provides suggestions"""
        response = client.get("/api/constructors/Ferrari")  # Capital F
        assert response.status_code == 404
        
        error = response.json()["detail"]
        assert "ferrari" in error.lower(), "Should suggest lowercase version"
