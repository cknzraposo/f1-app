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

const NATIONALITY_TO_FLAG_CODE = {
    'American': 'us',
    'British': 'gb',
    'German': 'de',
    'Brazilian': 'br',
    'French': 'fr',
    'Italian': 'it',
    'Spanish': 'es',
    'Finnish': 'fi',
    'Australian': 'au',
    'Austrian': 'at',
    'Belgian': 'be',
    'Canadian': 'ca',
    'Dutch': 'nl',
    'Japanese': 'jp',
    'Mexican': 'mx',
    'Polish': 'pl',
    'Swedish': 'se',
    'Swiss': 'ch',
    'Argentine': 'ar',
    'Colombian': 'co',
    'Danish': 'dk',
    'Indian': 'in',
    'Irish': 'ie',
    'Malaysian': 'my',
    'Monegasque': 'mc',
    'New Zealander': 'nz',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'South African': 'za',
    'Thai': 'th',
    'Venezuelan': 've',
    'Chinese': 'cn',
    'Czech': 'cz',
    'Hungarian': 'hu',
    'Liechtensteiner': 'li',
    'Rhodesian': 'zw',
    'East German': 'de',
    'Chilean': 'cl',
    'Uruguayan': 'uy',
    'Indonesian': 'id'
};

/**
 * Get flag emoji for nationality using GitHub CDN
 * Returns an img tag with the flag from GitHub's emoji CDN
 */
function getFlagEmoji(nationality) {
    const countryCode = NATIONALITY_TO_FLAG_CODE[nationality];
    
    if (!countryCode) {
        return '🏁'; // Fallback for unknown nationalities
    }
    
    // Use GitHub's emoji CDN directly (no API call needed)
    const flagUrl = `https://github.githubassets.com/images/icons/emoji/unicode/1f1${getRegionalIndicator(countryCode[0])}-1f1${getRegionalIndicator(countryCode[1])}.png`;
    
    return `<img src="${flagUrl}" alt="${nationality} flag" style="width: 20px; height: 20px; vertical-align: middle; display: inline-block;" onerror="this.style.display='none'; this.nextSibling.style.display='inline';" /><span style="display:none;">${getUnicodeFlagEmoji(countryCode)}</span>`;
}

/**
 * Convert country code letter to regional indicator hex
 */
function getRegionalIndicator(letter) {
    // Regional indicator symbols start at U+1F1E6 (A) through U+1F1FF (Z)
    // a = 97 in ASCII, A would be 65, so we normalize to lowercase
    const code = letter.toLowerCase().charCodeAt(0) - 97 + 0xe6;
    return code.toString(16);
}

/**
 * Get Unicode flag emoji as fallback
 */
function getUnicodeFlagEmoji(countryCode) {
    // Convert country code to Unicode flag emoji
    // e.g., 'us' -> U+1F1FA U+1F1F8 -> 🇺🇸
    const codePoints = countryCode
        .toUpperCase()
        .split('')
        .map(char => 0x1F1E6 - 65 + char.charCodeAt(0));
    
    return String.fromCodePoint(...codePoints);
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
    
    console.log('Loading driver data for:', driverId);
    console.log('Elements found:', {
        profileEl: !!profileEl,
        statsEl: !!statsEl,
        teamsEl: !!teamsEl,
        seasonEl: !!seasonEl,
        raceResultsEl: !!raceResultsEl
    });
    
    try {
        // Load driver basic info and stats in parallel
        console.log('Fetching driver data and stats...');
        const [driverData, statsData] = await Promise.all([
            getDriver(driverId),
            getDriverStats(driverId)
        ]);
        
        console.log('Driver data received:', driverData);
        console.log('Stats data received:', statsData);
        
        // Extract driver from response
        const driver = driverData.MRData?.DriverTable?.Drivers?.[0];
        
        if (!driver) {
            throw new Error('Driver not found');
        }
        
        console.log('Driver extracted:', driver);
        
        // Render components
        console.log('Rendering driver profile...');
        renderDriverProfile(driver, profileEl);
        
        console.log('Rendering career stats...');
        renderCareerStats(statsData, statsEl);
        
        console.log('Rendering teams...');
        await renderTeams(statsData, teamsEl, driverId);
        
        console.log('Loading season history...');
        await loadSeasonHistory(driverId, seasonEl);
        
        console.log('Loading race results...');
        await loadRaceResults(driverId, raceResultsEl);
        
        console.log('All data loaded successfully!');
        
    } catch (error) {
        console.error('Error loading driver data:', error);
        console.error('Error stack:', error.stack);
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
 * Render teams section with years calculated from race data
 */
async function renderTeams(statsData, container, driverId) {
    if (!container) return;
    
    showLoading(container, 'Loading teams...');
    
    const teams = statsData.statistics?.teams || [];
    
    if (!teams || teams.length === 0) {
        container.innerHTML = `
            <div class="note-message">
                No team information available for this driver.
            </div>
        `;
        return;
    }
    
    try {
        // Fetch all season data to calculate years per team
        const maxYear = 2024;
        const promises = [];
        
        for (let year = 1984; year <= maxYear; year++) {
            promises.push(
                fetch(`/api/drivers/${driverId}/seasons/${year}`)
                    .then(res => res.json())
                    .then(data => {
                        const races = data.MRData?.RaceTable?.Races || [];
                        if (races.length > 0) {
                            // Get unique teams for this year
                            const teamsInYear = new Set();
                            races.forEach(race => {
                                const teamName = race.Results?.[0]?.Constructor?.name;
                                if (teamName) {
                                    teamsInYear.add(teamName);
                                }
                            });
                            return { year, teams: Array.from(teamsInYear) };
                        }
                        return null;
                    })
                    .catch(() => null)
            );
        }
        
        const results = await Promise.all(promises);
        const validSeasons = results.filter(s => s !== null);
        
        // Build team-to-years map
        const teamYears = {};
        validSeasons.forEach(season => {
            season.teams.forEach(teamName => {
                if (!teamYears[teamName]) {
                    teamYears[teamName] = [];
                }
                teamYears[teamName].push(season.year);
            });
        });
        
        // Calculate year ranges for each team
        const teamData = Object.keys(teamYears).map(teamName => {
            const years = teamYears[teamName].sort((a, b) => a - b);
            const firstYear = years[0];
            const lastYear = years[years.length - 1];
            const totalRaces = years.length; // Approximation based on seasons
            
            return {
                name: teamName,
                startYear: firstYear,
                endYear: lastYear,
                years: years,
                displayYears: firstYear === lastYear ? `${firstYear}` : `${firstYear}-${lastYear}`
            };
        });
        
        // Sort by most recent first
        teamData.sort((a, b) => b.endYear - a.endYear);
        
        container.innerHTML = `
            <div class="teams-grid">
                ${teamData.map(team => `
                    <div class="team-card">
                        <div class="team-name">${escapeHtml(team.name)}</div>
                        <div class="team-years">${team.displayYears}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading team years:', error);
        // Fallback to simple display
        container.innerHTML = `
            <div class="teams-grid">
                ${teams.map(teamName => `
                    <div class="team-card">
                        <div class="team-name">${escapeHtml(teamName)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

/**
 * Load and render season history
 */
async function loadSeasonHistory(driverId, container) {
    if (!container) return;
    
    showLoading(container, 'Loading season history...');
    
    try {
        // Try to fetch results from available seasons (1984-2024)
        const maxYear = 2024; // Database has data through 2024
        const promises = [];
        
        for (let year = 1984; year <= maxYear; year++) {
            promises.push(
                fetch(`/api/drivers/${driverId}/seasons/${year}`)
                    .then(res => res.json())
                    .then(data => {
                        const races = data.MRData?.RaceTable?.Races || [];
                        if (races.length > 0) {
                            // Extract results from each race
                            const results = races.map(race => {
                                const result = race.Results?.[0]; // Driver's result is first in array
                                if (!result) return null;
                                
                                return {
                                    raceName: race.raceName,
                                    round: race.round,
                                    date: race.date,
                                    position: result.position,
                                    points: result.points,
                                    grid: result.grid,
                                    Constructor: result.Constructor
                                };
                            }).filter(r => r !== null);
                            
                            if (results.length > 0) {
                                return { year, results };
                            }
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
        const maxYear = 2024; // Database has data through 2024
        const promises = [];
        
        for (let year = 1984; year <= maxYear; year++) {
            promises.push(
                fetch(`/api/drivers/${driverId}/seasons/${year}`)
                    .then(res => res.json())
                    .then(data => {
                        const races = data.MRData?.RaceTable?.Races || [];
                        if (races.length > 0) {
                            // Extract results from each race
                            const results = races.map(race => {
                                const result = race.Results?.[0]; // Driver's result is first in array
                                if (!result) return null;
                                
                                return {
                                    year: year,
                                    raceName: race.raceName,
                                    round: race.round,
                                    date: race.date,
                                    position: result.position,
                                    points: result.points,
                                    grid: result.grid,
                                    Constructor: result.Constructor
                                };
                            }).filter(r => r !== null);
                            
                            return results;
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
