"""
JSON file loading utilities with caching for efficient data access.
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its contents.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_drivers() -> Dict[str, Any]:
    """
    Load drivers data with caching (cached permanently).
    
    Returns:
        Dictionary containing all driver data
    """
    filepath = Path(__file__).parent.parent / "f1drivers" / "drivers.json"
    return load_json_file(str(filepath))


@lru_cache(maxsize=1)
def load_constructors() -> Dict[str, Any]:
    """
    Load constructors data with caching (cached permanently).
    
    Returns:
        Dictionary containing all constructor data
    """
    filepath = Path(__file__).parent.parent / "f1constructors" / "constructors.json"
    return load_json_file(str(filepath))


@lru_cache(maxsize=5)
def load_season_results(year: int) -> Dict[str, Any]:
    """
    Load season results with LRU caching (keeps last 5 seasons in memory).
    
    Args:
        year: Season year (e.g., 2024)
        
    Returns:
        Dictionary containing all race results for the season
        
    Raises:
        FileNotFoundError: If the season data doesn't exist
    """
    filepath = Path(__file__).parent.parent / "f1data" / f"{year}_results.json"
    return load_json_file(str(filepath))


def get_available_seasons() -> list[int]:
    """
    Get list of available season years from the f1data directory.
    
    Returns:
        List of years (as integers) for which data is available
    """
    data_dir = Path(__file__).parent.parent / "f1data"
    season_files = data_dir.glob("*_results.json")
    years = []
    
    for file in season_files:
        try:
            year = int(file.stem.split('_')[0])
            years.append(year)
        except ValueError:
            continue
    
    return sorted(years)
