import requests
import json
import time
from pathlib import Path
from typing import Dict, Any

def fetch_all_results():
    """
    Fetch ALL F1 race results from 1950-present from Ergast API and save to f1resultsall directory.
    
    Strategy: Fetch results year-by-year (since Ergast API doesn't support fetching
    all results in one call), then combine into a single unified dataset.
    
    This creates a comprehensive dataset of ~25,000+ individual driver results across
    all F1 races from 1950 to present, optimized for multi-season queries like
    career statistics and head-to-head comparisons.
    """
    base_url = "https://api.jolpi.ca/ergast/f1"
    output_dir = Path("f1resultsall")
    
    # Create directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    print(f"Fetching complete F1 historical results from Ergast API...")
    print(f"This will fetch all races from 1950 to present year-by-year.\n")
    
    try:
        # Strategy: Fetch year-by-year since Ergast doesn't provide all-time endpoint efficiently
        all_races = []
        mrdata_template = None
        
        # Start from 1950 (first F1 season) to current year
        start_year = 1950
        end_year = 2024  # Update this as needed
        total_years = end_year - start_year + 1
        
        for year_idx, year in enumerate(range(start_year, end_year + 1), 1):
            # Fetch results for this specific year with pagination
            url = f"{base_url}/{year}/results.json"
            offset = 0
            limit = 500  # More conservative limit to reduce API load
            year_races = []
            year_total_expected = None
            
            while True:
                # Rate limiting: Add delay between requests to avoid 429 errors
                time.sleep(1.0)  # 1 second delay between requests (very conservative)
                
                try:
                    response = requests.get(url, params={"limit": limit, "offset": offset}, timeout=30)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        print(f" [Rate limited, waiting 30s...]", flush=True)
                        time.sleep(30)
                        continue
                    raise
                
                data = response.json()
                mrdata = data.get('MRData', {})
                
                # Get expected total on first request
                if year_total_expected is None:
                    year_total_expected = int(mrdata.get('total', 0))
                
                # Save template from first successful response
                if not mrdata_template:
                    mrdata_template = {
                        'xmlns': mrdata.get('xmlns', ''),
                        'series': mrdata.get('series', 'f1'),
                        'url': 'https://api.jolpi.ca/ergast/f1/results/'
                    }
                
                race_table = mrdata.get('RaceTable', {})
                batch_races = race_table.get('Races', [])
                
                # Add races, deduplicating if necessary (same race can appear in multiple batches)
                for race in batch_races:
                    race_key = (race['season'], race['round'])
                    # Check if we already have this race
                    if not any(r['season'] == race['season'] and r['round'] == race['round'] for r in year_races):
                        year_races.append(race)
                
                # Count how many individual results we've fetched so far
                fetched_results = sum(len(r.get('Results', [])) for r in year_races)
                
                # Stop if no more races or we've fetched all expected results
                if not batch_races or fetched_results >= year_total_expected:
                    break
                
                offset += limit
            
            all_races.extend(year_races)
            total_results = sum(len(race.get('Results', [])) for race in year_races)
            print(f"📡 [{year_idx}/{total_years}] {year}: {len(year_races)} races, {total_results} driver results ✓")
        
        # Build final unified data structure
        total_individual_results = sum(len(race.get('Results', [])) for race in all_races)
        
        final_data = {
            "MRData": {
                **mrdata_template,
                "limit": str(len(all_races)),
                "offset": "0",
                "total": str(total_individual_results),  # Total individual driver results
                "RaceTable": {
                    "Races": all_races
                }
            }
        }
        
        # Save to file
        output_file = output_dir / "all_results.json"
        print(f"\n💾 Saving complete dataset...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        file_size_mb = output_file.stat().st_size / (1024*1024)
        print(f"\n✅ Successfully saved complete F1 historical dataset!")
        print(f"📊 Total races: {len(all_races)}")
        print(f"📊 Total individual driver results: {total_individual_results}")
        print(f"📊 Year range: {start_year}-{end_year} ({total_years} seasons)")
        print(f"📊 File: {output_file}")
        print(f"📊 File size: {file_size_mb:.2f} MB")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching data: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"\n❌ Error parsing JSON: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    fetch_all_results()