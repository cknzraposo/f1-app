"""Quick endpoint validation script for driver endpoints (T011-T014)"""
from app.api_server import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 60)
print("T011: Testing GET /api/drivers")
print("=" * 60)
response = client.get("/api/drivers")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Returns JSON data")
    if "MRData" in data:
        drivers_count = len(data.get("MRData", {}).get("DriverTable", {}).get("Drivers", []))
        print(f"✓ Contains {drivers_count} drivers")
print()

print("=" * 60)
print("T012: Testing GET /api/drivers/{driver_id}")
print("=" * 60)
response = client.get("/api/drivers/hamilton")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Returns driver data for 'hamilton'")
    if "MRData" in data:
        drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
        if drivers and len(drivers) > 0:
            driver = drivers[0]
            print(f"✓ Driver: {driver.get('givenName')} {driver.get('familyName')}")
            print(f"✓ Nationality: {driver.get('nationality')}")
print()

print("=" * 60)
print("T014: Testing GET /api/drivers/{driver_id}/stats")
print("=" * 60)
response = client.get("/api/drivers/hamilton/stats")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Returns statistics")
    print(f"Stats keys: {list(data.keys())[:5]}...")
print()

print("✅ Driver endpoints validation complete!")
