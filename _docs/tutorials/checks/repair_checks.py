"""Opt-in shared repair contract; run explicitly with python -m pytest."""

import pytest
from fastapi.testclient import TestClient

from app.api_server import app
from app.query_parser import QueryParser
from app.routers import query as query_router


CASES = [
    ("who won the most races in 2023", 2023, "winners", "season_winners"),
    ("  WHO WON THE MOST RACES IN 2023  ", 2023, "winners", "season_winners"),
    ("who won the 2010 championship", 2010, "standings", "championship_standings"),
    ("2023 standings", 2023, "standings", "championship_standings"),
]


@pytest.mark.parametrize("text,year,resource,data_type", CASES)
def test_keyword_routing(text, year, resource, data_type):
    parsed = QueryParser().parse(text)
    assert parsed is not None
    assert parsed["endpoint"] == f"/api/seasons/{year}/{resource}"
    assert parsed["source"] == "keyword_parser"


@pytest.mark.parametrize("text,year,resource,data_type", CASES)
def test_response_contract(monkeypatch, text, year, resource, data_type):
    monkeypatch.setattr(
        query_router,
        "get_season_winners",
        lambda season: {"season": season, "winners": [{"driverId": "fixture"}]},
    )
    monkeypatch.setattr(
        query_router,
        "get_season_standings",
        lambda season: {"season": season, "driverStandings": [{"driverId": "fixture"}]},
    )
    with TestClient(app) as client:
        response = client.post("/api/query", json={"query": text})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["query"] == text.strip()
    assert body["action"] == "api_call"
    assert body["dataType"] == data_type
    assert body["data"]["season"] == year
    field = "winners" if resource == "winners" else "driverStandings"
    assert body["data"][field] == [{"driverId": "fixture"}]


def test_empty_query_is_rejected():
    with TestClient(app) as client:
        response = client.post("/api/query", json={"query": "   "})
    assert response.status_code == 400
    assert response.json()["detail"]
