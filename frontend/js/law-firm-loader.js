/**
 * Law Firm Info Loader
 * Lightweight utility to load ONLY law firm info (not full dashboard)
 * Used by all pages for sidebar/header display
 */

/**
 * Load law firm information - STATIC VALUES
 * Returns static hardcoded law firm data
 */
async function loadLawFirmInfo() {
    // Static law firm info - does not change
    return {
        firm_name: 'IOLTA Guard Insurance Law',
        address: '',
        city: 'San Francisco',
        state: 'CA',
        zip_code: '',
        phone: '(415) 555-0100',
        email: 'info@ioltaguard.com'
    };
}

/**
 * Update sidebar with law firm info
 * Handles both ID naming conventions (lawFirmName and firmNameSidebar)
 */
function updateSidebar(firmData) {
    // Try both ID naming conventions
    const firmNameElement = document.getElementById('lawFirmName') || document.getElementById('firmNameSidebar');
    const locationElement = document.getElementById('lawFirmLocation') || document.getElementById('firmLocation');
    const phoneElement = document.getElementById('lawFirmPhone') || document.getElementById('firmPhone');
    const emailElement = document.getElementById('lawFirmEmail') || document.getElementById('firmEmail');

    if (firmNameElement) {
        firmNameElement.textContent = firmData.firm_name || 'Law Firm';
    }

    if (locationElement) {
        const location = [firmData.city, firmData.state].filter(Boolean).join(', ');
        locationElement.textContent = location || '';
    }

    if (phoneElement) {
        phoneElement.textContent = firmData.phone || '';
    }

    if (emailElement) {
        emailElement.textContent = firmData.email || '';
    }
}

/**
 * Update header with law firm info
 * Handles both ID naming conventions
 */
function updateHeader(firmData) {
    // Try both header ID conventions
    const headerNameElement = document.getElementById('firmNameHeader');
    const headerAddressElement = document.getElementById('headerFirmAddress') || document.getElementById('firmAddressFull');

    if (headerNameElement) {
        headerNameElement.textContent = firmData.firm_name || 'IOLTA Guard Insurance Law';
    }

    if (headerAddressElement) {
        // Build clean location string
        const location = [firmData.city, firmData.state].filter(Boolean).join(', ');
        const addressParts = [location, firmData.phone, firmData.email].filter(Boolean);
        headerAddressElement.textContent = addressParts.join(' | ');
    }
}

/**
 * Initialize law firm info on page load
 * Loads in background - HTML has default values so no "Loading..." flash
 */
async function initLawFirmInfo() {
    // Don't block page load - run in background
    setTimeout(async () => {
        try {
            const firmData = await loadLawFirmInfo();
            // Only update if we got valid data and it's different from defaults
            if (firmData && firmData.firm_name) {
                updateSidebar(firmData);
                updateHeader(firmData);
            }
        } catch (error) {
            // console.error('Failed to load law firm info:', error);
            // Keep default HTML values
        }
    }, 0);

    // Return immediately so page continues loading
    return null;
}
