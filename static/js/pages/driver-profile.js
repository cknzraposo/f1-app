/**
 * Driver Profile Page Controller
 * Handles driver profile page rendering and data fetching
 */

import { getDriver, getDriverStats, getConstructors } from '../core/api-client.js';
import { showLoading, showError } from '../utils/dom-helpers.js';
import { parseQueryString, escapeHtml } from '../utils/formatters.js';

// ============================================
// NATIONALITY TO FLAG EMOJI MAPPING
// ============================================

const NATIONALITY_FLAGS = {
    'American': '🇺🇸',
    'British': '🇬🇧',
    'German': '🇩🇪',
    'Brazilian': '🇧🇷',
    'French': '🇫🇷',
    'Italian': '🇮🇹',
    'Spanish': '🇪🇸',
    'Finnish': '🇫🇮',
    'Australian': '🇦🇺',
    'Austrian': '🇦🇹',
    'Belgian': '🇧🇪',
    'Canadian': '🇨🇦',
    'Dutch': '🇳🇱',
    'Japanese': '🇯🇵',
    'Mexican': '🇲🇽',
    'Polish': '🇵🇱',
    'Swedish': '🇸🇪',
    'Swiss': '🇨🇭',
    'Argentine': '🇦🇷',
    'Colombian': '🇨🇴',
    'Danish': '🇩🇰',
    'Indian': '🇮🇳',
    'Irish': '🇮🇪',
    'Malaysian': '🇲🇾',
    'Monegasque': '🇲🇨',
    'New Zealander': '🇳🇿',
    'Portuguese': '🇵🇹',
    'Russian': '🇷🇺',
    'South African': '🇿🇦',
    'Thai': '🇹🇭',
    'Venezuelan': '🇻🇪',
    'Chinese': '🇨🇳',
    'Czech': '🇨🇿',
    'Hungarian': '🇭🇺',
    'Liechtensteiner': '🇱🇮',
    'Rhodesian': '🇿🇼',
    'East German': '🇩🇪',
    'Chilean': '🇨🇱',
    'Uruguayan': '🇺🇾',
    'Indonesian': '🇮🇩'
};

/**
 * Get flag emoji for nationality
 */
function getFlagEmoji(nationality) {
    return NATIONALITY_FLAGS[nationality] || '🏁';
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize driver profile page
 */
async function init() {
    console.log('Initializing driver profile page...');
    
    // Get driver ID from URL
    const params = parseQueryString(window.location.search);
    const driverId = params.id;
    
    if (!driverId) {
        const profileEl = document.getElementById('driverProfile');
        if (profileEl) {
            showError(profileEl, 'No driver ID provided', 'Please select a driver to view');
        }
        return;
    }
    
    // Load driver data
    await loadDriverData(driverId);
}

// ============================================
// DATA LOADING
// ============================================

/**
 * Load all driver data
 */
async function loadDriverData(driverId) {
    const profileEl = document.getElementById('driverProfile');
    const statsEl = document.getElementById('careerStats');
    const teamsEl = document.getElementById('teamsSection');
    const seasonEl = document.getElementById('seasonHistory');
    const raceResultsEl = document.getElementById('raceResults');
    
    try {
        // Load driver basic info and stats in parallel
        const [driverData, statsData] = await Promise.all([
            getDriver(driverId),
            getDriverStats(driverId)
        ]);
        
        // Extract driver from response
        const driver = driverData.MRData?.DriverTable?.Drivers?.[0];
        
        if (!driver) {
            throw new Error('Driver not found');
        }
        
        // Render components
        renderDriverProfile(driver, profileEl);
        renderCareerStats(statsData, statsEl);
        await renderTeams(statsData.statistics?.teams || [], teamsEl);
        await loadSeasonHistory(driverId, seasonEl);
        await loadRaceResults(driverId, raceResultsEl);
        
    } catch (error) {
        console.error('Error loading driver data:', error);
        showError(profileEl, 'Error loading driver data', error.message);
        if (statsEl) statsEl.innerHTML = '';
        if (teamsEl) teamsEl.innerHTML = '';
        if (seasonEl) seasonEl.innerHTML = '';
        if (raceResultsEl) raceResultsEl.innerHTML = '';
    }
}

// ============================================
// RENDERING FUNCTIONS
// ============================================

/**
 * Render driver profile header
 */
function renderDriverProfile(driver, container) {
    if (!container) return;
    
    const fullName = `${driver.givenName} ${driver.familyName}`;
    const nationality = driver.nationality || 'Unknown';
    const flagEmoji = getFlagEmoji(nationality);
    const dob = driver.dateOfBirth || 'Unknown';
    const number = driver.permanentNumber || 'N/A';
    const code = driver.code || 'N/A';
    
    container.innerHTML = `
        <div class="driver-name">${escapeHtml(fullName)}</div>
        <div class="driver-info-grid">
            <div>
                <div class="info-label">Nationality</div>
                <div class="info-value">${flagEmoji} ${escapeHtml(nationality)}</div>
            </div>
            <div>
                <div class="info-label">Date of Birth</div>
                <div class="info-value">${escapeHtml(dob)}</div>
            </div>
            <div>
                <div class="info-label">Race Number</div>
                <div class="info-value">#${escapeHtml(number)}</div>
            </div>
            <div>
                <div class="info-label">Driver Code</div>
                <div class="info-value">${escapeHtml(code)}</div>
            </div>
        </div>
        <div style="margin-top: 20px; text-align: center;">
            <a href="/static/compare.html?driver1=${encodeURIComponent(driver.driverId)}" 
               class="compare-button"
               style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.1)';">
                🏎️ Compare with Another Driver
            </a>
        </div>
    `;
}

/**
 * Render career statistics
 */
function renderCareerStats(statsData, container) {
    if (!container) return;
    
    const stats = statsData.statistics || {};
    const note = statsData.note || '';
    
    if (note) {
        container.innerHTML = `
            <div class="note-message">${escapeHtml(note)}</div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${stats.totalRaces || 0}</div>
                <div class="stat-label">Races</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.wins || 0}</div>
                <div class="stat-label">Wins</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.podiums || 0}</div>
                <div class="stat-label">Podiums</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.polePositions || 0}</div>
                <div class="stat-label">Poles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.fastestLaps || 0}</div>
                <div class="stat-label">Fastest Laps</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.totalPoints || 0}</div>
                <div class="stat-label">Points</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.dnfs || 0}</div>
                <div class="stat-label">DNFs</div>
            </div>
        </div>
    `;
}

/**
 * Load and render season history
 */
async function loadSeasonHistory(driverId, container) {
    if (!container) return;
    
    showLoading(container, 'Loading season history...');
    
    try {
        // Try to fetch results from available seasons (1984-2024)
        const currentYear = new Date().getFullYear();
        const promises = [];
        
        for (let year = 1984; year <= currentYear; year++) {
            promises.push(
                fetch(`/api/drivers/${driverId}/seasons/${year}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            return { year, results: data.results };
                        }
                        return null;
                    })
                    .catch(() => null)
            );
        }
        
        const results = await Promise.all(promises);
        const validSeasons = results.filter(s => s !== null);
        
        if (validSeasons.length === 0) {
            container.innerHTML = `
                <div class="note-message">
                    No season history available for this driver in the database (1984-2024).
                </div>
            `;
            return;
        }
        
        // Sort by year descending
        validSeasons.sort((a, b) => b.year - a.year);
        
        // Calculate season summaries
        const seasonSummaries = validSeasons.map(season => {
            const results = season.results;
            const wins = results.filter(r => r.position === '1' || r.position === 1).length;
            const podiums = results.filter(r => {
                const pos = parseInt(r.position);
                return pos >= 1 && pos <= 3;
            }).length;
            const points = results.reduce((sum, r) => sum + (parseFloat(r.points) || 0), 0);
            const races = results.length;
            
            // Get primary team (most races)
            const teamCounts = {};
            results.forEach(r => {
                const team = r.Constructor?.name || 'Unknown';
                teamCounts[team] = (teamCounts[team] || 0) + 1;
            });
            const primaryTeam = Object.keys(teamCounts).reduce((a, b) => 
                teamCounts[a] > teamCounts[b] ? a : b
            );
            
            return {
                year: season.year,
                races,
                wins,
                podiums,
                points: points.toFixed(1),
                team: primaryTeam
            };
        });
        
        container.innerHTML = `
            <div class="table-container">
                <table class="season-history-table">
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>Team</th>
                            <th class="text-center">Races</th>
                            <th class="text-center">Wins</th>
                            <th class="text-center">Podiums</th>
                            <th class="text-right">Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${seasonSummaries.map(s => `
                            <tr>
                                <td class="highlight">${s.year}</td>
                                <td>${escapeHtml(s.team)}</td>
                                <td class="text-center">${s.races}</td>
                                <td class="text-center highlight">${s.wins}</td>
                                <td class="text-center">${s.podiums}</td>
                                <td class="text-right">${s.points}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading season history:', error);
        showError(container, 'Failed to load season history', error.message);
    }
}

/**
 * Load and render detailed race results
 */
async function loadRaceResults(driverId, container) {
    if (!container) return;
    
    showLoading(container, 'Loading race results...');
    
    try {
        // Try to fetch results from available seasons (1984-2024)
        const currentYear = new Date().getFullYear();
        const promises = [];
        
        for (let year = 1984; year <= currentYear; year++) {
            promises.push(
                fetch(`/api/drivers/${driverId}/seasons/${year}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            return data.results.map(r => ({ ...r, year }));
                        }
                        return [];
                    })
                    .catch(() => [])
            );
        }
        
        const results = await Promise.all(promises);
        const allRaces = results.flat().filter(r => r.raceName);
        
        if (allRaces.length === 0) {
            container.innerHTML = `
                <div class="note-message">
                    No race results available for this driver in the database (1984-2024).
                </div>
            `;
            return;
        }
        
        // Sort by year and round descending (most recent first)
        allRaces.sort((a, b) => {
            if (b.year !== a.year) return b.year - a.year;
            return (parseInt(b.round) || 0) - (parseInt(a.round) || 0);
        });
        
        container.innerHTML = `
            <div class="table-container" style="max-height: 600px; overflow-y: auto;">
                <table class="season-history-table">
                    <thead style="position: sticky; top: 0; background: #fff; z-index: 10;">
                        <tr>
                            <th>Year</th>
                            <th>Round</th>
                            <th>Race</th>
                            <th>Team</th>
                            <th class="text-center">Grid</th>
                            <th class="text-center">Position</th>
                            <th class="text-right">Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${allRaces.map(race => {
                            const position = race.position || 'DNF';
                            const isWin = position === '1' || position === 1;
                            const isPodium = ['1', '2', '3', 1, 2, 3].includes(position);
                            const positionClass = isWin ? 'highlight' : isPodium ? 'podium' : '';
                            
                            return `
                                <tr>
                                    <td>${race.year}</td>
                                    <td class="text-center">${race.round}</td>
                                    <td>
                                        <a href="/static/results.html?year=${race.year}" style="color: #e10600; text-decoration: none;">
                                            ${escapeHtml(race.raceName)}
                                        </a>
                                    </td>
                                    <td>
                                        ${race.Constructor?.constructorId ? 
                                            `<a href="/static/constructor.html?id=${race.Constructor.constructorId}" style="color: #e10600; text-decoration: none;">
                                                ${escapeHtml(race.Constructor.name)}
                                            </a>` :
                                            escapeHtml(race.Constructor?.name || 'Unknown')
                                        }
                                    </td>
                                    <td class="text-center">${race.grid || 'N/A'}</td>
                                    <td class="text-center ${positionClass}" style="font-weight: ${isPodium ? 'bold' : 'normal'};">
                                        ${position}
                                    </td>
                                    <td class="text-right">${race.points || '0'}</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
            <div style="margin-top: 1rem; color: #666; font-size: 0.875rem;">
                Showing ${allRaces.length} race${allRaces.length !== 1 ? 's' : ''}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading race results:', error);
        showError(container, 'Failed to load race results', error.message);
    }
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
