"""Opt-in future feature contract; intentionally red on the tutorial starter."""

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.api_server import app
from app.routers import seasons


NOTICE = "Local dataset; full-season completeness is not verified."


@pytest.fixture
def local_season(monkeypatch):
    data = {
        "MRData": {
            "total": "999",
            "RaceTable": {
                "season": "2023",
                "Races": [{"round": "1"}, {"round": "7"}],
            },
        }
    }

    def load(year):
        if year != 2023:
            raise FileNotFoundError(f"No fixture for {year}")
        return data

    monkeypatch.setattr(seasons, "load_season_results", load)
    monkeypatch.setattr(seasons, "get_available_seasons", lambda: [2021, 2023, 2024])
    return data


@pytest.mark.parametrize(
    "race_count,standings_lists",
    [(0, None), (2, None), (2, []), (2, [{"season": "2023"}])],
)
def test_coverage_contract(local_season, race_count, standings_lists):
    local_season["MRData"]["RaceTable"]["Races"] = [
        {"round": str(index * 3 + 1)} for index in range(race_count)
    ]
    if standings_lists is not None:
        local_season["MRData"]["StandingsTable"] = {"StandingsLists": standings_lists}
    original = deepcopy(local_season)

    with TestClient(app) as client:
        response = client.get("/api/seasons/2023/coverage")
        raw_response = client.get("/api/seasons/2023")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "season": 2023,
        "raceCount": race_count,
        "hasStandings": bool(standings_lists),
        "completeness": "unknown",
        "notice": NOTICE,
    }
    assert type(body["season"]) is int
    assert type(body["raceCount"]) is int
    assert type(body["hasStandings"]) is bool
    assert local_season == original, "Do not mutate cached loader data"
    assert raw_response.status_code == 200
    assert raw_response.json() == original, "Preserve the raw Ergast endpoint"


@pytest.mark.parametrize("year", [2022, 2030, 1983])
def test_missing_local_file_is_404(local_season, year):
    with TestClient(app) as client:
        response = client.get(f"/api/seasons/{year}/coverage")
    assert response.status_code == 404
    assert response.json()["detail"]


def test_invalid_year_is_422(local_season):
    with TestClient(app) as client:
        response = client.get("/api/seasons/not-a-year/coverage")
    assert response.status_code == 422
