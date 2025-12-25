import requests
import os
import json
from typing import Dict, Any

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_all_drivers() -> Dict[str, Any]:
    """Fetch all F1 drivers from Ergast mirror and return JSON."""
    url = f"{BASE_URL}/drivers.json"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()

def save_drivers(data: Dict[str, Any], folder: str = "f1drivers"):
    """Save driver list into f1drivers/drivers.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "drivers.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved driver list to {filepath}")
