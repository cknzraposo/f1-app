/**
 * Data Formatters and Transformers
 * Helper functions for data manipulation and display
 */

import { getAllDrivers } from '../core/state-manager.js';

/**
 * Get nested value from object using dot notation path
 * @param {Object} obj - The source object
 * @param {string} path - Dot-separated path (e.g., 'driver.name')
 * @returns {*} The value at the path, or undefined
 */
export function getNestedValue(obj, path) {
    if (!path || !obj) return undefined;
    
    if (path.includes('.')) {
        const parts = path.split('.');
        let value = obj;
        for (const part of parts) {
            value = value?.[part];
            if (value === undefined) break;
        }
        return value;
    }
    return obj[path];
}

/**
 * Check if a column key represents driver information
 * @param {string} columnKey - The column key to check
 * @returns {boolean} True if column contains driver info
 */
export function isDriverColumn(columnKey) {
    const driverKeys = ['name', 'fullName', 'driver', 'driver.name', 'Driver.givenName', 'Driver.familyName'];
    return driverKeys.includes(columnKey);
}

/**
 * Extract driver ID from row data
 * @param {Object} row - The data row
 * @param {string} columnKey - The column key being processed
 * @returns {string|null} Driver ID or null if not found
 */
export function getDriverId(row, columnKey) {
    // Try multiple possible locations for driver ID
    if (row.driverId) return row.driverId;
    if (row.Driver?.driverId) return row.Driver.driverId;
    if (row.driver?.driverId) return row.driver.driverId;
    
    // If we have a name but no ID, try to find it from the global drivers list
    let driverName = null;
    if (columnKey === 'name' || columnKey === 'fullName') {
        driverName = row.name || row.fullName;
    } else if (columnKey === 'driver.name') {
        driverName = row.driver?.name;
    } else if (columnKey === 'Driver.familyName') {
        driverName = `${row.Driver?.givenName} ${row.Driver?.familyName}`;
    }
    
    if (driverName) {
        const drivers = getAllDrivers();
        const driver = drivers.find(d => {
            const fullName = `${d.givenName} ${d.familyName}`;
            return fullName === driverName || d.familyName === driverName;
        });
        if (driver) return driver.driverId;
    }
    
    return null;
}

/**
 * Create clickable driver link HTML
 * @param {string} driverName - The driver's display name
 * @param {string} driverId - The driver's ID
 * @returns {string} HTML string for driver link
 */
export function createDriverLink(driverName, driverId) {
    if (!driverName || driverName === 'N/A') return driverName;
    if (!driverId) return driverName;
    
    return `<a href="/static/drivers.html?id=${driverId}" class="driver-link" style="color: #60a5fa; text-decoration: none; font-weight: 600; transition: color 0.2s;" onmouseover="this.style.color='#93c5fd'" onmouseout="this.style.color='#60a5fa'">${escapeHtml(driverName)}</a>`;
}

/**
 * Format date string for display
 * @param {string} dateString - ISO date string or similar
 * @returns {string} Formatted date
 */
export function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Format time string (e.g., lap times)
 * @param {string} timeString - Time string (e.g., "1:23.456")
 * @returns {string} Formatted time
 */
export function formatTime(timeString) {
    if (!timeString) return 'N/A';
    return timeString;
}

/**
 * Format number with thousands separator
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    return num.toLocaleString();
}

/**
 * Format points with decimal places
 * @param {number} points - Points value
 * @returns {string} Formatted points
 */
export function formatPoints(points) {
    if (points === null || points === undefined) return '0';
    
    // Check if it has decimal places
    if (points % 1 !== 0) {
        return points.toFixed(1);
    }
    return points.toString();
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped HTML
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text with ellipsis if needed
 */
export function truncateText(text, maxLength = 50) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Get podium class for position
 * @param {number} position - Finishing position
 * @returns {string} CSS class name
 */
export function getPodiumClass(position) {
    if (position === 1) return 'podium-1';
    if (position === 2) return 'podium-2';
    if (position === 3) return 'podium-3';
    return '';
}

/**
 * Parse query string parameters
 * @param {string} queryString - URL query string (with or without ?). If not provided, uses window.location.search
 * @returns {Object} Object with key-value pairs
 */
export function parseQueryString(queryString) {
    // If no queryString provided, use window.location.search
    const searchString = queryString !== undefined ? queryString : window.location.search;
    const params = new URLSearchParams(searchString);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

/**
 * Build query string from object
 * @param {Object} params - Object with key-value pairs
 * @returns {string} Query string (without leading ?)
 */
export function buildQueryString(params) {
    return new URLSearchParams(params).toString();
}

/**
 * Get ordinal suffix for a number (1st, 2nd, 3rd, etc.)
 * @param {number} num - The number to convert
 * @returns {string} Ordinal string (e.g., "1st", "2nd", "3rd")
 */
export function getOrdinal(num) {
    if (num === null || num === undefined) return '';
    
    const n = parseInt(num);
    if (isNaN(n)) return '';
    
    const suffix = ['th', 'st', 'nd', 'rd'];
    const v = n % 100;
    return n + (suffix[(v - 20) % 10] || suffix[v] || suffix[0]);
}
