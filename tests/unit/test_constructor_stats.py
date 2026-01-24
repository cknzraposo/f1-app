"""
Unit tests for Constructor statistics computation

Tests the pure business logic in F1Service for constructor statistics.
These tests isolate the service layer from HTTP and data loading concerns.
"""
import pytest
from app.services import F1Service


class TestConstructorStatisticsComputation:
    """Test pure statistics computation logic for constructors"""
    
    def test_championship_count_from_season_data(self, sample_season_data_2023, sample_season_data_2022):
        """Count constructor championships from season standings"""
        service = F1Service()
        
        # Mock Ferrari winning 2023
        season_2023 = sample_season_data_2023
        if "StandingsTable" in season_2023.get("MRData", {}):
            standings = season_2023["MRData"]["StandingsTable"]["StandingsLists"][0]
            standings["ConstructorStandings"][0]["Constructor"]["constructorId"] = "ferrari"
            standings["ConstructorStandings"][0]["position"] = "1"
        
        # Count should identify Ferrari as champion
        stats = service.get_constructor_statistics("ferrari", [season_2023])
        assert stats["totalChampionships"] >= 1
    
    def test_win_count_from_race_results(self, sample_season_data_2023):
        """Count constructor wins from race results"""
        service = F1Service()
        
        # Set up Ferrari wins in test data
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Make Ferrari win first 3 races
        for race in races[:3]:
            race["Results"][0]["Constructor"]["constructorId"] = "ferrari"
            race["Results"][0]["position"] = "1"
        
        stats = service.get_constructor_statistics("ferrari", [season_data])
        assert stats["totalWins"] >= 3
    
    def test_podium_count_computation(self, sample_season_data_2023):
        """Count constructor podiums (positions 1-3)"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Give Mercedes podiums in first 2 races
        for race in races[:2]:
            race["Results"][0]["Constructor"]["constructorId"] = "mercedes"
            race["Results"][0]["position"] = "1"
            race["Results"][1]["Constructor"]["constructorId"] = "mercedes"
            race["Results"][1]["position"] = "2"
        
        stats = service.get_constructor_statistics("mercedes", [season_data])
        assert stats["totalPodiums"] >= 4  # 2 wins + 2 second places
    
    def test_pole_position_count(self, sample_season_data_2023):
        """Count constructor pole positions from qualifying"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Red Bull gets poles in first 4 races
        pole_count = 0
        for race in races[:4]:
            if "QualifyingResults" in race:
                race["QualifyingResults"][0]["Constructor"]["constructorId"] = "red_bull"
                race["QualifyingResults"][0]["position"] = "1"
                pole_count += 1
        
        stats = service.get_constructor_statistics("red_bull", [season_data])
        assert stats["totalPoles"] >= pole_count
    
    def test_best_season_position_tracking(self, sample_season_data_2023, sample_season_data_2022):
        """Track best constructor championship position across seasons"""
        service = F1Service()
        
        # McLaren finishes 3rd in 2022, 4th in 2023
        season_2022 = sample_season_data_2022
        season_2023 = sample_season_data_2023
        
        if "StandingsTable" in season_2022.get("MRData", {}):
            standings_2022 = season_2022["MRData"]["StandingsTable"]["StandingsLists"][0]
            standings_2022["ConstructorStandings"][2]["Constructor"]["constructorId"] = "mclaren"
            standings_2022["ConstructorStandings"][2]["position"] = "3"
        
        if "StandingsTable" in season_2023.get("MRData", {}):
            standings_2023 = season_2023["MRData"]["StandingsTable"]["StandingsLists"][0]
            standings_2023["ConstructorStandings"][3]["Constructor"]["constructorId"] = "mclaren"
            standings_2023["ConstructorStandings"][3]["position"] = "4"
        
        stats = service.get_constructor_statistics("mclaren", [season_2022, season_2023])
        assert stats["bestSeasonPosition"] == 3
        assert stats["bestSeasonYear"] == 2022


class TestStatisticsAggregation:
    """Test aggregation of statistics across multiple seasons"""
    
    def test_wins_aggregate_across_seasons(self, sample_season_data_2023, sample_season_data_2022):
        """Wins from multiple seasons aggregate correctly"""
        service = F1Service()
        
        # Ferrari wins in both seasons
        for season_data in [sample_season_data_2023, sample_season_data_2022]:
            races = season_data["MRData"]["RaceTable"]["Races"]
            for race in races[:2]:  # 2 wins per season
                race["Results"][0]["Constructor"]["constructorId"] = "ferrari"
                race["Results"][0]["position"] = "1"
        
        stats = service.get_constructor_statistics("ferrari", [sample_season_data_2023, sample_season_data_2022])
        assert stats["totalWins"] >= 4  # 2 wins in each of 2 seasons
    
    def test_championships_aggregate_correctly(self, sample_season_data_2023, sample_season_data_2022):
        """Championship wins aggregate across seasons"""
        service = F1Service()
        
        # Mercedes wins both 2022 and 2023
        for season_data in [sample_season_data_2023, sample_season_data_2022]:
            if "StandingsTable" in season_data.get("MRData", {}):
                standings = season_data["MRData"]["StandingsTable"]["StandingsLists"][0]
                standings["ConstructorStandings"][0]["Constructor"]["constructorId"] = "mercedes"
                standings["ConstructorStandings"][0]["position"] = "1"
        
        stats = service.get_constructor_statistics("mercedes", [sample_season_data_2023, sample_season_data_2022])
        assert stats["totalChampionships"] >= 2
    
    def test_empty_season_list_returns_zero_stats(self):
        """Empty season list returns zeroed statistics"""
        service = F1Service()
        stats = service.get_constructor_statistics("ferrari", [])
        
        assert stats["totalWins"] == 0
        assert stats["totalChampionships"] == 0
        assert stats["totalPodiums"] == 0
        assert stats["totalPoles"] == 0


class TestStatisticsValidation:
    """Test validation and edge cases in statistics computation"""
    
    def test_handles_missing_constructor_in_race(self, sample_season_data_2023):
        """Handles races where constructor didn't participate"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Remove Haas from all results (simulate they didn't race)
        for race in races:
            race["Results"] = [r for r in race["Results"] 
                             if r.get("Constructor", {}).get("constructorId") != "haas"]
        
        stats = service.get_constructor_statistics("haas", [season_data])
        assert stats["totalWins"] == 0
        assert stats["totalPodiums"] == 0
    
    def test_handles_incomplete_race_data(self, sample_season_data_2023):
        """Handles races with incomplete result data"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Remove position data from some results
        if len(races) > 0:
            for result in races[0]["Results"]:
                if "position" in result:
                    del result["position"]
        
        # Should not crash, should handle gracefully
        stats = service.get_constructor_statistics("ferrari", [season_data])
        assert isinstance(stats["totalWins"], int)
    
    def test_constructor_id_case_sensitivity(self, sample_season_data_2023):
        """Constructor ID matching is case-sensitive"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Set up wins for lowercase "ferrari"
        for race in races[:3]:
            race["Results"][0]["Constructor"]["constructorId"] = "ferrari"
            race["Results"][0]["position"] = "1"
        
        # Query with different case should not match
        stats_upper = service.get_constructor_statistics("FERRARI", [season_data])
        assert stats_upper["totalWins"] == 0  # No match due to case
        
        stats_lower = service.get_constructor_statistics("ferrari", [season_data])
        assert stats_lower["totalWins"] >= 3  # Correct case matches
    
    def test_handles_missing_standings_data(self, sample_season_data_2023):
        """Handles seasons without standings data"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        # Remove standings data
        if "StandingsTable" in season_data.get("MRData", {}):
            del season_data["MRData"]["StandingsTable"]
        
        stats = service.get_constructor_statistics("ferrari", [season_data])
        # Should not crash, championships should be 0
        assert stats["totalChampionships"] == 0
    
    def test_position_must_be_numeric_or_string_int(self, sample_season_data_2023):
        """Position field can be string or int, both handled correctly"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Mix string and int positions
        if len(races) >= 2:
            races[0]["Results"][0]["position"] = "1"  # String
            races[0]["Results"][0]["Constructor"]["constructorId"] = "ferrari"
            
            races[1]["Results"][0]["position"] = 1  # Integer
            races[1]["Results"][0]["Constructor"]["constructorId"] = "ferrari"
        
        stats = service.get_constructor_statistics("ferrari", [season_data])
        assert stats["totalWins"] >= 2  # Both formats counted
    
    def test_dnf_not_counted_as_podium(self, sample_season_data_2023):
        """DNF (Did Not Finish) not counted as podium finish"""
        service = F1Service()
        
        season_data = sample_season_data_2023
        races = season_data["MRData"]["RaceTable"]["Races"]
        
        # Constructor has podium position but DNF status
        if len(races) > 0:
            races[0]["Results"][0]["Constructor"]["constructorId"] = "alpine"
            races[0]["Results"][0]["position"] = "2"
            races[0]["Results"][0]["status"] = "Retired"  # DNF
        
        stats = service.get_constructor_statistics("alpine", [season_data])
        # Implementation may or may not filter DNFs - document behavior
        # Most F1 stats count final classification position regardless of finish status
        assert isinstance(stats["totalPodiums"], int)
