import requests
import os
import json
from typing import Dict, Any, List

BASE_URL = "https://api.jolpi.ca/ergast/f1/results"
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
    races_by_round: Dict[tuple[str, str], Dict[str, Any]] = {}
    mrdata_master: Dict[str, Any] = {}
    total = 0

    while True:
        params = {"limit": DEFAULT_LIMIT, "offset": offset}
        data = _get(url, params=params)

        mrdata = data.get("MRData", {})
        race_table = mrdata.get("RaceTable", {})
        batch = race_table.get("Races", [])

        if not mrdata_master:
            mrdata_master = mrdata.copy()
            mrdata_master["RaceTable"] = race_table.copy()
            mrdata_master["RaceTable"]["Races"] = []
            total = int(mrdata.get("total", 0))

        for race in batch:
            race_key = (race.get("season", str(year)), race.get("round", ""))
            existing_race = races_by_round.get(race_key)
            if existing_race is None:
                races_by_round[race_key] = race
                continue

            existing_results = existing_race.setdefault("Results", [])
            result_ids = {
                result.get("Driver", {}).get("driverId")
                for result in existing_results
            }
            for result in race.get("Results", []):
                result_id = result.get("Driver", {}).get("driverId")
                if result_id not in result_ids:
                    existing_results.append(result)
                    result_ids.add(result_id)

        offset += int(mrdata.get("limit", DEFAULT_LIMIT))
        if not batch or offset >= total:
            break

    mrdata_master["RaceTable"]["Races"] = list(races_by_round.values())
    return {"MRData": mrdata_master}

def save_results(year: int, data: Dict[str, Any], folder: str = "f1data"):
    """Save season results into f1data/<year>_results.json."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{year}_results.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {year} results to {filepath}")
