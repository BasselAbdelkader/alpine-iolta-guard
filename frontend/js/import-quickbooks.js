/**
 * QuickBooks Import Page JavaScript
 * Handles CSV upload, validation, and import
 */

// Authentication check - MUST be authenticated to access this page
(async () => {
    // Setup page protection against back button after logout
    if (!api.setupPageProtection()) {
        return; // User was logged out, redirect handled
    }

    const isAuth = await api.isAuthenticated();
    if (!isAuth) {
        window.location.href = '/login.html';
    }
})();

// API Configuration
const API_BASE_URL = '/api/v1';

// Global state
let selectedFile = null;
let validationResults = null;

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

function initializePage() {
    // Load law firm and user info
    loadLawFirmInfo();
    loadUserInfo();

    // Set up event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // File input change
    const csvFileInput = document.getElementById('csvFile');
    csvFileInput.addEventListener('change', handleFileSelect);

    // Validate button
    const validateBtn = document.getElementById('validateBtn');
    validateBtn.addEventListener('click', validateFile);

    // Import button
    const importBtn = document.getElementById('importBtn');
    importBtn.addEventListener('click', importData);

    // Back to upload button
    const backToUploadBtn = document.getElementById('backToUploadBtn');
    backToUploadBtn.addEventListener('click', () => {
        showSection('uploadSection');
        resetUpload();
    });

    // Import another button
    const importAnotherBtn = document.getElementById('importAnotherBtn');
    importAnotherBtn.addEventListener('click', () => {
        showSection('uploadSection');
        resetUpload();
    });
}

function handleFileSelect(event) {
    const file = event.target.files[0];

    if (!file) {
        selectedFile = null;
        document.getElementById('validateBtn').disabled = true;
        return;
    }

    // Check if it's a CSV file
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showAlert('danger', 'Please select a CSV file');
        selectedFile = null;
        document.getElementById('validateBtn').disabled = true;
        return;
    }

    selectedFile = file;
    document.getElementById('validateBtn').disabled = false;

    console.log('File selected:', file.name, file.size, 'bytes');
}

async function validateFile() {
    if (!selectedFile) {
        showAlert('danger', 'Please select a file first');
        return;
    }

    // Show loading state
    const validateBtn = document.getElementById('validateBtn');
    const originalText = validateBtn.innerHTML;
    validateBtn.disabled = true;
    validateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Validating...';

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Make API call
        const response = await fetch(`${API_BASE_URL}/quickbooks/validate/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'include',
            body: formData
        });

        // Check content type before parsing
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            throw new Error(`Server returned ${response.status}: ${response.statusText}. Expected JSON but got ${contentType || 'unknown'}`);
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Validation failed');
        }

        // Store results
        validationResults = data;

        // Display validation results
        displayValidationResults(data);

        // Show validation section
        showSection('validationSection');

    } catch (error) {
        console.error('Validation error:', error);
        showAlert('danger', `Validation failed: ${error.message}`);
    } finally {
        // Restore button
        validateBtn.disabled = false;
        validateBtn.innerHTML = originalText;
    }
}

function displayValidationResults(data) {
    const summary = data.summary || {};
    const errors = data.errors || [];
    const warnings = data.warnings || [];

    // Update stats
    document.getElementById('clientCount').textContent = summary.unique_clients || 0;
    document.getElementById('transactionCount').textContent = summary.total_rows || 0;
    document.getElementById('validRowCount').textContent = summary.valid_rows || 0;
    document.getElementById('errorCount').textContent = summary.error_rows || 0;

    // Display warnings
    if (warnings.length > 0) {
        document.getElementById('warningsContainer').style.display = 'block';
        const warningsList = document.getElementById('warningsList');
        warningsList.innerHTML = warnings.map(warning => `
            <div class="warning-item">
                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                ${warning.message}
            </div>
        `).join('');
    } else {
        document.getElementById('warningsContainer').style.display = 'none';
    }

    // Display errors
    if (errors.length > 0) {
        document.getElementById('errorsContainer').style.display = 'block';
        const errorsList = document.getElementById('errorsList');
        errorsList.innerHTML = errors.map(error => {
            let errorMsg = '';
            if (error.row) {
                errorMsg += `<strong>Row ${error.row}:</strong> `;
            }
            if (error.field) {
                errorMsg += `<strong>${error.field}</strong> - `;
            }
            errorMsg += error.error;
            if (error.value) {
                errorMsg += ` (value: "${error.value}")`;
            }

            return `
                <div class="error-item">
                    <i class="fas fa-times-circle text-danger me-2"></i>
                    ${errorMsg}
                </div>
            `;
        }).join('');
    } else {
        document.getElementById('errorsContainer').style.display = 'none';
    }

    // Enable/disable import button
    const importBtn = document.getElementById('importBtn');
    if (data.valid && summary.valid_rows > 0) {
        importBtn.disabled = false;
    } else {
        importBtn.disabled = true;
    }

    // Show success message if no errors
    if (errors.length === 0) {
        showAlert('success',
            `File validated successfully! Found ${summary.unique_clients} clients and ${summary.valid_rows} transactions ready to import.`,
            'validationSection'
        );
    }
}

async function importData() {
    if (!selectedFile) {
        showAlert('danger', 'Please select a file first');
        return;
    }

    // Show progress section
    showSection('progressSection');

    // Update progress
    updateProgress(10, 'Uploading file...');

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('skip_errors', 'true');  // Skip error rows

        updateProgress(30, 'Validating data...');

        // Make API call
        const response = await fetch(`${API_BASE_URL}/quickbooks/import/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'include',
            body: formData
        });

        updateProgress(60, 'Importing clients and cases...');

        // Check content type before parsing
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            throw new Error(`Server returned ${response.status}: ${response.statusText}. Expected JSON but got ${contentType || 'unknown'}`);
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Import failed');
        }

        updateProgress(90, 'Finalizing import...');

        // Small delay for effect
        await sleep(500);

        updateProgress(100, 'Complete!');

        // Display results
        displayImportResults(data);

        // Show summary section
        await sleep(500);
        showSection('summarySection');

    } catch (error) {
        console.error('Import error:', error);
        showSection('validationSection');
        showAlert('danger', `Import failed: ${error.message}`, 'validationSection');
    }
}

function displayImportResults(data) {
    const summary = data.summary || {};

    // Update summary stats
    document.getElementById('clientsCreated').textContent = summary.clients_created || 0;
    document.getElementById('clientsExisting').textContent = summary.clients_existing || 0;
    document.getElementById('casesCreated').textContent = summary.cases_created || 0;
    document.getElementById('transactionsImported').textContent = summary.transactions_imported || 0;
    document.getElementById('transactionsSkipped').textContent = summary.transactions_skipped || 0;
    document.getElementById('importDuration').textContent = summary.duration_seconds || 0;

    // Display import errors if any
    const errors = summary.errors || [];
    if (errors.length > 0) {
        document.getElementById('importErrorsContainer').style.display = 'block';
        const importErrorsList = document.getElementById('importErrorsList');
        importErrorsList.innerHTML = errors.map(error => {
            let errorMsg = '';
            if (error.row) {
                errorMsg += `Row ${error.row}: `;
            }
            if (error.client) {
                errorMsg += `Client "${error.client}": `;
            }
            errorMsg += error.error;

            return `<div><i class="fas fa-exclamation-circle me-2"></i>${errorMsg}</div>`;
        }).join('');
    } else {
        document.getElementById('importErrorsContainer').style.display = 'none';
    }
}

function updateProgress(percent, text) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
    progressText.textContent = text;
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionId).classList.add('active');

    // Scroll to top
    window.scrollTo(0, 0);
}

function resetUpload() {
    // Reset file input
    document.getElementById('csvFile').value = '';
    selectedFile = null;
    validationResults = null;

    // Reset buttons
    document.getElementById('validateBtn').disabled = true;
    document.getElementById('importBtn').disabled = true;

    // Clear validation results
    document.getElementById('clientCount').textContent = '0';
    document.getElementById('transactionCount').textContent = '0';
    document.getElementById('validRowCount').textContent = '0';
    document.getElementById('errorCount').textContent = '0';
    document.getElementById('warningsContainer').style.display = 'none';
    document.getElementById('errorsContainer').style.display = 'none';

    // Reset progress
    updateProgress(0, 'Initializing...');
}

function showAlert(type, message, containerId = 'uploadSection') {
    const container = document.getElementById(containerId);
    const existingAlert = container.querySelector('.alert');

    if (existingAlert) {
        existingAlert.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.insertBefore(alertDiv, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function loadLawFirmInfo() {
    // This would normally load from API
    // For now, use placeholder
    const firmName = localStorage.getItem('lawFirmName') || 'Sample Law Firm';
    document.getElementById('lawFirmName').textContent = firmName;
    document.getElementById('lawFirmDetails').textContent = '';
}

function loadUserInfo() {
    // This would normally load from API
    // For now, use placeholder
    const userName = localStorage.getItem('userName') || 'admin';
    document.getElementById('userName').textContent = userName;
    document.getElementById('headerUserName').textContent = userName;
}

function getCSRFToken() {
    // Get CSRF token from cookie
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function logout() {
    // Use API client's logout method
    api.logout();
}
