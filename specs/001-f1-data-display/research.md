# Research: F1 Data Display System

**Phase**: 0 - Outline & Research  
**Date**: December 26, 2025  
**Plan**: [plan.md](plan.md)

## Purpose

This document resolves all technical clarifications and research needs identified during Technical Context review. All decisions are based on existing implementation and constitution principles.

---

## Research Findings

### 1. Data Storage Strategy

**Decision**: JSON files with LRU caching (functools.lru_cache)

**Rationale**:
- Constitution Principle I: Self-contained operation without external dependencies
- 41 seasons × ~20 races × ~20 drivers = ~16,400 race results fit easily in memory
- LRU cache provides automatic memory management for season data
- Permanent caching for static data (drivers, constructors) never expires
- File-based storage eliminates database setup, maintenance, and failure points

**Alternatives Considered**:
- **SQLite database**: Rejected - adds dependency, query complexity, and migration overhead for read-only data
- **Redis caching**: Rejected - external service dependency violates Constitution
- **In-memory database**: Rejected - unnecessary complexity for deterministic lookups

**Implementation Pattern**:
```python
# Permanent cache for static data
@lru_cache(maxsize=1)
def load_drivers() -> Dict[str, Any]:
    """Single cached instance, never evicted"""
    
# LRU cache for temporal data  
@lru_cache(maxsize=5)
def load_season_results(year: int) -> Dict[str, Any]:
    """Keep last 5 accessed seasons in memory"""
```

---

### 2. API Framework Selection

**Decision**: FastAPI with router-based architecture

**Rationale**:
- Already implemented in existing codebase
- Automatic OpenAPI documentation generation (Swagger UI, ReDoc)
- Type hints enable IDE support and validation
- Minimal framework (~5 dependencies in requirements.txt)
- Router pattern provides clean module separation (drivers, seasons, constructors, analytics, query)
- Native async support (though not required for file-based data)

**Alternatives Considered**:
- **Flask**: Rejected - no automatic API documentation, more manual validation
- **Django REST Framework**: Rejected - heavy framework violates minimal dependencies principle
- **Direct HTTP server**: Rejected - reinventing routing, validation, documentation

**Best Practices Applied**:
- Separate routers by resource type (entity-based routing)
- Tags for API documentation grouping
- Consistent error handling with HTTPException
- Dependency injection for services (if needed)

---

### 3. Query Processing Architecture

**Decision**: Keyword-first pattern matching with optional LLM fallback

**Rationale**:
- Constitution Principle II: 90%+ deterministic processing before non-deterministic
- Keyword matching: ~1-5ms response time
- LLM fallback: ~1-5s response time (100-1000x slower)
- Regex patterns for years (1984-2024)
- Fuzzy matching (difflib.get_close_matches) for driver/constructor names
- Pattern matching for query types (championship, stats, standings, comparison)

**Alternatives Considered**:
- **LLM-only processing**: Rejected - violates deterministic-first principle, requires external service
- **NLP library (spaCy, NLTK)**: Rejected - heavy dependencies for simple entity extraction
- **Graph-based query**: Rejected - over-engineering for straightforward lookups

**Supported Pattern Types**:
1. Championship queries: "who won 2010 championship"
2. Driver statistics: "how many wins hamilton"
3. Team information: "about red bull"
4. Season standings: "2023 standings"
5. Comparisons: "compare vettel verstappen"
6. Race winners: "most races 2023"

**Implementation Pattern**:
```python
class QueryParser:
    def parse(self, query: str) -> Optional[Dict[str, Any]]:
        # Try championship query
        result = self.parse_championship_query(query)
        if result: return result
        
        # Try driver stats query
        result = self.parse_driver_stats_query(query)
        if result: return result
        
        # Continue pattern chain...
        
        # No keyword match found
        return None  # Falls back to LLM
```

---

### 4. Frontend Architecture

**Decision**: Vanilla HTML, CSS (Tailwind CDN), JavaScript

**Rationale**:
- Constitution Principle III: Zero build complexity (NON-NEGOTIABLE)
- Tailwind CSS via CDN: utility-first styling without compilation
- No bundlers (Webpack, Vite, Parcel)
- No transpilers (Babel, TypeScript)
- No package managers (npm, yarn) for frontend
- Direct browser execution of source code
- FastAPI serves static files via StaticFiles mount

**Alternatives Considered**:
- **React/Vue/Svelte**: Rejected - requires build process, violates Constitution
- **TypeScript**: Rejected - requires compilation step
- **CSS preprocessors (Sass, Less)**: Rejected - requires compilation
- **Module bundlers**: Rejected - violates zero-build principle

**Best Practices Applied**:
- Progressive enhancement: core features work without JavaScript
- Semantic HTML for accessibility
- CSS custom properties for theming
- Vanilla JavaScript ES6+ features (fetch, async/await, template literals)
- Event delegation for dynamic content
- Responsive design with Tailwind utilities

**File Organization**:
```
static/
├── index.html        # Main query interface
├── drivers.html      # Driver listing/profiles
├── results.html      # Season results
├── app.js           # Main application logic
├── drivers.css      # Driver-specific styles
└── global.css       # Global styles and layout
```

---

### 5. Data Format & API Contracts

**Decision**: Preserve Ergast API JSON format unmodified

**Rationale**:
- Constitution Principle IV: Data format stability
- Ergast API is de facto standard for F1 data
- Existing tools and libraries expect this format
- No transformation layer = fewer bugs
- Direct passthrough from JSON files to API response
- Consistent with existing implementation

**Alternatives Considered**:
- **Custom JSON schema**: Rejected - breaks compatibility, adds transformation complexity
- **GraphQL**: Rejected - requires schema layer, query parsing, resolver complexity
- **Protobuf/Binary formats**: Rejected - not web-friendly, requires encoding/decoding

**Format Example**:
```json
{
  "MRData": {
    "DriverTable": {
      "Drivers": [
        {
          "driverId": "hamilton",
          "givenName": "Lewis",
          "familyName": "Hamilton",
          "dateOfBirth": "1985-01-07",
          "nationality": "British"
        }
      ]
    }
  }
}
```

---

### 6. Testing Strategy

**Decision**: pytest for unit and integration tests, contract tests for API

**Rationale**:
- pytest already in requirements.txt
- pytest-asyncio for testing async endpoints
- Fixtures for test data isolation
- Contract tests validate OpenAPI spec compliance
- Integration tests verify router → service → data layer flow
- Unit tests for pure functions (query parsing, data transformation)

**Test Organization**:
```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Pure function tests
│   ├── test_query_parser.py
│   └── test_json_loader.py
├── integration/          # Multi-layer tests
│   ├── test_driver_endpoints.py
│   ├── test_season_endpoints.py
│   └── test_constructor_endpoints.py
└── contract/             # API contract validation
    └── test_openapi_compliance.py
```

**Best Practices Applied**:
- Fast unit tests (<100ms each)
- Integration tests use TestClient (no server startup)
- Fixtures for data loading (avoid repeated file I/O)
- Parameterized tests for multiple scenarios
- Clear test naming: test_<function>_<scenario>_<expected_result>

---

### 7. Performance Optimization

**Decision**: Aggressive caching with functool.lru_cache

**Rationale**:
- Constitution Principle V: Aggressive optimization
- No cache invalidation needed (historical data is immutable)
- Zero external cache dependencies (Redis, Memcached)
- Python's LRU cache is thread-safe and built-in
- Automatic memory management with maxsize parameter

**Cache Strategy**:
- **Drivers**: maxsize=1 (load once, keep forever) - ~850 drivers = ~2MB
- **Constructors**: maxsize=1 (load once, keep forever) - ~210 constructors = ~500KB
- **Seasons**: maxsize=5 (last 5 accessed) - ~20 races × ~20 drivers × 5 seasons = ~2,000 records per season
- **Total memory**: ~15-20MB for fully loaded cache (negligible)

**Performance Targets**:
- First request (cold cache): <500ms
- Subsequent requests (warm cache): <100ms (95th percentile)
- Keyword parsing: <5ms
- Page load: <2s (network dependent)

---

### 8. Error Handling & Fault Tolerance

**Decision**: Graceful degradation with meaningful error messages

**Rationale**:
- Constitution Principle V: Fault tolerance for optional features
- LLM unavailable? Fall back to keyword parsing
- Season data missing? Return clear error
- Invalid query? Suggest similar entities

**Error Handling Patterns**:
```python
# Invalid year range
if year < 1984 or year > 2024:
    raise HTTPException(
        status_code=400,
        detail=f"Year {year} outside available range (1984-2024)"
    )

# Driver not found with suggestions
if not driver:
    suggestions = get_close_matches(driver_id, all_driver_ids, n=3)
    raise HTTPException(
        status_code=404,
        detail=f"Driver '{driver_id}' not found. Did you mean: {suggestions}?"
    )

# LLM service unavailable
try:
    result = await llm_service.query(text)
except Exception:
    return {"message": "LLM unavailable, please use specific queries"}
```

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.12+ | Already implemented, mature ecosystem |
| API Framework | FastAPI 0.115.5 | Minimal, auto-documentation, type hints |
| Server | Uvicorn 0.32.1 | ASGI server, production-ready |
| Data Storage | JSON files | Self-contained, no external dependencies |
| Caching | functools.lru_cache | Built-in, thread-safe, automatic eviction |
| Frontend HTML | Vanilla HTML5 | Zero build, direct execution |
| Frontend CSS | Tailwind (CDN) | Utility-first, no compilation |
| Frontend JS | Vanilla ES6+ | Zero build, native browser support |
| Testing | pytest 7.4.0+ | Mature, fixtures, async support |
| Query Parsing | Regex + difflib | Built-in, deterministic, fast |
| LLM (Optional) | Ollama / Azure | Fallback only, graceful degradation |

---

## Architecture Decisions

### Layered Architecture

```
┌─────────────────────────────────────┐
│   Presentation Layer (Frontend)     │
│   - index.html, drivers.html        │
│   - app.js, global.css              │
└─────────────────────────────────────┘
              ↓ HTTP
┌─────────────────────────────────────┐
│   API Layer (FastAPI Routers)       │
│   - drivers.py, seasons.py          │
│   - constructors.py, analytics.py   │
│   - query.py                         │
└─────────────────────────────────────┘
              ↓ Function calls
┌─────────────────────────────────────┐
│   Service Layer (Business Logic)    │
│   - f1_service.py                   │
│   - query_parser.py                 │
│   - llm_service.py (optional)       │
└─────────────────────────────────────┘
              ↓ Function calls
┌─────────────────────────────────────┐
│   Data Layer (JSON Loading)         │
│   - json_loader.py                  │
│   - @lru_cache decorators           │
└─────────────────────────────────────┘
              ↓ File I/O
┌─────────────────────────────────────┐
│   Storage (File System)             │
│   - f1data/*.json                   │
│   - f1drivers/drivers.json          │
│   - f1constructors/constructors.json│
└─────────────────────────────────────┘
```

### Query Processing Flow

```
User Query
    ↓
QueryParser (keyword matching) ← 90% of queries (~1-5ms)
    ↓
  Match Found?
    ↓ YES
    API Call → JSON Loader → Cache → Response
    
    ↓ NO (10% of queries)
    LLMService (optional fallback)
    ↓
    Ollama Available?
    ↓ YES
    Parse Intent → API Call → Response (~1-5s)
    
    ↓ NO
    Azure OpenAI Available?
    ↓ YES  
    Parse Intent → API Call → Response (~1-3s)
    
    ↓ NO
    Return "Use specific queries" message
```

---

## Conclusion

All technical decisions align with Constitution principles:
- ✅ Self-contained (no external runtime dependencies)
- ✅ Deterministic-first (keyword parsing before LLM)
- ✅ Zero build complexity (vanilla frontend, Python source execution)
- ✅ Data format stability (Ergast API format preserved)
- ✅ Aggressive optimization (LRU caching throughout)
- ✅ Code quality (clear module boundaries, testable functions)

**No unresolved clarifications remain** - ready for Phase 1 (Design & Contracts).
