import requests
import os
import json
from typing import Dict, Any

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_all_constructors() -> Dict[str, Any]:
    """Fetch all F1 constructors from Ergast mirror and return JSON."""
    url = f"{BASE_URL}/constructors.json"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()

def save_constructors(data: Dict[str, Any], folder: str = "f1constructors"):
    """Save constructor list into f1constructors/constructors.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "constructors.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved constructor list to {filepath}")
