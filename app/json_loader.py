"""
JSON file loading utilities with caching for efficient data access.

Performance Metrics:
- Driver/Constructor cache: @lru_cache(maxsize=1) - permanent cache (historical data immutable)
- Season cache: @lru_cache(maxsize=5) - LRU eviction keeps 5 most recent seasons
- Cache hit: ~0.001ms, Cache miss: ~10-50ms (file I/O)
"""
import json
import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


# Configure logging
logger = logging.getLogger(__name__)


def load_json_file(filepath: str, operation_name: str = "load_json") -> Dict[str, Any]:
    """
    Load a JSON file and return its contents with performance logging.
    
    Args:
        filepath: Path to the JSON file
        operation_name: Name of operation for logging purposes
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    start_time = time.perf_counter()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"{operation_name}: Loaded {filepath} in {elapsed_ms:.2f}ms")
        
        return data
    except FileNotFoundError:
        logger.error(f"{operation_name}: File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"{operation_name}: Invalid JSON in {filepath}: {e}")
        raise


@lru_cache(maxsize=1)
def load_drivers() -> Dict[str, Any]:
    """
    Load drivers data with caching (cached permanently).
    
    Performance: First call ~10-30ms (file I/O), subsequent calls ~0.001ms (cache hit)
    Cache eviction: Never (maxsize=1 means only one instance, never evicted)
    
    Returns:
        Dictionary containing all driver data
    """
    filepath = Path(__file__).parent.parent / "f1drivers" / "drivers.json"
    logger.info(f"load_drivers: Cache miss, loading from disk")
    return load_json_file(str(filepath), "load_drivers")


@lru_cache(maxsize=1)
def load_constructors() -> Dict[str, Any]:
    """
    Load constructors data with caching (cached permanently).
    
    Performance: First call ~10-30ms (file I/O), subsequent calls ~0.001ms (cache hit)
    Cache eviction: Never (maxsize=1 means only one instance, never evicted)
    
    Returns:
        Dictionary containing all constructor data
    """
    filepath = Path(__file__).parent.parent / "f1constructors" / "constructors.json"
    logger.info(f"load_constructors: Cache miss, loading from disk")
    return load_json_file(str(filepath), "load_constructors")


@lru_cache(maxsize=5)
def load_season_results(year: int) -> Dict[str, Any]:
    """
    Load season results with LRU caching (keeps last 5 seasons in memory).
    
    Performance: 
    - Cache hit: ~0.001ms
    - Cache miss: ~10-50ms (file I/O)
    Cache eviction: LRU - when 6th unique season requested, least recently used is evicted
    
    Args:
        year: Season year (e.g., 2024)
        
    Returns:
        Dictionary containing all race results for the season
        
    Raises:
        FileNotFoundError: If the season data doesn't exist
    """
    filepath = Path(__file__).parent.parent / "f1data" / f"{year}_results.json"
    logger.info(f"load_season_results: Cache miss for year {year}, loading from disk")
    logger.debug(f"load_season_results: Current cache info: {load_season_results.cache_info()}")
    return load_json_file(str(filepath), f"load_season_results[{year}]")


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
