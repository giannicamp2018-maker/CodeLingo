/**
 * Main JavaScript file for the Programming Learning Platform
 * Handles client-side interactivity and AJAX requests
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
    
    // Initialize any global functionality here
    console.log('Programming Learning Platform loaded');
});

/**
 * Utility function to show a loading indicator
 * @param {boolean} show - Whether to show or hide the loading indicator
 */
function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

/**
 * Utility function to display error messages
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

/**
 * Utility function to hide error messages
 */
function hideError() {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

/**
 * Utility function to copy text to clipboard
 * @param {string} text - Text to copy to clipboard
 */
function copyToClipboard(text) {
    // Create a temporary textarea element
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        // Copy to clipboard
        document.execCommand('copy');
        // Show feedback (could be improved with a toast notification)
        alert('Copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy text:', err);
        alert('Failed to copy to clipboard');
    } finally {
        // Clean up
        document.body.removeChild(textarea);
    }
}

/**
 * Format code for display with syntax highlighting
 * This is a basic implementation - could be enhanced with a library like Prism.js
 * @param {string} code - Code to format
 * @param {string} language - Programming language
 */
function formatCode(code, language) {
    // Basic formatting - in a real application, you might use a syntax highlighter
    // For now, we'll just return the code as-is
    return code;
}

/**
 * Handle AJAX errors
 * @param {Error} error - Error object
 */
function handleAjaxError(error) {
    console.error('AJAX Error:', error);
    showError('An error occurred. Please try again.');
    showLoading(false);
}

// Export functions for use in other scripts (if using modules)
// For now, these are global functions accessible from HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showLoading,
        showError,
        hideError,
        copyToClipboard,
        formatCode,
        handleAjaxError
    };
}

