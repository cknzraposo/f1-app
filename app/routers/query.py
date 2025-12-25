"""
Unified natural language query endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import logging

from ..query_parser import QueryParser

# Import other routers to access their endpoint functions
from .drivers import get_driver_stats, search_drivers
from .seasons import get_season_standings, get_season_winners
from .constructors import get_constructor_stats
from .analytics import get_head_to_head

# Configure logging
logger = logging.getLogger(__name__)

# Initialize QueryParser
query_parser = QueryParser()

router = APIRouter(prefix="/api", tags=["Query"])


# Pydantic model for request
class QueryRequest(BaseModel):
    query: str


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
            raise HTTPException(
                status_code=400, 
                detail="Could not understand query. Try being more specific (e.g., 'hamilton stats', '2023 championship')"
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
            # Driver stats - use existing endpoint
            parts = endpoint.split('/')
            driver_id = parts[parts.index('drivers') + 1]
            
            start_year = params.get('start_year')
            end_year = params.get('end_year')
            
            data = get_driver_stats(driver_id, start_year, end_year)
            
        elif '/stats' in endpoint and '/constructors/' in endpoint:
            # Constructor stats - use existing endpoint
            parts = endpoint.split('/')
            constructor_id = parts[parts.index('constructors') + 1]
            
            start_year = params.get('start_year')
            end_year = params.get('end_year')
            
            data = get_constructor_stats(constructor_id, start_year, end_year)
            
        elif 'head-to-head' in endpoint:
            # Head to head comparison - use existing endpoint
            driver1 = params.get('driver1')
            driver2 = params.get('driver2')
            
            if not driver1 or not driver2:
                raise HTTPException(status_code=400, detail="Both drivers required for comparison")
            
            data = get_head_to_head(driver1, driver2)
            
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
