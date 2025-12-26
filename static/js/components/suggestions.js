/**
 * Smart Query Suggestions Component
 * Generates contextual query suggestions based on user input
 */

import { getAllDrivers, getAllConstructors } from '../core/state-manager.js';

/**
 * Generate smart suggestions based on input
 * @param {string} input - User's current input text
 * @returns {Array<string>} Array of suggestion strings
 */
export function generateSuggestions(input) {
    if (!input || input.length < 3) {
        return [];
    }
    
    const lowerInput = input.toLowerCase();
    const suggestions = [];
    
    // Year-based suggestions
    const yearMatch = input.match(/\d{4}/);
    if (yearMatch) {
        const year = yearMatch[0];
        if (year >= 1984 && year <= 2024) {
            suggestions.push(`Who won the ${year} championship?`);
            suggestions.push(`${year} standings`);
            suggestions.push(`${year} race winners`);
        }
    }
    
    // Driver-based suggestions
    const drivers = getAllDrivers();
    const driverMatch = drivers.find(d => 
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
    const constructors = getAllConstructors();
    const constructorMatch = constructors.find(c =>
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
    
    // General suggestions if no specific context
    if (suggestions.length === 0 && !yearMatch && !driverMatch && !constructorMatch) {
        if (lowerInput.includes('champion')) {
            suggestions.push('Who won the 2023 championship?');
            suggestions.push('Most championships all time');
        } else if (lowerInput.includes('win')) {
            suggestions.push('Most wins 2023');
            suggestions.push('Most wins all time');
        } else if (lowerInput.includes('pole')) {
            suggestions.push('Most pole positions 2023');
            suggestions.push('Most pole positions all time');
        }
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
