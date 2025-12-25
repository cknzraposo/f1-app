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
    
    # Fetch all drivers in one request with the total as limit
    url = f"{BASE_URL}/drivers.json?limit={total}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    all_data = response.json()
    fetched_count = len(all_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", []))
    print(f"Successfully fetched {fetched_count} drivers")
    
    return all_data

def save_drivers(data: Dict[str, Any], folder: str = "f1drivers"):
    """Save driver list into f1drivers/drivers.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "drivers.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved driver list to {filepath}")
