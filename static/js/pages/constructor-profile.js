/**
 * Constructor Profile Page Controller
 * Handles individual constructor/team detail pages
 * Constructor data comes from constructors.json via the stats endpoint
 */

import { getConstructor, getConstructorStats, getDrivers } from '../core/api-client.js';
import { parseQueryString, getOrdinal } from '../utils/formatters.js';

// Nationality to country code mapping
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

/**
 * Initialize the constructor profile page
 */
function init() {
    console.log('Constructor profile init called');
    console.log('Current URL:', window.location.href);
    const params = parseQueryString();
    console.log('Parsed params:', params);
    const constructorId = params.id;
    console.log('Constructor ID:', constructorId);
    
    if (!constructorId) {
        console.error('No constructor ID found');
        showError('No constructor ID specified');
        return;
    }
    
    loadConstructorData(constructorId);
}

/**
 * Load constructor data from API with lazy loading
 * Priority 1: Basic constructor info from constructors.json (fast)
 * Priority 2: Statistics (slower, computed from all season files)
 */
async function loadConstructorData(constructorId) {
    console.log('loadConstructorData called with:', constructorId);
    try {
        // Show loading state
        const loadingEl = document.getElementById('loading');
        const errorEl = document.getElementById('error');
        const detailsEl = document.getElementById('constructor-details');
        
        console.log('Elements found:', {
            loading: !!loadingEl,
            error: !!errorEl,
            details: !!detailsEl
        });
        
        if (loadingEl) loadingEl.classList.remove('hidden');
        if (errorEl) errorEl.classList.add('hidden');
        if (detailsEl) detailsEl.classList.add('hidden');
        
        console.log('Fetching basic constructor info...');
        // PRIORITY 1: Load basic info first (fast - single JSON file)
        const basicData = await getConstructor(constructorId);
        console.log('Basic data fetched:', basicData);
        
        const constructor = basicData.MRData?.ConstructorTable?.Constructors?.[0];
        
        if (!constructor) {
            console.error('Constructor not found in response');
            throw new Error('Constructor not found');
        }
        
        console.log('Constructor found:', constructor);
        
        // Display basic info immediately
        displayBasicInfo(constructor);
        
        // Show the page with basic info
        if (loadingEl) loadingEl.classList.add('hidden');
        if (detailsEl) detailsEl.classList.remove('hidden');
        
        // PRIORITY 2: Load statistics in background (slower)
        console.log('Fetching statistics in background...');
        loadStatisticsAsync(constructorId, constructor);
        
    } catch (error) {
        console.error('Error loading constructor data:', error);
        console.error('Error stack:', error.stack);
        showError(error.message || 'Failed to load constructor details');
    }
}

/**
 * Load statistics asynchronously in the background
 */
async function loadStatisticsAsync(constructorId, constructor) {
    try {
        const statsData = await getConstructorStats(constructorId);
        console.log('Stats data fetched:', { statsData });
        
        // Update page with statistics
        displayStatistics(statsData.statistics || {});
        
        // Load drivers list
        await renderDriversList(statsData.statistics?.drivers || []);
        
        // Load season history
        renderSeasonHistory(statsData.statistics?.seasons || []);
        
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Show error in stats sections but don't break the page
        const statsCards = document.querySelectorAll('[id^="stat-"]');
        statsCards.forEach(card => {
            if (card.textContent === '-') {
                card.textContent = 'N/A';
            }
        });
    }
}

/**
 * Display basic constructor information immediately (from constructors.json)
 */
function displayBasicInfo(constructor) {
    // Update header
    const nameEl = document.getElementById('constructor-name');
    const nationalityEl = document.getElementById('constructor-nationality');
    
    if (nameEl) {
        nameEl.textContent = constructor.name;
    }
    
    if (nationalityEl) {
        const flagEmoji = getFlagEmoji(constructor.nationality);
        nationalityEl.innerHTML = `${flagEmoji} ${constructor.nationality}`;
    }
    
    // Wikipedia link
    const wikiLink = document.getElementById('wikipedia-link');
    if (wikiLink && constructor.url) {
        wikiLink.href = constructor.url;
    }
    
    // Show loading placeholders for stats
    const driversListEl = document.getElementById('drivers-list');
    const seasonHistoryEl = document.getElementById('season-history');
    
    if (driversListEl) {
        driversListEl.innerHTML = '<p class="text-gray-600">Loading drivers...</p>';
    }
    
    if (seasonHistoryEl) {
        seasonHistoryEl.innerHTML = '<p class="text-gray-600">Loading season history...</p>';
    }
}

/**
 * Display statistics once they're loaded
 */
function displayStatistics(stats) {
    // Update statistics cards
    updateStatCard('stat-championships', stats.totalChampionships || 0);
    updateStatCard('stat-wins', stats.totalWins || 0);
    updateStatCard('stat-podiums', stats.totalPodiums || 0);
    updateStatCard('stat-poles', stats.totalPoles || 0);
    updateStatCard('stat-fastest-laps', stats.totalFastestLaps || 0);
    updateStatCard('stat-points', Math.round(stats.totalPoints || 0));
    
    // Update team information
    updateInfoField('info-races', stats.totalRaces || 0);
    updateInfoField('info-seasons', stats.seasons?.length || 0);
    
    if (stats.firstRace) {
        updateInfoField('info-first-race', `${stats.firstRace.raceName} ${stats.firstRace.season}`);
    }
    
    if (stats.lastRace) {
        updateInfoField('info-last-race', `${stats.lastRace.raceName} ${stats.lastRace.season}`);
    }
    
    if (stats.bestSeasonPosition) {
        const ordinal = getOrdinal(stats.bestSeasonPosition);
        updateInfoField('info-best-position', `${ordinal} (${stats.bestSeasonYear}`);
    }
}

/**
 * Display constructor information and statistics (LEGACY - keeping for compatibility)
 */
async function displayConstructor(statsData) {
    // Get constructor info from stats endpoint (comes from constructors.json)
    const constructor = statsData.constructorInfo || {};
    const stats = statsData.statistics || {};
    
    if (!constructor || !constructor.name) {
        showError('Constructor not found');
        return;
    }
    
    displayBasicInfo(constructor);
    displayStatistics(stats);
    
    // Display drivers list
    await renderDriversList(stats.drivers || []);
    
    // Display season history
    renderSeasonHistory(stats.seasons || []);
    
    // Wikipedia link
    const wikiLink = document.getElementById('wikipedia-link');
    if (wikiLink && constructor.url) {
        wikiLink.href = constructor.url;
    }
    
    // Show details, hide loading
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('constructor-details').classList.remove('hidden');
}

/**
 * Update a statistic card value
 */
function updateStatCard(elementId, value) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = value;
    }
}

/**
 * Update an information field
 */
function updateInfoField(elementId, value) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = value;
    }
}

/**
 * Render the list of drivers who raced for this constructor
 */
async function renderDriversList(drivers) {
    const driversListEl = document.getElementById('drivers-list');
    if (!driversListEl) return;
    
    if (!drivers || drivers.length === 0) {
        driversListEl.innerHTML = '<p class="text-gray-600">No driver information available</p>';
        return;
    }
    
    driversListEl.innerHTML = '<p class="text-gray-600">Loading drivers...</p>';
    
    try {
        // Fetch all drivers to get names
        const driversData = await getDrivers();
        const allDrivers = driversData.MRData?.DriverTable?.Drivers || [];
        
        // Create a map of driverId to driver info
        const driverMap = {};
        allDrivers.forEach(driver => {
            driverMap[driver.driverId] = driver;
        });
        
        // Build driver list with names
        const driversList = drivers.map(driverId => {
            const driver = driverMap[driverId];
            if (driver) {
                return {
                    id: driverId,
                    name: `${driver.givenName} ${driver.familyName}`,
                    nationality: driver.nationality
                };
            }
            return { id: driverId, name: driverId, nationality: null };
        });
        
        driversListEl.innerHTML = `
            <p class="text-sm text-gray-600 mb-3">${driversList.length} drivers have raced for this team</p>
            <div class="space-y-1 max-h-96 overflow-y-auto">
                ${driversList.map(driver => `
                    <a href="drivers.html?id=${driver.id}" 
                       class="block p-2 rounded hover:bg-gray-700 transition-colors">
                        <span class="text-white hover:text-red-600 font-medium">${driver.name}</span>
                        ${driver.nationality ? `<span class="text-gray-400 text-sm ml-2">${getFlagEmoji(driver.nationality)} ${driver.nationality}</span>` : ''}
                    </a>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading driver names:', error);
        driversListEl.innerHTML = `
            <p class="text-sm text-gray-600 mb-3">${drivers.length} drivers</p>
            <div class="grid grid-cols-2 gap-2">
                ${drivers.map(driverId => `
                    <a href="drivers.html?id=${driverId}" 
                       class="text-red-600 hover:underline text-sm">
                        ${driverId}
                    </a>
                `).join('')}
            </div>
        `;
    }
}

/**
 * Render season-by-season history table with drivers
 */
function renderSeasonHistory(seasons) {
    const historyEl = document.getElementById('season-history');
    if (!historyEl) return;
    
    if (!seasons || seasons.length === 0) {
        historyEl.innerHTML = '<p class="text-gray-600">No season history available</p>';
        return;
    }
    
    // Sort seasons by year descending
    const sortedSeasons = [...seasons].sort((a, b) => b.season - a.season);
    
    historyEl.innerHTML = `
        <table class="min-w-full">
            <thead>
                <tr class="border-b-2 border-gray-300">
                    <th class="text-left py-3 px-4 font-bold">Year</th>
                    <th class="text-left py-3 px-4 font-bold">Drivers</th>
                    <th class="text-center py-3 px-4 font-bold">Races</th>
                    <th class="text-center py-3 px-4 font-bold">Wins</th>
                    <th class="text-center py-3 px-4 font-bold">Podiums</th>
                    <th class="text-center py-3 px-4 font-bold">Poles</th>
                    <th class="text-right py-3 px-4 font-bold">Points</th>
                </tr>
            </thead>
            <tbody>
                ${sortedSeasons.map(season => renderSeasonRow(season)).join('')}
            </tbody>
        </table>
    `;
    
    // Load driver names for each season
    loadDriverNamesForSeasons(sortedSeasons);
}

/**
 * Render a single season row
 */
function renderSeasonRow(season) {
    return `
        <tr class="border-b border-gray-200 hover:bg-gray-50 transition-colors" data-season="${season.season}">
            <td class="py-3 px-4">
                <a href="/static/results.html?year=${season.season}" class="text-red-600 font-bold hover:underline">
                    ${season.season}
                </a>
            </td>
            <td class="py-3 px-4">
                <div id="drivers-${season.season}" class="text-sm text-gray-600">
                    Loading...
                </div>
            </td>
            <td class="py-3 px-4 text-center">${season.races}</td>
            <td class="py-3 px-4 text-center ${season.wins > 0 ? 'text-green-600 font-bold' : ''}">${season.wins}</td>
            <td class="py-3 px-4 text-center">${season.podiums}</td>
            <td class="py-3 px-4 text-center">${season.poles || 0}</td>
            <td class="py-3 px-4 text-right font-semibold">${season.points.toFixed(1)}</td>
        </tr>
    `;
}

/**
 * Load driver names for all seasons by fetching the drivers database
 */
async function loadDriverNamesForSeasons(seasons) {
    try {
        // Fetch all drivers to get names
        const driversData = await getDrivers();
        const allDrivers = driversData.MRData?.DriverTable?.Drivers || [];
        
        // Create a map of driverId to driver name
        const driverMap = {};
        allDrivers.forEach(driver => {
            driverMap[driver.driverId] = `${driver.givenName} ${driver.familyName}`;
        });
        
        // Get the current constructor ID
        const params = parseQueryString();
        const constructorId = params.id;
        
        // For each season, we need to get the actual drivers from season results
        for (const season of seasons) {
            const driversCell = document.getElementById(`drivers-${season.season}`);
            if (!driversCell) continue;
            
            try {
                // Fetch season data to get actual drivers
                const seasonData = await fetch(`/api/constructors/${constructorId}/seasons/${season.season}`);
                const seasonJson = await seasonData.json();
                
                const races = seasonJson.MRData?.RaceTable?.Races || [];
                const driverIds = new Set();
                
                // Extract unique driver IDs from all races
                races.forEach(race => {
                    (race.Results || []).forEach(result => {
                        const driverId = result.Driver?.driverId;
                        if (driverId) {
                            driverIds.add(driverId);
                        }
                    });
                });
                
                // Convert to names and display
                const driverNames = Array.from(driverIds)
                    .map(id => driverMap[id] || id)
                    .sort();
                
                if (driverNames.length > 0) {
                    driversCell.innerHTML = driverNames.map(name => 
                        `<span class="inline-block mr-2 mb-1">${name}</span>`
                    ).join('');
                } else {
                    driversCell.innerHTML = '<span class="text-gray-400">No data</span>';
                }
            } catch (err) {
                console.error(`Error loading drivers for ${season.season}:`, err);
                driversCell.innerHTML = '<span class="text-gray-400">N/A</span>';
            }
        }
    } catch (error) {
        console.error('Error loading driver names:', error);
    }
}

/**
 * Show error message
 */
function showError(message) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error').classList.remove('hidden');
    document.getElementById('constructor-details').classList.add('hidden');
    
    const errorMessageEl = document.getElementById('error-message');
    if (errorMessageEl) {
        errorMessageEl.textContent = message;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
