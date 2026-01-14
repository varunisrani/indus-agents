/**
 * Utility Functions
 * Common helper functions used across the application
 */

// ================================
// String Utilities
// ================================

/**
 * Truncate string to specified length
 * @param {string} str - String to truncate
 * @param {number} length - Maximum length
 * @param {string} suffix - Suffix to add (default: '...')
 * @returns {string}
 */
export function truncate(str, length, suffix = '...') {
    if (!str || str.length <= length) return str;
    return str.substring(0, length - suffix.length) + suffix;
}

/**
 * Escape HTML special characters
 * @param {string} str - String to escape
 * @returns {string}
 */
export function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Strip ANSI codes from string
 * @param {string} str - String with ANSI codes
 * @returns {string}
 */
export function stripAnsi(str) {
    return str.replace(/\x1b\[[0-9;]*m/g, '');
}

/**
 * Convert string to title case
 * @param {string} str - String to convert
 * @returns {string}
 */
export function toTitleCase(str) {
    return str.replace(/\w\S*/g, txt => 
        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
}

/**
 * Generate random string ID
 * @param {number} length - Length of ID (default: 8)
 * @returns {string}
 */
export function generateId(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// ================================
// Array Utilities
// ================================

/**
 * Remove duplicates from array
 * @param {Array} arr - Array with duplicates
 * @returns {Array}
 */
export function unique(arr) {
    return [...new Set(arr)];
}

/**
 * Shuffle array
 * @param {Array} arr - Array to shuffle
 * @returns {Array}
 */
export function shuffle(arr) {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * Chunk array into smaller arrays
 * @param {Array} arr - Array to chunk
 * @param {number} size - Chunk size
 * @returns {Array}
 */
export function chunk(arr, size) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    return chunks;
}

// ================================
// Object Utilities
// ================================

/**
 * Deep clone object
 * @param {object} obj - Object to clone
 * @returns {object}
 */
export function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Merge objects deeply
 * @param {object} target - Target object
 * @param {object} source - Source object
 * @returns {object}
 */
export function deepMerge(target, source) {
    const output = { ...target };
    if (isObject(target) && isObject(source)) {
        Object.keys(source).forEach(key => {
            if (isObject(source[key])) {
                if (!(key in target)) {
                    Object.assign(output, { [key]: source[key] });
                } else {
                    output[key] = deepMerge(target[key], source[key]);
                }
            } else {
                Object.assign(output, { [key]: source[key] });
            }
        });
    }
    return output;
}

/**
 * Check if value is object
 * @param {*} item - Item to check
 * @returns {boolean}
 */
export function isObject(item) {
    return item && typeof item === 'object' && !Array.isArray(item);
}

/**
 * Get nested object property
 * @param {object} obj - Object
 * @param {string} path - Path (e.g., 'a.b.c')
 * @param {*} defaultValue - Default value if not found
 * @returns {*}
 */
export function getNested(obj, path, defaultValue = undefined) {
    const value = path.split('.').reduce((acc, part) => acc && acc[part], obj);
    return value !== undefined ? value : defaultValue;
}

// ================================
// Number Utilities
// ================================

/**
 * Clamp number between min and max
 * @param {number} num - Number to clamp
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {number}
 */
export function clamp(num, min, max) {
    return Math.min(Math.max(num, min), max);
}

/**
 * Round number to specified decimals
 * @param {number} num - Number to round
 * @param {number} decimals - Number of decimals
 * @returns {number}
 */
export function round(num, decimals = 0) {
    const factor = Math.pow(10, decimals);
    return Math.round(num * factor) / factor;
}

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string}
 */
export function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// ================================
// Date Utilities
// ================================

/**
 * Format date to localized string
 * @param {Date} date - Date to format
 * @param {string} format - Format type ('short', 'long', 'full')
 * @returns {string}
 */
export function formatDate(date, format = 'short') {
    const options = {
        short: { month: 'short', day: 'numeric', year: 'numeric' },
        long: { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' },
        full: { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }
    };
    return date.toLocaleDateString(undefined, options[format]);
}

/**
 * Get relative time string (e.g., "2 hours ago")
 * @param {Date} date - Date to compare
 * @returns {string}
 */
export function getRelativeTime(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 7) {
        return formatDate(date, 'short');
    } else if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

// ================================
// Validation Utilities
// ================================

/**
 * Validate email address
 * @param {string} email - Email to validate
 * @returns {boolean}
 */
export function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate URL
 * @param {string} url - URL to validate
 * @returns {boolean}
 */
export function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * Validate hex color
 * @param {string} color - Color to validate
 * @returns {boolean}
 */
export function isValidHexColor(color) {
    return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
}

// ================================
// File Size Utilities
// ================================

/**
 * Format bytes to human readable size
 * @param {number} bytes - Bytes to format
 * @param {number} decimals - Number of decimals
 * @returns {string}
 */
export function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// ================================
// Debounce and Throttle
// ================================

/**
 * Debounce function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function}
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function execution
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in ms
 * @returns {Function}
 */
export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ================================
// DOM Utilities
// ================================

/**
 * Query selector with error handling
 * @param {string} selector - CSS selector
 * @param {Element} parent - Parent element (default: document)
 * @returns {Element}
 */
export function querySelector(selector, parent = document) {
    const element = parent.querySelector(selector);
    if (!element) {
        throw new Error(`Element not found: ${selector}`);
    }
    return element;
}

/**
 * Query selector all
 * @param {string} selector - CSS selector
 * @param {Element} parent - Parent element (default: document)
 * @returns {NodeList}
 */
export function querySelectorAll(selector, parent = document) {
    return parent.querySelectorAll(selector);
}

/**
 * Add event listener with cleanup
 * @param {Element} element - Target element
 * @param {string} event - Event name
 * @param {Function} handler - Event handler
 * @param {object} options - Event options
 * @returns {Function} Cleanup function
 */
export function addEventListener(element, event, handler, options = {}) {
    element.addEventListener(event, handler, options);
    return () => element.removeEventListener(event, handler, options);
}

// ================================
// Console Utilities
// ================================

/**
 * Safe console log (only in development)
 * @param {...*} args - Arguments to log
 */
export function log(...args) {
    if (window.__DEV__) {
        console.log('[AI CLI]', ...args);
    }
}

/**
 * Safe console warn
 * @param {...*} args - Arguments to warn
 */
export function warn(...args) {
    console.warn('[AI CLI]', ...args);
}

/**
 * Safe console error
 * @param {...*} args - Arguments to error
 */
export function error(...args) {
    console.error('[AI CLI]', ...args);
}

// ================================
// Performance Utilities
// ================================

/**
 * Measure function execution time
 * @param {Function} func - Function to measure
 * @returns {*} Function result
 */
export function measureTime(func) {
    const start = performance.now();
    const result = func();
    const end = performance.now();
    log(`Execution time: ${round(end - start, 2)}ms`);
    return result;
}

/**
 * Async sleep
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise}
 */
export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ================================
// Clipboard Utilities
// ================================

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>}
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        error('Failed to copy:', err);
        return false;
    }
}

// ================================
// LocalStorage Utilities
// ================================

/**
 * Safe get from localStorage
 * @param {string} key - Storage key
 * @param {*} defaultValue - Default value if not found
 * @returns {*}
 */
export function getStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (err) {
        error('Storage get error:', err);
        return defaultValue;
    }
}

/**
 * Safe set to localStorage
 * @param {string} key - Storage key
 * @param {*} value - Value to store
 * @returns {boolean}
 */
export function setStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (err) {
        error('Storage set error:', err);
        return false;
    }
}

/**
 * Remove from localStorage
 * @param {string} key - Storage key
 * @returns {boolean}
 */
export function removeStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (err) {
        error('Storage remove error:', err);
        return false;
    }
}

// Export all utilities
export default {
    truncate,
    escapeHtml,
    stripAnsi,
    toTitleCase,
    generateId,
    unique,
    shuffle,
    chunk,
    deepClone,
    deepMerge,
    isObject,
    getNested,
    clamp,
    round,
    formatNumber,
    formatDate,
    getRelativeTime,
    isValidEmail,
    isValidUrl,
    isValidHexColor,
    formatBytes,
    debounce,
    throttle,
    querySelector,
    querySelectorAll,
    addEventListener,
    log,
    warn,
    error,
    measureTime,
    sleep,
    copyToClipboard,
    getStorage,
    setStorage,
    removeStorage
};