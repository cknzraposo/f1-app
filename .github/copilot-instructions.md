# F1 AI Assistant - Copilot Agent Instructions

## Application Overview

This is a **FastAPI-based REST API** with a web interface for querying Formula 1 historical data (1984-2024). The app uses a **keyword-first, LLM-optional** architecture for maximum speed and reliability.

---

## Core Design Principles

1. **Zero Database Dependency**: All data stored in JSON files (`f1data/`, `f1drivers/`, `f1constructors/`)
2. **LRU Caching**: Efficient in-memory caching via `@lru_cache` decorators in `app/json_loader.py`
3. **Keyword-First Processing**: 90%+ of queries handled by pattern matching without LLM
4. **Progressive Enhancement**: LLM is optional fallback, app fully functional without it
5. **Original Data Format**: API returns unmodified Ergast API JSON structure

---

## Key Components & Responsibilities

### 1. Data Layer (`app/json_loader.py`)
- **Purpose**: Load and cache JSON data files
- **Functions**:
  - `load_drivers()` - Single cached instance of all drivers
  - `load_constructors()` - Single cached instance of all constructors  
  - `load_season_results(year)` - LRU cache for last 5 seasons
  - `get_available_seasons()` - Scan f1data directory for available years
- **When to modify**: Adding new data sources or changing caching strategy

### 2. REST API Layer (`app/api_server.py`)
- **Purpose**: FastAPI server with comprehensive F1 data endpoints
- **Endpoint Categories**:
  - **Drivers**: `/api/drivers`, `/api/drivers/{driver_id}`, `/api/drivers/{driver_id}/stats`
  - **Seasons**: `/api/seasons/{year}`, `/api/seasons/{year}/standings`, `/api/seasons/{year}/winners`
  - **Constructors**: `/api/constructors/{constructor_id}`, `/api/constructors/{constructor_id}/stats`
  - **Analytics**: `/api/stats/head-to-head`, `/api/stats/fastest-laps/{year}`
- **When to modify**: Adding new endpoints or analytics features

### 3. Query Parser (`app/query_parser.py`) - **PRIMARY QUERY HANDLER**
- **Purpose**: Pattern-based natural language understanding
- **Architecture**:
  - Loads driver database on initialization for name matching
  - Uses regex patterns for years (1984-2024)
  - Keyword matching for query types (championship, stats, standings, etc.)
  - Fuzzy matching with `difflib.get_close_matches` for driver names
- **Supported Patterns**:
  - Championship queries: "who won 2010 championship"
  - Driver stats: "how many wins hamilton"
  - Team info: "about red bull"
  - Standings: "2023 standings"
  - Comparisons: "compare vettel verstappen"
  - Race winners: "most races 2023"
- **When to modify**: Adding new query patterns or improving entity extraction

### 4. LLM Service (`app/llm_service.py`) - **FALLBACK ONLY**
- **Purpose**: Handle complex queries that keyword parser cannot match
- **Strategy**: Ollama (local) → Azure OpenAI (cloud) fallback chain
- **Configuration**: Controlled by `config.json` and `app/config.py`
- **When to modify**: Adding new LLM providers or changing prompt engineering

### 5. Configuration (`config.json`, `app/config.py`)
- **Purpose**: Centralized LLM and app settings
- **Features**:
  - Environment variable overrides for secrets (`AZURE_OPENAI_API_KEY`)
  - Graceful degradation if config missing
  - Primary LLM selection (Ollama or Azure)
- **When to modify**: Adding new configuration options or providers

### 6. Web Interface (`static/index.html`, `static/app.js`)
- **Purpose**: User-facing chat interface
- **Tech Stack**: Vanilla HTML/JS + Tailwind CSS (no build process)
- **Features**:
  - Form-based query interface for structured queries
  - Real-time data visualization (standings tables, driver cards)
  - Status indicators showing which processing tier handled query
- **When to modify**: UI/UX improvements or adding new visualization types

---

## Query Processing Flow

```
User Query
    ↓
QueryParser.parse() ← Try keyword matching FIRST
    ↓
  Match Found?
    ↓ YES (90%+ of queries)
    Execute API Call
    Generate Simple Summary
    Return to User ⚡ (~1-5ms)
    
    ↓ NO (rare, complex queries)
    LLMService.query()
    ↓
    Ollama Available?
    ↓ YES
    Query Ollama
    Execute API Call
    Return to User 🤖 (~1-5s)
    
    ↓ NO
    Azure OpenAI Available?
    ↓ YES
    Query Azure
    Execute API Call
    Return to User ☁️ (~1-3s)
    
    ↓ NO
    Return "LLM not available" error
```

---

## Development Patterns

### Adding New Endpoints
1. Add endpoint to `app/api_server.py` with appropriate tags
2. Use `load_drivers()`, `load_constructors()`, or `load_season_results()` for data
3. Return data in Ergast-compatible JSON format
4. Update `_docs/readme.md` with endpoint documentation

### Adding New Query Patterns
1. Add pattern method to `QueryParser` class in `app/query_parser.py`
2. Add keywords to class constants (e.g., `CHAMPIONSHIP_KEYWORDS`)
3. Call new parser method in `parse()` method's pattern matching chain
4. Return dict with `action`, `endpoint`, `params`, `context`, `source: "keyword_parser"`
5. Update `_docs/keyword-first-architecture.md`

### Data Refresh
- Use fetch scripts: `app/fetch_drivers.py`, `app/fetch_constructors.py`, `app/fetch_season.py`
- These scripts query Ergast API and save to JSON files
- Run annually to add new season data

---

## Technology Stack

- **Backend**: FastAPI 0.115.5, Uvicorn, Python 3.x
- **Data**: JSON files (no database)
- **Caching**: Python `functools.lru_cache`
- **LLM**: Ollama (local) or Azure OpenAI (cloud) - OPTIONAL
- **Frontend**: Vanilla HTML/JS, Tailwind CSS CDN
- **API**: RESTful, auto-documented with Swagger UI

---

## Development Guidelines

### ✅ DO

- **Always prefer keyword parsing over LLM** - Add patterns to `app/query_parser.py` first
- **Maintain data format consistency** - Keep Ergast API structure intact
- **Use caching appropriately** - Drivers/constructors cached permanently, seasons LRU(5)
- **Keep UI build-free** - No bundlers, use vanilla JS and CDN resources
- **Test without LLM** - Ensure keyword parser handles common cases
- **Document patterns** - Update markdown docs when adding features

### ❌ DON'T

- **Don't make LLM required** - App must work without any LLM setup
- **Don't add database** - Keep JSON-based architecture
- **Don't modify cached data structure** - Use decorators on loader functions
- **Don't add build tools** - Keep frontend simple and direct
- **Don't break Ergast API compatibility** - Maintain original data structure

---

## Code Modification Examples

### Adding a New Keyword Pattern

When adding a new query pattern, follow this structure:

```python
# In app/query_parser.py

# 1. Add keywords to class constants
FEATURE_KEYWORDS = ['keyword1', 'keyword2', 'phrase']

# 2. Add parser method
def parse_feature_query(self, query: str) -> Optional[Dict[str, Any]]:
    """Parse queries about [feature description]"""
    if not any(keyword in query for keyword in self.FEATURE_KEYWORDS):
        return None
    
    # Extract entities (year, driver, etc.)
    year = self.extract_year(query)
    driver = self.extract_driver_name(query)
    
    # Build response
    return {
        'action': 'feature_query',
        'endpoint': f'/api/feature/{year}',
        'params': {'driver': driver},
        'context': f'Fetching feature data for {driver} in {year}',
        'source': 'keyword_parser'
    }

# 3. Add to parse() method chain
def parse(self, query: str) -> Optional[Dict[str, Any]]:
    # ... existing patterns ...
    
    result = self.parse_feature_query(query)
    if result:
        return result
    
    # ... continue with other patterns ...
```

### Adding a New API Endpoint

When adding a new endpoint:

```python
# In app/api_server.py

@app.get("/api/new-endpoint/{param}", tags=["Category"])
async def get_new_data(param: str):
    """
    Brief description of what this endpoint does.
    
    - **param**: Description of parameter
    """
    try:
        # Load data using cached loaders
        data = load_drivers()  # or load_constructors(), load_season_results()
        
        # Process data
        result = process_data(data, param)
        
        # Return in consistent format
        return {
            "data": result,
            "count": len(result),
            "param": param
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing and Running

### Start the Server
```bash
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Test Query Parser
```python
from app.query_parser import QueryParser

parser = QueryParser()
result = parser.parse("who won 2023 championship")
print(result)
```

---

## Architecture Priorities

This architecture prioritizes:
1. **Speed** - Keyword parsing returns results in 1-5ms
2. **Reliability** - No external dependencies required for core functionality
3. **Simplicity** - No database, no build process, no complex setup
4. **Flexibility** - LLM integration available but optional

When making changes, preserve these principles above all else.
