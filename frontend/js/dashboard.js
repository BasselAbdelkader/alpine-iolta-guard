/**
 * Dashboard Page JavaScript
 * Loads all dashboard data from API and populates the page
 */

// BUG #11 FIX: Check authentication and setup page protection on page load
(async () => {
    // Setup page protection against back button after logout
    if (!api.setupPageProtection()) {
        return; // User was logged out, redirect handled
    }

    const isAuth = await api.isAuthenticated();
    if (!isAuth) {
        window.location.href = '/login';
    }
})();

// Helper function to format currency
function formatCurrency(value) {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';

    if (num < 0) {
        return `($${Math.abs(num).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})})`;
    }
    return `$${num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

// Logout function
function logout() {
    api.logout();
}

// Load all dashboard data
async function loadDashboard() {
    try {
        // console.log('Loading dashboard data...');

        // Call dashboard API
        const data = await api.get('/v1/dashboard/');
        // console.log('Dashboard data received:', data);

        // Populate law firm info
        populateLawFirm(data.law_firm);

        // Populate metric cards
        populateMetricCards(data);

        // Populate trust health
        populateTrustHealth(data.trust_health, data.health_details);

        // Populate client tables
        populateClientTables(data);

        // Populate outstanding checks
        populateOutstandingChecks(data.outstanding_checks);

    } catch (error) {
        // console.error('Error loading dashboard:', error);

        // Show error message
        document.querySelector('main').innerHTML = `
            <div class="alert alert-danger">
                <h4><i class="fas fa-exclamation-triangle"></i> Error Loading Dashboard</h4>
                <p>${error.message}</p>
                <button class="btn btn-primary" onclick="loadDashboard()">Retry</button>
                <button class="btn btn-secondary" onclick="logout()">Logout</button>
            </div>
        `;
    }
}

// Populate law firm information
function populateLawFirm(lawFirm) {
    if (lawFirm) {
        document.getElementById('lawFirmName').textContent = lawFirm.firm_name;
        document.getElementById('lawFirmLocation').textContent = `${lawFirm.city}, ${lawFirm.state}`;
        document.getElementById('lawFirmPhone').textContent = lawFirm.phone;
        document.getElementById('lawFirmEmail').textContent = lawFirm.email;
    }
}

// Populate metric cards
function populateMetricCards(data) {
    // Trust Balance
    document.getElementById('trustBalance').textContent = formatCurrency(data.trust_balance);

    // Bank Register
    const bankBalance = parseFloat(data.bank_register_balance);
    const trustBalance = parseFloat(data.trust_balance);
    const balancesMatch = data.balances_match;

    document.getElementById('bankRegisterBalance').textContent = formatCurrency(data.bank_register_balance);

    const bankCard = document.getElementById('bankRegisterCard');
    const balanceMatchText = document.getElementById('balanceMatchText');

    if (balancesMatch) {
        bankCard.className = 'card text-white bg-success';
        balanceMatchText.textContent = '✓ Matches Trust Balance';
    } else {
        bankCard.className = 'card text-white bg-danger';
        balanceMatchText.textContent = `⚠ Diff: ${formatCurrency(data.balance_difference)}`;
    }

    // Clients with Funds
    document.getElementById('activeClientsCount').textContent = data.active_clients_count;

    // Next Reconciliation
    document.getElementById('nextReconciliation').textContent = data.next_reconciliation;
    document.getElementById('pendingCount').textContent = data.pending_transactions_count;
}

// Populate trust health section
function populateTrustHealth(trustHealth, healthDetails) {
    // Health score and status
    const score = trustHealth.score;
    const status = trustHealth.status;
    const color = trustHealth.color;

    document.getElementById('healthScore').textContent = score;
    document.getElementById('healthStatus').textContent = status;
    document.getElementById('healthStatus').className = `badge bg-${color} fs-6`;
    document.getElementById('healthScoreCircle').className =
        `text-white rounded-circle d-flex align-items-center justify-content-center bg-${color}`;

    // Total issues badge
    const totalIssues = trustHealth.issues.length + trustHealth.warnings.length;
    document.getElementById('healthIssuesBadge').textContent = totalIssues;

    // Warnings
    document.getElementById('warningsCount').textContent = trustHealth.warnings.length;
    const warningsContainer = document.getElementById('warningsContainer');

    if (trustHealth.warnings.length === 0) {
        warningsContainer.innerHTML = '<small class="text-muted">No warnings</small>';
    } else {
        warningsContainer.innerHTML = '<ul class="list-unstyled mb-0">' +
            trustHealth.warnings.map(warning => {
                // Make uncleared transactions warning clickable
                if (warning.toLowerCase().includes('uncleared transactions')) {
                    return `
                        <li class="small text-warning mb-2">
                            <i class="fas fa-minus me-1"></i>
                            <a href="/uncleared-transactions" target="_blank" class="text-warning text-decoration-none" style="border-bottom: 1px dotted;">
                                ${warning}
                            </a>
                        </li>
                    `;
                // Make unallocated funds warning clickable
                } else if (warning.toLowerCase().includes('unallocated funds')) {
                    return `
                        <li class="small text-warning mb-2">
                            <i class="fas fa-minus me-1"></i>
                            <a href="/unallocated-funds" target="_blank" class="text-warning text-decoration-none" style="border-bottom: 1px dotted;">
                                ${warning}
                            </a>
                        </li>
                    `;
                } else {
                    return `
                        <li class="small text-warning mb-2">
                            <i class="fas fa-minus me-1"></i>${warning}
                        </li>
                    `;
                }
            }).join('') +
            '</ul>';
    }

    // Issues
    document.getElementById('issuesCount').textContent = trustHealth.issues.length;
    const issuesContainer = document.getElementById('issuesContainer');

    if (trustHealth.issues.length === 0) {
        issuesContainer.innerHTML = '<small class="text-muted">No issues</small>';
    } else {
        issuesContainer.innerHTML = '<ul class="list-unstyled mb-0">' +
            trustHealth.issues.map(issue => {
                // Make uncleared transactions issue clickable
                if (issue.toLowerCase().includes('uncleared transactions')) {
                    return `
                        <li class="small text-danger mb-2">
                            <i class="fas fa-times me-1"></i>
                            <a href="/uncleared-transactions" target="_blank" class="text-danger text-decoration-none" style="border-bottom: 1px dotted;">
                                ${issue}
                            </a>
                        </li>
                    `;
                // Make negative balance issue clickable with dropdown
                } else if (issue.toLowerCase().includes('negative balance')) {
                    // Get negative balance clients from health details
                    const negativeClients = healthDetails?.negative_balance_clients || [];
                    
                    if (negativeClients.length === 0) {
                        return `
                            <li class="small text-danger mb-2">
                                <i class="fas fa-times me-1"></i>${issue}
                            </li>
                        `;
                    }
                    
                    // Create collapsible dropdown with client list
                    const dropdownId = 'negativeBalanceDropdown';
                    const clientsList = negativeClients.map(client => `
                        <div class="px-3 py-1">
                            <a href="/clients/${client.id}" class="text-danger text-decoration-none d-block">
                                <i class="fas fa-user me-1"></i>
                                <strong>${client.name}</strong>: ${formatCurrency(client.balance)}
                            </a>
                        </div>
                    `).join('');
                    
                    return `
                        <li class="small text-danger mb-2">
                            <div>
                                <i class="fas fa-times me-1"></i>
                                <a href="#" class="text-danger text-decoration-none" 
                                   data-bs-toggle="collapse" 
                                   data-bs-target="#${dropdownId}" 
                                   aria-expanded="false" 
                                   style="border-bottom: 1px dotted;">
                                    ${issue}
                                    <i class="fas fa-chevron-down ms-1" style="font-size: 0.8em;"></i>
                                </a>
                            </div>
                            <div class="collapse mt-2" id="${dropdownId}">
                                <div class="border rounded bg-light">
                                    ${clientsList}
                                </div>
                            </div>
                        </li>
                    `;
                } else {
                    return `
                        <li class="small text-danger mb-2">
                            <i class="fas fa-times me-1"></i>${issue}
                        </li>
                    `;
                }
            }).join('') +
            '</ul>';
    }
}

// Populate client tables
function populateClientTables(data) {
    // Top 5 clients with balances
    const topClientsTable = document.getElementById('topClientsTable');
    const clientsWithBalances = data.clients_with_balances || [];

    document.getElementById('topClientsBadge').textContent = clientsWithBalances.length;

    if (clientsWithBalances.length === 0) {
        topClientsTable.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No clients with open balances</td></tr>';
    } else {
        topClientsTable.innerHTML = clientsWithBalances.map(client => `
            <tr>
                <td>
                    <div>
                        <a href="/clients/${client.id}" class="text-decoration-none">
                            ${client.full_name}
                        </a>
                    </div>
                    ${client.cases && client.cases.length > 0 ?
                        `<small class="text-muted" style="font-size: 0.75rem;">${client.cases.join(' | ')}</small>` :
                        '<small class="text-muted" style="font-size: 0.75rem;">No active cases</small>'
                    }
                </td>
                <td><span style="font-size: 0.75rem;" class="text-success">${formatCurrency(client.balance)}</span></td>
                <td>
                    ${client.last_activity ?
                        `<small style="font-size: 0.75rem;">${client.last_activity}</small>` :
                        '<small class="text-muted" style="font-size: 0.75rem;">No activity</small>'
                    }
                </td>
            </tr>
        `).join('');
    }

    // Stale clients
    const staleClientsTable = document.getElementById('staleClientsTable');
    const staleClients = data.stale_clients || [];

    document.getElementById('staleClientsBadge').textContent = data.stale_clients_count || 0;

    if (staleClients.length === 0) {
        staleClientsTable.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No stale client balances found</td></tr>';
    } else {
        staleClientsTable.innerHTML = staleClients.map(client => `
            <tr>
                <td>
                    <a href="/clients/${client.id}" class="text-decoration-none">
                        ${client.full_name}
                    </a>
                </td>
                <td class="${parseFloat(client.balance) < 0 ? 'text-danger' : 'text-success'}">${formatCurrency(client.balance)}</td>
                <td>${client.last_deposit || 'Unknown'}</td>
            </tr>
        `).join('');
    }
}

// Populate outstanding checks
function populateOutstandingChecks(checks) {
    const checksTable = document.getElementById('outstandingChecksTable');

    document.getElementById('outstandingChecksBadge').textContent = checks.length;

    if (checks.length === 0) {
        checksTable.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No outstanding checks over 90 days</td></tr>';
    } else {
        checksTable.innerHTML = checks.map(check => `
            <tr>
                <td>${check.reference_number}</td>
                <td>${check.date_issued}</td>
                <td>${check.client_name}</td>
                <td>${check.payee}</td>
                <td><small>${check.description || ''}</small></td>
                <td><span class="text-dark">(${formatCurrency(check.amount).replace('$', '')})</span></td>
                <td><span class="badge bg-danger">${check.days_outstanding} days</span></td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary btn-sm" onclick="editTransaction(${check.id}, ${check.bank_account_id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-warning btn-sm" onclick="reissueCheck(${check.id}, '${check.reference_number}')" title="Reissue">
                            <i class="fas fa-redo"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="voidCheck(${check.id}, '${check.reference_number}')" title="Void">
                            <i class="fas fa-ban"></i>
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="viewAuditTrail(${check.id}, '${check.reference_number}')" title="Audit Trail">
                            <i class="fas fa-history"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

// Edit transaction - redirect to bank transactions page with transaction ID
function editTransaction(transactionId, bankAccountId) {
    // Use the bank account ID from the check data, or default to 2 if not provided
    const accountId = bankAccountId || 2;
    window.location.href = `/bank-transactions?account_id=${accountId}&edit=${transactionId}`;
}

// Reissue check
async function reissueCheck(transactionId, checkNumber) {
    if (!confirm(`Reissue check #${checkNumber}?\n\nThis will:\n1. Void the current check\n2. Create a new check with a new check number`)) {
        return;
    }

    try {
        const response = await api.post(`/api/v1/bank-accounts/bank-transactions/${transactionId}/reissue/`, {});

        if (response.success) {
            showSuccessMessage(`Check #${checkNumber} reissued successfully. New check #${response.new_reference_number}`);
            // Reload dashboard
            loadDashboard();
        }
    } catch (error) {
        showErrorMessage(error.message || 'Failed to reissue check');
    }
}

// Void check
async function voidCheck(transactionId, checkNumber) {
    const reason = prompt(`Void check #${checkNumber}?\n\nPlease enter the reason for voiding:`);

    if (!reason) {
        return; // User cancelled
    }

    try {
        const response = await api.post(`/api/v1/bank-accounts/bank-transactions/${transactionId}/void/`, {
            void_reason: reason
        });

        if (response.success) {
            showSuccessMessage(`Check #${checkNumber} voided successfully`);
            // Reload dashboard
            loadDashboard();
        }
    } catch (error) {
        showErrorMessage(error.message || 'Failed to void check');
    }
}

// Store current transaction ID for printing
let currentAuditTransactionId = null;

// View audit trail (copied from case-detail.js)
async function viewAuditTrail(transactionId, checkNumber) {
    try {
        // Store transaction ID for print function
        currentAuditTransactionId = transactionId;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('auditTrailModal'));
        modal.show();

        // Show loading state
        document.getElementById('auditTrailContent').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Loading audit history...</p>
            </div>
        `;

        // Load audit history
        const response = await api.get(`/v1/bank-accounts/bank-transactions/${transactionId}/audit_history/`);

        if (response.success) {
            const txn = response.transaction;
            const logs = response.audit_logs || [];

            let html = `
                <div class="mb-3">
                    <h6 class="fw-bold">Transaction Details</h6>
                    <table class="table table-sm table-bordered">
                        <tr>
                            <td class="fw-bold" style="width: 30%;">Transaction Number:</td>
                            <td>${txn.transaction_number}</td>
                        </tr>
                        <tr>
                            <td class="fw-bold">Date:</td>
                            <td>${txn.transaction_date}</td>
                        </tr>
                        <tr>
                            <td class="fw-bold">Amount:</td>
                            <td>$${parseFloat(txn.amount).toFixed(2)}</td>
                        </tr>
                        <tr>
                            <td class="fw-bold">Status:</td>
                            <td><span class="badge ${txn.status.toLowerCase() === 'voided' ? 'bg-danger' : txn.status.toLowerCase() === 'cleared' ? 'bg-success' : 'bg-warning text-dark'}">${txn.status.toUpperCase()}</span></td>
                        </tr>
                        <tr>
                            <td class="fw-bold">Payee:</td>
                            <td>${txn.payee}</td>
                        </tr>
                    </table>
                </div>

                <div>
                    <h6 class="fw-bold">Audit History <span class="badge bg-secondary">${logs.length} entries</span></h6>
                    ${logs.length === 0 ? '<p class="text-muted">No audit history found.</p>' : ''}
            `;

            logs.forEach((log, index) => {
                let actionBadge = '';
                if (log.action === 'CREATED') {
                    actionBadge = '<span class="badge bg-success">CREATED</span>';
                } else if (log.action === 'VOIDED') {
                    actionBadge = '<span class="badge bg-danger">VOIDED</span>';
                } else if (log.action === 'UPDATED') {
                    actionBadge = '<span class="badge bg-primary">UPDATED</span>';
                } else if (log.action === 'CLEARED') {
                    actionBadge = '<span class="badge bg-info">CLEARED</span>';
                } else if (log.action === 'PENDING') {
                    actionBadge = '<span class="badge bg-warning text-dark">PENDING</span>';
                } else {
                    // Fallback: use action_display if available, otherwise use action itself
                    const displayText = log.action_display || log.action || 'UPDATED';
                    actionBadge = `<span class="badge bg-secondary">${displayText}</span>`;
                }

                html += `
                    <div class="card mb-2">
                        <div class="card-body py-2">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="mb-1">
                                        ${actionBadge}
                                        <strong class="ms-2">${log.action_date}</strong>
                                        <span class="text-muted ms-2">by ${log.action_by}</span>
                                    </div>
                                    <div class="text-muted small">
                                        ${log.changes_summary}
                                    </div>
                                    ${log.change_reason ? `
                                        <div class="mt-1 small text-break">
                                            <strong>Reason:</strong> ${log.change_reason}
                                        </div>
                                    ` : ''}
                                    ${log.ip_address ? `
                                        <div class="mt-1 small text-muted">
                                            <i class="fas fa-network-wired"></i> ${log.ip_address}
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';

            document.getElementById('auditTrailContent').innerHTML = html;
        } else {
            document.getElementById('auditTrailContent').innerHTML = `
                <div class="alert alert-danger">
                    Failed to load audit history.
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('auditTrailContent').innerHTML = `
            <div class="alert alert-danger">
                Error loading audit history: ${error.message}
            </div>
        `;
    }
}

// Print audit trail
function printAuditTrail() {
    // Open the PDF in a new tab
    if (currentAuditTransactionId) {
        window.open(`/api/v1/bank-accounts/bank-transactions/${currentAuditTransactionId}/audit_history_pdf/`, '_blank');
    }
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);
