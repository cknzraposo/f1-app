"""Verify tutorial links and the repair contract's sensitivity to the seeded bug."""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from app.query_parser import QueryParser
from _docs.tutorials.checks import repair_checks


TUTORIALS = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("document", sorted(TUTORIALS.glob("*.md")), ids=lambda p: p.name)
def test_local_links_exist(document):
    text = document.read_text(encoding="utf-8")
    for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        parsed = urlsplit(target)
        if parsed.scheme or not parsed.path:
            continue
        destination = document.parent / unquote(parsed.path)
        assert destination.exists(), f"{document.name}: missing {target}"


@pytest.fixture
def priority_regression(monkeypatch):
    original = QueryParser.parse

    def championship_first(self, text):
        result = self._parse_championship_query(text.lower().strip())
        return result if result is not None else original(self, text)

    monkeypatch.setattr(QueryParser, "parse", championship_first)


def test_keyword_check_detects_seeded_regression(priority_regression):
    with pytest.raises(AssertionError):
        repair_checks.test_keyword_routing(
            "who won the most races in 2023", 2023, "winners", "season_winners"
        )


def test_api_check_detects_seeded_regression(priority_regression, monkeypatch):
    with pytest.raises(AssertionError):
        repair_checks.test_response_contract(
            monkeypatch,
            "who won the most races in 2023",
            2023,
            "winners",
            "season_winners",
        )
