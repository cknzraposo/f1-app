# Tasks: F1 Data Display System

**Branch**: `001-f1-data-display` | **Created**: December 26, 2025  
**Input**: Design documents from `/specs/001-f1-data-display/`  
**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) | **Data Model**: [data-model.md](data-model.md)

**Implementation Strategy**: This feature builds on EXISTING implementation. Tasks focus on validation, enhancement, and documentation rather than building from scratch.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- All file paths are relative to repository root

---

## Phase 1: Setup (Project Validation)

**Purpose**: Validate existing implementation and ensure development environment is ready

- [ ] T001 Verify Python 3.12+ installed and virtual environment configured
- [ ] T002 Validate all dependencies in requirements.txt are installed correctly
- [ ] T003 [P] Verify data files exist: f1data/*.json, f1drivers/drivers.json, f1constructors/constructors.json
- [ ] T004 [P] Run existing tests with `pytest tests/` to establish baseline
- [ ] T005 Start server with `uvicorn app.api_server:app --reload` and verify http://localhost:8000 loads

**Checkpoint**: Development environment ready - all existing code functional

---

## Phase 2: Foundational (Core Infrastructure Enhancement)

**Purpose**: Enhance existing infrastructure to support all user stories

**⚠️ CRITICAL**: These enhancements must be complete before user story validation begins

- [ ] T006 [P] Add input validation helpers in app/services/validation.py for year range (1984-2024), driver IDs, constructor IDs
- [ ] T007 [P] Enhance error responses in app/routers/*.py to include helpful suggestions using difflib.get_close_matches
- [ ] T008 Add comprehensive logging to app/json_loader.py for cache hits/misses and file load times
- [ ] T009 [P] Create test fixtures in tests/conftest.py for driver data, constructor data, and season data
- [ ] T010 Document existing LRU cache configuration in app/json_loader.py with performance metrics

**Checkpoint**: Infrastructure enhanced - ready for user story validation and testing

---

## Phase 3: User Story 1 - View Driver Information (Priority: P1) 🎯 MVP

**Goal**: Users can access comprehensive driver profiles via API and web interface with biographical data and career statistics

**Independent Test**: Request `/api/drivers/hamilton` via API and view driver profile page - should display complete driver information and computed statistics

### Validation for User Story 1

- [ ] T011 [P] [US1] Verify `/api/drivers` endpoint returns complete driver list from app/routers/drivers.py
- [ ] T012 [P] [US1] Verify `/api/drivers/{driver_id}` endpoint returns driver biographical data correctly
- [ ] T013 [US1] Validate driver statistics computation in app/services/f1_service.py (wins, podiums, poles, fastest laps)
- [ ] T014 [P] [US1] Test `/api/drivers/{driver_id}/stats` endpoint computes career totals correctly
- [ ] T015 [US1] Verify driver data caching with @lru_cache(maxsize=1) in app/json_loader.py performs as expected

### Testing for User Story 1

- [ ] T016 [P] [US1] Create contract tests for driver endpoints in tests/contract/test_drivers.py
- [ ] T017 [P] [US1] Create integration tests for driver data flow in tests/integration/test_driver_flow.py
- [ ] T018 [P] [US1] Create unit tests for driver statistics computation in tests/unit/test_driver_stats.py

### Enhancement for User Story 1

- [ ] T019 [US1] Enhance static/drivers.html to display driver statistics cards with responsive layout
- [ ] T020 [US1] Add driver search/filter functionality in static/drivers.html using JavaScript
- [ ] T021 [US1] Implement driver profile detail view with season-by-season breakdown in static/drivers.html
- [ ] T022 [P] [US1] Add error handling for driver not found with suggestions in app/routers/drivers.py

**Checkpoint**: User Story 1 complete - driver information fully accessible and tested

---

## Phase 4: User Story 2 - View Constructor Information (Priority: P1)

**Goal**: Users can access comprehensive constructor team profiles via API and web interface with team history and performance statistics

**Independent Test**: Request `/api/constructors/ferrari` via API and view constructor profile - should display complete team information and statistics

### Validation for User Story 2

- [ ] T023 [P] [US2] Verify `/api/constructors` endpoint returns complete constructor list from app/routers/constructors.py
- [ ] T024 [P] [US2] Verify `/api/constructors/{constructor_id}` endpoint returns team information correctly
- [ ] T025 [US2] Validate constructor statistics computation in app/services/f1_service.py
- [ ] T026 [P] [US2] Test `/api/constructors/{constructor_id}/stats` endpoint computes team career totals
- [ ] T027 [US2] Verify constructor data caching with @lru_cache(maxsize=1) performs as expected

### Testing for User Story 2

- [ ] T028 [P] [US2] Create contract tests for constructor endpoints in tests/contract/test_constructors.py
- [ ] T029 [P] [US2] Create integration tests for constructor data flow in tests/integration/test_constructor_flow.py
- [ ] T030 [P] [US2] Create unit tests for constructor statistics computation in tests/unit/test_constructor_stats.py

### Enhancement for User Story 2

- [ ] T031 [US2] Create or enhance constructor listing page in static/constructors.html with team cards
- [ ] T032 [US2] Add constructor search/filter functionality in static/constructors.html
- [ ] T033 [US2] Implement constructor profile detail view with driver history in static/constructors.html
- [ ] T034 [P] [US2] Add error handling for constructor not found with suggestions in app/routers/constructors.py

**Checkpoint**: User Story 2 complete - constructor information fully accessible and tested

---

## Phase 5: User Story 3 - View Season Race Results (Priority: P1)

**Goal**: Users can access comprehensive season data including race results, championship standings, and season statistics for any year 1984-2024

**Independent Test**: Request `/api/seasons/2023` via API and view results page - should display all races, results, and championship standings

### Validation for User Story 3

- [ ] T035 [P] [US3] Verify `/api/seasons` endpoint returns available years (1984-2024) from app/routers/seasons.py
- [ ] T036 [P] [US3] Verify `/api/seasons/{year}` endpoint returns complete race results for a season
- [ ] T037 [US3] Test `/api/seasons/{year}/standings` endpoint returns driver and constructor championship tables
- [ ] T038 [P] [US3] Test `/api/seasons/{year}/winners` endpoint returns season champions correctly
- [ ] T039 [US3] Verify season data caching with @lru_cache(maxsize=5) evicts old seasons correctly
- [ ] T040 [P] [US3] Validate year range validation (1984-2024) in app/routers/seasons.py

### Testing for User Story 3

- [ ] T041 [P] [US3] Create contract tests for season endpoints in tests/contract/test_seasons.py
- [ ] T042 [P] [US3] Create integration tests for season data flow in tests/integration/test_season_flow.py
- [ ] T043 [P] [US3] Create unit tests for standings computation in tests/unit/test_season_stats.py

### Enhancement for User Story 3

- [ ] T044 [US3] Enhance static/results.html to display season selector (1984-2024)
- [ ] T045 [US3] Implement race-by-race results table in static/results.html with sortable columns
- [ ] T046 [US3] Add championship standings tables (drivers and constructors) in static/results.html
- [ ] T047 [US3] Create season summary view with champions and statistics in static/results.html
- [ ] T048 [P] [US3] Add error handling for invalid year with range message in app/routers/seasons.py

**Checkpoint**: User Story 3 complete - season information fully accessible and tested

---

## Phase 6: User Story 4 - Query Data via Natural Language (Priority: P2)

**Goal**: Users can ask natural language questions and receive accurate answers using keyword-first pattern matching with optional LLM fallback

**Independent Test**: Submit query "Who won the 2010 championship?" via web interface or POST to `/api/query` - should return Sebastian Vettel (driver) and Red Bull (constructor)

### Validation for User Story 4

- [ ] T049 [P] [US4] Verify query parser extracts years correctly using regex in app/query_parser.py
- [ ] T050 [P] [US4] Verify query parser extracts driver names with fuzzy matching in app/query_parser.py
- [ ] T051 [P] [US4] Verify query parser extracts constructor names in app/query_parser.py
- [ ] T052 [US4] Test championship query pattern matching in app/query_parser.py
- [ ] T053 [P] [US4] Test driver statistics query pattern matching in app/query_parser.py
- [ ] T054 [P] [US4] Test standings query pattern matching in app/query_parser.py
- [ ] T055 [US4] Verify query processing flow in app/routers/query.py routes to correct endpoints
- [ ] T056 [P] [US4] Test LLM fallback graceful degradation when services unavailable in app/llm_service.py

### Testing for User Story 4

- [ ] T057 [P] [US4] Create contract tests for query endpoint in tests/contract/test_query.py
- [ ] T058 [P] [US4] Create integration tests for query patterns in tests/integration/test_query_parsing.py
- [ ] T059 [P] [US4] Create unit tests for entity extraction in tests/unit/test_query_parser.py

### Enhancement for User Story 4

- [ ] T060 [US4] Enhance static/index.html search interface with query suggestions
- [ ] T061 [US4] Add query result rendering based on query type in static/app.js
- [ ] T062 [US4] Implement query history and autocomplete in static/index.html
- [ ] T063 [US4] Add processing time and source indicator (keyword_parser/llm) in static/app.js
- [ ] T064 [P] [US4] Add error handling for ambiguous queries with suggestions in app/routers/query.py

**Checkpoint**: User Story 4 complete - natural language queries working with keyword-first approach

---

## Phase 7: User Story 5 - Compare Driver or Constructor Performance (Priority: P3)

**Goal**: Users can compare multiple drivers or constructors side-by-side with statistics, head-to-head records, and career trajectories

**Independent Test**: Request `/api/stats/head-to-head?driver1=hamilton&driver2=verstappen` - should return comparative statistics with common seasons and head-to-head data

### Validation for User Story 5

- [ ] T065 [P] [US5] Verify `/api/stats/head-to-head` endpoint in app/routers/analytics.py accepts multiple entities
- [ ] T066 [US5] Test comparative statistics calculation in app/services/f1_service.py
- [ ] T067 [P] [US5] Verify head-to-head record computation for overlapping seasons
- [ ] T068 [P] [US5] Test `/api/stats/fastest-laps/{year}` endpoint for fastest lap rankings

### Testing for User Story 5

- [ ] T069 [P] [US5] Create contract tests for analytics endpoints in tests/contract/test_analytics.py
- [ ] T070 [P] [US5] Create integration tests for comparison flow in tests/integration/test_comparison.py
- [ ] T071 [P] [US5] Create unit tests for comparison calculations in tests/unit/test_comparison_stats.py

### Implementation for User Story 5

- [ ] T072 [US5] Create comparison interface in static/compare.html with entity selector
- [ ] T073 [US5] Implement side-by-side statistics display in static/compare.html
- [ ] T074 [US5] Add common season highlighting and head-to-head records in static/compare.html
- [ ] T075 [US5] Create visualization for career trajectory comparison using Chart.js or similar (CDN)
- [ ] T076 [P] [US5] Add comparison link from driver/constructor profile pages in static/drivers.html and static/constructors.html

**Checkpoint**: User Story 5 complete - comparison analytics fully functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories and overall system quality

- [ ] T077 [P] Validate all API endpoints match OpenAPI specification in specs/001-f1-data-display/contracts/openapi.yaml
- [ ] T078 [P] Run performance benchmarking on all endpoints and verify <100ms response time (95th percentile)
- [ ] T079 Verify LRU cache performance: drivers/constructors permanent, seasons LRU(5)
- [ ] T080 [P] Test error handling: invalid year, driver not found, constructor not found, missing data
- [ ] T081 [P] Validate responsive design across device sizes (mobile, tablet, desktop)
- [ ] T082 Add API rate limiting or throttling if needed for production deployment
- [ ] T083 [P] Review module responsibilities per Constitution Principle VI in app/ directory
- [ ] T084 [P] Verify function testability without extensive mocking per Constitution Principle VI
- [ ] T085 Code cleanup: remove unused imports, dead code, debug statements
- [ ] T086 [P] Update _docs/readme.md with architecture changes if any
- [ ] T087 [P] Add JSDoc comments to static/app.js for key functions
- [ ] T088 Validate all acceptance scenarios from spec.md are satisfied
- [ ] T089 Run full test suite with coverage report: `pytest --cov=app tests/`
- [ ] T090 Follow quickstart.md steps on fresh environment to validate setup instructions
- [ ] T091 [P] Verify all success criteria (SC-001 through SC-012) are met
- [ ] T092 Final Constitution Check: verify all 6 principles still satisfied
- [ ] T093 [P] Validate edge case handling: year outside 1984-2024 range returns helpful error
- [ ] T094 [P] Validate edge case handling: similar driver/constructor names use fuzzy matching suggestions
- [ ] T095 Validate edge case handling: drivers with incomplete race data display correctly
- [ ] T096 [P] Validate edge case handling: constructor name changes (e.g., Toro Rosso → AlphaTauri) are handled
- [ ] T097 [P] Validate edge case handling: special characters and accents in names are processed correctly
- [ ] T098 [P] Validate edge case handling: missing JSON data files return graceful error messages

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1, 2, 3 (P1): Can proceed in parallel after Phase 2
  - User Story 4 (P2): Depends on US1, US2, US3 (needs data to query)
  - User Story 5 (P3): Depends on US1, US2 (needs entities to compare)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 2 (Foundational)
    ↓
    ├──→ US1 (Drivers) ────┐
    ├──→ US2 (Constructors) ┼──→ US4 (Natural Language) ──→ US5 (Comparison)
    └──→ US3 (Seasons) ─────┘
```

- **US1, US2, US3**: Independent, can run in parallel
- **US4**: Needs US1, US2, US3 data endpoints to query against
- **US5**: Needs US1, US2 for entity comparison

### Within Each User Story

1. **Validation tasks** (verify existing implementation works)
2. **Testing tasks** (add test coverage - can run in parallel within phase)
3. **Enhancement tasks** (improve UI/features sequentially)

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T006 (validation helpers) || T007 (error responses) || T008 (logging) || T009 (test fixtures) || T010 (documentation)

**Within Phase 3 (US1)**:
- T011 (drivers list) || T012 (driver detail) || T014 (driver stats) || T015 (caching)
- T016 (contract tests) || T017 (integration tests) || T018 (unit tests)
- T022 (error handling) can run parallel with T019-T021

**Within Phase 4 (US2)**:
- T023 (constructors list) || T024 (constructor detail) || T026 (constructor stats) || T027 (caching)
- T028 (contract tests) || T029 (integration tests) || T030 (unit tests)
- T034 (error handling) can run parallel with T031-T033

**Within Phase 5 (US3)**:
- T035 (seasons list) || T036 (season detail) || T038 (winners) || T040 (validation)
- T041 (contract tests) || T042 (integration tests) || T043 (unit tests)
- T048 (error handling) can run parallel with T044-T047

**Within Phase 6 (US4)**:
- T049 (year extraction) || T050 (driver names) || T051 (constructor names) || T053 (driver stats patterns) || T054 (standings patterns)
- T057 (contract tests) || T058 (integration tests) || T059 (unit tests)
- T064 (error handling) can run parallel with T060-T063

**Within Phase 7 (US5)**:
- T065 (head-to-head) || T067 (overlapping seasons) || T068 (fastest laps)
- T069 (contract tests) || T070 (integration tests) || T071 (unit tests)
- T076 (links) can run parallel with T072-T075

**Within Phase 8 (Polish)**:
- Most polish tasks marked [P] can run in parallel: T077, T078, T080, T081, T083, T084, T086, T087, T091

**Cross-Phase Parallelism**:
- Once Phase 2 completes, Phases 3, 4, 5 can start in parallel (US1, US2, US3)
- Different team members can own different user stories

---

## Implementation Strategy

### MVP Delivery (Minimum Viable Product)

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1 only)**

This delivers:
- ✅ Working development environment
- ✅ Enhanced infrastructure
- ✅ Complete driver information system (API + Web UI)
- ✅ Tests and documentation

**Time estimate**: ~8-12 hours for MVP

### Incremental Delivery

**v1.0** (MVP): User Story 1 - Drivers  
**v1.1**: Add User Story 2 - Constructors  
**v1.2**: Add User Story 3 - Seasons  
**v2.0**: Add User Story 4 - Natural Language Queries  
**v2.1**: Add User Story 5 - Comparisons  
**v2.2**: Polish phase complete

Each version is independently deployable and testable.

---

## Testing Strategy

### Test Coverage Goals

- **Unit tests**: Pure functions, data computations, parsers (90%+ coverage)
- **Integration tests**: Multi-layer flows, API → Service → Data (80%+ coverage)
- **Contract tests**: API endpoint compliance with OpenAPI spec (100% endpoint coverage)

### Test Execution

```bash
# Run all tests
pytest tests/

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific user story tests
pytest -k "test_driver" tests/
pytest -k "test_constructor" tests/
```

### Test Data

- Use fixtures from `tests/conftest.py`
- Avoid real file I/O in unit tests (mock json_loader)
- Integration tests can use real test data files
- Contract tests validate against OpenAPI spec

---

## Performance Validation

### Success Criteria Verification

After completing all phases, verify:

- **SC-001**: Driver profile <2s → Test: `time curl http://localhost:8000/api/drivers/hamilton`
- **SC-002**: Constructor profile <2s → Test: `time curl http://localhost:8000/api/constructors/ferrari`
- **SC-003**: Season results <3s → Test: `time curl http://localhost:8000/api/seasons/2023`
- **SC-004**: Natural language queries <5s → Test query endpoint response time
- **SC-009**: API <100ms (95%) → Run load test with 100 concurrent requests
- **SC-010**: Comparison <3s → Test head-to-head endpoint
- **SC-011**: Page load <2s → Test with browser developer tools

### Load Testing

```bash
# Install Apache Bench or similar
ab -n 1000 -c 100 http://localhost:8000/api/drivers/hamilton

# Should show:
# - 95th percentile < 100ms (cached)
# - No failed requests
# - Consistent performance
```

---

## Completion Checklist

### All Phases Complete When:

- [ ] All tasks T001-T092 marked as complete
- [ ] All tests passing: `pytest tests/` returns 0 failures
- [ ] All user stories independently testable and functional
- [ ] All acceptance scenarios from spec.md validated
- [ ] All success criteria (SC-001 through SC-012) verified
- [ ] Constitution compliance maintained (all 6 principles)
- [ ] Quickstart guide validated on fresh environment
- [ ] Performance benchmarks meet targets
- [ ] Code coverage >80% for integration, >90% for unit tests
- [ ] OpenAPI spec matches implementation
- [ ] Documentation updated and accurate

### Ready for Production When:

- [ ] All completion checklist items above satisfied
- [ ] Security review completed (if applicable)
- [ ] Performance under load validated (100+ concurrent users)
- [ ] Error handling tested for all edge cases
- [ ] Logging and monitoring configured
- [ ] Deployment documentation written
- [ ] Rollback procedure documented

---

## Notes

**Existing Implementation**: This F1 app already has substantial implementation. Tasks focus on:
1. **Validation**: Ensuring existing code meets all requirements
2. **Testing**: Adding comprehensive test coverage
3. **Enhancement**: Improving UI and user experience
4. **Documentation**: Validating and updating docs

**Not Building From Scratch**: Unlike a greenfield project, we're validating and enhancing existing code. This means:
- Many "implementation" tasks are actually "validation" tasks
- Focus is on test coverage and documentation
- Enhancements are incremental improvements
- Constitution compliance already achieved

**File Preservation**: Per requirements, current files are preserved and used as reference. Tasks respect existing architecture and patterns.

---

**Total Tasks**: 98  
**Estimated Effort**: 42-64 hours (with existing implementation as baseline)  
**MVP Effort**: 8-12 hours (Phase 1-3: Setup + Foundational + US1)  
**Parallelizable Tasks**: ~51 tasks marked [P] for concurrent execution
