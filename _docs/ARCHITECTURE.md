# F1 App - Module Architecture Diagram

## Phase 1: Modular Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser / HTML Pages                     │
│  (index.html, results.html, drivers.html, constructors.html)    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ ES6 Module Imports
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                        PAGES (Phase 2)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ index.js │  │results.js│  │drivers.js│  │compare.js│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  COMPONENTS  │    │     CORE     │    │   UTILITIES  │
├──────────────┤    ├──────────────┤    ├──────────────┤
│              │    │              │    │              │
│ autocomplete │◄───┤ state-       │    │ formatters   │
│     .js      │    │ manager.js   │    │     .js      │
│   (199 L)    │    │   (197 L)    │    │   (197 L)    │
│              │    │              │    │              │
├──────────────┤    │              │    ├──────────────┤
│ query-       │◄───┤              │    │ dom-helpers  │
│ history.js   │    │              │    │     .js      │
│   (165 L)    │    │              │    │   (229 L)    │
│              │    │              │    │              │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ suggestions  │◄───┤ api-client   │    │ pagination   │
│     .js      │    │     .js      │    │     .js      │
│   (179 L)    │    │   (179 L)    │    │   (216 L)    │
│              │    │              │    │              │
├──────────────┤    └──────┬───────┘    └──────────────┘
│ table-       │           │                    ▲
│ renderer.js  │           │                    │
│   (392 L)    │◄──────────┘                    │
│              │                                 │
└──────────────┘                                 │
        │                                        │
        └────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Backend API   │
                    │  FastAPI       │
                    │  /api/*        │
                    └────────────────┘
```

## Module Dependencies

### Core Layer (Foundation)
```
state-manager.js (197 lines)
  - Manages all application state
  - No dependencies
  - Used by: ALL components

api-client.js (179 lines)
  - Centralized API calls
  - No dependencies
  - Used by: page controllers
```

### Component Layer (Reusable UI)
```
autocomplete.js (199 lines)
  ├─ Depends on: state-manager
  └─ Provides: Search dropdown with keyboard nav

query-history.js (165 lines)
  ├─ Depends on: state-manager
  └─ Provides: localStorage-backed history

suggestions.js (179 lines)
  ├─ Depends on: state-manager
  └─ Provides: Context-aware suggestions

table-renderer.js (392 lines)
  ├─ Depends on: state-manager, formatters, pagination
  └─ Provides: 6 table configurations + rendering
```

### Utility Layer (Helpers)
```
formatters.js (197 lines)
  ├─ Depends on: state-manager (for driver lookups)
  └─ Provides: Data transformation functions

dom-helpers.js (229 lines)
  ├─ Depends on: Nothing (pure utilities)
  └─ Provides: DOM manipulation, loading states

pagination.js (216 lines)
  ├─ Depends on: state-manager
  └─ Provides: Pagination logic + UI
```

## Data Flow Example: Search Query

```
1. User types in search box
   │
   ▼
2. autocomplete.js
   ├─ Debounces input (300ms)
   ├─ Reads state-manager (getAllDrivers)
   ├─ Filters matches
   └─ Renders dropdown
   │
   ▼
3. User selects item
   │
   ▼
4. Page controller (Phase 2)
   ├─ Calls api-client.executeQuery()
   ├─ Updates state-manager.setCurrentResults()
   └─ Calls table-renderer.renderResults()
   │
   ▼
5. table-renderer.js
   ├─ Reads config (TABLE_CONFIGS)
   ├─ Uses formatters (createDriverLink, etc.)
   ├─ Uses pagination (if needed)
   └─ Renders HTML to container
```

## File Size Summary

```
Category        Files  Lines   Size    Avg/File
─────────────────────────────────────────────────
Core              2     376    8.6 KB   188 lines
Components        4     935   31.6 KB   234 lines
Utils             3     642   20.7 KB   214 lines
─────────────────────────────────────────────────
Total             9   1,953   60.9 KB   217 lines
```

## Comparison: Before vs After

### Before (Monolithic app.js)
```
app.js (920 lines)
  ├─ Global state (19 variables)
  ├─ Query history (80 lines)
  ├─ Suggestions (71 lines)
  ├─ Search/Init (105 lines)
  ├─ Autocomplete (116 lines)
  ├─ Results page (100 lines)
  └─ Table rendering (412 lines)
      ├─ TABLE_CONFIGS
      ├─ renderResults
      ├─ renderKeyValueTable
      ├─ renderHeadToHead
      ├─ renderDataTable
      └─ Pagination (48 lines)

Problems:
❌ Everything in global scope
❌ Mixed concerns
❌ No reusability
❌ Can't test
❌ Hard to maintain
```

### After (Modular)
```
js/
├─ core/
│  ├─ api-client.js (179 lines)
│  │  ├─ All API calls
│  │  ├─ Caching strategy
│  │  └─ Error handling
│  │
│  └─ state-manager.js (197 lines)
│     ├─ Encapsulated state
│     ├─ Getters/setters
│     └─ No direct access
│
├─ components/
│  ├─ autocomplete.js (199 lines)
│  ├─ query-history.js (165 lines)
│  ├─ suggestions.js (179 lines)
│  └─ table-renderer.js (392 lines)
│
└─ utils/
   ├─ formatters.js (197 lines)
   ├─ dom-helpers.js (229 lines)
   └─ pagination.js (216 lines)

Benefits:
✅ Clear module boundaries
✅ Single responsibility
✅ Reusable components
✅ Testable functions
✅ Easy to maintain
```

## Phase 2 Preview: Page Controllers

```
js/pages/
├─ index.js (Landing Page)
│  ├─ Imports: autocomplete, query-history, suggestions, api-client
│  ├─ Orchestrates: search UI
│  └─ Handles: form submission, navigation
│
├─ results.js (Query Results)
│  ├─ Imports: api-client, table-renderer, state-manager
│  ├─ Orchestrates: query execution, results display
│  └─ Replaces: 419 lines of inline JS
│
├─ driver-profile.js (Driver Pages)
│  ├─ Imports: api-client, formatters, dom-helpers
│  ├─ Orchestrates: driver data fetching, rendering
│  └─ Replaces: 225 lines of inline JS
│
└─ compare.js (Comparison Tool)
   ├─ Imports: api-client, table-renderer, Chart.js
   ├─ Orchestrates: comparison logic, visualization
   └─ Refactors: existing 529-line compare.js
```

---

**Legend:**
- **L** = Lines of code
- **◄─** = Depends on
- **▼** = Data flows to
- **✅** = Achieved
- **❌** = Problem solved

---

Generated: December 26, 2024 - Phase 1 Complete
