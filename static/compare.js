/**
 * Compare.js - Driver comparison interface (Refactored for Phase 2)
 * 
 * Features:
 * - Driver autocomplete with fuzzy search
 * - Head-to-head statistics
 * - Career trajectory visualization
 * - Season-by-season breakdown
 * - Race-by-race comparison
 * 
 * Now uses modular architecture:
 * - api-client.js for data fetching
 * - autocomplete.js for driver selection (could be used in future)
 * - dom-helpers.js for loading states
 * - formatters.js for data formatting
 */

import { getDrivers, getHeadToHead } from './js/core/api-client.js';
import { showLoading, showError, hideElement, showElement } from './js/utils/dom-helpers.js';
import { parseQueryString } from './js/utils/formatters.js';

let allDrivers = [];
let selectedDriver1 = null;
let selectedDriver2 = null;
let trajectoryChart = null;

// Initialize on page load
async function init() {
    await loadAllDrivers();
    setupEventListeners();
    checkUrlParams();
}

/**
 * Load all drivers for autocomplete
 */
async function loadAllDrivers() {
    try {
        const data = await getDrivers();
        allDrivers = data.MRData?.DriverTable?.Drivers || data.drivers || [];
        console.log(`Loaded ${allDrivers.length} drivers for comparison`);
    } catch (error) {
        console.error('Error loading drivers:', error);
        showError(document.body, 'Failed to load drivers', error.message);
    }
}

/**
 * Setup event listeners for inputs
 */
function setupEventListeners() {
    const driver1Input = document.getElementById('driver1Input');
    const driver2Input = document.getElementById('driver2Input');

    driver1Input.addEventListener('input', (e) => showDriverSuggestions(1, e.target.value));
    driver2Input.addEventListener('input', (e) => showDriverSuggestions(2, e.target.value));

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#driver1Input') && !e.target.closest('#driver1Suggestions')) {
            document.getElementById('driver1Suggestions').classList.add('hidden');
        }
        if (!e.target.closest('#driver2Input') && !e.target.closest('#driver2Suggestions')) {
            document.getElementById('driver2Suggestions').classList.add('hidden');
        }
    });
}

/**
 * Check URL parameters for pre-selected drivers
 */
function checkUrlParams() {
    const params = parseQueryString();
    const driver1Id = params.driver1;
    const driver2Id = params.driver2;

    if (driver1Id && driver2Id) {
        // Find and select drivers
        const d1 = allDrivers.find(d => d.driverId === driver1Id);
        const d2 = allDrivers.find(d => d.driverId === driver2Id);

        if (d1) selectDriver(1, d1);
        if (d2) selectDriver(2, d2);

        if (d1 && d2) {
            setTimeout(() => compareDrivers(), 500);
        }
    }
}

/**
 * Show driver suggestions based on input
 */
function showDriverSuggestions(driverNum, query) {
    const suggestionsDiv = document.getElementById(`driver${driverNum}Suggestions`);

    if (query.length < 2) {
        suggestionsDiv.classList.add('hidden');
        return;
    }

    const queryLower = query.toLowerCase();
    const matches = allDrivers.filter(driver => {
        const fullName = `${driver.givenName} ${driver.familyName}`.toLowerCase();
        const familyName = driver.familyName.toLowerCase();
        return fullName.includes(queryLower) || familyName.includes(queryLower) || driver.driverId.includes(queryLower);
    }).slice(0, 10);

    if (matches.length === 0) {
        suggestionsDiv.innerHTML = '<div class="p-3 text-gray-500 text-sm">No drivers found</div>';
        suggestionsDiv.classList.remove('hidden');
        return;
    }

    suggestionsDiv.innerHTML = matches.map(driver => `
        <div class="p-3 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0 transition"
             onclick='selectDriver(${driverNum}, ${JSON.stringify(driver).replace(/'/g, "&#39;")})'>
            <div class="font-semibold text-gray-800">${driver.givenName} ${driver.familyName}</div>
            <div class="text-sm text-gray-600">${driver.driverId}</div>
        </div>
    `).join('');

    suggestionsDiv.classList.remove('hidden');
}

/**
 * Select a driver
 */
function selectDriver(driverNum, driver) {
    if (driverNum === 1) {
        selectedDriver1 = driver;
    } else {
        selectedDriver2 = driver;
    }

    // Update UI
    document.getElementById(`driver${driverNum}Input`).value = '';
    document.getElementById(`driver${driverNum}Suggestions`).classList.add('hidden');
    document.getElementById(`driver${driverNum}Selected`).classList.remove('hidden');
    document.getElementById(`driver${driverNum}Name`).textContent = `${driver.givenName} ${driver.familyName}`;
    document.getElementById(`driver${driverNum}Id`).textContent = driver.driverId;
    document.getElementById(`driver${driverNum}Initial`).textContent = driver.familyName.charAt(0).toUpperCase();

    // Enable compare button if both selected
    updateCompareButton();
}

/**
 * Clear driver selection
 */
function clearDriver(driverNum) {
    if (driverNum === 1) {
        selectedDriver1 = null;
    } else {
        selectedDriver2 = null;
    }

    document.getElementById(`driver${driverNum}Selected`).classList.add('hidden');
    updateCompareButton();
}

/**
 * Update compare button state
 */
function updateCompareButton() {
    const btn = document.getElementById('compareBtn');
    btn.disabled = !(selectedDriver1 && selectedDriver2);
}

/**
 * Compare drivers using API client
 */
async function compareDrivers() {
    if (!selectedDriver1 || !selectedDriver2) return;

    // Show loading, hide results/errors
    const loadingState = document.getElementById('loadingState');
    const resultsDiv = document.getElementById('comparisonResults');
    const errorState = document.getElementById('errorState');
    
    showElement(loadingState);
    hideElement(resultsDiv);
    hideElement(errorState);

    try {
        const data = await getHeadToHead(selectedDriver1.driverId, selectedDriver2.driverId);
        displayComparison(data);

        // Update URL
        const url = new URL(window.location);
        url.searchParams.set('driver1', selectedDriver1.driverId);
        url.searchParams.set('driver2', selectedDriver2.driverId);
        window.history.pushState({}, '', url);

    } catch (error) {
        console.error('Comparison error:', error);
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.textContent = error.message;
        }
        showElement(errorState);
    } finally {
        hideElement(loadingState);
    }
}

/**
 * Display comparison results
 */
function displayComparison(data) {
    displayHeadToHeadSummary(data);
    displayStatsComparison(data);
    displayCareerTrajectory(data);
    displaySeasonBreakdown(data);
    displayRaceByRace(data);

    document.getElementById('comparisonResults').classList.remove('hidden');
    
    // Scroll to results
    const resultsDiv = document.getElementById('comparisonResults');
    showElement(resultsDiv);
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export functions for onclick handlers in HTML
window.selectDriver = selectDriver;
window.clearDriver = clearDriver;
window.compareDrivers = compareDrivers;* Display head-to-head summary
 */
function displayHeadToHeadSummary(data) {
    const h2h = data.headToHead;
    const driver1Name = `${selectedDriver1.givenName} ${selectedDriver1.familyName}`;
    const driver2Name = `${selectedDriver2.givenName} ${selectedDriver2.familyName}`;

    const html = `
        <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-3xl font-bold text-blue-600">${h2h.driver1Better}</div>
            <div class="text-sm text-gray-600">${driver1Name} better finishes</div>
        </div>
        <div class="text-center p-4 bg-gray-100 rounded-lg">
            <div class="text-3xl font-bold text-gray-700">${h2h.racesTogetherCount}</div>
            <div class="text-sm text-gray-600">Races together</div>
        </div>
        <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-3xl font-bold text-green-600">${h2h.driver2Better}</div>
            <div class="text-sm text-gray-600">${driver2Name} better finishes</div>
        </div>
    `;

    document.getElementById('h2hSummary').innerHTML = html;
}

/**
 * Display statistics comparison table
 */
function displayStatsComparison(data) {
    const stats1 = data.driver1.statistics;
    const stats2 = data.driver2.statistics;
    const driver1Name = `${selectedDriver1.familyName}`;
    const driver2Name = `${selectedDriver2.familyName}`;

    const statRows = [
        { label: 'Total Races', key: 'totalRaces' },
        { label: 'Wins', key: 'wins' },
        { label: 'Win Rate', calc: (s) => ((s.wins / s.totalRaces) * 100).toFixed(1) + '%' },
        { label: 'Podiums', key: 'podiums' },
        { label: 'Podium Rate', calc: (s) => ((s.podiums / s.totalRaces) * 100).toFixed(1) + '%' },
        { label: 'Pole Positions', key: 'polePositions' },
        { label: 'Fastest Laps', key: 'fastestLaps' },
        { label: 'Total Points', key: 'totalPoints' },
        { label: 'Points Per Race', calc: (s) => (s.totalPoints / s.totalRaces).toFixed(2) },
        { label: 'DNFs', key: 'dnfs' },
        { label: 'Teams', calc: (s) => s.teams.length },
        { label: 'Seasons', calc: (s) => s.seasons.length }
    ];

    const html = `
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statistic</th>
                    <th class="px-6 py-3 text-center text-xs font-medium text-blue-600 uppercase">${driver1Name}</th>
                    <th class="px-6 py-3 text-center text-xs font-medium text-green-600 uppercase">${driver2Name}</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                ${statRows.map(row => {
                    const val1 = row.calc ? row.calc(stats1) : stats1[row.key];
                    const val2 = row.calc ? row.calc(stats2) : stats2[row.key];
                    const num1 = parseFloat(val1);
                    const num2 = parseFloat(val2);
                    
                    // Determine which is better (lower is better for DNFs)
                    let class1 = '';
                    let class2 = '';
                    if (row.key !== 'dnfs') {
                        if (num1 > num2) class1 = 'stat-better';
                        else if (num2 > num1) class2 = 'stat-better';
                    } else {
                        if (num1 < num2) class1 = 'stat-better';
                        else if (num2 < num1) class2 = 'stat-better';
                    }

                    return `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${row.label}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-center ${class1}">${val1}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-center ${class2}">${val2}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;

    document.getElementById('statsComparison').innerHTML = html;
}

/**
 * Display career trajectory chart
 */
function displayCareerTrajectory(data) {
    const seasons1 = data.driver1.statistics.seasons;
    const seasons2 = data.driver2.statistics.seasons;

    // Get all unique years
    const allYears = [...new Set([...seasons1.map(s => s.season), ...seasons2.map(s => s.season)])].sort();

    // Map data by year
    const data1 = allYears.map(year => {
        const season = seasons1.find(s => s.season === year);
        return season ? season.wins : null;
    });

    const data2 = allYears.map(year => {
        const season = seasons2.find(s => s.season === year);
        return season ? season.wins : null;
    });

    // Destroy existing chart
    if (trajectoryChart) {
        trajectoryChart.destroy();
    }

    const ctx = document.getElementById('trajectoryChart').getContext('2d');
    trajectoryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allYears,
            datasets: [
                {
                    label: `${selectedDriver1.familyName}`,
                    data: data1,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    spanGaps: true
                },
                {
                    label: `${selectedDriver2.familyName}`,
                    data: data2,
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Wins Per Season'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Wins'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Season'
                    }
                }
            }
        }
    });
}

/**
 * Display season-by-season breakdown
 */
function displaySeasonBreakdown(data) {
    const seasons1 = data.driver1.statistics.seasons;
    const seasons2 = data.driver2.statistics.seasons;

    // Get common seasons
    const years1 = seasons1.map(s => s.season);
    const years2 = seasons2.map(s => s.season);
    const commonYears = years1.filter(y => years2.includes(y)).sort((a, b) => b - a);

    // Get all seasons sorted
    const allSeasons = [...seasons1, ...seasons2]
        .sort((a, b) => b.season - a.season)
        .filter((season, index, self) => 
            index === self.findIndex(s => s.season === season.season)
        )
        .slice(0, 10); // Show last 10 seasons

    const html = `
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Season</th>
                    <th class="px-4 py-3 text-center text-xs font-medium text-blue-600 uppercase">${selectedDriver1.familyName}</th>
                    <th class="px-4 py-3 text-center text-xs font-medium text-green-600 uppercase">${selectedDriver2.familyName}</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                ${allSeasons.map(season => {
                    const s1 = seasons1.find(s => s.season === season.season);
                    const s2 = seasons2.find(s => s.season === season.season);
                    const isCommon = commonYears.includes(season.season);

                    return `
                        <tr class="${isCommon ? 'common-season' : ''}">
                            <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">${season.season}</td>
                            <td class="px-4 py-3 text-sm text-center">
                                ${s1 ? `
                                    <div class="text-gray-900">${s1.wins} wins / ${s1.podiums} podiums</div>
                                    <div class="text-xs text-gray-500">${s1.races} races · ${s1.points} pts</div>
                                ` : '<span class="text-gray-400">—</span>'}
                            </td>
                            <td class="px-4 py-3 text-sm text-center">
                                ${s2 ? `
                                    <div class="text-gray-900">${s2.wins} wins / ${s2.podiums} podiums</div>
                                    <div class="text-xs text-gray-500">${s2.races} races · ${s2.points} pts</div>
                                ` : '<span class="text-gray-400">—</span>'}
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
        ${commonYears.length > 0 ? `
            <div class="mt-3 text-sm text-gray-600">
                <span class="inline-block w-4 h-4 bg-blue-100 border border-blue-300 rounded mr-2"></span>
                Common seasons highlighted
            </div>
        ` : ''}
    `;

    document.getElementById('seasonBreakdown').innerHTML = html;
}

/**
 * Display race-by-race comparison
 */
function displayRaceByRace(data) {
    const races = data.headToHead.races;

    if (races.length === 0) {
        document.getElementById('raceByRaceSection').classList.add('hidden');
        return;
    }

    // Show most recent 20 races
    const recentRaces = races.slice(0, 20);

    const html = `
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Race</th>
                    <th class="px-4 py-3 text-center text-xs font-medium text-blue-600 uppercase">${selectedDriver1.familyName}</th>
                    <th class="px-4 py-3 text-center text-xs font-medium text-green-600 uppercase">${selectedDriver2.familyName}</th>
                    <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Winner</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                ${recentRaces.map(race => {
                    const pos1 = race.driver1Position;
                    const pos2 = race.driver2Position;
                    
                    let winner = '—';
                    let class1 = '';
                    let class2 = '';
                    
                    if (pos1 && pos2) {
                        try {
                            const p1 = parseInt(pos1);
                            const p2 = parseInt(pos2);
                            if (p1 < p2) {
                                winner = selectedDriver1.familyName;
                                class1 = 'stat-better';
                            } else if (p2 < p1) {
                                winner = selectedDriver2.familyName;
                                class2 = 'stat-better';
                            }
                        } catch (e) {
                            // Handle non-numeric positions
                        }
                    }

                    return `
                        <tr>
                            <td class="px-4 py-3 whitespace-nowrap text-sm">
                                <div class="font-medium text-gray-900">${race.raceName}</div>
                                <div class="text-xs text-gray-500">${race.season} · Round ${race.round}</div>
                            </td>
                            <td class="px-4 py-3 whitespace-nowrap text-center text-sm ${class1}">P${pos1 || '—'}</td>
                            <td class="px-4 py-3 whitespace-nowrap text-center text-sm ${class2}">P${pos2 || '—'}</td>
                            <td class="px-4 py-3 whitespace-nowrap text-center text-sm text-gray-700">${winner}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
        ${races.length > 20 ? `
            <div class="mt-3 text-sm text-gray-600 text-center">
                Showing most recent 20 of ${races.length} races together
            </div>
        ` : ''}
    `;

    document.getElementById('raceByRace').innerHTML = html;
    document.getElementById('raceByRaceSection').classList.remove('hidden');
}
