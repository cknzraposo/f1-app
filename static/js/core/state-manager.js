/**
 * F1 App State Manager
 * Centralized state management with encapsulation
 */

// Private state object
const state = {
    // Autocomplete data
    allDrivers: [],
    allConstructors: [],
    
    // Autocomplete UI state
    autocompleteTimeout: null,
    autocompleteIndex: -1,
    
    // Pagination state
    currentPage: 1,
    pageSize: 25,
    
    // Results state
    currentData: null,
    currentDataType: null,
    
    // Query history
    queryHistory: [],
    maxHistory: 10
};

// ============================================
// AUTOCOMPLETE DATA
// ============================================

export function getAllDrivers() {
    return state.allDrivers;
}

export function setAllDrivers(drivers) {
    state.allDrivers = drivers;
}

export function getAllConstructors() {
    return state.allConstructors;
}

export function setAllConstructors(constructors) {
    state.allConstructors = constructors;
}

// ============================================
// AUTOCOMPLETE UI STATE
// ============================================

export function getAutocompleteTimeout() {
    return state.autocompleteTimeout;
}

export function setAutocompleteTimeout(timeout) {
    state.autocompleteTimeout = timeout;
}

export function getAutocompleteIndex() {
    return state.autocompleteIndex;
}

export function setAutocompleteIndex(index) {
    state.autocompleteIndex = index;
}

export function incrementAutocompleteIndex() {
    state.autocompleteIndex++;
}

export function decrementAutocompleteIndex() {
    state.autocompleteIndex--;
}

export function resetAutocompleteIndex() {
    state.autocompleteIndex = -1;
}

// ============================================
// PAGINATION STATE
// ============================================

export function getCurrentPage() {
    return state.currentPage;
}

export function setCurrentPage(page) {
    state.currentPage = page;
}

export function getPageSize() {
    return state.pageSize;
}

export function setPageSize(size) {
    state.pageSize = size;
    state.currentPage = 1; // Reset to first page when changing page size
}

// ============================================
// RESULTS STATE
// ============================================

export function getCurrentData() {
    return state.currentData;
}

export function setCurrentData(data) {
    state.currentData = data;
}

export function getCurrentDataType() {
    return state.currentDataType;
}

export function setCurrentDataType(dataType) {
    state.currentDataType = dataType;
}

export function setCurrentResults(data, dataType) {
    state.currentData = data;
    state.currentDataType = dataType;
    state.currentPage = 1; // Reset to first page
}

// ============================================
// QUERY HISTORY
// ============================================

export function getQueryHistory() {
    return [...state.queryHistory]; // Return copy to prevent external mutation
}

export function setQueryHistory(history) {
    state.queryHistory = history;
}

export function addToQueryHistory(query) {
    // Remove duplicates
    state.queryHistory = state.queryHistory.filter(q => q.text !== query);
    
    // Add to beginning
    state.queryHistory.unshift({
        text: query,
        timestamp: new Date().toISOString()
    });
    
    // Limit history size
    if (state.queryHistory.length > state.maxHistory) {
        state.queryHistory = state.queryHistory.slice(0, state.maxHistory);
    }
}

export function clearQueryHistory() {
    state.queryHistory = [];
}

export function getMaxHistory() {
    return state.maxHistory;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Reset all state to initial values
 */
export function resetState() {
    state.allDrivers = [];
    state.allConstructors = [];
    state.autocompleteTimeout = null;
    state.autocompleteIndex = -1;
    state.currentPage = 1;
    state.pageSize = 25;
    state.currentData = null;
    state.currentDataType = null;
    state.queryHistory = [];
}

/**
 * Get snapshot of entire state (for debugging)
 */
export function getStateSnapshot() {
    return {
        driversCount: state.allDrivers.length,
        constructorsCount: state.allConstructors.length,
        autocompleteIndex: state.autocompleteIndex,
        currentPage: state.currentPage,
        pageSize: state.pageSize,
        hasCurrentData: state.currentData !== null,
        currentDataType: state.currentDataType,
        queryHistoryCount: state.queryHistory.length
    };
}
