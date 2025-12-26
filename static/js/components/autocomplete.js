/**
 * Autocomplete Component
 * Handles driver and constructor search autocomplete with keyboard navigation
 */

import {
    getAllDrivers,
    getAllConstructors,
    getAutocompleteIndex,
    setAutocompleteIndex,
    getAutocompleteTimeout,
    setAutocompleteTimeout
} from '../core/state-manager.js';

/**
 * Initialize autocomplete on an input element
 * @param {HTMLElement} inputElement - The search input element
 * @param {HTMLElement} autocompleteElement - The autocomplete dropdown container
 * @param {Function} onSelect - Callback when item is selected (value, type)
 */
export function initAutocomplete(inputElement, autocompleteElement, onSelect) {
    if (!inputElement || !autocompleteElement) {
        console.error('Autocomplete: Missing required elements');
        return;
    }
    
    // Debounced input handler
    inputElement.addEventListener('input', (e) => {
        handleAutocompleteInput(e.target.value, autocompleteElement, onSelect);
    });
    
    // Keyboard navigation
    inputElement.addEventListener('keydown', (e) => {
        const isOpen = autocompleteElement.classList.contains('active');
        
        if (e.key === 'ArrowDown' && isOpen) {
            e.preventDefault();
            navigateAutocomplete(autocompleteElement, 1);
        } else if (e.key === 'ArrowUp' && isOpen) {
            e.preventDefault();
            navigateAutocomplete(autocompleteElement, -1);
        } else if (e.key === 'Enter' && isOpen) {
            const index = getAutocompleteIndex();
            if (index >= 0) {
                e.preventDefault();
                const items = autocompleteElement.querySelectorAll('.autocomplete-item');
                if (items[index]) {
                    items[index].click();
                }
            }
        } else if (e.key === 'Escape') {
            hideAutocomplete(autocompleteElement);
        }
    });
}

/**
 * Handle input with debouncing
 */
function handleAutocompleteInput(value, autocompleteElement, onSelect) {
    const timeout = getAutocompleteTimeout();
    if (timeout) {
        clearTimeout(timeout);
    }
    
    if (!value || value.length < 2) {
        hideAutocomplete(autocompleteElement);
        return;
    }
    
    // Debounce: wait 300ms before showing autocomplete
    const newTimeout = setTimeout(() => {
        showAutocomplete(value, autocompleteElement, onSelect);
    }, 300);
    
    setAutocompleteTimeout(newTimeout);
}

/**
 * Show autocomplete results
 */
function showAutocomplete(query, autocompleteElement, onSelect) {
    const lowerQuery = query.toLowerCase();
    const results = [];
    
    // Search drivers
    const drivers = getAllDrivers();
    drivers.forEach(driver => {
        const fullName = `${driver.givenName} ${driver.familyName}`.toLowerCase();
        const familyName = driver.familyName.toLowerCase();
        
        if (fullName.includes(lowerQuery) || familyName.includes(lowerQuery)) {
            results.push({
                type: 'driver',
                label: `${driver.givenName} ${driver.familyName}`,
                sublabel: `${driver.nationality}${driver.permanentNumber ? ' • #' + driver.permanentNumber : ''}`,
                value: driver.driverId
            });
        }
    });
    
    // Search constructors
    const constructors = getAllConstructors();
    constructors.forEach(constructor => {
        const name = constructor.name.toLowerCase();
        
        if (name.includes(lowerQuery)) {
            results.push({
                type: 'constructor',
                label: constructor.name,
                sublabel: constructor.nationality,
                value: constructor.constructorId
            });
        }
    });
    
    // Limit to 10 results
    const limitedResults = results.slice(0, 10);
    
    if (limitedResults.length === 0) {
        hideAutocomplete(autocompleteElement);
        return;
    }
    
    // Render autocomplete
    autocompleteElement.innerHTML = limitedResults.map((result, index) => `
        <div class="autocomplete-item" data-index="${index}" data-value="${result.value}" data-type="${result.type}">
            <div class="autocomplete-main">${result.label}</div>
            <div class="autocomplete-sub">${result.sublabel}</div>
        </div>
    `).join('');
    
    // Add click handlers
    autocompleteElement.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
            if (onSelect) {
                onSelect(item.dataset.value, item.dataset.type);
            }
            hideAutocomplete(autocompleteElement);
        });
    });
    
    autocompleteElement.classList.add('active');
    setAutocompleteIndex(-1);
}

/**
 * Hide autocomplete dropdown
 */
export function hideAutocomplete(autocompleteElement) {
    if (autocompleteElement) {
        autocompleteElement.classList.remove('active');
        autocompleteElement.innerHTML = '';
    }
    setAutocompleteIndex(-1);
}

/**
 * Navigate autocomplete with arrow keys
 */
function navigateAutocomplete(autocompleteElement, direction) {
    const items = autocompleteElement.querySelectorAll('.autocomplete-item');
    if (items.length === 0) return;
    
    let index = getAutocompleteIndex();
    
    // Remove previous selection
    if (index >= 0 && index < items.length) {
        items[index].classList.remove('selected');
    }
    
    // Update index with wrapping
    index += direction;
    if (index < 0) index = items.length - 1;
    if (index >= items.length) index = 0;
    
    setAutocompleteIndex(index);
    
    // Add new selection
    items[index].classList.add('selected');
    items[index].scrollIntoView({ block: 'nearest' });
}

/**
 * Programmatically select an autocomplete item
 */
export function selectAutocompleteItem(value, type, inputElement, onSelect) {
    if (!inputElement) return;
    
    if (type === 'driver') {
        inputElement.value = `Tell me about ${value} stats`;
    } else if (type === 'constructor') {
        inputElement.value = `Tell me about ${value}`;
    }
    
    if (onSelect) {
        onSelect(value, type);
    }
}
