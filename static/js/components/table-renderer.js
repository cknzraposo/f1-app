/**
 * Table Renderer Component
 * Handles rendering of various F1 data table types with pagination
 */

import { getAllDrivers } from '../core/state-manager.js';
import { 
    getNestedValue, 
    isDriverColumn, 
    getDriverId, 
    createDriverLink,
    getPodiumClass,
    escapeHtml
} from '../utils/formatters.js';
import { 
    paginateData, 
    renderPaginationControls 
} from '../utils/pagination.js';

// ============================================
// TABLE CONFIGURATIONS
// ============================================

export const TABLE_CONFIGS = {
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

// ============================================
// MAIN RENDER FUNCTIONS
// ============================================

/**
 * Render results based on data type
 * @param {*} data - Data to render
 * @param {string} dataType - Type of data (matches TABLE_CONFIGS keys)
 * @param {HTMLElement} container - Container element
 * @param {Object} options - Additional rendering options
 */
export function renderResults(data, dataType, container, options = {}) {
    if (!container) {
        console.error('Table Renderer: Container element required');
        return;
    }
    
    console.log('Rendering results:', { dataType, data });
    
    const config = TABLE_CONFIGS[dataType];
    
    if (!config) {
        console.warn(`No config found for dataType: ${dataType}`);
        renderAutoDetect(data, container, options);
        return;
    }
    
    if (config.format === 'key-value') {
        renderKeyValueTable(data, dataType, container, options);
    } else if (config.format === 'head-to-head') {
        renderHeadToHead(data, container, options);
    } else {
        renderDataTable(data, config, container, options);
    }
}

/**
 * Render key-value statistics table
 */
function renderKeyValueTable(data, dataType, container, options = {}) {
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
    
    container.innerHTML = `
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

/**
 * Render head-to-head comparison
 */
function renderHeadToHead(data, container, options = {}) {
    const driver1Stats = data.driver1 || {};
    const driver2Stats = data.driver2 || {};
    const headToHead = data.headToHead || {};
    
    let racesTableHTML = '';
    if (headToHead.races && headToHead.races.length > 0) {
        const tableConfig = {
            columns: [
                { key: 'season', label: 'Year', width: '70px', align: 'center' },
                { key: 'raceName', label: 'Grand Prix', width: 'auto' },
                { key: 'driver1Position', label: `${driver1Stats.name} Pos`, width: '100px', align: 'center' },
                { key: 'driver2Position', label: `${driver2Stats.name} Pos`, width: '100px', align: 'center' },
                { key: 'better', label: 'Better', width: '100px', align: 'center', highlight: true }
            ],
            sortable: true,
            paginate: true
        };
        
        const tempContainer = document.createElement('div');
        renderDataTable(headToHead.races, tableConfig, tempContainer, { wrapInHeader: false });
        racesTableHTML = tempContainer.innerHTML;
    } else {
        racesTableHTML = '<p style="text-align: center; color: #888;">No race data available</p>';
    }
    
    container.innerHTML = `
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
        
        ${racesTableHTML}
    `;
}

/**
 * Render data table with columns
 */
function renderDataTable(data, config, container, options = {}) {
    const { wrapInHeader = true } = options;
    
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
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🏁</div>
                <div class="empty-title">No results found</div>
                <p class="empty-text">Try a different query</p>
            </div>
        `;
        return;
    }
    
    // Pagination
    const shouldPaginate = config.paginate && rows.length > 25;
    const totalItems = rows.length;
    
    let paginatedRows = rows;
    let paginationHTML = '';
    
    if (shouldPaginate) {
        const { data: paginated, pagination } = paginateData(rows);
        paginatedRows = paginated;
        paginationHTML = renderPaginationControls(pagination);
    }
    
    // Build table HTML
    const tableHTML = buildTableHTML(paginatedRows, config);
    
    // Wrap in header if requested
    if (wrapInHeader) {
        container.innerHTML = `
            <div class="results-header">
                <div class="results-title">Results</div>
                <div class="results-count">${totalItems} ${totalItems === 1 ? 'item' : 'items'}</div>
            </div>
            ${tableHTML}
            ${paginationHTML}
        `;
    } else {
        container.innerHTML = tableHTML + paginationHTML;
    }
}

/**
 * Build table HTML from rows and config
 */
function buildTableHTML(rows, config) {
    return `
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
                    ${rows.map((row, index) => {
                        const podiumClass = row.position <= 3 ? getPodiumClass(row.position) : '';
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
    `;
}

/**
 * Auto-detect data type and render appropriately
 */
function renderAutoDetect(data, container, options = {}) {
    console.log('Auto-detecting data type for rendering');
    
    // Try to intelligently detect the data type
    if (data.statistics) {
        console.log('Detected statistics data, using key-value format');
        renderKeyValueTable(data, 'driver_stats', container, options);
    } else if (data.driverStandings || data.constructorStandings) {
        console.log('Detected standings data');
        renderDataTable(data, TABLE_CONFIGS.championship_standings, container, options);
    } else if (data.MRData?.DriverTable?.Drivers) {
        console.log('Detected driver search data');
        renderDataTable(data, TABLE_CONFIGS.driver_search, container, options);
    } else if (data.races || Array.isArray(data)) {
        console.log('Detected array/races data');
        const firstItem = Array.isArray(data) ? data[0] : data.races?.[0];
        if (firstItem?.raceName && firstItem?.driver) {
            renderDataTable(data, TABLE_CONFIGS.season_winners, container, options);
        } else {
            // Fallback to JSON
            container.innerHTML = `
                <div class="results-header">
                    <div class="results-title">Results</div>
                </div>
                <pre style="color: #ddd; overflow-x: auto; background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px;">${JSON.stringify(data, null, 2)}</pre>
            `;
        }
    } else {
        // Default: show JSON
        container.innerHTML = `
            <div class="results-header">
                <div class="results-title">Results</div>
            </div>
            <pre style="color: #ddd; overflow-x: auto; background: rgba(0,0,0,0.3); padding: 20px; border-radius: 8px;">${JSON.stringify(data, null, 2)}</pre>
        `;
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get table config by data type
 */
export function getTableConfig(dataType) {
    return TABLE_CONFIGS[dataType] || null;
}

/**
 * Check if data type has table config
 */
export function hasTableConfig(dataType) {
    return dataType in TABLE_CONFIGS;
}
