"""
Pytest configuration and fixtures for F1 app tests.
"""
import pytest
import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir.parent))


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
