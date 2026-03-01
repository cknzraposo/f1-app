"""
update_results.py - Incremental updater for f1resultsall/all_results.json

Fetches only new seasons not already in the dataset and merges them in.
Run this each season (or mid-season) to keep the data current.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "https://api.jolpi.ca/ergast/f1"
OUTPUT_FILE = Path("f1resultsall/all_results.json")


def fetch_season(year: int) -> list:
    """Fetch all races for a given season with pagination."""
    url = f"{BASE_URL}/{year}/results.json"
    offset = 0
    limit = 100
    all_races = []

    while True:
        time.sleep(0.5)
        try:
            resp = requests.get(url, params={"limit": limit, "offset": offset}, timeout=30)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"  [Rate limited, waiting 30s...]")
                time.sleep(30)
                continue
            raise

        data = resp.json()
        mrdata = data.get("MRData", {})
        races = mrdata.get("RaceTable", {}).get("Races", [])

        for race in races:
            key = (race["season"], race["round"])
            if not any(r["season"] == race["season"] and r["round"] == race["round"] for r in all_races):
                all_races.append(race)

        if not races or len(races) < limit:
            break
        offset += limit

    return all_races


def main():
    current_year = datetime.now().year

    # Load existing data
    print(f"Loading existing dataset from {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "r") as f:
        existing = json.load(f)

    existing_races = existing["MRData"]["RaceTable"]["Races"]
    existing_seasons = set(r["season"] for r in existing_races)
    latest_existing = max(int(s) for s in existing_seasons)

    print(f"Existing data: {len(existing_races)} races, latest season: {latest_existing}")
    print(f"Current year: {current_year}")

    new_races = []

    for year in range(latest_existing + 1, current_year + 1):
        print(f"\nFetching {year}...", end=" ", flush=True)
        races = fetch_season(year)
        if races:
            print(f"{len(races)} races found ✓")
            new_races.extend(races)
        else:
            print(f"no data yet, skipping.")

    # Also refresh current year in case season is ongoing (new races added)
    if str(current_year) in existing_seasons:
        print(f"\nRefreshing {current_year} (season may be ongoing)...", end=" ", flush=True)
        existing_races = [r for r in existing_races if r["season"] != str(current_year)]
        refreshed = fetch_season(current_year)
        if refreshed:
            print(f"{len(refreshed)} races found ✓")
            new_races.extend(refreshed)

    if not new_races:
        print("\nNo new data found. Dataset is up to date.")
        return

    # Merge and save
    all_races = existing_races + new_races
    all_races.sort(key=lambda r: (int(r["season"]), int(r["round"])))
    total_results = sum(len(r.get("Results", [])) for r in all_races)

    existing["MRData"]["RaceTable"]["Races"] = all_races
    existing["MRData"]["total"] = str(total_results)
    existing["MRData"]["limit"] = str(len(all_races))

    print(f"\nSaving updated dataset...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    seasons = sorted(set(r["season"] for r in all_races))
    print(f"✅ Done! {len(all_races)} total races | {seasons[0]}–{seasons[-1]} | {total_results} driver results")


if __name__ == "__main__":
    main()
