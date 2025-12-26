/**
 * Driver List Page Controller
 * Handles browsing and searching the complete F1 driver database
 */

import { getDrivers } from '../core/api-client.js';
import { showLoading, showError } from '../utils/dom-helpers.js';

// Page state
let allDrivers = [];
let filteredDrivers = [];

/**
 * Initialize the driver list page
 */
function init() {
    setupEventListeners();
    loadAllDrivers();
}

/**
 * Setup page event listeners
 */
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const nationalityFilter = document.getElementById('nationalityFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterDrivers);
    }
    
    if (nationalityFilter) {
        nationalityFilter.addEventListener('change', filterDrivers);
    }
}

/**
 * Load all drivers from API
 */
async function loadAllDrivers() {
    const resultsContainer = document.getElementById('driverResults');
    
    try {
        showLoading(resultsContainer, 'Loading driver database...');
        
        const data = await getDrivers();
        allDrivers = data.MRData?.DriverTable?.Drivers || [];
        
        if (allDrivers.length === 0) {
            throw new Error('No drivers found in database');
        }
        
        // Populate nationality filter
        populateNationalityFilter();
        
        // Initial render
        filteredDrivers = [...allDrivers];
        renderDriverList();
        updateSearchStats();
        
    } catch (error) {
        console.error('Error loading drivers:', error);
        showError(resultsContainer, 'Error loading drivers', error.message);
    }
}

/**
 * Populate nationality dropdown with unique values
 */
function populateNationalityFilter() {
    const nationalitySelect = document.getElementById('nationalityFilter');
    if (!nationalitySelect) return;
    
    // Extract unique nationalities and sort
    const nationalities = [...new Set(allDrivers.map(d => d.nationality))].sort();
    
    // Clear existing options (keep "All Nationalities")
    nationalitySelect.innerHTML = '<option value="">All Nationalities</option>';
    
    // Add nationality options
    nationalities.forEach(nationality => {
        const option = document.createElement('option');
        option.value = nationality;
        option.textContent = nationality;
        nationalitySelect.appendChild(option);
    });
}

/**
 * Filter drivers based on search and nationality
 */
function filterDrivers() {
    const searchInput = document.getElementById('searchInput');
    const nationalityFilter = document.getElementById('nationalityFilter');
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedNationality = nationalityFilter ? nationalityFilter.value : '';
    
    filteredDrivers = allDrivers.filter(driver => {
        // Name matching
        const fullName = `${driver.givenName} ${driver.familyName}`.toLowerCase();
        const matchesSearch = !searchTerm || 
                             fullName.includes(searchTerm) || 
                             driver.familyName.toLowerCase().includes(searchTerm) ||
                             (driver.code && driver.code.toLowerCase().includes(searchTerm));
        
        // Nationality matching
        const matchesNationality = !selectedNationality || 
                                  driver.nationality === selectedNationality;
        
        return matchesSearch && matchesNationality;
    });
    
    renderDriverList();
    updateSearchStats();
}

/**
 * Render the driver list as cards
 */
function renderDriverList() {
    const resultsDiv = document.getElementById('driverResults');
    if (!resultsDiv) return;
    
    // Handle empty results
    if (filteredDrivers.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <h3>No drivers found</h3>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }
    
    // Limit display to first 100 for performance
    const displayDrivers = filteredDrivers.slice(0, 100);
    
    const driverCards = displayDrivers.map(driver => {
        const fullName = `${driver.givenName} ${driver.familyName}`;
        const driverId = driver.driverId;
        const nationality = driver.nationality || 'Unknown';
        const dob = driver.dateOfBirth || 'Unknown';
        const code = driver.code || '?';
        const number = driver.permanentNumber || 'N/A';
        
        return `
            <a href="/static/drivers.html?id=${driverId}" class="driver-card">
                <div class="driver-card-name">${fullName}</div>
                <div class="driver-card-info"><strong>Code:</strong> ${code}</div>
                <div class="driver-card-info"><strong>Number:</strong> #${number}</div>
                <div class="driver-card-info"><strong>Nationality:</strong> ${nationality}</div>
                <div class="driver-card-info"><strong>Born:</strong> ${dob}</div>
            </a>
        `;
    }).join('');
    
    resultsDiv.innerHTML = `<div class="driver-grid">${driverCards}</div>`;
    
    // Show truncation notice if applicable
    if (filteredDrivers.length > 100) {
        resultsDiv.innerHTML += `
            <div style="text-align: center; margin-top: 2rem; color: #666; padding: 1rem;">
                Showing first 100 of ${filteredDrivers.length} drivers. 
                Use search to narrow results.
            </div>
        `;
    }
}

/**
 * Update search statistics display
 */
function updateSearchStats() {
    const statsDiv = document.getElementById('searchStats');
    if (!statsDiv) return;
    
    const total = allDrivers.length;
    const showing = filteredDrivers.length;
    
    if (showing === total) {
        statsDiv.textContent = `Showing all ${total} drivers`;
    } else {
        statsDiv.textContent = `Showing ${showing} of ${total} drivers`;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
