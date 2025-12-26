"""
Input validation helpers for F1 API endpoints.

Provides validation functions for:
- Year ranges (1984-2024)
- Driver IDs
- Constructor IDs
"""

from typing import Optional, List
from difflib import get_close_matches


# Valid year range for F1 data
MIN_YEAR = 1984
MAX_YEAR = 2024


def validate_year(year: int, raise_on_invalid: bool = True) -> bool:
    """
    Validate that a year is within the valid F1 data range (1984-2024).
    
    Args:
        year: Year to validate
        raise_on_invalid: If True, raises ValueError on invalid year
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If year is outside valid range and raise_on_invalid=True
    """
    is_valid = MIN_YEAR <= year <= MAX_YEAR
    
    if not is_valid and raise_on_invalid:
        raise ValueError(
            f"Year {year} is outside the valid range {MIN_YEAR}-{MAX_YEAR}. "
            f"F1 data is available for seasons {MIN_YEAR} through {MAX_YEAR}."
        )
    
    return is_valid


def validate_driver_id(
    driver_id: str,
    available_drivers: Optional[List[str]] = None,
    raise_on_invalid: bool = True,
    suggest_matches: bool = True
) -> Optional[List[str]]:
    """
    Validate a driver ID and optionally suggest close matches.
    
    Args:
        driver_id: Driver ID to validate
        available_drivers: List of valid driver IDs (if None, no validation performed)
        raise_on_invalid: If True, raises ValueError on invalid driver ID
        suggest_matches: If True, suggests similar driver IDs using fuzzy matching
        
    Returns:
        None if valid or validation skipped, list of suggestions if invalid and suggest_matches=True
        
    Raises:
        ValueError: If driver_id is invalid and raise_on_invalid=True
    """
    if available_drivers is None:
        return None
    
    if driver_id in available_drivers:
        return None
    
    # Driver not found - generate suggestions if requested
    suggestions = []
    if suggest_matches:
        suggestions = get_close_matches(driver_id, available_drivers, n=5, cutoff=0.6)
    
    if raise_on_invalid:
        error_msg = f"Driver '{driver_id}' not found."
        if suggestions:
            error_msg += f" Did you mean: {', '.join(suggestions)}?"
        raise ValueError(error_msg)
    
    return suggestions


def validate_constructor_id(
    constructor_id: str,
    available_constructors: Optional[List[str]] = None,
    raise_on_invalid: bool = True,
    suggest_matches: bool = True
) -> Optional[List[str]]:
    """
    Validate a constructor ID and optionally suggest close matches.
    
    Args:
        constructor_id: Constructor ID to validate
        available_constructors: List of valid constructor IDs (if None, no validation performed)
        raise_on_invalid: If True, raises ValueError on invalid constructor ID
        suggest_matches: If True, suggests similar constructor IDs using fuzzy matching
        
    Returns:
        None if valid or validation skipped, list of suggestions if invalid and suggest_matches=True
        
    Raises:
        ValueError: If constructor_id is invalid and raise_on_invalid=True
    """
    if available_constructors is None:
        return None
    
    if constructor_id in available_constructors:
        return None
    
    # Constructor not found - generate suggestions if requested
    suggestions = []
    if suggest_matches:
        suggestions = get_close_matches(constructor_id, available_constructors, n=5, cutoff=0.6)
    
    if raise_on_invalid:
        error_msg = f"Constructor '{constructor_id}' not found."
        if suggestions:
            error_msg += f" Did you mean: {', '.join(suggestions)}?"
        raise ValueError(error_msg)
    
    return suggestions


def get_year_range_message() -> str:
    """Get a user-friendly message about the valid year range."""
    return f"Valid years: {MIN_YEAR}-{MAX_YEAR}"


def get_available_driver_ids(drivers_data: dict) -> List[str]:
    """
    Extract list of driver IDs from drivers data.
    
    Args:
        drivers_data: Dictionary containing driver data from JSON
        
    Returns:
        List of driver IDs
    """
    try:
        drivers_table = drivers_data.get("MRData", {}).get("DriverTable", {})
        drivers = drivers_table.get("Drivers", [])
        return [driver.get("driverId") for driver in drivers if "driverId" in driver]
    except (AttributeError, TypeError):
        return []


def get_available_constructor_ids(constructors_data: dict) -> List[str]:
    """
    Extract list of constructor IDs from constructors data.
    
    Args:
        constructors_data: Dictionary containing constructor data from JSON
        
    Returns:
        List of constructor IDs
    """
    try:
        constructors_table = constructors_data.get("MRData", {}).get("ConstructorTable", {})
        constructors = constructors_table.get("Constructors", [])
        return [c.get("constructorId") for c in constructors if "constructorId" in c]
    except (AttributeError, TypeError):
        return []
