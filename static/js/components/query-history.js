/**
 * Query History Component
 * Manages localStorage-backed query history with UI rendering
 */

import {
    getQueryHistory,
    setQueryHistory,
    addToQueryHistory as addToStateHistory,
    clearQueryHistory as clearStateHistory
} from '../core/state-manager.js';

const STORAGE_KEY = 'f1QueryHistory';

/**
 * Load query history from localStorage
 */
export function loadQueryHistory() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            const history = JSON.parse(stored);
            setQueryHistory(history);
        }
    } catch (error) {
        console.error('Failed to load query history:', error);
        setQueryHistory([]);
    }
}

/**
 * Save query to history (persists to localStorage)
 */
export function saveQueryToHistory(query) {
    if (!query || !query.trim()) return;
    
    // Update state
    addToStateHistory(query);
    
    // Persist to localStorage
    try {
        const history = getQueryHistory();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
        console.error('Failed to save query history:', error);
    }
}

/**
 * Clear all query history
 */
export function clearQueryHistory() {
    clearStateHistory();
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
        console.error('Failed to clear query history:', error);
    }
}

/**
 * Show query history dropdown
 * @param {HTMLElement} historyElement - The history dropdown container
 * @param {Function} onSelect - Callback when history item is clicked
 */
export function showQueryHistory(historyElement, onSelect) {
    if (!historyElement) {
        console.error('Query History: Missing history element');
        return;
    }
    
    const history = getQueryHistory();
    
    if (history.length === 0) {
        historyElement.classList.remove('active');
        return;
    }
    
    // Render history (show only last 5)
    historyElement.innerHTML = `
        <div class="history-header">
            <span>Recent Queries</span>
            <button class="clear-history">Clear</button>
        </div>
        ${history.slice(0, 5).map(q => `
            <div class="history-item" data-query="${escapeHtml(q.text)}">
                <svg class="history-icon" viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M13,3A9,9 0 0,0 4,12H1L4.89,15.89L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3Z"/>
                </svg>
                ${escapeHtml(q.text)}
            </div>
        `).join('')}
    `;
    
    // Add click handler for history items
    historyElement.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const query = item.dataset.query;
            if (onSelect) {
                onSelect(query);
            }
        });
    });
    
    // Add click handler for clear button
    const clearButton = historyElement.querySelector('.clear-history');
    if (clearButton) {
        clearButton.addEventListener('click', (e) => {
            e.stopPropagation();
            clearQueryHistory();
            hideQueryHistory(historyElement);
        });
    }
    
    historyElement.classList.add('active');
}

/**
 * Hide query history dropdown
 */
export function hideQueryHistory(historyElement) {
    if (historyElement) {
        historyElement.classList.remove('active');
    }
}

/**
 * Initialize query history on an input element
 * @param {HTMLElement} inputElement - The search input element
 * @param {HTMLElement} historyElement - The history dropdown container
 * @param {Function} onSelect - Callback when history item is selected
 */
export function initQueryHistory(inputElement, historyElement, onSelect) {
    if (!inputElement || !historyElement) {
        console.error('Query History: Missing required elements');
        return;
    }
    
    // Load history on init
    loadQueryHistory();
    
    // Show history on focus if input is empty
    inputElement.addEventListener('focus', () => {
        if (!inputElement.value.trim()) {
            showQueryHistory(historyElement, onSelect);
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
 * Get recent queries (for external use)
 */
export function getRecentQueries(limit = 5) {
    const history = getQueryHistory();
    return history.slice(0, limit).map(q => q.text);
}
