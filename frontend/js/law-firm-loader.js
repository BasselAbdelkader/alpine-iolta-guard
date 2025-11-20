/**
 * Law Firm Info Loader
 * Lightweight utility to load ONLY law firm info (not full dashboard)
 * Used by all pages for sidebar/header display
 */

/**
 * Load law firm information from lightweight API
 * Returns promise with law firm data
 */
async function loadLawFirmInfo() {
    // Check if we already have it cached
    const cached = sessionStorage.getItem('lawFirmInfo');
    if (cached) {
        try {
            return JSON.parse(cached);
        } catch (e) {
            // Invalid cache, continue to fetch
        }
    }

    try {
        // Use the lightweight law firm API - NOT the full dashboard
        const response = await fetch('/api/v1/dashboard/law-firm/', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to load law firm info');
        }

        const firmData = await response.json();

        // Cache it for the session
        sessionStorage.setItem('lawFirmInfo', JSON.stringify(firmData));

        return firmData;
    } catch (error) {
        // console.error('Error loading law firm info:', error);
        // Return default values
        return {
            firm_name: 'Trust Account System',
            address: '',
            city: '',
            state: '',
            zip_code: '',
            phone: '',
            email: ''
        };
    }
}

/**
 * Update sidebar with law firm info
 */
function updateSidebar(firmData) {
    const elements = {
        lawFirmName: document.getElementById('lawFirmName'),
        lawFirmLocation: document.getElementById('lawFirmLocation'),
        lawFirmPhone: document.getElementById('lawFirmPhone'),
        lawFirmEmail: document.getElementById('lawFirmEmail')
    };

    if (elements.lawFirmName) {
        elements.lawFirmName.textContent = firmData.firm_name || 'Law Firm';
    }

    if (elements.lawFirmLocation) {
        const location = [firmData.city, firmData.state].filter(Boolean).join(', ');
        elements.lawFirmLocation.textContent = location;
    }

    if (elements.lawFirmPhone) {
        elements.lawFirmPhone.textContent = firmData.phone || '';
    }

    if (elements.lawFirmEmail) {
        elements.lawFirmEmail.textContent = firmData.email || '';
    }
}

/**
 * Update header with law firm info
 */
function updateHeader(firmData) {
    const headerFirmAddress = document.getElementById('headerFirmAddress');

    if (headerFirmAddress) {
        const addressParts = [
            firmData.address,
            firmData.city,
            firmData.state,
            firmData.zip_code
        ].filter(Boolean);

        headerFirmAddress.textContent = addressParts.join(', ');
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
