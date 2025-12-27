/**
 * Smart Query Suggestions Component
 * Generates contextual driver search suggestions based on user input
 */

import { getAllDrivers } from '../core/state-manager.js';

/**
 * Generate smart driver suggestions based on input
 * @param {string} input - User's current input text
 * @returns {Array<string>} Array of driver name suggestions
 */
export function generateSuggestions(input) {
    if (!input || input.length < 2) {
        return [];
    }
    
    const lowerInput = input.toLowerCase();
    const suggestions = [];
    
    // Get all drivers
    const drivers = getAllDrivers();
    
    // Find drivers that match the input
    const matchingDrivers = drivers.filter(d => {
        const fullName = `${d.givenName} ${d.familyName}`.toLowerCase();
        const familyName = d.familyName.toLowerCase();
        const givenName = d.givenName.toLowerCase();
        
        return fullName.includes(lowerInput) || 
               familyName.includes(lowerInput) || 
               givenName.includes(lowerInput);
    });
    
    // Add up to 5 matching drivers
    matchingDrivers.slice(0, 5).forEach(driver => {
        suggestions.push(`${driver.givenName} ${driver.familyName}`);
    });
    
    // If no matches, suggest popular drivers
    if (suggestions.length === 0) {
        const popularDrivers = ['Lewis Hamilton', 'Max Verstappen', 'Fernando Alonso', 'Sebastian Vettel', 'Michael Schumacher'];
        const availableDrivers = drivers.filter(d => 
            popularDrivers.includes(`${d.givenName} ${d.familyName}`)
        );
        availableDrivers.slice(0, 3).forEach(driver => {
            suggestions.push(`${driver.givenName} ${driver.familyName}`);
        });
    }
    
    return suggestions;
}

/**
 * Show suggestions in UI
 * @param {string} input - User's current input text
 * @param {HTMLElement} suggestionsElement - The suggestions container
 * @param {Function} onSelect - Callback when suggestion is clicked
 */
export function showSmartSuggestions(input, suggestionsElement, onSelect) {
    if (!suggestionsElement) {
        console.error('Suggestions: Missing suggestions element');
        return;
    }
    
    const suggestions = generateSuggestions(input);
    
    if (suggestions.length === 0) {
        hideSuggestions(suggestionsElement);
        return;
    }
    
    // Render suggestions (limit to 3)
    suggestionsElement.innerHTML = `
        <div class="suggestions-header">Suggested queries:</div>
        ${suggestions.slice(0, 3).map(s => `
            <div class="suggestion-item" data-query="${escapeHtml(s)}">
                <svg class="suggestion-icon" viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                </svg>
                ${escapeHtml(s)}
            </div>
        `).join('')}
    `;
    
    // Add click handlers
    suggestionsElement.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            const query = item.dataset.query;
            if (onSelect) {
                onSelect(query);
            }
        });
    });
    
    suggestionsElement.classList.add('active');
}

/**
 * Hide suggestions dropdown
 */
export function hideSuggestions(suggestionsElement) {
    if (suggestionsElement) {
        suggestionsElement.classList.remove('active');
    }
}

/**
 * Initialize suggestions on an input element
 * @param {HTMLElement} inputElement - The search input element
 * @param {HTMLElement} suggestionsElement - The suggestions container
 * @param {Function} onSelect - Callback when suggestion is selected
 */
export function initSuggestions(inputElement, suggestionsElement, onSelect) {
    if (!inputElement || !suggestionsElement) {
        console.error('Suggestions: Missing required elements');
        return;
    }
    
    inputElement.addEventListener('input', (e) => {
        const value = e.target.value;
        if (value.length > 2) {
            showSmartSuggestions(value, suggestionsElement, onSelect);
        } else {
            hideSuggestions(suggestionsElement);
        }
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Get popular/common suggestions (not context-dependent)
 */
export function getPopularSuggestions() {
    return [
        'Who won the 2024 championship?',
        'Who won the 2023 championship?',
        'Hamilton career stats',
        'Verstappen career stats',
        'Most wins 2024',
        'Compare Hamilton vs Verstappen',
        'Red Bull statistics',
        'Ferrari statistics'
    ];
}
