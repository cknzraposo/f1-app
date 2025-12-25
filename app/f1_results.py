import requests
import os
import json
from typing import Dict, Any, List

BASE_URL = "https://api.jolpi.ca/ergast/f1"
DEFAULT_LIMIT = 100  # Ergast supports pagination, bigger limit reduces calls

def _get(url: str, params: Dict[str, Any], timeout: int = 20, max_retries: int = 3) -> Dict[str, Any]:
    """Internal helper to GET with retries."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            last_exc = exc
    raise RuntimeError(f"Failed after {max_retries} attempts: {last_exc}")

def fetch_season_results(year: int) -> Dict[str, Any]:
    """Fetch all race results for a season and return merged JSON."""
    url = f"{BASE_URL}/{year}/results.json"
    offset = 0
    races: List[Dict[str, Any]] = []
    mrdata_master: Dict[str, Any] = {}

    while True:
        params = {"limit": DEFAULT_LIMIT, "offset": offset}
        data = _get(url, params=params)

        mrdata = data.get("MRData", {})
        race_table = mrdata.get("RaceTable", {})
        batch = race_table.get("Races", [])

        if not mrdata_master:
            mrdata_master = mrdata.copy()
            mrdata_master["RaceTable"]["Races"] = []

        races.extend(batch)

        if len(batch) < DEFAULT_LIMIT:
            break
        offset += DEFAULT_LIMIT

    mrdata_master["RaceTable"]["Races"] = races
    return {"MRData": mrdata_master}

def save_results(year: int, data: Dict[str, Any], folder: str = "f1data"):
    """Save season results into f1data/<year>_results.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{year}_results.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {year} results to {filepath}")
