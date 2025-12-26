/**
 * Season Browser Page Controller
 * Handles browsing F1 seasons (1984-2024) with race results and standings
 */

import { getSeasonResults, getSeasonStandings, getSeasonWinners } from '../core/api-client.js';
import { parseQueryString } from '../utils/formatters.js';

// Constants
const MIN_YEAR = 1984;
const MAX_YEAR = 2024;
const DEFAULT_YEAR = 2023;

// Page state
let currentYear = DEFAULT_YEAR;
let seasonData = null;
let standingsData = null;
let winnersData = null;
let viewMode = 'list'; // 'list' or 'detail'

/**
 * Initialize the season browser page
 */
function init() {
    // Check for year in URL
    const params = parseQueryString();
    if (params.year) {
        currentYear = parseInt(params.year);
        viewMode = 'detail';
        showSeasonDetail();
    } else {
        viewMode = 'list';
        showSeasonsList();
    }
    
    setupEventListeners();
}

/**
 * Show the seasons list view
 */
window.showSeasonsList = function() {
    viewMode = 'list';
    document.getElementById('seasonsListView').style.display = 'block';
    document.getElementById('seasonDetailView').style.display = 'none';
    
    // Update URL to remove year parameter
    const url = new URL(window.location);
    url.searchParams.delete('year');
    window.history.pushState({}, '', url);
    
    renderSeasonsList();
};

/**
 * Show the season detail view for a specific year
 */
function showSeasonDetail(year = currentYear) {
    if (year) {
        currentYear = year;
    }
    
    viewMode = 'detail';
    document.getElementById('seasonsListView').style.display = 'none';
    document.getElementById('seasonDetailView').style.display = 'block';
    
    updateYearDisplay();
    loadSeasonData();
    
    // Update URL
    const url = new URL(window.location);
    url.searchParams.set('year', currentYear);
    window.history.pushState({}, '', url);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Make showSeasonDetail globally accessible
 */
window.showSeasonDetail = showSeasonDetail;

/**
 * Render the seasons list with all available years
 */
function renderSeasonsList() {
    const container = document.getElementById('seasonsTableContainer');
    if (!container) return;
    
    const decades = [];
    for (let year = MAX_YEAR; year >= MIN_YEAR; year--) {
        const decade = Math.floor(year / 10) * 10;
        let decadeGroup = decades.find(d => d.decade === decade);
        
        if (!decadeGroup) {
            decadeGroup = { decade, years: [] };
            decades.push(decadeGroup);
        }
        
        decadeGroup.years.push(year);
    }
    
    let html = '';
    
    decades.forEach(group => {
        html += `
            <h2 class="season-decade-header">${group.decade}s</h2>
            <div class="seasons-grid">
        `;
        
        group.years.forEach(year => {
            html += `
                <div class="season-card" onclick="showSeasonDetail(${year})">
                    <div class="season-year">${year}</div>
                    <div class="season-meta">Click to view details</div>
                </div>
            `;
        });
        
        html += '</div>';
    });
    
    container.innerHTML = html;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Year navigation buttons
    const prevBtn = document.getElementById('prevYear');
    const nextBtn = document.getElementById('nextYear');
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => changeYear(-1));
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => changeYear(1));
    }
}

/**
 * Change the current year in detail view
 */
function changeYear(delta) {
    const newYear = currentYear + delta;
    
    if (newYear >= MIN_YEAR && newYear <= MAX_YEAR) {
        showSeasonDetail(newYear);
    }
}

/**
 * Update year display and button states
 */
function updateYearDisplay() {
    const yearDisplay = document.getElementById('currentYear');
    const prevBtn = document.getElementById('prevYear');
    const nextBtn = document.getElementById('nextYear');
    
    if (yearDisplay) {
        yearDisplay.textContent = currentYear;
    }
    
    if (prevBtn) {
        prevBtn.disabled = currentYear <= MIN_YEAR;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentYear >= MAX_YEAR;
    }
}

/**
 * Switch between tabs
 * @param {string} tabName - Name of tab to switch to
 */
window.switchTab = function(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetTab = document.getElementById(`${tabName}Tab`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
};

/**
 * Load all season data from API
 */
async function loadSeasonData() {
    showLoading();
    
    try {
        // Load all data in parallel
        const [season, standings, winners] = await Promise.all([
            getSeasonResults(currentYear),
            getSeasonStandings(currentYear),
            getSeasonWinners(currentYear)
        ]);
        
        seasonData = season;
        standingsData = standings;
        winnersData = winners;
        
        renderAllTabs();
        hideLoading();
        
    } catch (error) {
        console.error('Error loading season data:', error);
        hideLoading();
        showError(`Failed to load season ${currentYear}: ${error.message}`);
    }
}

/**
 * Render all tab contents
 */
function renderAllTabs() {
    renderSummary();
    renderRaces();
    renderDriverStandings();
    renderConstructorStandings();
}

/**
 * Render summary tab with season overview
 */
function renderSummary() {
    const summaryContent = document.getElementById('summaryContent');
    if (!summaryContent || !standingsData || !winnersData) return;
    
    const driverChampion = standingsData.driverStandings[0];
    const constructorChampion = standingsData.constructorStandings[0];
    const totalRaces = winnersData.count;
    const uniqueWinners = countUniqueWinners();
    
    summaryContent.innerHTML = `
        <div class="stats-summary">
            <div class="stat-card">
                <div class="stat-label">Driver Champion</div>
                <div class="stat-value">
                    <a href="/static/drivers.html?id=${driverChampion.driverId}" class="driver-link">
                        ${driverChampion.name}
                    </a>
                </div>
                <div style="margin-top: 0.5rem; color: #666;">
                    ${driverChampion.points} points • ${driverChampion.wins} wins
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Constructor Champion</div>
                <div class="stat-value">
                    <a href="/static/constructor.html?id=${constructorChampion.constructorId}" class="constructor-link">
                        ${constructorChampion.name}
                    </a>
                </div>
                <div style="margin-top: 0.5rem; color: #666;">
                    ${constructorChampion.points} points • ${constructorChampion.wins} wins
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Total Races</div>
                <div class="stat-value">${totalRaces}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Different Winners</div>
                <div class="stat-value">${uniqueWinners}</div>
            </div>
        </div>
        
        <h2 style="margin-top: 2rem;">Race Winners</h2>
        ${renderWinnersTable()}
    `;
}

/**
 * Count unique race winners in the season
 */
function countUniqueWinners() {
    if (!winnersData || !winnersData.winners) return 0;
    const uniqueDrivers = new Set(winnersData.winners.map(w => w.driver.driverId));
    return uniqueDrivers.size;
}

/**
 * Render winners table HTML
 */
function renderWinnersTable() {
    if (!winnersData || !winnersData.winners) return '';
    
    const rows = winnersData.winners.map(winner => `
        <tr>
            <td>${winner.round}</td>
            <td>${winner.raceName}</td>
            <td>${winner.date}</td>
            <td>
                <a href="/static/drivers.html?id=${winner.driver.driverId}" class="driver-link">
                    ${winner.driver.name}
                </a>
            </td>
            <td>
                <a href="/static/constructor.html?id=${winner.constructor.constructorId}" class="constructor-link">
                    ${winner.constructor.name}
                </a>
            </td>
            <td>${winner.grid || 'N/A'}</td>
        </tr>
    `).join('');
    
    return `
        <table class="races-table">
            <thead>
                <tr>
                    <th>Round</th>
                    <th>Race</th>
                    <th>Date</th>
                    <th>Winner</th>
                    <th>Constructor</th>
                    <th>Grid</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

/**
 * Render races tab with all race results
 */
function renderRaces() {
    const racesContent = document.getElementById('racesContent');
    if (!racesContent || !seasonData) return;
    
    const races = seasonData.MRData?.RaceTable?.Races || [];
    
    racesContent.innerHTML = `
        <h2>All Race Results</h2>
        <p style="color: #666; margin-bottom: 1rem;">
            ${races.length} races in ${currentYear} season
        </p>
        ${races.map(race => renderRaceResults(race)).join('')}
    `;
}

/**
 * Render single race results
 */
function renderRaceResults(race) {
    const rows = race.Results.slice(0, 10).map(result => {
        const position = parseInt(result.position);
        const positionClass = position === 1 ? 'position-1' : 
                            position === 2 ? 'position-2' : 
                            position === 3 ? 'position-3' : 'position-other';
        
        return `
            <tr>
                <td>
                    <span class="position-badge ${positionClass}">
                        ${result.position}
                    </span>
                </td>
                <td>
                    <a href="/static/drivers.html?id=${result.Driver.driverId}" class="driver-link">
                        ${result.Driver.givenName} ${result.Driver.familyName}
                    </a>
                </td>
                <td>
                    <a href="/static/constructor.html?id=${result.Constructor.constructorId}" class="constructor-link">
                        ${result.Constructor.name}
                    </a>
                </td>
                <td>${result.grid}</td>
                <td>${result.Time ? result.Time.time : result.status}</td>
                <td>${result.points}</td>
            </tr>
        `;
    }).join('');
    
    return `
        <div style="margin-bottom: 2rem;">
            <h3>${race.raceName}</h3>
            <p style="color: #666; margin-bottom: 0.5rem;">
                ${race.Circuit.circuitName} • ${race.date}
            </p>
            <table class="races-table">
                <thead>
                    <tr>
                        <th>Pos</th>
                        <th>Driver</th>
                        <th>Constructor</th>
                        <th>Grid</th>
                        <th>Time/Status</th>
                        <th>Points</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Render driver championship standings
 */
function renderDriverStandings() {
    const driversContent = document.getElementById('driversContent');
    if (!driversContent || !standingsData) return;
    
    const rows = standingsData.driverStandings.map(driver => {
        const position = parseInt(driver.position);
        const positionClass = position === 1 ? 'position-1' : 
                            position === 2 ? 'position-2' : 
                            position === 3 ? 'position-3' : 'position-other';
        
        return `
            <tr>
                <td>
                    <span class="position-badge ${positionClass}">
                        ${driver.position}
                    </span>
                </td>
                <td>
                    <a href="/static/drivers.html?id=${driver.driverId}" class="driver-link">
                        ${driver.name}
                    </a>
                    ${driver.position === 1 ? '<span class="champion-badge">Champion</span>' : ''}
                </td>
                <td>
                    <a href="/static/constructor.html?id=${driver.constructorId}" class="constructor-link">
                        ${driver.constructor}
                    </a>
                </td>
                <td><strong>${driver.points}</strong></td>
                <td>${driver.wins}</td>
                <td>${driver.podiums || 0}</td>
            </tr>
        `;
    }).join('');
    
    driversContent.innerHTML = `
        <h2>Driver Championship Standings</h2>
        <table class="standings-table">
            <thead>
                <tr>
                    <th>Pos</th>
                    <th>Driver</th>
                    <th>Constructor</th>
                    <th>Points</th>
                    <th>Wins</th>
                    <th>Podiums</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

/**
 * Render constructor championship standings
 */
function renderConstructorStandings() {
    const constructorsContent = document.getElementById('constructorsContent');
    if (!constructorsContent || !standingsData) return;
    
    const rows = standingsData.constructorStandings.map(constructor => {
        const position = parseInt(constructor.position);
        const positionClass = position === 1 ? 'position-1' : 
                            position === 2 ? 'position-2' : 
                            position === 3 ? 'position-3' : 'position-other';
        
        return `
            <tr>
                <td>
                    <span class="position-badge ${positionClass}">
                        ${constructor.position}
                    </span>
                </td>
                <td>
                    <a href="/static/constructor.html?id=${constructor.constructorId}" class="constructor-link">
                        ${constructor.name}
                    </a>
                    ${constructor.position === 1 ? '<span class="champion-badge">Champion</span>' : ''}
                </td>
                <td><strong>${constructor.points}</strong></td>
                <td>${constructor.wins}</td>
                <td>${constructor.podiums || 0}</td>
            </tr>
        `;
    }).join('');
    
    constructorsContent.innerHTML = `
        <h2>Constructor Championship Standings</h2>
        <table class="standings-table">
            <thead>
                <tr>
                    <th>Pos</th>
                    <th>Constructor</th>
                    <th>Points</th>
                    <th>Wins</th>
                    <th>Podiums</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div>
            <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
            <p>Loading ${currentYear} season...</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Show error message
 */
function showError(message) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${message}
            </div>
        `;
    });
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
