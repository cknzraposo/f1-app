/**
 * Constructor List Page Controller
 * Handles browsing and searching the complete F1 constructor/team database
 * Grouped by country, sorted alphabetically
 */

import { getConstructors } from '../core/api-client.js';

// Page state
let allConstructors = [];
let filteredConstructors = [];
let currentPage = 1;
const ITEMS_PER_PAGE = 20;

/**
 * Initialize the constructor list page
 */
function init() {
    setupEventListeners();
    loadAllConstructors();
}

/**
 * Setup page event listeners
 */
function setupEventListeners() {
    const searchInput = document.getElementById('search');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            currentPage = 1; // Reset to first page on search
            filterConstructors();
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                displayConstructors();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredConstructors.length / ITEMS_PER_PAGE);
            if (currentPage < totalPages) {
                currentPage++;
                displayConstructors();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }
}

/**
 * Load all constructors from API and fetch their stats efficiently
 */
async function loadAllConstructors() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    try {
        if (loading) loading.classList.remove('hidden');
        if (error) error.classList.add('hidden');
        
        const data = await getConstructors();
        allConstructors = data.MRData?.ConstructorTable?.Constructors || [];
        
        if (allConstructors.length === 0) {
            throw new Error('No constructors found in database');
        }
        
        // Sort by constructor name alphabetically for initial display
        allConstructors.sort((a, b) => a.name.localeCompare(b.name));
        
        // Initialize filtered list
        filteredConstructors = [...allConstructors];
        
        // Display constructors (no stats needed for list view)
        displayConstructors();
        
        // Hide loading
        if (loading) loading.classList.add('hidden');
        
    } catch (err) {
        console.error('Error loading constructors:', err);
        if (loading) loading.classList.add('hidden');
        if (error) error.classList.remove('hidden');
    }
}

/**
 * Get constructors for the current page
 */
function getPaginatedConstructors() {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    return filteredConstructors.slice(startIndex, endIndex);
}

/**
 * Filter constructors based on search term (matches name or nationality)
 */
function filterConstructors() {
    const searchInput = document.getElementById('search');
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    
    filteredConstructors = allConstructors.filter(constructor => {
        return searchTerm === '' || 
            constructor.name.toLowerCase().includes(searchTerm) ||
            constructor.constructorId.toLowerCase().includes(searchTerm) ||
            constructor.nationality.toLowerCase().includes(searchTerm);
    });
    
    displayConstructors();
}

/**
 * Display constructors grouped by country (paginated)
 */
function displayConstructors() {
    const grid = document.getElementById('constructors-grid');
    const noResults = document.getElementById('no-results');
    const resultsCount = document.getElementById('results-count');
    const paginationControls = document.getElementById('pagination-controls');
    
    if (!grid) return;
    
    const totalPages = Math.ceil(filteredConstructors.length / ITEMS_PER_PAGE);
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, filteredConstructors.length);
    
    // Update results count
    if (resultsCount) {
        resultsCount.textContent = `Showing ${startIndex + 1}-${endIndex} of ${filteredConstructors.length} constructors (${allConstructors.length} total)`;
    }
    
    // Handle empty results
    if (filteredConstructors.length === 0) {
        grid.innerHTML = '';
        if (noResults) noResults.classList.remove('hidden');
        if (paginationControls) paginationControls.classList.add('hidden');
        return;
    }
    
    if (noResults) noResults.classList.add('hidden');
    
    // Update pagination controls
    updatePaginationControls(totalPages);
    
    // Get constructors for current page
    const paginatedConstructors = getPaginatedConstructors();
    
    // Group constructors by nationality
    const byNationality = {};
    paginatedConstructors.forEach(constructor => {
        if (!byNationality[constructor.nationality]) {
            byNationality[constructor.nationality] = [];
        }
        byNationality[constructor.nationality].push(constructor);
    });
    
    // Sort each nationality group alphabetically by name
    Object.keys(byNationality).forEach(nationality => {
        byNationality[nationality].sort((a, b) => a.name.localeCompare(b.name));
    });
    
    // Sort nationalities alphabetically
    const sortedNationalities = Object.keys(byNationality).sort();
    
    // Generate HTML for each nationality group
    let html = '';
    sortedNationalities.forEach(nationality => {
        const constructors = byNationality[nationality];
        
        html += `
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-red-600">
                    ${nationality} (${constructors.length})
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        `;
        
        constructors.forEach(constructor => {
            html += `
                <div class="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
                    <a href="constructor.html?id=${constructor.constructorId}" class="block p-6">
                        <div class="mb-3">
                            <h3 class="text-xl font-bold text-gray-900 hover:text-red-600">
                                ${constructor.name}
                            </h3>
                        </div>
                        
                        <div class="space-y-2">
                            <div class="flex items-center text-sm text-gray-600">
                                <span class="font-medium mr-2">🏴</span>
                                <span>${constructor.nationality}</span>
                            </div>
                            
                            <div class="flex items-center text-sm text-red-600">
                                <span class="font-medium mr-2">🔗</span>
                                <span class="hover:underline">
                                    View Details
                                </span>
                            </div>
                        </div>
                    </a>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
}



/**
 * Update pagination controls state
 */
function updatePaginationControls(totalPages) {
    const paginationControls = document.getElementById('pagination-controls');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    
    if (!paginationControls) return;
    
    // Show pagination if more than one page
    if (totalPages > 1) {
        paginationControls.classList.remove('hidden');
    } else {
        paginationControls.classList.add('hidden');
        return;
    }
    
    // Update page info
    if (pageInfo) {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    }
    
    // Update button states
    if (prevBtn) {
        prevBtn.disabled = currentPage <= 1;
    }
    
    if (nextBtn) {
        nextBtn.disabled = currentPage >= totalPages;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
