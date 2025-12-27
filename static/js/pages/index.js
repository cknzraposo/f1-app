/**
 * Index Page Controller
 * Handles landing page functionality: search, autocomplete, history, suggestions
 */

import { getDrivers, getConstructors, prefetchCommonData } from '../core/api-client.js';
import { setAllDrivers, setAllConstructors, getAllDrivers } from '../core/state-manager.js';
import { initAutocomplete, hideAutocomplete } from '../components/autocomplete.js';
import { initQueryHistory, saveQueryToHistory, hideQueryHistory } from '../components/query-history.js';
import { initSuggestions, hideSuggestions } from '../components/suggestions.js';

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize the landing page
 */
async function init() {
    console.log('Initializing landing page...');
    
    // Load autocomplete data
    await loadAutocompleteData();
    
    // Initialize components
    setupSearch();
    setupAutocomplete();
    setupQueryHistory();
    setupSuggestions();
    setupChips();
    
    console.log('Landing page initialized');
}

/**
 * Load drivers and constructors for autocomplete
 */
async function loadAutocompleteData() {
    try {
        console.log('Loading autocomplete data...');
        
        // Use prefetch to load both in parallel
        await prefetchCommonData();
        
        // Get the cached data
        const driversData = await getDrivers();
        const constructorsData = await getConstructors();
        
        // Extract arrays from response
        const drivers = driversData.MRData?.DriverTable?.Drivers || [];
        const constructors = constructorsData.MRData?.ConstructorTable?.Constructors || [];
        
        // Store in state
        setAllDrivers(drivers);
        setAllConstructors(constructors);
        
        console.log(`Loaded ${drivers.length} drivers and ${constructors.length} constructors`);
    } catch (error) {
        console.error('Failed to load autocomplete data:', error);
    }
}

// ============================================
// SEARCH SETUP
// ============================================

/**
 * Setup search input and form handlers
 */
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (!searchInput) {
        console.error('Search input not found');
        return;
    }
    
    // Enter key handler
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSearch();
        }
    });
    
    // Click outside to hide dropdowns
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            const autocompleteEl = document.getElementById('autocomplete');
            const historyEl = document.getElementById('queryHistory');
            const suggestionsEl = document.getElementById('suggestions');
            
            hideAutocomplete(autocompleteEl);
            hideQueryHistory(historyEl);
            hideSuggestions(suggestionsEl);
        }
    });
}

/**
 * Handle search submission - redirect to driver details page
 */
function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput?.value.trim();
    
    if (!query) {
        console.warn('Empty query');
        return;
    }
    
    console.log('Searching for driver:', query);
    
    // Save to history
    saveQueryToHistory(query);
    
    // Search for matching driver
    const drivers = getAllDrivers();
    const lowerQuery = query.toLowerCase();
    
    // Find matching driver
    let matchedDriver = null;
    
    for (const driver of drivers) {
        const fullName = `${driver.givenName} ${driver.familyName}`.toLowerCase();
        const familyName = driver.familyName.toLowerCase();
        const givenName = driver.givenName.toLowerCase();
        
        // Exact match or contains match
        if (fullName === lowerQuery || 
            familyName === lowerQuery || 
            givenName === lowerQuery ||
            fullName.includes(lowerQuery)) {
            matchedDriver = driver;
            break;
        }
    }
    
    if (matchedDriver) {
        // Redirect to driver details page
        window.location.href = `/static/drivers.html?id=${matchedDriver.driverId}`;
    } else {
        // No match found - could show error or redirect to drivers list
        alert('Driver not found. Please try another search or use the autocomplete suggestions.');
        searchInput.value = '';
    }
}

// Make handleSearch global for onclick attributes
window.handleSearch = handleSearch;

// ============================================
// AUTOCOMPLETE SETUP
// ============================================

/**
 * Setup autocomplete component
 */
function setupAutocomplete() {
    const searchInput = document.getElementById('searchInput');
    const autocompleteEl = document.getElementById('autocomplete');
    
    if (!searchInput || !autocompleteEl) {
        console.error('Autocomplete elements not found');
        return;
    }
    
    initAutocomplete(searchInput, autocompleteEl, (value, type) => {
        // When autocomplete item is selected (value is driverId)
        if (type === 'driver') {
            // Redirect directly to driver details page
            window.location.href = `/static/drivers.html?id=${value}`;
        }
    });
}

// ============================================
// QUERY HISTORY SETUP
// ============================================

/**
 * Setup query history component
 */
function setupQueryHistory() {
    const searchInput = document.getElementById('searchInput');
    const historyEl = document.getElementById('queryHistory');
    
    if (!searchInput || !historyEl) {
        console.error('Query history elements not found');
        return;
    }
    
    initQueryHistory(searchInput, historyEl, (query) => {
        // When history item is selected
        searchInput.value = query;
        handleSearch();
    });
}

// ============================================
// SUGGESTIONS SETUP
// ============================================

/**
 * Setup suggestions component
 */
function setupSuggestions() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsEl = document.getElementById('suggestions');
    
    if (!searchInput || !suggestionsEl) {
        console.error('Suggestions elements not found');
        return;
    }
    
    initSuggestions(searchInput, suggestionsEl, (query) => {
        // When suggestion is selected
        searchInput.value = query;
        handleSearch();
    });
}

// ============================================
// CHIP SETUP
// ============================================

/**
 * Setup query chips functionality
 */
function setupChips() {
    // Make setQuery function available globally for onclick attributes
    window.setQuery = function(query) {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = query;
            hideAutocomplete(document.getElementById('autocomplete'));
            hideQueryHistory(document.getElementById('queryHistory'));
            hideSuggestions(document.getElementById('suggestions'));
            handleSearch();
        }
    };
}

// ============================================
// START APPLICATION
// ============================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
