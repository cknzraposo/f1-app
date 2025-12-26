/**
 * ⚠️ DEPRECATED - DO NOT USE FOR NEW FEATURES
 * 
 * This monolithic file has been replaced by the modular system in /static/js/
 * 
 * Phase 2 Migration Complete (December 26, 2025):
 * - All 8 pages now use dedicated controllers in /static/js/pages/
 * - Shared functionality extracted to /static/js/core/ and /static/js/components/
 * - This file remains for reference and rollback capability only
 * 
 * New Architecture:
 * - Landing page: index.html → js/pages/index.js
 * - Query results: query-results.html → js/pages/results.js
 * - Driver profiles: drivers.html → js/pages/driver-profile.js
 * - Driver list: drivers-list.html → js/pages/driver-list.js
 * - Constructor profiles: constructor.html → js/pages/constructor-profile.js
 * - Constructor list: constructors-list.html → js/pages/constructor-list.js
 * - Season browser: results.html → js/pages/season-browser.js
 * - Driver comparison: compare.html → compare.js (refactored)
 * 
 * Documentation: /static/js/PHASE2-FINAL.md
 * 
 * @deprecated Use /static/js/pages/ controllers instead
 */

// ============================================================================
// LEGACY CODE BELOW - Use /static/js/ modules for new features
// ============================================================================

/**
 * F1 Stats - Modern JavaScript Application
 * Handles search, autocomplete, table rendering, and pagination
 */

// ============================================
// GLOBAL STATE
// ============================================
let autocompleteTimeout;
let autocompleteIndex = -1;
let allDrivers = [];
let allConstructors = [];
let currentPage = 1;
let pageSize = 25;
let currentData = null;
let currentDataType = null;
let queryHistory = [];
const MAX_HISTORY = 10;

// ============================================
// QUERY HISTORY MANAGEMENT
// ============================================

function loadQueryHistory() {
    try {
        const stored = localStorage.getItem('f1QueryHistory');
        if (stored) {
            queryHistory = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Failed to load query history:', error);
        queryHistory = [];
    }
}

function saveQueryToHistory(query) {
    // Remove duplicates
    queryHistory = queryHistory.filter(q => q.text !== query);
    
    // Add to beginning
    queryHistory.unshift({
        text: query,
        timestamp: new Date().toISOString()
    });
    
    // Limit history size
    if (queryHistory.length > MAX_HISTORY) {
        queryHistory = queryHistory.slice(0, MAX_HISTORY);
    }
    
    // Save to localStorage
    try {
        localStorage.setItem('f1QueryHistory', JSON.stringify(queryHistory));
    } catch (error) {
        console.error('Failed to save query history:', error);
    }
}

function showQueryHistory() {
    const historyEl = document.getElementById('queryHistory');
    if (!historyEl || queryHistory.length === 0) return;
    
    historyEl.innerHTML = `
        <div class="history-header">
            <span>Recent Queries</span>
            <button class="clear-history" onclick="clearQueryHistory()">Clear</button>
        </div>
        ${queryHistory.slice(0, 5).map(q => `
            <div class="history-item" onclick="setQuery('${q.text.replace(/'/g, "\\'")}')">
                <svg class="history-icon" viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M13,3A9,9 0 0,0 4,12H1L4.89,15.89L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3Z"/>
                </svg>
                ${q.text}
            </div>
        `).join('')}
    `;
    historyEl.classList.add('active');
}

function hideQueryHistory() {
    const historyEl = document.getElementById('queryHistory');
    if (historyEl) {
        historyEl.classList.remove('active');
    }
}

function clearQueryHistory() {
    queryHistory = [];
    localStorage.removeItem('f1QueryHistory');
    hideQueryHistory();
}

// ============================================
// SMART QUERY SUGGESTIONS
// ============================================

function showSmartSuggestions(input) {
    const suggestionsEl = document.getElementById('suggestions');
    if (!suggestionsEl) return;
    
    const lowerInput = input.toLowerCase();
    const suggestions = [];
    
    // Year-based suggestions
    if (/\d{4}/.test(input)) {
        const year = input.match(/\d{4}/)[0];
        if (year >= 1984 && year <= 2024) {
            suggestions.push(`Who won the ${year} championship?`);
            suggestions.push(`${year} standings`);
            suggestions.push(`${year} race winners`);
        }
    }
    
    // Driver-based suggestions
    const driverMatch = allDrivers.find(d => 
        lowerInput.includes(d.familyName.toLowerCase()) ||
        lowerInput.includes(`${d.givenName} ${d.familyName}`.toLowerCase())
    );
    if (driverMatch) {
        const fullName = `${driverMatch.givenName} ${driverMatch.familyName}`;
        suggestions.push(`How many wins does ${fullName} have?`);
        suggestions.push(`${fullName} career stats`);
        suggestions.push(`${fullName} championships`);
    }
    
    // Constructor-based suggestions
    const constructorMatch = allConstructors.find(c =>
        lowerInput.includes(c.name.toLowerCase())
    );
    if (constructorMatch) {
        suggestions.push(`${constructorMatch.name} statistics`);
        suggestions.push(`${constructorMatch.name} championships`);
    }
    
    // Comparison suggestions
    if (lowerInput.includes('compare') || lowerInput.includes('vs') || lowerInput.includes('versus')) {
        if (!driverMatch) {
            suggestions.push('Compare Hamilton vs Verstappen');
            suggestions.push('Compare Vettel vs Alonso');
        }
    }
    
    // Show suggestions if any
    if (suggestions.length > 0 && input.length > 3) {
        suggestionsEl.innerHTML = `
            <div class="suggestions-header">Suggested queries:</div>
            ${suggestions.slice(0, 3).map(s => `
                <div class="suggestion-item" onclick="setQuery('${s.replace(/'/g, "\\'")}')">
                    <svg class="suggestion-icon" viewBox="0 0 24 24" width="16" height="16">
                        <path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                    </svg>
                    ${s}
                </div>
            `).join('')}
        `;
        suggestionsEl.classList.add('active');
    } else {
        suggestionsEl.classList.remove('active');
    }
}

// ============================================
// INITIALIZATION
// ============================================

// Load drivers and constructors for autocomplete
async function loadAutocompleteData() {
    try {
        // Load all drivers
        const driversResponse = await fetch('/api/drivers');
        const driversData = await driversResponse.json();
        allDrivers = driversData.MRData?.DriverTable?.Drivers || [];
        
        // Load all constructors
        const constructorsResponse = await fetch('/api/constructors');
        const constructorsData = await constructorsResponse.json();
        allConstructors = constructorsData.MRData?.ConstructorTable?.Constructors || [];
    } catch (error) {
        console.error('Failed to load autocomplete data:', error);
    }
}

// Load on page start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadAutocompleteData();
        loadQueryHistory();
    });
} else {
    loadAutocompleteData();
    loadQueryHistory();
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

function setQuery(query) {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = query;
    hideAutocomplete();
    hideQueryHistory();
    handleSearch();
}

function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (!query) return;
    
    // Save to history
    saveQueryToHistory(query);
    
    // Redirect to results page with query parameter
    window.location.href = `/static/results.html?q=${encodeURIComponent(query)}`;
}

// Handle Enter key on search input
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            const autocompleteEl = document.getElementById('autocomplete');
            const isAutocompleteOpen = autocompleteEl && autocompleteEl.classList.contains('active');
            
            if (e.key === 'Enter') {
                if (isAutocompleteOpen && autocompleteIndex >= 0) {
                    // Select autocomplete item
                    const items = autocompleteEl.querySelectorAll('.autocomplete-item');
                    if (items[autocompleteIndex]) {
                        items[autocompleteIndex].click();
                    }
                } else {
                    // Execute search
                    handleSearch();
                }
            } else if (e.key === 'ArrowDown') {
                if (isAutocompleteOpen) {
                    e.preventDefault();
                    navigateAutocomplete(1);
                }
            } else if (e.key === 'ArrowUp') {
                if (isAutocompleteOpen) {
                    e.preventDefault();
                    navigateAutocomplete(-1);
                }
            } else if (e.key === 'Escape') {
                hideAutocomplete();
            }
        });
        
        // Trigger autocomplete on input
        searchInput.addEventListener('input', (e) => {
            const value = e.target.value;
            handleAutocompleteInput(value);
            
            // Show smart suggestions
            if (value.length > 2) {
                showSmartSuggestions(value);
            } else {
                document.getElementById('suggestions')?.classList.remove('active');
            }
        });
        
        // Show history on focus if input is empty
        searchInput.addEventListener('focus', (e) => {
            if (!e.target.value && queryHistory.length > 0) {
                showQueryHistory();
            }
        });
        
        // Hide autocomplete/suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                hideAutocomplete();
                hideQueryHistory();
                document.getElementById('suggestions')?.classList.remove('active');
            }
        });
    }
});

// ============================================
// AUTOCOMPLETE FUNCTIONALITY
// ============================================

function handleAutocompleteInput(value) {
    clearTimeout(autocompleteTimeout);
    
    if (!value || value.length < 2) {
        hideAutocomplete();
        return;
    }
    
    // Debounce: wait 300ms before showing autocomplete
    autocompleteTimeout = setTimeout(() => {
        showAutocomplete(value);
    }, 300);
}

function showAutocomplete(query) {
    const autocompleteEl = document.getElementById('autocomplete');
    if (!autocompleteEl) return;
    
    const lowerQuery = query.toLowerCase();
    const results = [];
    
    // Search drivers
    allDrivers.forEach(driver => {
        const fullName = `${driver.givenName} ${driver.familyName}`.toLowerCase();
        const familyName = driver.familyName.toLowerCase();
        
        if (fullName.includes(lowerQuery) || familyName.includes(lowerQuery)) {
            results.push({
                type: 'driver',
                label: `${driver.givenName} ${driver.familyName}`,
                sublabel: `${driver.nationality}${driver.permanentNumber ? ' • #' + driver.permanentNumber : ''}`,
                value: driver.driverId
            });
        }
    });
    
    // Search constructors (client-side filtering)
    allConstructors.forEach(constructor => {
        const name = constructor.name.toLowerCase();
        
        if (name.includes(lowerQuery)) {
            results.push({
                type: 'constructor',
                label: constructor.name,
                sublabel: constructor.nationality,
                value: constructor.constructorId
            });
        }
    });
    
    // Limit to 10 results
    const limitedResults = results.slice(0, 10);
    
    if (limitedResults.length === 0) {
        hideAutocomplete();
        return;
    }
    
    // Render autocomplete
    autocompleteEl.innerHTML = limitedResults.map((result, index) => `
        <div class="autocomplete-item" data-index="${index}" data-value="${result.value}" data-type="${result.type}">
            <div class="autocomplete-main">${result.label}</div>
            <div class="autocomplete-sub">${result.sublabel}</div>
        </div>
    `).join('');
    
    // Add click handlers
    autocompleteEl.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            selectAutocompleteItem(item.dataset.value, item.dataset.type);
        });
    });
    
    autocompleteEl.classList.add('active');
    autocompleteIndex = -1;
}

function hideAutocomplete() {
    const autocompleteEl = document.getElementById('autocomplete');
    if (autocompleteEl) {
        autocompleteEl.classList.remove('active');
        autocompleteEl.innerHTML = '';
    }
    autocompleteIndex = -1;
}

function navigateAutocomplete(direction) {
    const autocompleteEl = document.getElementById('autocomplete');
    if (!autocompleteEl) return;
    
    const items = autocompleteEl.querySelectorAll('.autocomplete-item');
    if (items.length === 0) return;
    
    // Remove previous selection
    if (autocompleteIndex >= 0 && autocompleteIndex < items.length) {
        items[autocompleteIndex].classList.remove('selected');
    }
    
    // Update index
    autocompleteIndex += direction;
    if (autocompleteIndex < 0) autocompleteIndex = items.length - 1;
    if (autocompleteIndex >= items.length) autocompleteIndex = 0;
    
    // Add new selection
    items[autocompleteIndex].classList.add('selected');
    items[autocompleteIndex].scrollIntoView({ block: 'nearest' });
}

function selectAutocompleteItem(value, type) {
    const searchInput = document.getElementById('searchInput');
    
    if (type === 'driver') {
        searchInput.value = `Tell me about ${value} stats`;
    } else if (type === 'constructor') {
        searchInput.value = `Tell me about ${value}`;
    }
    
    hideAutocomplete();
    handleSearch();
}

// ============================================
// RESULTS PAGE FUNCTIONALITY
// ============================================

function initResultsPage() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    
    if (!query) {
        showError('No query provided');
        return;
    }
    
    // Display query
    const queryDisplay = document.getElementById('queryDisplay');
    if (queryDisplay) {
        queryDisplay.textContent = query;
    }
    
    // Execute query
    executeQuery(query);
}

async function executeQuery(query) {
    const resultsContent = document.getElementById('resultsContent');
    const startTime = performance.now();
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const endTime = performance.now();
        const processingTime = Math.round(endTime - startTime);
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || result.error || 'Query failed');
        }
        
        if (!result.success) {
            throw new Error(result.error || 'Query returned unsuccessful');
        }
        
        // Store data globally
        currentData = result.data;
        currentDataType = result.dataType;
        currentPage = 1;
        
        // Show processing info
        showProcessingInfo(processingTime, result.action || 'keyword_parser', result.dataType);
        
        // Render results
        renderResults(result.data, result.dataType);
        
    } catch (error) {
        showError(error.message);
    }
}

function showProcessingInfo(timeMs, source, dataType) {
    const resultsContent = document.getElementById('resultsContent');
    
    // Determine source label and color
    let sourceLabel = '⚡ Keyword Parser';
    let sourceColor = '#10b981'; // green
    
    if (source.includes('llm')) {
        sourceLabel = '🤖 LLM';
        sourceColor = '#3b82f6'; // blue
    }
    
    // Create processing info banner
    const infoBanner = `
        <div class="processing-info" style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; font-size: 0.875rem;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="color: ${sourceColor}; font-weight: 600;">${sourceLabel}</span>
                <span style="color: #6b7280;">•</span>
                <span style="color: #374151;">
                    <strong>${timeMs}ms</strong> response time
                </span>
                <span style="color: #6b7280;">•</span>
                <span style="color: #374151;">
                    Type: <strong>${dataType.replace(/_/g, ' ')}</strong>
                </span>
            </div>
            <div style="color: #9ca3af; font-size: 0.75rem;">
                ${new Date().toLocaleTimeString()}
            </div>
        </div>
    `;
    
    resultsContent.insertAdjacentHTML('afterbegin', infoBanner);
}

function showError(message) {
    const resultsContent = document.getElementById('resultsContent');
    if (resultsContent) {
        resultsContent.innerHTML = `
            <div class="error">
                <div class="error-title">⚠️ Error</div>
                <p>${message}</p>
            </div>
        `;
    }
}

function showEmpty(message = 'No results found') {
    const resultsContent = document.getElementById('resultsContent');
    if (resultsContent) {
        resultsContent.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🏁</div>
                <div class="empty-title">${message}</div>
                <p class="empty-text">Try a different query</p>
            </div>
        `;
    }
}

// ============================================
// TABLE RENDERING
// ============================================

const TABLE_CONFIGS = {
    championship_standings: {
        columns: [
            { key: 'position', label: 'Pos', width: '60px', align: 'center' },
            { key: 'name', label: 'Driver', width: 'auto' },
            { key: 'constructor', label: 'Team', width: 'auto' },
            { key: 'nationality', label: 'Nation', width: '100px' },
            { key: 'points', label: 'Points', width: '80px', align: 'right', highlight: true },
            { key: 'wins', label: 'Wins', width: '60px', align: 'center' }
        ],
        sortable: true,
        paginate: false
    },
    driver_stats: {
        format: 'key-value',
        paginate: false
    },
    constructor_stats: {
        format: 'key-value',
        paginate: false
    },
    season_winners: {
        columns: [
            { key: 'round', label: 'Rd', width: '50px', align: 'center' },
            { key: 'raceName', label: 'Grand Prix', width: 'auto' },
            { key: 'date', label: 'Date', width: '100px' },
            { key: 'driver.name', label: 'Winner', width: 'auto', highlight: true },
            { key: 'constructor.name', label: 'Team', width: '150px' },
            { key: 'grid', label: 'Grid', width: '60px', align: 'center' }
        ],
        sortable: true,
        paginate: true
    },
    race_results: {
        columns: [
            { key: 'position', label: 'Pos', width: '50px', align: 'center' },
            { key: 'Driver.givenName', label: 'First', width: 'auto' },
            { key: 'Driver.familyName', label: 'Last', width: 'auto', highlight: true },
            { key: 'Constructor.name', label: 'Team', width: '150px' },
            { key: 'grid', label: 'Grid', width: '60px', align: 'center' },
            { key: 'points', label: 'Pts', width: '60px', align: 'right' },
            { key: 'status', label: 'Status', width: '120px' }
        ],
        sortable: false,
        paginate: false
    },
    driver_search: {
        columns: [
            { key: 'fullName', label: 'Name', width: 'auto', highlight: true },
            { key: 'nationality', label: 'Nationality', width: '120px' },
            { key: 'dateOfBirth', label: 'Born', width: '100px' },
            { key: 'permanentNumber', label: 'Number', width: '80px', align: 'center' }
        ],
        sortable: true,
        paginate: true
    },
    head_to_head: {
        format: 'head-to-head',
        paginate: true
    }
};

function renderResults(data, dataType) {
    console.log('Rendering results:', { dataType, data });
    
    const config = TABLE_CONFIGS[dataType];
    
    if (!config) {
        console.warn(`No config found for dataType: ${dataType}. Available types:`, Object.keys(TABLE_CONFIGS));
        
        // Try to intelligently detect the data type
        if (data.statistics) {
            console.log('Detected statistics data, using key-value format');
            renderKeyValueTable(data, dataType);
        } else if (data.driverStandings || data.constructorStandings) {
            console.log('Detected standings data');
            renderDataTable(data, TABLE_CONFIGS.championship_standings);
        } else if (data.MRData?.DriverTable?.Drivers) {
            console.log('Detected driver search data');
            renderDataTable(data, TABLE_CONFIGS.driver_search);
        } else if (data.races || Array.isArray(data)) {
            console.log('Detected array/races data');
            // Try to infer the right table config based on data structure
            const firstItem = Array.isArray(data) ? data[0] : data.races?.[0];
            if (firstItem?.raceName && firstItem?.driver) {
                renderDataTable(data, TABLE_CONFIGS.season_winners);
            } else {
                // Fallback to JSON
                const resultsContent = document.getElementById('resultsContent');
                resultsContent.innerHTML = `
                    <div class="results-header">
                        <div class="results-title">Results</div>
                    </div>
                    <pre style="color: #ddd; overflow-x: auto; background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px;">${JSON.stringify(data, null, 2)}</pre>
                `;
            }
        } else {
            // Default: show JSON
            const resultsContent = document.getElementById('resultsContent');
            resultsContent.innerHTML = `
                <div class="results-header">
                    <div class="results-title">Results</div>
                </div>
                <pre style="color: #ddd; overflow-x: auto; background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px;">${JSON.stringify(data, null, 2)}</pre>
            `;
        }
        return;
    }
    
    if (config.format === 'key-value') {
        renderKeyValueTable(data, dataType);
    } else if (config.format === 'head-to-head') {
        renderHeadToHead(data);
    } else {
        renderDataTable(data, config);
    }
}

function renderKeyValueTable(data, dataType) {
    const resultsContent = document.getElementById('resultsContent');
    
    let stats = {};
    if (dataType === 'driver_stats') {
        stats = data.statistics || {};
    } else if (dataType === 'constructor_stats') {
        stats = data.statistics || {};
    }
    
    const rows = [
        ['Total Races', stats.totalRaces || 0],
        ['Wins', stats.wins || 0],
        ['Podiums', stats.podiums || 0],
        ['Pole Positions', stats.polePositions || 0],
        ['Fastest Laps', stats.fastestLaps || 0],
        ['Total Points', stats.totalPoints || 0],
        ['DNFs', stats.dnfs || 0]
    ];
    
    resultsContent.innerHTML = `
        <div class="results-header">
            <div class="results-title">Career Statistics</div>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Statistic</th>
                        <th class="text-right">Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(([stat, value]) => `
                        <tr>
                            <td>${stat}</td>
                            <td class="text-right highlight">${value}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderHeadToHead(data) {
    const resultsContent = document.getElementById('resultsContent');
    
    const driver1Stats = data.driver1 || {};
    const driver2Stats = data.driver2 || {};
    const headToHead = data.headToHead || {};
    
    resultsContent.innerHTML = `
        <div class="results-header">
            <div class="results-title">Head-to-Head Comparison</div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: #e10600; margin-bottom: 15px;">${driver1Stats.name || 'Driver 1'}</h3>
                <p><strong>Wins:</strong> ${driver1Stats.wins || 0}</p>
                <p><strong>Podiums:</strong> ${driver1Stats.podiums || 0}</p>
                <p><strong>Points:</strong> ${driver1Stats.totalPoints || 0}</p>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="color: #e10600; margin-bottom: 15px;">${driver2Stats.name || 'Driver 2'}</h3>
                <p><strong>Wins:</strong> ${driver2Stats.wins || 0}</p>
                <p><strong>Podiums:</strong> ${driver2Stats.podiums || 0}</p>
                <p><strong>Points:</strong> ${driver2Stats.totalPoints || 0}</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-bottom: 30px; font-size: 1.1em;">
            <strong>Races Together:</strong> ${headToHead.racesTogetherCount || 0} | 
            <strong style="color: #4ade80;">${driver1Stats.name}: ${headToHead.driver1Better || 0}</strong> | 
            <strong style="color: #f87171;">${driver2Stats.name}: ${headToHead.driver2Better || 0}</strong>
        </div>
        
        ${headToHead.races && headToHead.races.length > 0 ? renderDataTable(headToHead.races, {
            columns: [
                { key: 'season', label: 'Year', width: '70px', align: 'center' },
                { key: 'raceName', label: 'Grand Prix', width: 'auto' },
                { key: 'driver1Position', label: `${driver1Stats.name} Pos`, width: '100px', align: 'center' },
                { key: 'driver2Position', label: `${driver2Stats.name} Pos`, width: '100px', align: 'center' },
                { key: 'better', label: 'Better', width: '100px', align: 'center', highlight: true }
            ],
            sortable: true,
            paginate: true
        }, false) : '<p style="text-align: center; color: #888;">No race data available</p>'}
    `;
}

function renderDataTable(data, config, wrapInContainer = true) {
    const resultsContent = document.getElementById('resultsContent');
    
    // Handle different data structures
    let rows = [];
    
    if (Array.isArray(data)) {
        rows = data;
    } else if (data.driverStandings) {
        rows = data.driverStandings;
    } else if (data.MRData?.DriverTable?.Drivers) {
        rows = data.MRData.DriverTable.Drivers;
        // Add fullName for display
        rows = rows.map(d => ({...d, fullName: `${d.givenName} ${d.familyName}`}));
    } else if (data.races) {
        rows = data.races;
    }
    
    if (!rows || rows.length === 0) {
        showEmpty();
        return '';
    }
    
    // Pagination
    const shouldPaginate = config.paginate && rows.length > 25;
    const totalItems = rows.length;
    const totalPages = shouldPaginate ? Math.ceil(totalItems / pageSize) : 1;
    
    let paginatedRows = rows;
    if (shouldPaginate) {
        const start = (currentPage - 1) * pageSize;
        const end = start + pageSize;
        paginatedRows = rows.slice(start, end);
    }
    
    // Build table HTML
    const tableHTML = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        ${config.columns.map(col => `
                            <th class="${col.align ? 'text-' + col.align : ''} ${config.sortable ? 'sortable' : ''}"
                                ${col.width ? `style="width: ${col.width}"` : ''}>
                                ${col.label}
                            </th>
                        `).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${paginatedRows.map((row, index) => {
                        const podiumClass = row.position <= 3 ? `podium-${row.position}` : '';
                        return `
                            <tr class="${podiumClass}">
                                ${config.columns.map(col => {
                                    let value = getNestedValue(row, col.key);
                                    if (value === undefined || value === null) value = 'N/A';
                                    
                                    // Make driver names clickable
                                    if (isDriverColumn(col.key) && value !== 'N/A') {
                                        const driverId = getDriverId(row, col.key);
                                        if (driverId) {
                                            value = createDriverLink(value, driverId);
                                        }
                                    }
                                    
                                    return `<td class="${col.align ? 'text-' + col.align : ''} ${col.highlight ? 'highlight' : ''}">${value}</td>`;
                                }).join('')}
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
        
        ${shouldPaginate ? `
            <div class="pagination">
                <div class="pagination-info">
                    Showing ${(currentPage - 1) * pageSize + 1}-${Math.min(currentPage * pageSize, totalItems)} of ${totalItems}
                </div>
                <div class="pagination-controls">
                    <button class="pagination-button" onclick="changePage(1)" ${currentPage === 1 ? 'disabled' : ''}>First</button>
                    <button class="pagination-button" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Previous</button>
                    <span style="color: #888; padding: 0 10px;">Page ${currentPage} of ${totalPages}</span>
                    <button class="pagination-button" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>
                    <button class="pagination-button" onclick="changePage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''}>Last</button>
                    <select class="page-size-selector" onchange="changePageSize(this.value)">
                        <option value="25" ${pageSize === 25 ? 'selected' : ''}>25 per page</option>
                        <option value="50" ${pageSize === 50 ? 'selected' : ''}>50 per page</option>
                        <option value="100" ${pageSize === 100 ? 'selected' : ''}>100 per page</option>
                    </select>
                </div>
            </div>
        ` : ''}
    `;
    
    if (wrapInContainer) {
        resultsContent.innerHTML = `
            <div class="results-header">
                <div class="results-title">Results</div>
                <div class="results-count">${totalItems} ${totalItems === 1 ? 'item' : 'items'}</div>
            </div>
            ${tableHTML}
        `;
    } else {
        return tableHTML;
    }
}

// Helper function to create driver link
function createDriverLink(driverName, driverId) {
    if (!driverName || driverName === 'N/A') return driverName;
    if (!driverId) return driverName;
    return `<a href="/static/drivers.html?id=${driverId}" class="driver-link" style="color: #60a5fa; text-decoration: none; font-weight: 600; transition: color 0.2s;" onmouseover="this.style.color='#93c5fd'" onmouseout="this.style.color='#60a5fa'">${driverName}</a>`;
}

// Helper function to check if column contains driver info
function isDriverColumn(columnKey) {
    const driverKeys = ['name', 'fullName', 'driver', 'driver.name', 'Driver.givenName', 'Driver.familyName'];
    return driverKeys.includes(columnKey);
}

// Helper function to extract driver ID from row data
function getDriverId(row, columnKey) {
    // Try multiple possible locations for driver ID
    if (row.driverId) return row.driverId;
    if (row.Driver?.driverId) return row.Driver.driverId;
    if (row.driver?.driverId) return row.driver.driverId;
    
    // If we have a name but no ID, try to find it from the global drivers list
    let driverName = null;
    if (columnKey === 'name' || columnKey === 'fullName') {
        driverName = row.name || row.fullName;
    } else if (columnKey === 'driver.name') {
        driverName = row.driver?.name;
    } else if (columnKey === 'Driver.familyName') {
        driverName = `${row.Driver?.givenName} ${row.Driver?.familyName}`;
    }
    
    if (driverName && allDrivers.length > 0) {
        const driver = allDrivers.find(d => {
            const fullName = `${d.givenName} ${d.familyName}`;
            return fullName === driverName || d.familyName === driverName;
        });
        if (driver) return driver.driverId;
    }
    
    return null;
}

function getNestedValue(obj, path) {
    if (path.includes('.')) {
        const parts = path.split('.');
        let value = obj;
        for (const part of parts) {
            value = value?.[part];
        }
        return value;
    }
    return obj[path];
}

function changePage(page) {
    currentPage = page;
    renderResults(currentData, currentDataType);
}

function changePageSize(size) {
    pageSize = parseInt(size);
    currentPage = 1;
    renderResults(currentData, currentDataType);
}
