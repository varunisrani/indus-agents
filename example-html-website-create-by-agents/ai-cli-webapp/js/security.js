/**
 * Security Module
 * Input sanitization, output sanitization, and security utilities
 */

// ================================
// Configuration
// ================================

const SECURITY_CONFIG = {
    // Allowed HTML tags for DOMPurify
    ALLOWED_TAGS: ['div', 'span', 'p', 'br', 'strong', 'em', 'code', 'pre', 
                   'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                   'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
    
    // Allowed attributes
    ALLOWED_ATTR: ['class', 'id', 'href', 'title', 'target', 'rel'],
    
    // Maximum command length
    MAX_COMMAND_LENGTH: 1000,
    
    // Rate limiting
    MAX_REQUESTS_PER_MINUTE: 10,
    MIN_REQUEST_INTERVAL: 500,
    
    // Blocked patterns
    BLOCKED_PATTERNS: [
        /<script/i,
        /javascript:/i,
        /onerror=/i,
        /onload=/i,
        /onclick=/i,
        /eval\(/i,
        /document\.cookie/i,
        /localStorage/i,
        /\.innerHTML/i,
        /dangerouslySetInnerHTML/i
    ]
};

// ================================
// Input Sanitization
// ================================

/**
 * Sanitize user command input
 * @param {string} input - Raw user input
 * @returns {object} { sanitized: string, safe: boolean, reason: string }
 */
export function sanitizeCommand(input) {
    if (!input || typeof input !== 'string') {
        return {
            sanitized: '',
            safe: true,
            reason: 'Empty or invalid input'
        };
    }
    
    // Check length
    if (input.length > SECURITY_CONFIG.MAX_COMMAND_LENGTH) {
        return {
            sanitized: '',
            safe: false,
            reason: `Command too long (max ${SECURITY_CONFIG.MAX_COMMAND_LENGTH} characters)`
        };
    }
    
    // Check for blocked patterns
    for (const pattern of SECURITY_CONFIG.BLOCKED_PATTERNS) {
        if (pattern.test(input)) {
            return {
                sanitized: '',
                safe: false,
                reason: `Blocked pattern detected: ${pattern}`
            };
        }
    }
    
    // Trim whitespace
    let sanitized = input.trim();
    
    // Remove null bytes
    sanitized = sanitized.replace(/\0/g, '');
    
    // Remove control characters (except newline, tab, carriage return)
    sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
    
    // Limit multiple spaces
    sanitized = sanitized.replace(/\s{2,}/g, ' ');
    
    return {
        sanitized: sanitized,
        safe: true,
        reason: 'Sanitized successfully'
    };
}

/**
 * Validate command against allowlist
 * @param {string} command - Command name
 * @param {Array} allowlist - Allowed commands
 * @returns {boolean}
 */
export function validateCommand(command, allowlist = []) {
    if (!command || typeof command !== 'string') {
        return false;
    }
    
    // If no allowlist provided, allow all (for development)
    if (allowlist.length === 0) {
        return true;
    }
    
    return allowlist.includes(command.toLowerCase());
}

/**
 * Sanitize file path
 * @param {string} path - File path
 * @returns {string}
 */
export function sanitizePath(path) {
    if (!path) return '';
    
    // Remove directory traversal attempts
    let sanitized = path.replace(/\.\./g, '');
    
    // Remove drive letters (Windows)
    sanitized = sanitized.replace(/^[A-Za-z]:/g, '');
    
    // Remove special characters
    sanitized = sanitized.replace(/[<>:"|?*]/g, '');
    
    // Limit length
    if (sanitized.length > 260) {
        sanitized = sanitized.substring(0, 260);
    }
    
    return sanitized.trim();
}

/**
 * Sanitize natural language input for AI
 * @param {string} input - User prompt
 * @returns {string}
 */
export function sanitizePrompt(input) {
    if (!input) return '';
    
    let sanitized = input.trim();
    
    // Remove potential prompt injection attempts
    sanitized = sanitized.replace(/\[SYSTEM\]/gi, '');
    sanitized = sanitized.replace(/\[IGNORE\]/gi, '');
    sanitized = sanitized.replace(/\[INSTRUCT\]/gi, '');
    
    // Remove instructions to ignore previous context
    sanitized = sanitized.replace(/ignore\s+(all\s+)?previous\s+(instructions?|text?)/gi, '');
    
    // Limit length
    if (sanitized.length > SECURITY_CONFIG.MAX_COMMAND_LENGTH) {
        sanitized = sanitized.substring(0, SECURITY_CONFIG.MAX_COMMAND_LENGTH);
    }
    
    return sanitized;
}

// ================================
// Output Sanitization (DOMPurify)
// ================================

/**
 * Sanitize HTML output using DOMPurify
 * @param {string} dirty - Dirty HTML
 * @returns {string} Clean HTML
 */
export function sanitizeOutput(dirty) {
    if (typeof window === 'undefined' || typeof DOMPurify === 'undefined') {
        // Fallback: strip all HTML tags
        return dirty.replace(/<[^>]*>/g, '');
    }
    
    return DOMPurify.sanitize(dirty, {
        ALLOWED_TAGS: SECURITY_CONFIG.ALLOWED_TAGS,
        ALLOWED_ATTR: SECURITY_CONFIG.ALLOWED_ATTR,
        ALLOW_DATA_ATTR: false,
        SAFE_FOR_TEMPLATES: true,
        SAFE_FOR_JQUERY: true,
        WHOLE_DOCUMENT: false,
        RETURN_DOM: false,
        RETURN_DOM_FRAGMENT: false,
        RETURN_TRUSTED_TYPE: false,
        FORCE_BODY: false,
        SANITIZE_DOM: true,
        KEEP_CONTENT: true
    });
}

/**
 * Sanitize markdown output
 * @param {string} markdown - Markdown content
 * @returns {string} Sanitized HTML
 */
export function sanitizeMarkdown(markdown) {
    // Basic markdown to HTML conversion (simplified)
    let html = markdown
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/`(.*?)`/gim, '<code>$1</code>')
        .replace(/\n/gim, '<br>');
    
    // Sanitize the resulting HTML
    return sanitizeOutput(html);
}

/**
 * Create safe element from HTML
 * @param {string} html - HTML string
 * @param {string} tagName - Tag name (default: 'div')
 * @returns {HTMLElement}
 */
export function createElement(html, tagName = 'div') {
    const sanitized = sanitizeOutput(html);
    const element = document.createElement(tagName);
    element.innerHTML = sanitized;
    return element;
}

// ================================
// Rate Limiting
// ================================

class RateLimiter {
    constructor(maxRequests, timeWindow) {
        this.maxRequests = maxRequests;
        this.timeWindow = timeWindow;
        this.requests = [];
    }
    
    canMakeRequest() {
        const now = Date.now();
        
        // Remove old requests outside time window
        this.requests = this.requests.filter(time => now - time < this.timeWindow);
        
        if (this.requests.length < this.maxRequests) {
            this.requests.push(now);
            return true;
        }
        
        return false;
    }
    
    getTimeUntilNextRequest() {
        const now = Date.now();
        const oldestRequest = this.requests[0];
        const timeElapsed = now - oldestRequest;
        const timeRemaining = this.timeWindow - timeElapsed;
        
        return Math.max(0, timeRemaining);
    }
}

// Create global rate limiter instance
const aiRateLimiter = new RateLimiter(
    SECURITY_CONFIG.MAX_REQUESTS_PER_MINUTE,
    60000 // 1 minute
);

/**
 * Check if AI request can be made
 * @returns {object} { allowed: boolean, waitTime: number }
 */
export function checkRateLimit() {
    const allowed = aiRateLimiter.canMakeRequest();
    const waitTime = aiRateLimiter.getTimeUntilNextRequest();
    
    return { allowed, waitTime };
}

/**
 * Reset rate limiter (for testing)
 */
export function resetRateLimiter() {
    aiRateLimiter.requests = [];
}

// ================================
// Content Security Policy
// ================================

/**
 * Check if CSP is supported
 * @returns {boolean}
 */
export function supportsCSP() {
    return typeof window !== 'undefined' && 
           window.SecurityPolicyViolationEvent !== undefined;
}

/**
 * Report CSP violation
 * @param {SecurityPolicyViolationEvent} event - CSP violation event
 */
export function reportCSPViolation(event) {
    console.error('CSP Violation:', {
        violatedDirective: event.violatedDirective,
        effectiveDirective: event.effectiveDirective,
        originalPolicy: event.originalPolicy,
        blockedURI: event.blockedURI,
        documentURI: event.documentURI,
        lineNumber: event.lineNumber,
        columnNumber: event.columnNumber
    });
}

// ================================
// XSS Protection
// ================================

/**
 * Check for XSS attack patterns
 * @param {string} input - Input to check
 * @returns {boolean}
 */
export function detectXSS(input) {
    const xssPatterns = [
        /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
        /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi, // Event handlers like onclick=
        /<img[^>]+src[^>]*>/gi,
        /<embed[^>]*>/gi,
        /<object[^>]*>/gi
    ];
    
    for (const pattern of xssPatterns) {
        if (pattern.test(input)) {
            return true;
        }
    }
    
    return false;
}

/**
 * Escape JavaScript string
 * @param {string} str - String to escape
 * @returns {string}
 */
export function escapeJS(str) {
    return str
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t')
        .replace(/\f/g, '\\f')
        .replace(/\v/g, '\\v')
        .replace(/\0/g, '\\0');
}

// ================================
// Security Headers
// ================================

/**
 * Get current security headers (for information)
 * @returns {object}
 */
export function getSecurityHeaders() {
    if (typeof window === 'undefined') return {};
    
    const metaTags = document.querySelectorAll('meta[http-equiv]');
    const headers = {};
    
    metaTags.forEach(tag => {
        const header = tag.getAttribute('http-equiv');
        const value = tag.getAttribute('content');
        headers[header] = value;
    });
    
    return headers;
}

// ================================
// Validation Utilities
// ================================

/**
 * Validate API key format
 * @param {string} key - API key to validate
 * @returns {boolean}
 */
export function validateApiKey(key) {
    if (!key || typeof key !== 'string') return false;
    
    // OpenAI API key format: sk-...
    const openAIKeyPattern = /^sk-[a-zA-Z0-9]{48}$/;
    
    return openAIKeyPattern.test(key);
}

/**
 * Check if input is safe for AI processing
 * @param {string} input - Input to check
 * @returns {object} { safe: boolean, reason: string }
 */
export function isSafeForAI(input) {
    const sanitization = sanitizeCommand(input);
    
    if (!sanitization.safe) {
        return {
            safe: false,
            reason: sanitization.reason
        };
    }
    
    // Check for prompt injection attempts
    const promptInjectionPatterns = [
        /ignore\s+(all\s+)?previous\s+/gi,
        /override\s+instructions/gi,
        /new\s+(task|instruction|command)/gi,
        /system\s*:/gi
    ];
    
    for (const pattern of promptInjectionPatterns) {
        if (pattern.test(input)) {
            return {
                safe: false,
                reason: 'Potential prompt injection detected'
            };
        }
    }
    
    return {
        safe: true,
        reason: 'Input is safe'
    };
}

// ================================
// Export
// ================================

export default {
    sanitizeCommand,
    validateCommand,
    sanitizePath,
    sanitizePrompt,
    sanitizeOutput,
    sanitizeMarkdown,
    createElement,
    checkRateLimit,
    resetRateLimiter,
    supportsCSP,
    reportCSPViolation,
    detectXSS,
    escapeJS,
    getSecurityHeaders,
    validateApiKey,
    isSafeForAI,
    SECURITY_CONFIG
};