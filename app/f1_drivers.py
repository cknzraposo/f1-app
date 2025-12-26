import requests
import os
import json
from typing import Dict, Any, List

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_all_drivers() -> Dict[str, Any]:
    """Fetch all F1 drivers from Ergast mirror with pagination."""
    print("Fetching all F1 drivers...")
    
    # First request to get total count
    url = f"{BASE_URL}/drivers.json?limit=1"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
    
    total = int(data.get("MRData", {}).get("total", 0))
    print(f"Total drivers to fetch: {total}")
    
    # Fetch all drivers with pagination
    all_drivers = []
    limit = 100
    offset = 0
    
    while offset < total:
        url = f"{BASE_URL}/drivers.json?limit={limit}&offset={offset}"
        print(f"Fetching drivers {offset} to {offset + limit}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        page_data = response.json()
        drivers = page_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
        all_drivers.extend(drivers)
        offset += limit
    
    print(f"Successfully fetched {len(all_drivers)} drivers")
    
    # Return in Ergast format
    return {
        "MRData": {
            "DriverTable": {
                "Drivers": all_drivers
            },
            "total": str(len(all_drivers))
        }
    }

def save_drivers(data: Dict[str, Any], folder: str = "f1drivers"):
    """Save driver list into f1drivers/drivers.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "drivers.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved driver list to {filepath}")
