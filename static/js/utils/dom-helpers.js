/**
 * DOM Helper Functions
 * Utility functions for DOM manipulation
 */

/**
 * Show loading spinner in element
 * @param {HTMLElement} element - Container element
 * @param {string} message - Optional loading message
 */
export function showLoading(element, message = 'Loading...') {
    if (!element) return;
    
    element.innerHTML = `
        <div class="loading-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; color: #9ca3af;">
            <div class="spinner" style="width: 48px; height: 48px; border: 4px solid rgba(255,255,255,0.1); border-top-color: #e10600; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px;"></div>
            <div style="font-size: 0.875rem;">${message}</div>
        </div>
    `;
}

/**
 * Show error message in element
 * @param {HTMLElement} element - Container element
 * @param {string} message - Error message
 * @param {string} details - Optional error details
 */
export function showError(element, message, details = null) {
    if (!element) return;
    
    element.innerHTML = `
        <div class="error" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 20px; margin: 20px 0;">
            <div class="error-title" style="color: #ef4444; font-weight: 600; font-size: 1.125rem; margin-bottom: 8px;">
                ⚠️ Error
            </div>
            <p style="color: #fca5a5; margin: 0;">${message}</p>
            ${details ? `<p style="color: #9ca3af; font-size: 0.875rem; margin-top: 8px;">${details}</p>` : ''}
        </div>
    `;
}

/**
 * Show empty state in element
 * @param {HTMLElement} element - Container element
 * @param {string} message - Empty state message
 * @param {string} subtitle - Optional subtitle
 */
export function showEmpty(element, message = 'No results found', subtitle = 'Try a different query') {
    if (!element) return;
    
    element.innerHTML = `
        <div class="empty-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; color: #6b7280;">
            <div class="empty-icon" style="font-size: 4rem; margin-bottom: 16px;">🏁</div>
            <div class="empty-title" style="font-size: 1.25rem; font-weight: 600; color: #d1d5db; margin-bottom: 8px;">${message}</div>
            <p class="empty-text" style="margin: 0; font-size: 0.875rem;">${subtitle}</p>
        </div>
    `;
}

/**
 * Clear element content
 * @param {HTMLElement} element - Element to clear
 */
export function clearElement(element) {
    if (element) {
        element.innerHTML = '';
    }
}

/**
 * Create element from HTML string
 * @param {string} html - HTML string
 * @returns {HTMLElement} Created element
 */
export function createElementFromHTML(html) {
    const template = document.createElement('template');
    template.innerHTML = html.trim();
    return template.content.firstChild;
}

/**
 * Add CSS class with optional condition
 * @param {HTMLElement} element - Target element
 * @param {string} className - CSS class name
 * @param {boolean} condition - Whether to add the class
 */
export function toggleClass(element, className, condition) {
    if (!element) return;
    
    if (condition) {
        element.classList.add(className);
    } else {
        element.classList.remove(className);
    }
}

/**
 * Set element visibility
 * @param {HTMLElement} element - Target element
 * @param {boolean} visible - Whether element should be visible
 */
export function setVisibility(element, visible) {
    if (!element) return;
    
    if (visible) {
        element.classList.remove('hidden');
        element.style.display = '';
    } else {
        element.classList.add('hidden');
        element.style.display = 'none';
    }
}

/**
 * Smooth scroll to element
 * @param {HTMLElement} element - Target element
 * @param {Object} options - Scroll options
 */
export function scrollToElement(element, options = {}) {
    if (!element) return;
    
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
        ...options
    });
}

/**
 * Get element by ID with error handling
 * @param {string} id - Element ID
 * @returns {HTMLElement|null} Found element or null
 */
export function getElementById(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.warn(`Element with ID '${id}' not found`);
    }
    return element;
}

/**
 * Get all elements by selector
 * @param {string} selector - CSS selector
 * @param {HTMLElement} parent - Parent element (default: document)
 * @returns {Array<HTMLElement>} Array of elements
 */
export function querySelectorAll(selector, parent = document) {
    return Array.from(parent.querySelectorAll(selector));
}

/**
 * Add event listener with cleanup tracking
 * @param {HTMLElement} element - Target element
 * @param {string} event - Event name
 * @param {Function} handler - Event handler
 * @returns {Function} Cleanup function to remove listener
 */
export function addListener(element, event, handler) {
    if (!element) return () => {};
    
    element.addEventListener(event, handler);
    return () => element.removeEventListener(event, handler);
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, delay = 300) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Wait for element to appear in DOM
 * @param {string} selector - CSS selector
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<HTMLElement>} Resolves with element when found
 */
export function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }
        
        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        setTimeout(() => {
            observer.disconnect();
            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
        }, timeout);
    });
}
