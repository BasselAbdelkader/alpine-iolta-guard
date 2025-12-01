/**
 * Import Approval Management JavaScript
 * Handles viewing, approving, and rejecting pending imports
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    initializeApprovalPage();
});

// Global state
let pendingImports = [];
let currentUser = null;

async function initializeApprovalPage() {
    // Check authentication
    const isAuth = await api.isAuthenticated();
    if (!isAuth) {
        window.location.href = '/login.html';
        return;
    }

    // Load current user info
    await loadCurrentUser();

    // Load pending imports
    await loadPendingImports();

    // Set up event listeners
    setupEventListeners();
}

async function loadCurrentUser() {
    try {
        const response = await fetch('/api/auth/check/', {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

async function loadPendingImports() {
    try {
        console.log('Loading pending imports...');
        showLoading(true);

        console.log('Fetching /api/v1/imports/pending/');
        const response = await fetch('/api/v1/imports/pending/', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Failed to load pending imports (${response.status})`);
        }

        const data = await response.json();
        console.log('Received data:', data);
        pendingImports = data.pending_imports || [];
        const canApprove = data.can_approve || false;

        console.log(`Found ${pendingImports.length} pending imports, canApprove=${canApprove}`);

        // Display imports
        displayPendingImports(pendingImports, canApprove);

    } catch (error) {
        console.error('Error loading pending imports:', error);
        showAlert('danger', `Error loading imports: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displayPendingImports(imports, canApprove) {
    const container = document.getElementById('pendingImportsContainer');

    if (imports.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No pending imports at this time.
            </div>
        `;
        return;
    }

    container.innerHTML = imports.map(importData => {
        const canApproveThis = canApprove && importData.can_approve;
        const createdDate = new Date(importData.created_at);

        return `
            <div class="card mb-3 import-card" data-import-id="${importData.id}">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="mb-0">
                            <i class="fas fa-file-csv text-primary me-2"></i>
                            ${importData.filename}
                        </h5>
                        <small class="text-muted">
                            Imported by ${importData.created_by} on ${createdDate.toLocaleString()}
                        </small>
                    </div>
                    <span class="badge bg-warning">Pending Review</span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-box text-center">
                                <div class="stat-value text-primary">${importData.staging_counts.clients}</div>
                                <div class="stat-label">Clients</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-box text-center">
                                <div class="stat-value text-info">${importData.staging_counts.cases}</div>
                                <div class="stat-label">Cases</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-box text-center">
                                <div class="stat-value text-success">${importData.staging_counts.transactions}</div>
                                <div class="stat-label">Transactions</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-box text-center">
                                <div class="stat-value text-secondary">#${importData.id}</div>
                                <div class="stat-label">Batch ID</div>
                            </div>
                        </div>
                    </div>

                    ${canApproveThis ? `
                        <div class="mt-3 d-flex gap-2 justify-content-end">
                            <button class="btn btn-outline-secondary" onclick="viewImportDetails(${importData.id})">
                                <i class="fas fa-eye me-1"></i> View Details
                            </button>
                            <button class="btn btn-danger" onclick="rejectImport(${importData.id})">
                                <i class="fas fa-times me-1"></i> Reject
                            </button>
                            <button class="btn btn-success" onclick="approveImport(${importData.id})">
                                <i class="fas fa-check me-1"></i> Approve
                            </button>
                        </div>
                    ` : `
                        <div class="mt-3">
                            <div class="alert alert-info mb-0">
                                <i class="fas fa-info-circle me-2"></i>
                                ${importData.can_approve === false && canApprove ?
                                    'You cannot approve your own import. Another authorized user must review it.' :
                                    'You do not have permission to approve imports.'}
                            </div>
                        </div>
                    `}
                </div>
            </div>
        `;
    }).join('');
}

async function viewImportDetails(importId) {
    const importData = pendingImports.find(imp => imp.id === importId);
    if (!importData) {
        showAlert('danger', 'Import not found');
        return;
    }

    // TODO: Implement detailed view modal showing staging data
    // For now, show a summary
    const modal = `
        <div class="modal fade" id="importDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Import Details: ${importData.filename}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>Import Information</h6>
                        <table class="table table-sm">
                            <tr>
                                <th>Batch ID:</th>
                                <td>#${importData.id}</td>
                            </tr>
                            <tr>
                                <th>Filename:</th>
                                <td>${importData.filename}</td>
                            </tr>
                            <tr>
                                <th>Imported By:</th>
                                <td>${importData.created_by}</td>
                            </tr>
                            <tr>
                                <th>Import Date:</th>
                                <td>${new Date(importData.created_at).toLocaleString()}</td>
                            </tr>
                            <tr>
                                <th>Status:</th>
                                <td><span class="badge bg-warning">Pending Review</span></td>
                            </tr>
                        </table>

                        <h6 class="mt-4">Staging Data Summary</h6>
                        <table class="table table-sm">
                            <tr>
                                <th>Clients:</th>
                                <td>${importData.staging_counts.clients}</td>
                            </tr>
                            <tr>
                                <th>Cases:</th>
                                <td>${importData.staging_counts.cases}</td>
                            </tr>
                            <tr>
                                <th>Transactions:</th>
                                <td>${importData.staging_counts.transactions}</td>
                            </tr>
                        </table>

                        <div class="alert alert-info mt-3">
                            <i class="fas fa-info-circle me-2"></i>
                            This data is currently in staging and has not been committed to the production database.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('importDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modal);

    // Show modal
    const modalElement = document.getElementById('importDetailsModal');
    const bsModal = new bootstrap.Modal(modalElement);
    bsModal.show();

    // Clean up after modal is hidden
    modalElement.addEventListener('hidden.bs.modal', function () {
        modalElement.remove();
    });
}

async function approveImport(importId) {
    const importData = pendingImports.find(imp => imp.id === importId);
    if (!importData) {
        showAlert('danger', 'Import not found');
        return;
    }

    // Show confirmation dialog
    const confirmed = await showConfirmDialog(
        'Approve Import',
        `Are you sure you want to approve import "${importData.filename}"?<br><br>
        This will commit the following to production:<br>
        • ${importData.staging_counts.clients} clients<br>
        • ${importData.staging_counts.cases} cases<br>
        • ${importData.staging_counts.transactions} transactions<br><br>
        <strong>This action cannot be undone.</strong>`,
        'success'
    );

    if (!confirmed) {
        return;
    }

    try {
        showLoading(true);

        const response = await fetch(`/api/v1/imports/${importId}/approve/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'include'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to approve import');
        }

        const result = await response.json();

        showAlert('success', `Import approved successfully! Committed ${result.production_ids.clients.length} clients, ${result.production_ids.cases.length} cases, and ${result.production_ids.transactions.length} transactions to production.`);

        // Reload pending imports
        await loadPendingImports();

    } catch (error) {
        console.error('Error approving import:', error);
        showErrorModal('Import Approval Error', error.message);
    } finally {
        showLoading(false);
    }
}

async function rejectImport(importId) {
    const importData = pendingImports.find(imp => imp.id === importId);
    if (!importData) {
        showAlert('danger', 'Import not found');
        return;
    }

    // Prompt for rejection reason
    const reason = await promptForReason(
        'Reject Import',
        `Please provide a reason for rejecting import "${importData.filename}"`
    );

    if (!reason) {
        return; // User cancelled
    }

    try {
        showLoading(true);

        const response = await fetch(`/api/v1/imports/${importId}/reject/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'include',
            body: JSON.stringify({ reason: reason })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to reject import');
        }

        const result = await response.json();

        showAlert('warning', `Import rejected. Deleted ${result.deleted_counts.clients} clients, ${result.deleted_counts.cases} cases, and ${result.deleted_counts.transactions} transactions from staging.`);

        // Reload pending imports
        await loadPendingImports();

    } catch (error) {
        console.error('Error rejecting import:', error);
        showErrorModal('Import Rejection Error', error.message);
    } finally {
        showLoading(false);
    }
}

function showConfirmDialog(title, message, type = 'primary') {
    return new Promise((resolve) => {
        const modal = `
            <div class="modal fade" id="confirmModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-${type} text-white">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${message}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-${type}" id="confirmBtn">Confirm</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('confirmModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modal);

        // Show modal
        const modalElement = document.getElementById('confirmModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();

        // Handle confirm
        document.getElementById('confirmBtn').addEventListener('click', () => {
            bsModal.hide();
            resolve(true);
        });

        // Handle cancel/close
        modalElement.addEventListener('hidden.bs.modal', function () {
            modalElement.remove();
            resolve(false);
        });
    });
}

function promptForReason(title, message) {
    return new Promise((resolve) => {
        const modal = `
            <div class="modal fade" id="reasonModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-warning">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}:</p>
                            <textarea class="form-control" id="reasonText" rows="4" placeholder="Enter reason for rejection..." required></textarea>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-warning" id="submitReasonBtn">Submit</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('reasonModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modal);

        // Show modal
        const modalElement = document.getElementById('reasonModal');
        const bsModal = new bootstrap.Modal(modalElement);
        bsModal.show();

        // Handle submit
        document.getElementById('submitReasonBtn').addEventListener('click', () => {
            const reason = document.getElementById('reasonText').value.trim();
            if (!reason) {
                showAlert('warning', 'Please provide a reason for rejection');
                return;
            }
            bsModal.hide();
            resolve(reason);
        });

        // Handle cancel/close
        modalElement.addEventListener('hidden.bs.modal', function () {
            modalElement.remove();
            const reason = document.getElementById('reasonText')?.value.trim();
            if (!reason) {
                resolve(null);
            }
        });
    });
}

function showErrorModal(title, message) {
    // Create error modal that stays until user closes it
    const modal = `
        <div class="modal fade" id="errorModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-danger">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>${title}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-danger mb-0">
                            <strong>Error:</strong>
                            <div class="mt-2" style="white-space: pre-wrap;">${message}</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing error modal if any
    const existingModal = document.getElementById('errorModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modal);

    // Show modal
    const modalElement = document.getElementById('errorModal');
    const bsModal = new bootstrap.Modal(modalElement);
    bsModal.show();

    // Clean up after modal is hidden
    modalElement.addEventListener('hidden.bs.modal', function () {
        modalElement.remove();
    });
}

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadPendingImports);
    }
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

function showAlert(type, message) {
    const container = document.getElementById('alertContainer');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(alert);

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        alert.remove();
    }, 10000);
}

function getCSRFToken() {
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

function logout() {
    api.logout();
}
