"""
Unified natural language query endpoint

Thin HTTP handler that uses QueryParser and delegates to service layer.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
import logging
import difflib

from ..query_parser import QueryParser
from ..services import F1Service
from .seasons import get_season_standings, get_season_winners
from .drivers import search_drivers
from ..json_loader import load_drivers, load_constructors

# Configure logging
logger = logging.getLogger(__name__)

# Initialize QueryParser
query_parser = QueryParser()

router = APIRouter(prefix="/api", tags=["Query"])


# Pydantic model for request
class QueryRequest(BaseModel):
    query: str


def get_driver_suggestions(query_text: str) -> List[str]:
    """
    Get driver name suggestions based on fuzzy matching.
    
    Args:
        query_text: The original query text
        
    Returns:
        List of suggested driver names (max 3)
    """
    try:
        # Extract potential driver names from query
        words = query_text.lower().split()
        drivers_data = load_drivers()
        
        # Get all driver surnames
        all_surnames = []
        for driver in drivers_data.get('MRData', {}).get('DriverTable', {}).get('Drivers', []):
            surname = driver.get('familyName', '').lower()
            if surname:
                all_surnames.append(surname)
        
        # Find close matches for each word in query
        suggestions = []
        for word in words:
            if len(word) >= 3:  # Only match words 3+ chars
                matches = difflib.get_close_matches(word, all_surnames, n=3, cutoff=0.6)
                suggestions.extend(matches)
        
        # Remove duplicates, limit to 3
        return list(dict.fromkeys(suggestions))[:3]
        
    except Exception as e:
        logger.error(f"Error getting driver suggestions: {e}")
        return []


def get_query_suggestions(query_text: str) -> List[str]:
    """
    Get example query suggestions based on the failed query.
    
    Args:
        query_text: The original query text
        
    Returns:
        List of suggested queries (max 5)
    """
    suggestions = []
    query_lower = query_text.lower()
    
    # Detect what user might be asking for
    if 'win' in query_lower or 'victory' in query_lower or 'champion' in query_lower:
        suggestions.extend([
            "Who won the 2023 championship?",
            "How many wins does Hamilton have?",
            "2023 season winners"
        ])
    
    if 'stat' in query_lower or 'record' in query_lower or 'how many' in query_lower:
        suggestions.extend([
            "Hamilton stats",
            "Verstappen career statistics",
            "Red Bull stats 2020-2023"
        ])
    
    if 'compare' in query_lower or 'vs' in query_lower or 'versus' in query_lower:
        suggestions.extend([
            "Compare Hamilton vs Verstappen",
            "Vettel vs Alonso head to head"
        ])
    
    if 'stand' in query_lower:
        suggestions.extend([
            "2023 standings",
            "2022 championship standings"
        ])
    
    # Default suggestions if none matched
    if not suggestions:
        suggestions = [
            "Who won the 2023 championship?",
            "Hamilton career stats",
            "2023 standings",
            "Compare Hamilton vs Verstappen",
            "Red Bull statistics"
        ]
    
    # Remove duplicates, limit to 5
    return list(dict.fromkeys(suggestions))[:5]


@router.post("/query")
async def unified_query(request: QueryRequest) -> Dict[str, Any]:
    """
    Unified natural language query endpoint.
    
    Accepts natural language queries and routes them to appropriate backend endpoints.
    Uses QueryParser for keyword-based routing (no LLM required).
    
    Args:
        request: QueryRequest with 'query' field containing natural language text
        
    Returns:
        Standardized response with success status, data, dataType, and original query
        
    Example queries:
        - "Who won the 2023 championship?"
        - "How many wins does Hamilton have?"
        - "Compare Vettel vs Alonso"
        - "2022 standings"
    """
    try:
        query_text = request.query.strip()
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Parse the query using QueryParser
        parsed = query_parser.parse(query_text)
        
        if not parsed:
            # Get helpful suggestions
            driver_suggestions = get_driver_suggestions(query_text)
            query_suggestions = get_query_suggestions(query_text)
            
            error_msg = "Could not understand query."
            
            if driver_suggestions:
                error_msg += f" Did you mean: {', '.join(driver_suggestions)}?"
            
            error_msg += " Try queries like: " + " | ".join(query_suggestions)
            
            raise HTTPException(
                status_code=400, 
                detail=error_msg
            )
        
        # Route to appropriate endpoint based on action
        endpoint = parsed.get('endpoint', '')
        params = parsed.get('params', {})
        action = parsed.get('action', '')
        
        logger.info(f"Query parsed - Action: {action}, Endpoint: {parsed.get('endpoint')}, Params: {params}")
        
        # Infer data type from endpoint pattern since QueryParser returns generic "api_call"
        data_type = 'unknown'
        if '/standings' in endpoint:
            data_type = 'championship_standings'
        elif '/stats' in endpoint and '/drivers/' in endpoint:
            data_type = 'driver_stats'
        elif '/stats' in endpoint and '/constructors/' in endpoint:
            data_type = 'constructor_stats'
        elif 'head-to-head' in endpoint:
            data_type = 'head_to_head'
        elif '/winners' in endpoint:
            data_type = 'season_winners'
        elif '/search' in endpoint:
            data_type = 'driver_search'
        
        logger.info(f"Inferred dataType from endpoint: {data_type}")
        
        # Fetch data from internal endpoints
        data = None
        
        if 'standings' in endpoint:
            # Get standings - use existing endpoint
            year = endpoint.split('/')[-2]
            data = get_season_standings(int(year))
            
        elif '/stats' in endpoint and '/drivers/' in endpoint:
            # Driver stats - use service layer
            parts = endpoint.split('/')
            driver_id = parts[parts.index('drivers') + 1]
            
            start_year = params.get('start_year')
            end_year = params.get('end_year')
            
            try:
                data = F1Service.get_driver_statistics(driver_id, start_year, end_year)
            except ValueError as e:
                # Driver not found - provide suggestions
                driver_suggestions = get_driver_suggestions(driver_id)
                error_msg = f"Driver '{driver_id}' not found."
                if driver_suggestions:
                    error_msg += f" Did you mean: {', '.join(driver_suggestions)}?"
                raise HTTPException(status_code=404, detail=error_msg)
            
        elif '/stats' in endpoint and '/constructors/' in endpoint:
            # Constructor stats - use service layer
            parts = endpoint.split('/')
            constructor_id = parts[parts.index('constructors') + 1]
            
            start_year = params.get('start_year')
            end_year = params.get('end_year')
            
            try:
                data = F1Service.get_constructor_statistics(constructor_id, start_year, end_year)
            except ValueError as e:
                # Constructor not found - provide suggestions
                try:
                    constructors_data = load_constructors()
                    all_constructors = [
                        c.get('name', '').lower() 
                        for c in constructors_data.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', [])
                    ]
                    suggestions = difflib.get_close_matches(constructor_id.lower(), all_constructors, n=3, cutoff=0.6)
                    
                    error_msg = f"Constructor '{constructor_id}' not found."
                    if suggestions:
                        error_msg += f" Did you mean: {', '.join(suggestions)}?"
                    raise HTTPException(status_code=404, detail=error_msg)
                except:
                    raise HTTPException(status_code=404, detail=str(e))
            
        elif 'head-to-head' in endpoint:
            # Head to head comparison - use service layer
            driver1 = params.get('driver1')
            driver2 = params.get('driver2')
            
            if not driver1 or not driver2:
                raise HTTPException(status_code=400, detail="Both drivers required for comparison")
            
            try:
                data = F1Service.get_head_to_head_comparison(driver1, driver2)
            except ValueError as e:
                # Driver not found in comparison - provide suggestions
                error_str = str(e)
                driver_suggestions = []
                
                # Try to extract which driver wasn't found
                if driver1 and driver1 in error_str:
                    driver_suggestions = get_driver_suggestions(driver1)
                elif driver2 and driver2 in error_str:
                    driver_suggestions = get_driver_suggestions(driver2)
                
                error_msg = str(e)
                if driver_suggestions:
                    error_msg += f" Did you mean: {', '.join(driver_suggestions)}?"
                
                raise HTTPException(status_code=404, detail=error_msg)
            
        elif 'winners' in endpoint:
            # Season winners - use existing endpoint
            parts = endpoint.split('/')
            year = parts[parts.index('seasons') + 1]
            data = get_season_winners(int(year))
            
        elif 'search' in endpoint:
            # Driver search - use existing endpoint
            name = params.get('name', '')
            data = search_drivers(name=name)
        
        else:
            logger.warning(f"Unsupported endpoint: {endpoint} for action: {action}")
            raise HTTPException(status_code=400, detail=f"Unsupported query type: {action}")
        
        if data is None:
            logger.error(f"No data returned for endpoint: {endpoint}")
            raise HTTPException(status_code=500, detail="Failed to fetch data from backend")
        
        logger.info(f"Successfully fetched data, type: {data_type}")
        
        return {
            "success": True,
            "data": data,
            "dataType": data_type,
            "query": query_text,
            "action": action  # Include for debugging
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
