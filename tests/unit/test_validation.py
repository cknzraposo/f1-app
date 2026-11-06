import pytest

from app.services.validation import get_year_range_message, validate_year


def test_validate_year_uses_available_seasons():
    assert validate_year(2025)
    assert validate_year(2026)
    assert not validate_year(2030, raise_on_invalid=False)


def test_invalid_year_error_uses_available_range():
    with pytest.raises(ValueError, match="1984-2026"):
        validate_year(2030)


def test_year_range_message_uses_available_seasons():
    assert get_year_range_message() == "Valid years: 1984-2026"
