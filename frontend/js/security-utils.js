/**
 * Security utility functions to prevent XSS attacks
 */

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} unsafe - Untrusted user input
 * @returns {string} Safe HTML-escaped string
 */
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }

    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/\//g, "&#x2F;");
}

/**
 * Create a safe text node (alternative to innerHTML)
 * @param {HTMLElement} element - Target element
 * @param {string} text - Text to insert
 */
function setSafeText(element, text) {
    if (element) {
        element.textContent = text || '';
    }
}

/**
 * Create DOM element safely with attributes and content
 * @param {string} tag - HTML tag name
 * @param {Object} attrs - Attributes object
 * @param {string|Node} content - Content (text or child node)
 * @returns {HTMLElement}
 */
function createElement(tag, attrs = {}, content = null) {
    const element = document.createElement(tag);

    // Set attributes safely
    for (const [key, value] of Object.entries(attrs)) {
        if (key === 'className') {
            element.className = value;
        } else if (key.startsWith('data-')) {
            element.setAttribute(key, value);
        } else if (key === 'onclick' || key.startsWith('on')) {
            // Skip inline event handlers for security
            console.warn('Inline event handlers are not recommended. Use addEventListener instead.');
        } else {
            element.setAttribute(key, value);
        }
    }

    // Add content safely
    if (content !== null) {
        if (typeof content === 'string') {
            element.textContent = content;
        } else if (content instanceof Node) {
            element.appendChild(content);
        }
    }

    return element;
}

/**
 * Sanitize user input for display in HTML attributes
 * @param {string} input - User input
 * @returns {string} Sanitized string safe for HTML attributes
 */
function sanitizeAttribute(input) {
    if (!input) return '';
    return String(input)
        .replace(/[^a-zA-Z0-9\s\-_]/g, '') // Remove special characters
        .substring(0, 100); // Limit length
}

/**
 * Validate and sanitize numeric input
 * @param {any} input - Input value
 * @param {number} defaultValue - Default value if invalid
 * @returns {number} Validated number
 */
function sanitizeNumber(input, defaultValue = 0) {
    const num = Number(input);
    return isNaN(num) ? defaultValue : num;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        escapeHtml,
        setSafeText,
        createElement,
        sanitizeAttribute,
        sanitizeNumber
    };
}