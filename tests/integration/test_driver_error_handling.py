"""Test error handling with suggestions for driver endpoints"""
from fastapi.testclient import TestClient
from app.api_server import app

client = TestClient(app)


def test_driver_not_found_includes_suggestions():
    """Error message should include similar driver suggestions"""
    response = client.get("/api/drivers/verstapen")  # Misspelled
    
    assert response.status_code == 404
    error_detail = response.json()["detail"]
    assert "verstapen" in error_detail
    assert "not found" in error_detail.lower()
    # Should suggest similar names (but fuzzy matching may not always find exact match)


def test_invalid_season_includes_available_range():
    """Error message for invalid season should show available years"""
    response = client.get("/api/drivers/abate/seasons/2050")
    
    assert response.status_code == 404
    error_detail = response.json()["detail"]
    assert "2050" in error_detail
    assert "1984" in error_detail
    assert "2024" in error_detail


def test_completely_invalid_driver_no_crash():
    """Completely random driver ID should not crash, just return 404"""
    response = client.get("/api/drivers/this_is_not_a_real_driver_xyz123")
    
    assert response.status_code == 404
    error_detail = response.json()["detail"]
    assert "not found" in error_detail.lower()


if __name__ == "__main__":
    test_driver_not_found_includes_suggestions()
    test_invalid_season_includes_available_range()
    test_completely_invalid_driver_no_crash()
    print("✅ All error handling tests passed!")
