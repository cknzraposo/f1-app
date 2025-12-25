# F1 Data API - Refactoring Guide

## Overview

The F1 Data API has been refactored from a monolithic architecture to a modular router-based structure. This document describes the changes, benefits, and how to work with the new architecture.

## What Changed

### Before Refactoring

The application used a single monolithic file:

```
app/
└── api_server.py (1,064 lines)
    ├── All imports
    ├── App initialization
    ├── Query endpoint (POST /api/query)
    ├── Driver endpoints (5 endpoints)
    ├── Season endpoints (5 endpoints)
    ├── Constructor endpoints (4 endpoints)
    ├── Analytics endpoints (2 endpoints)
    └── Info endpoints (3 endpoints)
```

### After Refactoring

The application now uses a clean router-based architecture:

```
app/
├── api_server.py (107 lines) - Main application with router mounting
└── routers/
    ├── __init__.py (10 lines) - Module documentation
    ├── query.py (161 lines) - Unified natural language query endpoint
    ├── drivers.py (255 lines) - All driver-related endpoints
    ├── seasons.py (203 lines) - All season-related endpoints
    ├── constructors.py (209 lines) - All constructor-related endpoints
    └── analytics.py (169 lines) - Statistical analysis endpoints
```

## File Structure Details

### Main Application (`app/api_server.py`)

**Lines: 107 (90% reduction from original 1,064 lines)**

**Responsibilities:**
- FastAPI app initialization
- CORS middleware configuration
- Static file mounting
- Router registration
- Root, health check, and API info endpoints

**Key Code:**
```python
from .routers import query, drivers, seasons, constructors, analytics

app = FastAPI(...)

# Include routers
app.include_router(query.router)
app.include_router(drivers.router)
app.include_router(seasons.router)
app.include_router(constructors.router)
app.include_router(analytics.router)
```

### Query Router (`app/routers/query.py`)

**Lines: 161**

**Endpoints:**
- `POST /api/query` - Unified natural language query endpoint

**Key Features:**
- Imports QueryParser for natural language processing
- Routes queries to appropriate domain endpoints
- Infers data types from endpoint patterns
- Comprehensive logging for debugging

**Dependencies:**
- Imports endpoint functions from other routers
- Uses drivers.py, seasons.py, constructors.py, analytics.py

### Drivers Router (`app/routers/drivers.py`)

**Lines: 255**

**Endpoints:**
- `GET /api/drivers` - List all drivers
- `GET /api/drivers/search` - Search drivers by name/nationality
- `GET /api/drivers/{driver_id}` - Get specific driver
- `GET /api/drivers/{driver_id}/seasons/{year}` - Driver results for a season
- `GET /api/drivers/{driver_id}/stats` - Calculate driver career statistics

**Key Features:**
- Complete driver information retrieval
- Statistical calculations (wins, podiums, points, etc.)
- Season-by-season breakdowns
- Team history tracking

### Seasons Router (`app/routers/seasons.py`)

**Lines: 203**

**Endpoints:**
- `GET /api/seasons` - List available seasons
- `GET /api/seasons/{year}` - Get all race data for a season
- `GET /api/seasons/{year}/races/{round}` - Get specific race results
- `GET /api/seasons/{year}/standings` - Calculate championship standings
- `GET /api/seasons/{year}/winners` - List race winners for a season

**Key Features:**
- Championship calculations (driver & constructor)
- Race-by-race results
- Points aggregation
- Winner listings

### Constructors Router (`app/routers/constructors.py`)

**Lines: 209**

**Endpoints:**
- `GET /api/constructors` - List all constructors
- `GET /api/constructors/{constructor_id}` - Get specific constructor
- `GET /api/constructors/{constructor_id}/seasons/{year}` - Constructor results for a season
- `GET /api/constructors/{constructor_id}/stats` - Calculate constructor career statistics

**Key Features:**
- Team information retrieval
- Statistical calculations
- Driver lineup tracking
- Historical performance data

### Analytics Router (`app/routers/analytics.py`)

**Lines: 169**

**Endpoints:**
- `GET /api/stats/head-to-head` - Compare two drivers head-to-head
- `GET /api/stats/fastest-laps/{year}` - Get fastest laps for a season

**Key Features:**
- Driver comparisons with race-by-race analysis
- Fastest lap tracking and rankings
- Average speed calculations
- Win/loss records in direct competition

## Benefits of the Refactoring

### 1. Code Organization

**Before:** Finding a specific endpoint required searching through 1,064 lines.

**After:** Each domain has its own file - drivers in `drivers.py`, seasons in `seasons.py`, etc.

### 2. Maintainability

**Before:** Changes to one endpoint could inadvertently affect others in the same file.

**After:** Each router is isolated. Changes to driver endpoints don't risk breaking season endpoints.

### 3. Team Collaboration

**Before:** Multiple developers editing the same large file led to merge conflicts.

**After:** Developers can work on different routers simultaneously without conflicts.

### 4. Testing

**Before:** Testing required importing the entire application.

**After:** Individual routers can be tested in isolation.

```python
# Example: Test just the drivers router
from app.routers.drivers import router, get_driver_stats

# Test the function directly
stats = get_driver_stats("max_verstappen", 2020, 2023)
```

### 5. Scalability

**Before:** Adding new endpoints made the file longer and harder to navigate.

**After:** New domains get their own router file. For example, adding telemetry data:

```python
# Create app/routers/telemetry.py
router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

# In api_server.py, just add one line:
from .routers import telemetry
app.include_router(telemetry.router)
```

### 6. Industry Standard

This refactoring follows FastAPI's official best practices for larger applications:
- https://fastapi.tiangolo.com/tutorial/bigger-applications/

## How to Work with the New Structure

### Adding a New Endpoint

#### 1. Determine Which Router

- Driver-related? → `drivers.py`
- Season-related? → `seasons.py`
- Constructor-related? → `constructors.py`
- Statistical analysis? → `analytics.py`
- Natural language query? → `query.py`
- New domain? → Create new router file

#### 2. Add the Endpoint Function

```python
# In app/routers/drivers.py

@router.get("/{driver_id}/achievements")
def get_driver_achievements(driver_id: str) -> Dict[str, Any]:
    """
    Get notable achievements for a driver.
    
    Args:
        driver_id: The driver's unique identifier
    """
    # Implementation here
    return {"achievements": [...]}
```

#### 3. No Changes Needed to Main File

The router is already included in `api_server.py`. Your new endpoint is automatically available!

### Creating a New Router

For completely new functionality (e.g., circuits, penalties, weather data):

#### 1. Create Router File

```python
# app/routers/circuits.py
"""
Circuit-related API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ..json_loader import load_circuits  # If you have circuit data

router = APIRouter(prefix="/api/circuits", tags=["Circuits"])

@router.get("")
def get_all_circuits() -> Dict[str, Any]:
    """Get all F1 circuits."""
    return load_circuits()

@router.get("/{circuit_id}")
def get_circuit(circuit_id: str) -> Dict[str, Any]:
    """Get specific circuit by ID."""
    # Implementation
    pass
```

#### 2. Register in Main File

```python
# In app/api_server.py

# Import the new router
from .routers import query, drivers, seasons, constructors, analytics, circuits

# Include it
app.include_router(circuits.router)
```

Done! Your new domain is now fully integrated.

### Modifying Existing Endpoints

#### Example: Add Pagination to Driver Search

```python
# In app/routers/drivers.py

@router.get("/search")
def search_drivers(
    name: Optional[str] = Query(None, description="Search by driver name"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page")
) -> Dict[str, Any]:
    """Search for drivers by name or nationality with pagination."""
    
    drivers_data = load_drivers()
    drivers_list = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
    
    # Apply filters
    filtered_drivers = drivers_list
    if name:
        name_lower = name.lower()
        filtered_drivers = [
            d for d in filtered_drivers
            if name_lower in d.get("givenName", "").lower() or
               name_lower in d.get("familyName", "").lower()
        ]
    
    if nationality:
        filtered_drivers = [
            d for d in filtered_drivers
            if d.get("nationality", "").lower() == nationality.lower()
        ]
    
    # Apply pagination
    total = len(filtered_drivers)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered_drivers[start:end]
    
    return {
        "MRData": {
            "DriverTable": {
                "Drivers": paginated
            }
        },
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    }
```

Only one file needs to be modified. No risk to other endpoints.

## Router Architecture Patterns

### Import Structure

Each router follows this pattern:

```python
"""
Router description
"""
# FastAPI imports
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, Optional

# Local imports (relative to app/)
from ..json_loader import load_drivers, load_season_results
from ..query_parser import QueryParser

# Create router with prefix and tags
router = APIRouter(prefix="/api/domain", tags=["Domain"])

# Define endpoints
@router.get("/")
def endpoint_function():
    pass
```

### Cross-Router Dependencies

When one router needs functions from another:

```python
# In app/routers/analytics.py

def get_head_to_head(driver1: str, driver2: str):
    # Import at function level to avoid circular imports
    from .drivers import get_driver_stats
    
    driver1_stats = get_driver_stats(driver1)
    driver2_stats = get_driver_stats(driver2)
    # Compare...
```

### Shared Logic

For logic used across multiple routers, keep it in the module files:

- `json_loader.py` - Data loading and caching
- `query_parser.py` - Natural language processing
- New modules as needed (e.g., `calculators.py` for shared statistics)

## Migration Notes

### No Breaking Changes

**All existing endpoints work exactly as before:**

- `GET /api/drivers` → Still works, now handled by `drivers.router`
- `POST /api/query` → Still works, now handled by `query.router`
- `GET /api/seasons/{year}/standings` → Still works, now handled by `seasons.router`

### URL Paths Unchanged

Router prefixes match original paths:

```python
# drivers.py
router = APIRouter(prefix="/api/drivers", tags=["Drivers"])

# This creates:
# GET /api/drivers
# GET /api/drivers/{driver_id}
# etc.
```

### Swagger Documentation

The `/docs` endpoint automatically reflects all routers. Endpoints are organized by tags:

- **Query** - Natural language query endpoint
- **Drivers** - Driver endpoints
- **Seasons** - Season endpoints  
- **Constructors** - Constructor endpoints
- **Analytics** - Statistical endpoints
- **Info** - Health check and API info

## Testing

### Unit Testing Individual Routers

```python
# test_drivers.py
from fastapi.testclient import TestClient
from app.routers.drivers import router

client = TestClient(router)

def test_get_all_drivers():
    response = client.get("/")  # Relative to router prefix
    assert response.status_code == 200
    assert "MRData" in response.json()

def test_driver_stats():
    response = client.get("/verstappen/stats")
    assert response.status_code == 200
    data = response.json()
    assert "statistics" in data
```

### Integration Testing

```python
# test_integration.py
from fastapi.testclient import TestClient
from app.api_server import app

client = TestClient(app)

def test_full_query_flow():
    # Test the complete flow through query router
    response = client.post(
        "/api/query",
        json={"query": "Who won 2023 championship?"}
    )
    assert response.status_code == 200
    assert response.json()["dataType"] == "championship_standings"
```

## Performance Impact

### Startup Time

**Before:** 
- Single file import: Fast

**After:**
- Multiple imports: Still fast (Python imports are cached)
- No measurable difference in production

### Runtime Performance

**Identical.** Routers use the same underlying functions and data loaders. Request handling is identical.

### Memory Usage

**Identical.** All routers are loaded at startup (via `include_router`). No lazy loading of routers.

## Best Practices

### 1. Keep Routers Focused

Each router should handle one domain:
- ✅ `drivers.py` handles all driver operations
- ❌ Don't put season standings in `drivers.py`

### 2. Use Consistent Patterns

All routers follow the same structure:
- Module docstring
- Imports
- Router creation with prefix and tags
- Endpoint definitions

### 3. Document Endpoints

Every endpoint should have:
```python
@router.get("/endpoint")
def endpoint_function(param: str) -> Dict[str, Any]:
    """
    Brief description of what the endpoint does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
```

### 4. Handle Errors Consistently

Use FastAPI's HTTPException:
```python
if not found:
    raise HTTPException(
        status_code=404,
        detail=f"Resource '{id}' not found"
    )
```

### 5. Leverage Type Hints

FastAPI uses type hints for validation and documentation:
```python
def get_stats(
    driver_id: str,
    start_year: Optional[int] = Query(None, ge=1950, le=2025),
    end_year: Optional[int] = Query(None, ge=1950, le=2025)
) -> Dict[str, Any]:
```

## Summary

The refactoring achieved:

✅ **90% reduction** in main file size (1,064 → 107 lines)  
✅ **Better organization** - Each domain in its own file  
✅ **Easier maintenance** - Isolated changes  
✅ **Better collaboration** - No merge conflicts  
✅ **Improved testing** - Test routers independently  
✅ **Zero breaking changes** - All endpoints work as before  
✅ **Industry standard** - Follows FastAPI best practices  

The application is now well-positioned for future growth and team development while maintaining the same performance and functionality.

## References

- [FastAPI Bigger Applications Tutorial](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI APIRouter Documentation](https://fastapi.tiangolo.com/reference/apirouter/)
- Original project structure: See `keyword-first-architecture.md`
