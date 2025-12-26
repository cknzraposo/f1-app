/**
 * Results Page Controller
 * Handles query results display and rendering
 */

import { executeQuery } from '../core/api-client.js';
import { setCurrentResults, getCurrentData, getCurrentDataType } from '../core/state-manager.js';
import { renderResults } from '../components/table-renderer.js';
import { showLoading, showError } from '../utils/dom-helpers.js';
import { parseQueryString } from '../utils/formatters.js';

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize results page
 */
async function init() {
    console.log('Initializing results page...');
    
    // Get query from URL
    const params = parseQueryString(window.location.search);
    const query = params.q;
    
    if (!query) {
        showError(
            document.getElementById('resultsContent'),
            'No query provided',
            'Please go back and enter a search query'
        );
        return;
    }
    
    // Display query
    const queryDisplay = document.getElementById('queryDisplay');
    if (queryDisplay) {
        queryDisplay.textContent = query;
    }
    
    // Execute query
    await executeQueryAndRender(query);
}

// ============================================
// QUERY EXECUTION
// ============================================

/**
 * Execute query and render results
 */
async function executeQueryAndRender(query) {
    const resultsContent = document.getElementById('resultsContent');
    
    if (!resultsContent) {
        console.error('Results content element not found');
        return;
    }
    
    // Show loading state
    showLoading(resultsContent, 'Executing query...');
    
    const startTime = performance.now();
    
    try {
        const result = await executeQuery(query);
        
        const endTime = performance.now();
        const processingTime = Math.round(endTime - startTime);
        
        if (!result.success) {
            throw new Error(result.error || 'Query returned unsuccessful');
        }
        
        // Store results in state
        setCurrentResults(result.data, result.dataType);
        
        // Clear loading
        resultsContent.innerHTML = '';
        
        // Show processing info banner
        showProcessingInfo(resultsContent, processingTime, result.action || 'keyword_parser', result.dataType);
        
        // Render results
        renderResults(result.data, result.dataType, resultsContent);
        
    } catch (error) {
        showError(resultsContent, 'Query failed', error.message);
    }
}

/**
 * Show processing information banner
 */
function showProcessingInfo(container, timeMs, source, dataType) {
    // Determine source label and color
    let sourceLabel = '⚡ Keyword Parser';
    let sourceColor = '#10b981'; // green
    
    if (source.includes('llm')) {
        sourceLabel = '🤖 LLM';
        sourceColor = '#3b82f6'; // blue
    }
    
    // Create processing info banner
    const infoBanner = `
        <div class="processing-info" style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; font-size: 0.875rem;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="color: ${sourceColor}; font-weight: 600;">${sourceLabel}</span>
                <span style="color: #6b7280;">•</span>
                <span style="color: #374151;">
                    <strong>${timeMs}ms</strong> response time
                </span>
                <span style="color: #6b7280;">•</span>
                <span style="color: #374151;">
                    Type: <strong>${dataType.replace(/_/g, ' ')}</strong>
                </span>
            </div>
            <div style="color: #9ca3af; font-size: 0.75rem;">
                ${new Date().toLocaleTimeString()}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', infoBanner);
}

// ============================================
// PAGINATION HANDLERS (Global)
// ============================================

/**
 * Change to specific page (called from pagination controls)
 */
window.changePage = function(page) {
    const data = getCurrentData();
    const dataType = getCurrentDataType();
    const container = document.getElementById('resultsContent');
    
    if (data && dataType && container) {
        // Import dynamically to avoid circular dependency
        import('../core/state-manager.js').then(({ setCurrentPage }) => {
            setCurrentPage(page);
            renderResults(data, dataType, container);
        });
    }
};

/**
 * Change page size (called from pagination controls)
 */
window.changePageSize = function(size) {
    const data = getCurrentData();
    const dataType = getCurrentDataType();
    const container = document.getElementById('resultsContent');
    
    if (data && dataType && container) {
        // Import dynamically to avoid circular dependency
        import('../core/state-manager.js').then(({ setPageSize }) => {
            setPageSize(parseInt(size));
            renderResults(data, dataType, container);
        });
    }
};

// ============================================
// START APPLICATION
// ============================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
