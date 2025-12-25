"""
F1 Data API Server
A lightweight REST API for querying Formula 1 historical data.

Refactored with router-based architecture for better organization.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Any, Dict
from pathlib import Path
import logging

# Import routers
from .routers import query, drivers, seasons, constructors, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="F1 Data API",
    description="REST API for querying Formula 1 historical data (1984-2024)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(query.router)
app.include_router(drivers.router)
app.include_router(seasons.router)
app.include_router(constructors.router)
app.include_router(analytics.router)

# ============================================================================
# ROOT AND INFO ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
def root():
    """
    Serve the web UI for querying F1 stats.
    """
    static_dir = Path(__file__).parent.parent / "static"
    index_path = static_dir / "index.html"
    
    if index_path.exists():
        return FileResponse(index_path)
    
    # Fallback to API info if no UI is available
    return {
        "name": "F1 Data API",
        "version": "1.0.0",
        "description": "REST API for querying Formula 1 historical data (1984-2024)",
        "documentation": "/docs",
        "endpoints": {
            "drivers": "/api/drivers",
            "constructors": "/api/constructors",
            "seasons": "/api/seasons",
            "stats": "/api/stats",
            "query": "/api/query"
        }
    }


@app.get("/api", tags=["Info"])
def api_info() -> Dict[str, Any]:
    """
    API information endpoint.
    """
    return {
        "name": "F1 Data API",
        "version": "1.0.0",
        "description": "REST API for querying Formula 1 historical data (1984-2024)",
        "documentation": "/docs",
        "endpoints": {
            "drivers": "/api/drivers",
            "constructors": "/api/constructors",
            "seasons": "/api/seasons",
            "stats": "/api/stats",
            "query": "/api/query"
        }
    }


@app.get("/health", tags=["Info"])
def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

