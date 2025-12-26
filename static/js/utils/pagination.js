/**
 * Pagination Utilities
 * Helper functions for managing pagination state and rendering controls
 */

import { getCurrentPage, setCurrentPage, getPageSize, setPageSize } from '../core/state-manager.js';

/**
 * Calculate pagination metadata
 * @param {number} totalItems - Total number of items
 * @param {number} currentPage - Current page number (1-based)
 * @param {number} pageSize - Items per page
 * @returns {Object} Pagination metadata
 */
export function calculatePagination(totalItems, currentPage = null, pageSize = null) {
    const page = currentPage || getCurrentPage();
    const size = pageSize || getPageSize();
    
    const totalPages = Math.ceil(totalItems / size);
    const startIndex = (page - 1) * size;
    const endIndex = Math.min(startIndex + size, totalItems);
    
    return {
        currentPage: page,
        pageSize: size,
        totalItems,
        totalPages,
        startIndex,
        endIndex,
        startItem: startIndex + 1,
        endItem: endIndex,
        hasPrevious: page > 1,
        hasNext: page < totalPages,
        isFirstPage: page === 1,
        isLastPage: page === totalPages
    };
}

/**
 * Paginate array of data
 * @param {Array} data - Data array to paginate
 * @param {number} currentPage - Current page number (optional, uses state)
 * @param {number} pageSize - Items per page (optional, uses state)
 * @returns {Object} { data: paginatedData, pagination: metadata }
 */
export function paginateData(data, currentPage = null, pageSize = null) {
    if (!Array.isArray(data)) {
        return { data: [], pagination: calculatePagination(0, currentPage, pageSize) };
    }
    
    const pagination = calculatePagination(data.length, currentPage, pageSize);
    const paginatedData = data.slice(pagination.startIndex, pagination.endIndex);
    
    return {
        data: paginatedData,
        pagination
    };
}

/**
 * Render pagination controls HTML
 * @param {Object} pagination - Pagination metadata from calculatePagination
 * @param {string} onChangeCallback - Name of global function to call on page change
 * @returns {string} HTML string for pagination controls
 */
export function renderPaginationControls(pagination, onChangeCallback = 'changePage') {
    const { currentPage, totalPages, totalItems, startItem, endItem, hasPrevious, hasNext, isFirstPage, isLastPage } = pagination;
    
    if (totalPages <= 1) {
        return '';
    }
    
    return `
        <div class="pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 16px; background: rgba(255,255,255,0.03); border-radius: 8px;">
            <div class="pagination-info" style="color: #9ca3af; font-size: 0.875rem;">
                Showing ${startItem}-${endItem} of ${totalItems}
            </div>
            <div class="pagination-controls" style="display: flex; gap: 8px; align-items: center;">
                <button class="pagination-button" onclick="${onChangeCallback}(1)" ${isFirstPage ? 'disabled' : ''} 
                    style="padding: 6px 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #d1d5db; cursor: pointer; transition: all 0.2s; ${isFirstPage ? 'opacity: 0.5; cursor: not-allowed;' : ''}">
                    First
                </button>
                <button class="pagination-button" onclick="${onChangeCallback}(${currentPage - 1})" ${!hasPrevious ? 'disabled' : ''}
                    style="padding: 6px 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #d1d5db; cursor: pointer; transition: all 0.2s; ${!hasPrevious ? 'opacity: 0.5; cursor: not-allowed;' : ''}">
                    Previous
                </button>
                <span style="color: #888; padding: 0 10px;">Page ${currentPage} of ${totalPages}</span>
                <button class="pagination-button" onclick="${onChangeCallback}(${currentPage + 1})" ${!hasNext ? 'disabled' : ''}
                    style="padding: 6px 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #d1d5db; cursor: pointer; transition: all 0.2s; ${!hasNext ? 'opacity: 0.5; cursor: not-allowed;' : ''}">
                    Next
                </button>
                <button class="pagination-button" onclick="${onChangeCallback}(${totalPages})" ${isLastPage ? 'disabled' : ''}
                    style="padding: 6px 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #d1d5db; cursor: pointer; transition: all 0.2s; ${isLastPage ? 'opacity: 0.5; cursor: not-allowed;' : ''}">
                    Last
                </button>
                <select class="page-size-selector" onchange="changePageSize(this.value)"
                    style="padding: 6px 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: #d1d5db; cursor: pointer; margin-left: 8px;">
                    <option value="25" ${pagination.pageSize === 25 ? 'selected' : ''}>25 per page</option>
                    <option value="50" ${pagination.pageSize === 50 ? 'selected' : ''}>50 per page</option>
                    <option value="100" ${pagination.pageSize === 100 ? 'selected' : ''}>100 per page</option>
                </select>
            </div>
        </div>
    `;
}

/**
 * Change to specific page
 * @param {number} page - Target page number
 */
export function changePage(page) {
    setCurrentPage(page);
}

/**
 * Change page size
 * @param {number} size - New page size
 */
export function changePageSize(size) {
    setPageSize(parseInt(size));
}

/**
 * Go to next page
 */
export function nextPage() {
    const pagination = calculatePagination(Infinity); // We don't need total here
    if (pagination.hasNext) {
        setCurrentPage(pagination.currentPage + 1);
    }
}

/**
 * Go to previous page
 */
export function previousPage() {
    const page = getCurrentPage();
    if (page > 1) {
        setCurrentPage(page - 1);
    }
}

/**
 * Go to first page
 */
export function firstPage() {
    setCurrentPage(1);
}

/**
 * Go to last page
 * @param {number} totalItems - Total number of items
 */
export function lastPage(totalItems) {
    const pageSize = getPageSize();
    const totalPages = Math.ceil(totalItems / pageSize);
    setCurrentPage(totalPages);
}

/**
 * Reset pagination to first page
 */
export function resetPagination() {
    setCurrentPage(1);
}

/**
 * Get page numbers to display (for numbered pagination)
 * @param {number} currentPage - Current page
 * @param {number} totalPages - Total pages
 * @param {number} maxVisible - Maximum visible page numbers
 * @returns {Array<number|string>} Array of page numbers and '...' for gaps
 */
export function getPageNumbers(currentPage, totalPages, maxVisible = 7) {
    if (totalPages <= maxVisible) {
        return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    
    const pages = [];
    const halfVisible = Math.floor(maxVisible / 2);
    
    // Always show first page
    pages.push(1);
    
    let start = Math.max(2, currentPage - halfVisible);
    let end = Math.min(totalPages - 1, currentPage + halfVisible);
    
    // Adjust if we're near the beginning or end
    if (currentPage <= halfVisible) {
        end = maxVisible - 1;
    } else if (currentPage >= totalPages - halfVisible) {
        start = totalPages - maxVisible + 2;
    }
    
    // Add ellipsis after first page if needed
    if (start > 2) {
        pages.push('...');
    }
    
    // Add middle pages
    for (let i = start; i <= end; i++) {
        pages.push(i);
    }
    
    // Add ellipsis before last page if needed
    if (end < totalPages - 1) {
        pages.push('...');
    }
    
    // Always show last page
    if (totalPages > 1) {
        pages.push(totalPages);
    }
    
    return pages;
}
