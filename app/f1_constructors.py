import requests
import os
import json
from typing import Dict, Any

BASE_URL = "https://api.jolpi.ca/ergast/f1/constructors"

def fetch_all_constructors() -> Dict[str, Any]:
    """
    Fetch all F1 constructors from Ergast mirror and return JSON.
    Handles pagination to get all constructors (214+ total).
    """
    all_constructors = []
    offset = 0
    limit = 100
    
    while True:
        url = f"{BASE_URL}.json?limit={limit}&offset={offset}"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        constructors = data["MRData"]["ConstructorTable"]["Constructors"]
        if not constructors:
            break
            
        all_constructors.extend(constructors)
        
        # Check if we got all
        total = int(data["MRData"]["total"])
        if len(all_constructors) >= total:
            break
            
        offset += limit
    
    # Return in Ergast format
    return {
        "MRData": {
            "xmlns": data["MRData"]["xmlns"],
            "series": data["MRData"]["series"],
            "url": data["MRData"]["url"],
            "limit": str(len(all_constructors)),
            "offset": "0",
            "total": str(len(all_constructors)),
            "ConstructorTable": {
                "Constructors": all_constructors
            }
        }
    }

def save_constructors(data: Dict[str, Any], folder: str = "f1constructors"):
    """Save constructor list into f1constructors/constructors.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "constructors.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved constructor list to {filepath}")
