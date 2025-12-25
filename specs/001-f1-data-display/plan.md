# Implementation Plan: F1 Data Display System

**Branch**: `001-f1-data-display` | **Date**: December 26, 2025 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/001-f1-data-display/spec.md`

## Summary

Build a FastAPI-based REST API with vanilla HTML/CSS/JavaScript web interface for displaying Formula 1 historical data (1984-2024). System must serve driver profiles, constructor information, season results, and enable natural language queries using keyword-first pattern matching. All data stored in JSON files with aggressive LRU caching. Zero build process for frontend, minimal Python dependencies for backend.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI 0.115.5, Uvicorn 0.32.1 (minimal set - see requirements.txt)  
**Storage**: JSON files in `f1data/`, `f1drivers/`, `f1constructors/` directories (no database)  
**Testing**: pytest 7.4.0+, pytest-asyncio 0.21.0+  
**Target Platform**: Linux server (development), any platform with Python 3.12+ (production)  
**Project Type**: Web application (API backend + static frontend)  
**Performance Goals**: <100ms API response (95th percentile), <5ms keyword parsing, <2s full page load  
**Constraints**: Zero build process for frontend, no database, LRU caching for seasons (last 5), permanent caching for drivers/constructors  
**Scale/Scope**: 41 seasons (1984-2024), ~850 drivers, ~210 constructors, ~100 concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Self-Contained Operation** (Principle I):
- ✅ Core functionality works without external services (JSON files only)
- ✅ LLM is optional fallback, not required for operation
- ✅ No external databases or third-party APIs for core data display

**Deterministic-First Processing** (Principle II):
- ✅ Keyword pattern matching handles 90%+ of queries
- ✅ LLM is fallback only for complex/ambiguous queries
- ✅ Data retrieval is deterministic (file-based lookups)

**Zero Build Complexity** (Principle III):
- ✅ Frontend: vanilla HTML, CSS (Tailwind CDN), JavaScript - directly executable
- ✅ Backend: Python source files executed directly by Uvicorn
- ✅ No compilation, transpilation, bundling, or preprocessing required

**Data Format Stability** (Principle IV):
- ✅ API returns Ergast API JSON format unmodified
- ✅ No data transformation layers between storage and API response
- ✅ Original JSON structure preserved end-to-end

**Aggressive Optimization & Fault Tolerance** (Principle V):
- ✅ LRU cache for seasons (last 5 in memory)
- ✅ Permanent cache for drivers and constructors (@lru_cache maxsize=1)
- ✅ System continues operating if LLM services unavailable

**Code Quality Gates** (Principle VI):
- ✅ Each module has single, well-defined responsibility (json_loader, query_parser, api_server, routers)
- ✅ Functions independently testable without extensive mocking (pure functions, cached loaders)
- ✅ Related functionality co-located (routers by entity type, services isolated)
- ✅ Clear boundaries between modules/layers (data layer, service layer, API layer, presentation layer)

**Constitution Status**: ✅ **FULL COMPLIANCE** - No violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/001-f1-data-display/
├── plan.md              # This file
├── research.md          # Phase 0: Technology choices and patterns (GENERATED)
├── data-model.md        # Phase 1: Entity relationships and attributes (GENERATED)
├── quickstart.md        # Phase 1: Setup and running instructions (GENERATED)
├── contracts/           # Phase 1: API contracts (GENERATED)
│   └── openapi.yaml     # OpenAPI 3.0 specification
├── checklists/          # Quality validation
│   └── requirements.md  # Spec validation checklist (EXISTS)
└── tasks.md             # Phase 2: Implementation tasks (CREATED BY /speckit.tasks)
```

### Source Code (repository root - EXISTING STRUCTURE)

```text
app/                     # Backend application (EXISTING)
├── api_server.py       # FastAPI app with router inclusion (EXISTING)
├── json_loader.py      # Data loading with LRU caching (EXISTING)
├── query_parser.py     # Keyword-first query parsing (EXISTING)
├── llm_service.py      # Optional LLM fallback (EXISTING)
├── config.py           # Configuration management (EXISTING)
├── routers/            # API endpoint routers (EXISTING)
│   ├── __init__.py
│   ├── drivers.py      # Driver endpoints (EXISTING)
│   ├── seasons.py      # Season endpoints (EXISTING)
│   ├── constructors.py # Constructor endpoints (EXISTING)
│   ├── analytics.py    # Stats/comparison endpoints (EXISTING)
│   └── query.py        # Natural language query endpoint (EXISTING)
└── services/           # Business logic layer (EXISTING)
    ├── __init__.py
    └── f1_service.py   # F1 data service (EXISTING)

static/                 # Frontend application (EXISTING)
├── index.html         # Main query interface (EXISTING)
├── drivers.html       # Driver listing page (EXISTING)
├── results.html       # Season results page (EXISTING)
├── app.js             # Main application logic (EXISTING)
├── drivers.css        # Driver-specific styles (EXISTING)
└── global.css         # Global styles (EXISTING)

f1data/                # Season race results (EXISTING)
├── 1984_results.json
├── ...
└── 2024_results.json

f1drivers/             # Driver database (EXISTING)
└── drivers.json

f1constructors/        # Constructor database (EXISTING)
└── constructors.json

tests/                 # Test suite (EXISTING)
├── conftest.py        # Pytest configuration (EXISTING)
├── test_f1_service.py # Service layer tests (EXISTING)
├── contract/          # API contract tests (TO BE ADDED)
├── integration/       # Integration tests (TO BE ADDED)
└── unit/              # Unit tests (TO BE ADDED)

_docs/                 # Architecture documentation (EXISTING)
├── readme.md
├── keyword-first-architecture.md
└── ...

.specify/              # Specification framework (EXISTING)
├── templates/
├── scripts/
└── memory/
    └── constitution.md

config.json            # LLM configuration (EXISTING)
requirements.txt       # Python dependencies (EXISTING)
README-SETUP.md        # Setup documentation (EXISTING)
```

**Structure Decision**: Web application with separated backend (app/) and frontend (static/). Backend uses router-based FastAPI architecture with clear separation of concerns (routers → services → data loaders). Frontend is zero-build vanilla HTML/CSS/JavaScript served as static files. This structure is ALREADY IMPLEMENTED and must be preserved.

## Complexity Tracking

**No Complexity Violations** - Constitution fully satisfied with existing architecture.
