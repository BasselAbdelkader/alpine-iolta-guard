/**
 * Reports Page JavaScript
 * Handles reports dashboard display and navigation
 */

// Load law firm info on page load
document.addEventListener('DOMContentLoaded', async function() {
    // console.log('Reports page loaded');

    // Load law firm information using shared utility
    await initLawFirmInfo();
});

/**
 * Logout function
 */
function logout() {
    // Clear any stored session data
    localStorage.clear();
    sessionStorage.clear();

    // Redirect to login
    window.location.href = '/login';
}
