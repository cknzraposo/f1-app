"""
Pytest configuration and fixtures for F1 app tests.

Provides fixtures for:
- Sample driver data
- Sample constructor data  
- Sample season data
- Mock API responses
- Test IDs and years
- Test client for API testing
"""
import pytest
import sys
from pathlib import Path
from typing import Dict, Any
from fastapi.testclient import TestClient

# Add app directory to Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.api_server import app


# ===== FastAPI Test Client =====

@pytest.fixture
def client():
    """Provide a FastAPI test client for making HTTP requests."""
    return TestClient(app)


# ===== Test Data IDs and Constants =====

@pytest.fixture
def mock_driver_id():
    """Provide a known driver ID for testing."""
    return "hamilton"


@pytest.fixture
def mock_constructor_id():
    """Provide a known constructor ID for testing."""
    return "red_bull"


@pytest.fixture
def test_year():
    """Provide a test year that exists in the dataset."""
    return 2023


@pytest.fixture
def test_year_range():
    """Provide a range of test years."""
    return (1984, 2024)


@pytest.fixture
def invalid_year():
    """Provide an invalid year for testing error handling."""
    return 2030


# ===== Sample Driver Data =====

@pytest.fixture
def sample_driver_data() -> Dict[str, Any]:
    """
    Provide sample driver data matching Ergast API format.
    
    Returns minimal but valid driver data structure for testing.
    """
    return {
        "MRData": {
            "DriverTable": {
                "Drivers": [
                    {
                        "driverId": "hamilton",
                        "code": "HAM",
                        "url": "http://en.wikipedia.org/wiki/Lewis_Hamilton",
                        "givenName": "Lewis",
                        "familyName": "Hamilton",
                        "dateOfBirth": "1985-01-07",
                        "nationality": "British"
                    },
                    {
                        "driverId": "verstappen",
                        "code": "VER",
                        "url": "http://en.wikipedia.org/wiki/Max_Verstappen",
                        "givenName": "Max",
                        "familyName": "Verstappen",
                        "dateOfBirth": "1997-09-30",
                        "nationality": "Dutch"
                    },
                    {
                        "driverId": "alonso",
                        "code": "ALO",
                        "url": "http://en.wikipedia.org/wiki/Fernando_Alonso",
                        "givenName": "Fernando",
                        "familyName": "Alonso",
                        "dateOfBirth": "1981-07-29",
                        "nationality": "Spanish"
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_driver() -> Dict[str, Any]:
    """Provide a single driver object for testing."""
    return {
        "driverId": "hamilton",
        "code": "HAM",
        "givenName": "Lewis",
        "familyName": "Hamilton",
        "dateOfBirth": "1985-01-07",
        "nationality": "British"
    }


# ===== Sample Constructor Data =====

@pytest.fixture
def sample_constructor_data() -> Dict[str, Any]:
    """
    Provide sample constructor data matching Ergast API format.
    
    Returns minimal but valid constructor data structure for testing.
    """
    return {
        "MRData": {
            "ConstructorTable": {
                "Constructors": [
                    {
                        "constructorId": "red_bull",
                        "url": "http://en.wikipedia.org/wiki/Red_Bull_Racing",
                        "name": "Red Bull",
                        "nationality": "Austrian"
                    },
                    {
                        "constructorId": "mercedes",
                        "url": "http://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One",
                        "name": "Mercedes",
                        "nationality": "German"
                    },
                    {
                        "constructorId": "ferrari",
                        "url": "http://en.wikipedia.org/wiki/Scuderia_Ferrari",
                        "name": "Ferrari",
                        "nationality": "Italian"
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_constructor() -> Dict[str, Any]:
    """Provide a single constructor object for testing."""
    return {
        "constructorId": "red_bull",
        "name": "Red Bull",
        "nationality": "Austrian"
    }


# ===== Sample Season Data =====

@pytest.fixture
def sample_season_data() -> Dict[str, Any]:
    """
    Provide sample season results data matching Ergast API format.
    
    Returns minimal but valid season data structure for testing.
    """
    return {
        "MRData": {
            "RaceTable": {
                "season": "2023",
                "Races": [
                    {
                        "season": "2023",
                        "round": "1",
                        "raceName": "Bahrain Grand Prix",
                        "date": "2023-03-05",
                        "Circuit": {
                            "circuitId": "bahrain",
                            "circuitName": "Bahrain International Circuit",
                            "Location": {
                                "locality": "Sakhir",
                                "country": "Bahrain"
                            }
                        },
                        "Results": [
                            {
                                "number": "1",
                                "position": "1",
                                "points": "25",
                                "Driver": {
                                    "driverId": "verstappen",
                                    "givenName": "Max",
                                    "familyName": "Verstappen"
                                },
                                "Constructor": {
                                    "constructorId": "red_bull",
                                    "name": "Red Bull"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_season_data_2023() -> Dict[str, Any]:
    """
    Provide sample 2023 season data with comprehensive race structure.
    Includes standings data for championship testing.
    """
    return {
        "MRData": {
            "RaceTable": {
                "season": "2023",
                "Races": [
                    {
                        "season": "2023",
                        "round": "1",
                        "raceName": "Bahrain Grand Prix",
                        "date": "2023-03-05",
                        "Circuit": {
                            "circuitId": "bahrain",
                            "circuitName": "Bahrain International Circuit"
                        },
                        "Results": [
                            {
                                "number": "1",
                                "position": "1",
                                "points": "25",
                                "Driver": {"driverId": "verstappen", "givenName": "Max", "familyName": "Verstappen"},
                                "Constructor": {"constructorId": "red_bull", "name": "Red Bull"}
                            },
                            {
                                "number": "11",
                                "position": "2",
                                "points": "18",
                                "Driver": {"driverId": "perez", "givenName": "Sergio", "familyName": "Pérez"},
                                "Constructor": {"constructorId": "red_bull", "name": "Red Bull"}
                            }
                        ],
                        "QualifyingResults": [
                            {
                                "position": "1",
                                "Driver": {"driverId": "verstappen"},
                                "Constructor": {"constructorId": "red_bull"}
                            }
                        ]
                    },
                    {
                        "season": "2023",
                        "round": "2",
                        "raceName": "Saudi Arabian Grand Prix",
                        "date": "2023-03-19",
                        "Circuit": {
                            "circuitId": "jeddah",
                            "circuitName": "Jeddah Corniche Circuit"
                        },
                        "Results": [
                            {
                                "position": "1",
                                "points": "25",
                                "Driver": {"driverId": "perez"},
                                "Constructor": {"constructorId": "red_bull"}
                            }
                        ],
                        "QualifyingResults": [
                            {
                                "position": "1",
                                "Driver": {"driverId": "perez"},
                                "Constructor": {"constructorId": "red_bull"}
                            }
                        ]
                    }
                ]
            },
            "StandingsTable": {
                "season": "2023",
                "StandingsLists": [
                    {
                        "season": "2023",
                        "round": "22",
                        "DriverStandings": [
                            {"position": "1", "Driver": {"driverId": "verstappen"}, "Constructor": {"constructorId": "red_bull"}},
                            {"position": "2", "Driver": {"driverId": "perez"}, "Constructor": {"constructorId": "red_bull"}}
                        ],
                        "ConstructorStandings": [
                            {"position": "1", "Constructor": {"constructorId": "red_bull"}, "points": "860"},
                            {"position": "2", "Constructor": {"constructorId": "mercedes"}, "points": "409"},
                            {"position": "3", "Constructor": {"constructorId": "ferrari"}, "points": "406"}
                        ]
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_season_data_2022() -> Dict[str, Any]:
    """
    Provide sample 2022 season data for multi-season testing.
    Includes standings data for aggregation testing.
    """
    return {
        "MRData": {
            "RaceTable": {
                "season": "2022",
                "Races": [
                    {
                        "season": "2022",
                        "round": "1",
                        "raceName": "Bahrain Grand Prix",
                        "Results": [
                            {
                                "position": "1",
                                "points": "25",
                                "Driver": {"driverId": "leclerc"},
                                "Constructor": {"constructorId": "ferrari"}
                            }
                        ],
                        "QualifyingResults": [
                            {
                                "position": "1",
                                "Driver": {"driverId": "leclerc"},
                                "Constructor": {"constructorId": "ferrari"}
                            }
                        ]
                    },
                    {
                        "season": "2022",
                        "round": "2",
                        "raceName": "Saudi Arabian Grand Prix",
                        "Results": [
                            {
                                "position": "1",
                                "Driver": {"driverId": "verstappen"},
                                "Constructor": {"constructorId": "red_bull"}
                            }
                        ]
                    }
                ]
            },
            "StandingsTable": {
                "season": "2022",
                "StandingsLists": [
                    {
                        "season": "2022",
                        "round": "22",
                        "DriverStandings": [
                            {"position": "1", "Driver": {"driverId": "verstappen"}, "Constructor": {"constructorId": "red_bull"}},
                            {"position": "2", "Driver": {"driverId": "leclerc"}, "Constructor": {"constructorId": "ferrari"}}
                        ],
                        "ConstructorStandings": [
                            {"position": "1", "Constructor": {"constructorId": "red_bull"}, "points": "759"},
                            {"position": "2", "Constructor": {"constructorId": "ferrari"}, "points": "554"},
                            {"position": "3", "Constructor": {"constructorId": "mercedes"}, "points": "515"}
                        ]
                    }
                ]
            }
        }
    }


# ===== Sample Statistics =====

@pytest.fixture
def sample_driver_stats() -> Dict[str, Any]:
    """Provide sample driver statistics for testing."""
    return {
        "driver_id": "hamilton",
        "total_races": 334,
        "wins": 103,
        "podiums": 197,
        "poles": 104,
        "fastest_laps": 65,
        "championships": 7,
        "years_active": "2007-2024"
    }


@pytest.fixture
def sample_constructor_stats() -> Dict[str, Any]:
    """Provide sample constructor statistics for testing."""
    return {
        "constructor_id": "red_bull",
        "total_races": 365,
        "wins": 118,
        "podiums": 256,
        "poles": 96,
        "fastest_laps": 90,
        "championships": 6
    }


# ===== Mock Functions =====

@pytest.fixture
def mock_load_drivers(sample_driver_data, monkeypatch):
    """Mock load_drivers to return sample data."""
    def _mock():
        return sample_driver_data
    
    from app import json_loader
    monkeypatch.setattr(json_loader, "load_drivers", _mock)
    return _mock


@pytest.fixture
def mock_load_constructors(sample_constructor_data, monkeypatch):
    """Mock load_constructors to return sample data."""
    def _mock():
        return sample_constructor_data
    
    from app import json_loader
    monkeypatch.setattr(json_loader, "load_constructors", _mock)
    return _mock


@pytest.fixture
def mock_load_season_results(sample_season_data, monkeypatch):
    """Mock load_season_results to return sample data."""
    def _mock(year: int):
        return sample_season_data
    
    from app import json_loader
    monkeypatch.setattr(json_loader, "load_season_results", _mock)
    return _mock

