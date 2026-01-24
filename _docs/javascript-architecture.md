# F1 App - Modular JavaScript Architecture (Phase 1)

## Overview

This document describes the new modular JavaScript architecture created during **Phase 1** of the refactoring effort. The original monolithic `app.js` (920 lines) has been extracted into focused, reusable modules following Separation of Concerns principles.

## Directory Structure

```
static/js/
├── core/                      # Core functionality
│   ├── api-client.js          # Centralized API calls with caching
│   └── state-manager.js       # Application state management
├── components/                # Reusable UI components
│   ├── autocomplete.js        # Driver/constructor search autocomplete
│   ├── query-history.js       # Query history with localStorage
│   ├── suggestions.js         # Smart query suggestions
│   └── table-renderer.js      # Table rendering with configurations
├── utils/                     # Utility functions
│   ├── formatters.js          # Data formatting and transformation
│   ├── dom-helpers.js         # DOM manipulation utilities
│   └── pagination.js          # Pagination logic and controls
└── pages/                     # Page-specific controllers (Phase 2)
    └── (coming in Phase 2)
```

## Module Descriptions

### Core Modules

#### `api-client.js`
Centralized API client with built-in caching and error handling.

**Key Features:**
- LRU cache for season data (5 most recent)
- Permanent cache for drivers/constructors
- Unified error handling
- Prefetch capability

**Exports:**
```javascript
// Driver endpoints
getDrivers()
getDriver(driverId)
getDriverStats(driverId)

// Constructor endpoints
getConstructors()
getConstructor(constructorId)
getConstructorStats(constructorId)

// Season endpoints
getSeasonResults(year)
getSeasonStandings(year)
getSeasonWinners(year)

// Query & comparison
executeQuery(query)
getHeadToHead(driver1Id, driver2Id)

// Utilities
clearCache()
prefetchCommonData()
```

**Usage Example:**
```javascript
import { getDrivers, getSeasonStandings } from './js/core/api-client.js';

// Fetch drivers (cached after first call)
const drivers = await getDrivers();

// Fetch season standings
const standings = await getSeasonStandings(2023);
```

---

#### `state-manager.js`
Encapsulates all global state with getters/setters.

**State Categories:**
- Autocomplete data (drivers, constructors)
- Autocomplete UI state (timeout, index)
- Pagination state (page, page size)
- Results state (current data, data type)
- Query history (with max limit)

**Exports:**
```javascript
// Autocomplete data
getAllDrivers() / setAllDrivers(drivers)
getAllConstructors() / setAllConstructors(constructors)

// Pagination
getCurrentPage() / setCurrentPage(page)
getPageSize() / setPageSize(size)

// Results
getCurrentData() / setCurrentData(data)
getCurrentDataType() / setCurrentDataType(type)
setCurrentResults(data, dataType)

// Query history
getQueryHistory()
addToQueryHistory(query)
clearQueryHistory()

// Utilities
resetState()
getStateSnapshot()
```

**Usage Example:**
```javascript
import { setCurrentPage, getCurrentPage } from './js/core/state-manager.js';

// Change page
setCurrentPage(2);
console.log(getCurrentPage()); // 2
```

---

### Component Modules

#### `autocomplete.js`
Driver and constructor search autocomplete with keyboard navigation.

**Features:**
- Debounced input (300ms)
- Fuzzy matching on driver/constructor names
- Keyboard navigation (Arrow Up/Down, Enter, Escape)
- Visual selection highlighting

**Exports:**
```javascript
initAutocomplete(inputElement, autocompleteElement, onSelect)
hideAutocomplete(autocompleteElement)
selectAutocompleteItem(value, type, inputElement, onSelect)
```

**Usage Example:**
```javascript
import { initAutocomplete } from './js/components/autocomplete.js';

const searchInput = document.getElementById('searchInput');
const autocompleteDropdown = document.getElementById('autocomplete');

initAutocomplete(searchInput, autocompleteDropdown, (value, type) => {
    console.log(`Selected ${type}: ${value}`);
    // Handle selection
});
```

---

#### `query-history.js`
localStorage-backed query history with UI rendering.

**Features:**
- Persists to localStorage
- Deduplication (most recent first)
- Configurable max history size (default: 10)
- Shows last 5 in dropdown
- Clear all functionality

**Exports:**
```javascript
loadQueryHistory()
saveQueryToHistory(query)
clearQueryHistory()
showQueryHistory(historyElement, onSelect)
hideQueryHistory(historyElement)
initQueryHistory(inputElement, historyElement, onSelect)
getRecentQueries(limit)
```

**Usage Example:**
```javascript
import { initQueryHistory, saveQueryToHistory } from './js/components/query-history.js';

const input = document.getElementById('searchInput');
const historyDropdown = document.getElementById('queryHistory');

initQueryHistory(input, historyDropdown, (query) => {
    input.value = query;
    executeSearch(query);
});

// Save query after search
saveQueryToHistory('Who won 2023 championship?');
```

---

#### `suggestions.js`
Context-aware smart query suggestions.

**Features:**
- Year-based suggestions (1984-2024)
- Driver-based suggestions
- Constructor-based suggestions
- Comparison suggestions
- Fallback to popular queries

**Exports:**
```javascript
generateSuggestions(input)
showSmartSuggestions(input, suggestionsElement, onSelect)
hideSuggestions(suggestionsElement)
initSuggestions(inputElement, suggestionsElement, onSelect)
getPopularSuggestions()
```

**Usage Example:**
```javascript
import { initSuggestions } from './js/components/suggestions.js';

const input = document.getElementById('searchInput');
const suggestionsEl = document.getElementById('suggestions');

initSuggestions(input, suggestionsEl, (query) => {
    input.value = query;
    executeSearch(query);
});
```

---

#### `table-renderer.js`
Unified table rendering system with multiple configurations.

**Features:**
- 6 pre-configured table types
- Automatic pagination for large datasets
- Driver name linking
- Podium highlighting
- Auto-detection fallback
- Key-value and head-to-head formats

**Table Configurations:**
- `championship_standings` - Season championship tables
- `driver_stats` - Key-value statistics
- `constructor_stats` - Key-value statistics
- `season_winners` - Race winners (paginated)
- `race_results` - Individual race results
- `driver_search` - Driver directory (paginated)
- `head_to_head` - Driver comparison view

**Exports:**
```javascript
TABLE_CONFIGS  // Configuration object
renderResults(data, dataType, container, options)
getTableConfig(dataType)
hasTableConfig(dataType)
```

**Usage Example:**
```javascript
import { renderResults } from './js/components/table-renderer.js';

const container = document.getElementById('resultsContent');
const data = { driverStandings: [...] };

renderResults(data, 'championship_standings', container);
```

---

### Utility Modules

#### `formatters.js`
Data formatting and transformation utilities.

**Exports:**
```javascript
// Data extraction
getNestedValue(obj, path)

// Driver utilities
isDriverColumn(columnKey)
getDriverId(row, columnKey)
createDriverLink(driverName, driverId)

// Formatting
formatDate(dateString)
formatTime(timeString)
formatNumber(num)
formatPoints(points)

// Styling
getPodiumClass(position)

// Text utilities
escapeHtml(text)
truncateText(text, maxLength)

// URL utilities
parseQueryString(queryString)
buildQueryString(params)
```

**Usage Example:**
```javascript
import { getNestedValue, createDriverLink, formatDate } from './js/utils/formatters.js';

const driver = { Driver: { familyName: 'Hamilton' } };
const name = getNestedValue(driver, 'Driver.familyName'); // 'Hamilton'

const link = createDriverLink('Lewis Hamilton', 'hamilton');
// Returns: <a href="/static/drivers.html?id=hamilton">Lewis Hamilton</a>
```

---

#### `dom-helpers.js`
DOM manipulation and UI utilities.

**Exports:**
```javascript
// UI states
showLoading(element, message)
showError(element, message, details)
showEmpty(element, message, subtitle)
clearElement(element)

// Element utilities
createElementFromHTML(html)
toggleClass(element, className, condition)
setVisibility(element, visible)
scrollToElement(element, options)
getElementById(id)
querySelectorAll(selector, parent)

// Event handling
addListener(element, event, handler)  // Returns cleanup function

// Performance
debounce(func, delay)
throttle(func, limit)

// Async
waitForElement(selector, timeout)
```

**Usage Example:**
```javascript
import { showLoading, showError, debounce } from './js/utils/dom-helpers.js';

const container = document.getElementById('resultsContent');

// Show loading state
showLoading(container, 'Fetching data...');

// Debounced search
const debouncedSearch = debounce((query) => {
    performSearch(query);
}, 300);

input.addEventListener('input', (e) => debouncedSearch(e.target.value));
```

---

#### `pagination.js`
Pagination logic and UI rendering.

**Exports:**
```javascript
// Core logic
calculatePagination(totalItems, currentPage, pageSize)
paginateData(data, currentPage, pageSize)
renderPaginationControls(pagination, onChangeCallback)

// Navigation
changePage(page)
changePageSize(size)
nextPage()
previousPage()
firstPage()
lastPage(totalItems)
resetPagination()

// Utilities
getPageNumbers(currentPage, totalPages, maxVisible)
```

**Usage Example:**
```javascript
import { paginateData, renderPaginationControls } from './js/utils/pagination.js';

const allData = [...]; // Array of items
const { data: paginatedData, pagination } = paginateData(allData);

// Render paginated data
renderTable(paginatedData);

// Render pagination controls
const controlsHTML = renderPaginationControls(pagination);
container.innerHTML += controlsHTML;
```

---

## Testing

### Module Import Test
A test page is provided to verify all modules load correctly:

```bash
# Start server
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000

# Open test page
open http://localhost:8000/static/module-test.html
```

The test page checks:
- ✓ All modules can be imported
- ✓ All expected exports are present
- ✓ No import errors

---

## Migration Status

### ✅ Phase 1 Complete (Current)
- [x] Directory structure created
- [x] API client module extracted
- [x] State manager created
- [x] Autocomplete component extracted
- [x] Query history component extracted
- [x] Suggestions component extracted
- [x] Table renderer component extracted
- [x] Utility modules created
- [x] Module test page created

### 🔄 Phase 2 (Next Steps)
Phase 2 will migrate existing pages to use the new modules:

1. Create page controllers in `js/pages/`:
   - `index.js` - Landing page
   - `results.js` - Query results page
   - `driver-profile.js` - Driver detail pages
   - `constructor-profile.js` - Constructor detail pages
   - `compare.js` - Comparison page (refactor existing)

2. Update HTML files to use modules:
   - Remove inline JavaScript
   - Add `<script type="module">` imports
   - Replace old `app.js` references

3. Deprecation:
   - Mark old `app.js` as deprecated
   - Eventually remove once all pages migrated

---

## Design Principles Maintained

✅ **Vanilla JavaScript** - No frameworks, just ES6 modules  
✅ **No Build Process** - Direct browser imports  
✅ **Separation of Concerns** - Clear module boundaries  
✅ **Single Responsibility** - Each module has one purpose  
✅ **Testability** - Pure functions, minimal side effects  
✅ **Performance** - Caching, debouncing, pagination  
✅ **Backward Compatible** - Old `app.js` still functional  

---

## Browser Compatibility

ES6 modules are supported in:
- Chrome 61+
- Firefox 60+
- Safari 11+
- Edge 16+

For older browsers, consider using a simple bundler (optional, not required for development).

---

## Best Practices

### Importing Modules
```javascript
// Named imports (preferred)
import { getDrivers, getConstructors } from './js/core/api-client.js';

// Import all
import * as API from './js/core/api-client.js';
const drivers = await API.getDrivers();
```

### Error Handling
```javascript
import { getDriverStats } from './js/core/api-client.js';
import { showError } from './js/utils/dom-helpers.js';

try {
    const stats = await getDriverStats('hamilton');
    renderStats(stats);
} catch (error) {
    showError(container, 'Failed to load driver stats', error.message);
}
```

### State Management
```javascript
import { setCurrentResults, getCurrentData } from './js/core/state-manager.js';

// Store results
setCurrentResults(data, 'championship_standings');

// Retrieve later
const data = getCurrentData();
```

---

## File Size Comparison

**Before (monolithic):**
- `app.js`: 920 lines (single file)
- `compare.js`: 529 lines
- **Total:** 1,449 lines

**After (modular):**
- Core: 362 lines (2 files)
- Components: 735 lines (4 files)
- Utils: 507 lines (3 files)
- **Total:** 1,604 lines (9 files)

*Note: Slight increase due to improved documentation, error handling, and separation.*

---

## Performance Considerations

1. **Module Caching**: Browser caches imported modules
2. **API Caching**: Frequently accessed data cached in memory
3. **Lazy Loading**: Import modules only when needed
4. **Debouncing**: User input debounced to prevent excessive calls
5. **Pagination**: Large datasets automatically paginated

---

## Future Improvements

### Phase 2
- Page-specific controllers
- Migrate all HTML pages
- Remove inline JavaScript
- Deprecate old `app.js`

### Phase 3 (Optional)
- TypeScript type definitions (`.d.ts` files)
- Simple bundler for production (optional)
- Service Worker for offline support
- Web Components for better encapsulation

---

## Contributing

When adding new features:

1. **Choose the right location:**
   - API calls → `core/api-client.js`
   - State variables → `core/state-manager.js`
   - Reusable UI → `components/`
   - Helper functions → `utils/`
   - Page logic → `pages/` (Phase 2)

2. **Follow patterns:**
   - Use named exports
   - Add JSDoc comments
   - Handle errors gracefully
   - Write pure functions when possible

3. **Test your changes:**
   - Update `module-test.html` if adding exports
   - Verify imports work
   - Check browser console for errors

---

## Questions?

See:
- `_docs/keyword-first-architecture.md` - App architecture
- `_docs/web-interface.md` - Frontend design
- `.github/copilot-instructions.md` - Development guidelines

---

**Generated:** Phase 1 Complete - December 26, 2024
