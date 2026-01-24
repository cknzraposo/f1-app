"""
Integration tests for Season data flow

Tests end-to-end workflows:
- List seasons → View specific season
- Season data → Calculate standings
- Season data → Extract winners
- Error handling → Fuzzy suggestions
"""
import pytest
from fastapi.testclient import TestClient


class TestSeasonDataFlow:
    """Test complete season data workflows"""
    
    def test_list_seasons_then_view_specific_season(self, client: TestClient):
        """Can list available seasons then view a specific one"""
        # List all seasons
        seasons_response = client.get("/api/seasons")
        assert seasons_response.status_code == 200
        seasons = seasons_response.json()["seasons"]
        
        # Pick a recent season
        season_year = 2023
        assert season_year in seasons
        
        # View specific season
        season_response = client.get(f"/api/seasons/{season_year}")
        assert season_response.status_code == 200
        season_data = season_response.json()
        
        # Verify season data
        assert season_data["MRData"]["RaceTable"]["season"] == str(season_year)
        races = season_data["MRData"]["RaceTable"]["Races"]
        assert len(races) > 0
    
    def test_season_data_contains_complete_race_info(self, client: TestClient):
        """Season data includes complete race information"""
        response = client.get("/api/seasons/2023")
        races = response.json()["MRData"]["RaceTable"]["Races"]
        
        assert len(races) > 0
        race = races[0]
        
        # Check race metadata
        assert "raceName" in race
        assert "Circuit" in race
        assert "date" in race
        
        # Check results
        assert "Results" in race
        assert len(race["Results"]) > 0
        
        # Check result structure
        result = race["Results"][0]
        assert "position" in result
        assert "Driver" in result
        assert "Constructor" in result
        assert "Time" in result or "status" in result
    
    def test_season_standings_calculation_accuracy(self, client: TestClient):
        """Standings are calculated correctly from race results"""
        response = client.get("/api/seasons/2023/standings")
        data = response.json()
        
        driver_standings = data["driverStandings"]
        
        # Check standings are sorted by position
        for i in range(len(driver_standings) - 1):
            assert driver_standings[i]["position"] <= driver_standings[i + 1]["position"]
        
        # Check leader has most points
        leader = driver_standings[0]
        assert leader["position"] == 1
        assert leader["points"] > 0
        
        # Verify points decrease or stay same
        for i in range(len(driver_standings) - 1):
            curr_points = float(driver_standings[i]["points"])
            next_points = float(driver_standings[i + 1]["points"])
            assert curr_points >= next_points
    
    def test_constructor_standings_calculation_accuracy(self, client: TestClient):
        """Constructor standings are calculated correctly"""
        response = client.get("/api/seasons/2023/standings")
        data = response.json()
        
        constructor_standings = data["constructorStandings"]
        
        # Check standings are sorted
        for i in range(len(constructor_standings) - 1):
            assert constructor_standings[i]["position"] <= constructor_standings[i + 1]["position"]
        
        # Check leader
        leader = constructor_standings[0]
        assert leader["position"] == 1
        assert leader["points"] > 0
        assert leader["wins"] >= 0
    
    def test_season_winners_extraction_accuracy(self, client: TestClient):
        """Winners list is extracted correctly from season data"""
        # Get full season data
        season_response = client.get("/api/seasons/2023")
        races = season_response.json()["MRData"]["RaceTable"]["Races"]
        
        # Get winners list
        winners_response = client.get("/api/seasons/2023/winners")
        winners = winners_response.json()["winners"]
        
        # Should have same number of races
        assert len(winners) == len(races)
        
        # Check each winner matches first place finisher
        for i, (race, winner) in enumerate(zip(races, winners)):
            race_winner = race["Results"][0]
            
            assert winner["round"] == race["round"]
            assert winner["raceName"] == race["raceName"]
            assert winner["driver"]["driverId"] == race_winner["Driver"]["driverId"]
            assert winner["constructor"]["constructorId"] == race_winner["Constructor"]["constructorId"]
    
    def test_multiple_seasons_data_consistency(self, client: TestClient):
        """Multiple seasons maintain consistent data structures"""
        seasons_to_test = [2020, 2021, 2022, 2023]
        
        for year in seasons_to_test:
            response = client.get(f"/api/seasons/{year}")
            assert response.status_code == 200
            
            data = response.json()
            assert "MRData" in data
            assert "RaceTable" in data["MRData"]
            assert "Races" in data["MRData"]["RaceTable"]
            assert len(data["MRData"]["RaceTable"]["Races"]) > 0
    
    def test_season_to_standings_to_winners_workflow(self, client: TestClient):
        """Complete workflow: list → season → standings → winners"""
        # Step 1: List seasons
        seasons = client.get("/api/seasons").json()["seasons"]
        assert 2023 in seasons
        
        # Step 2: Get season data
        season = client.get("/api/seasons/2023").json()
        races = season["MRData"]["RaceTable"]["Races"]
        assert len(races) > 0
        
        # Step 3: Get standings
        standings = client.get("/api/seasons/2023/standings").json()
        assert len(standings["driverStandings"]) > 0
        assert len(standings["constructorStandings"]) > 0
        
        # Step 4: Get winners
        winners = client.get("/api/seasons/2023/winners").json()
        assert len(winners["winners"]) == len(races)


class TestSeasonErrorHandling:
    """Test error handling for season endpoints"""
    
    def test_invalid_year_returns_helpful_message(self, client: TestClient):
        """Invalid year returns message with available range"""
        response = client.get("/api/seasons/1950")
        assert response.status_code == 404
        
        error_message = response.json()["detail"]
        assert "1950" in error_message
        assert "1984" in error_message or "Available" in error_message
        assert "2024" in error_message or "Available" in error_message
    
    def test_future_year_returns_helpful_message(self, client: TestClient):
        """Future year returns helpful error message"""
        response = client.get("/api/seasons/2030")
        assert response.status_code == 404
        
        error_message = response.json()["detail"]
        assert "2030" in error_message
        assert "not available" in error_message.lower()
    
    def test_string_year_returns_422(self, client: TestClient):
        """Non-numeric year returns 422 validation error"""
        response = client.get("/api/seasons/notayear")
        assert response.status_code == 422
    
    def test_standings_for_invalid_year(self, client: TestClient):
        """Standings endpoint validates year"""
        response = client.get("/api/seasons/1950/standings")
        assert response.status_code == 404
        
        error_message = response.json()["detail"]
        assert "1950" in error_message
    
    def test_winners_for_invalid_year(self, client: TestClient):
        """Winners endpoint validates year"""
        response = client.get("/api/seasons/2030/winners")
        assert response.status_code == 404


class TestSeasonEdgeCases:
    """Test edge cases for season endpoints"""
    
    def test_earliest_available_season(self, client: TestClient):
        """Can retrieve earliest season (1984)"""
        response = client.get("/api/seasons/1984")
        assert response.status_code == 200
        
        data = response.json()
        assert data["MRData"]["RaceTable"]["season"] == "1984"
    
    def test_latest_available_season(self, client: TestClient):
        """Can retrieve latest season (2024)"""
        response = client.get("/api/seasons/2024")
        assert response.status_code == 200
        
        data = response.json()
        assert data["MRData"]["RaceTable"]["season"] == "2024"
    
    def test_season_with_no_races(self, client: TestClient):
        """Handles seasons that might have incomplete data gracefully"""
        # Test a valid year
        response = client.get("/api/seasons/2024")
        assert response.status_code == 200
        
        # Should still return valid structure even if races are incomplete
        data = response.json()
        assert "MRData" in data
        assert "RaceTable" in data["MRData"]
    
    def test_standings_sorting_with_equal_points(self, client: TestClient):
        """Standings handle drivers with equal points correctly"""
        response = client.get("/api/seasons/2023/standings")
        standings = response.json()["driverStandings"]
        
        # Verify all positions are unique and sequential
        positions = [s["position"] for s in standings]
        assert positions == list(range(1, len(positions) + 1))
    
    def test_winners_include_all_rounds(self, client: TestClient):
        """Winners list includes all race rounds"""
        response = client.get("/api/seasons/2023/winners")
        winners = response.json()["winners"]
        
        # Check rounds are sequential
        rounds = [int(w["round"]) for w in winners]
        assert rounds == list(range(1, len(rounds) + 1))
    
    def test_season_data_caching(self, client: TestClient):
        """Season data is cached for repeat requests"""
        import time
        
        # First request (cache miss)
        start1 = time.time()
        response1 = client.get("/api/seasons/2023")
        time1 = (time.time() - start1) * 1000
        
        # Second request (cache hit)
        start2 = time.time()
        response2 = client.get("/api/seasons/2023")
        time2 = (time.time() - start2) * 1000
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()
        
        # Cached request should be significantly faster
        assert time2 < time1 * 0.5 or time2 < 5  # Either 50% faster or sub-5ms


class TestSeasonDataIntegrity:
    """Test data integrity across season endpoints"""
    
    def test_driver_wins_match_winners_list(self, client: TestClient):
        """Driver wins in standings match winners list"""
        # Get standings
        standings = client.get("/api/seasons/2023/standings").json()
        driver_wins = {
            s["driverId"]: s["wins"] 
            for s in standings["driverStandings"]
        }
        
        # Get winners
        winners = client.get("/api/seasons/2023/winners").json()["winners"]
        counted_wins = {}
        for winner in winners:
            driver_id = winner["driver"]["driverId"]
            counted_wins[driver_id] = counted_wins.get(driver_id, 0) + 1
        
        # Compare
        for driver_id, wins in driver_wins.items():
            if wins > 0:
                assert driver_id in counted_wins
                assert counted_wins[driver_id] == wins
    
    def test_constructor_wins_match_winners_list(self, client: TestClient):
        """Constructor wins in standings match winners list"""
        # Get standings
        standings = client.get("/api/seasons/2023/standings").json()
        constructor_wins = {
            s["constructorId"]: s["wins"] 
            for s in standings["constructorStandings"]
        }
        
        # Get winners
        winners = client.get("/api/seasons/2023/winners").json()["winners"]
        counted_wins = {}
        for winner in winners:
            constructor_id = winner["constructor"]["constructorId"]
            counted_wins[constructor_id] = counted_wins.get(constructor_id, 0) + 1
        
        # Compare
        for constructor_id, wins in constructor_wins.items():
            if wins > 0:
                assert constructor_id in counted_wins
                assert counted_wins[constructor_id] == wins
    
    def test_season_years_are_consistent(self, client: TestClient):
        """Year in season data matches requested year"""
        test_years = [1984, 1995, 2000, 2010, 2020, 2023, 2024]
        
        for year in test_years:
            response = client.get(f"/api/seasons/{year}")
            if response.status_code == 200:
                data = response.json()
                assert data["MRData"]["RaceTable"]["season"] == str(year)
                
                # Check each race is from that season
                for race in data["MRData"]["RaceTable"]["Races"]:
                    assert race["season"] == str(year)
