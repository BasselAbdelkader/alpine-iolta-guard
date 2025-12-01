/**
 * Unallocated Funds Page JavaScript
 * Displays detailed breakdown of unallocated funds in trust account
 */

// Check authentication on page load
(async () => {
    if (!api.setupPageProtection()) {
        return;
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

// Load unallocated funds data
async function loadUnallocatedFunds() {
    try {
        console.log('Loading unallocated funds data...');

        // Call the API endpoint
        const data = await api.get('/v1/dashboard/unallocated-funds/');
        console.log('Unallocated funds data received:', data);

        // Populate summary cards
        populateSummaryCards(data);

        // Populate transactions table
        populateTransactionsTable(data.transactions || []);

        // Show recommendations
        showRecommendations(data);

    } catch (error) {
        console.error('Error loading unallocated funds:', error);

        document.querySelector('main').innerHTML = `
            <div class="alert alert-danger m-4">
                <h4><i class="fas fa-exclamation-triangle"></i> Error Loading Unallocated Funds</h4>
                <p>${error.message}</p>
                <button class="btn btn-primary" onclick="loadUnallocatedFunds()">Retry</button>
                <button class="btn btn-secondary" onclick="logout()">Logout</button>
            </div>
        `;
    }
}

// Populate summary cards
function populateSummaryCards(data) {
    document.getElementById('bankRegisterBalance').textContent = formatCurrency(data.bank_register_balance);
    document.getElementById('totalClientBalance').textContent = formatCurrency(data.total_client_balance);
    document.getElementById('unallocatedAmount').textContent = formatCurrency(data.unallocated_amount);
    document.getElementById('unallocatedPercentage').textContent = `${data.unallocated_percentage.toFixed(2)}%`;
}

// Populate transactions table
function populateTransactionsTable(transactions) {
    const tableBody = document.getElementById('unallocatedTransactionsTable');

    if (transactions.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No unallocated transactions found</td></tr>';
        return;
    }

    tableBody.innerHTML = transactions.map(txn => {
        const amountClass = txn.transaction_type === 'DEPOSIT' ? 'text-success' : 'text-danger';
        const amountDisplay = txn.transaction_type === 'DEPOSIT'
            ? formatCurrency(txn.amount)
            : `(${formatCurrency(Math.abs(txn.amount))})`;

        const statusBadge = getStatusBadge(txn.status);

        return `
            <tr style="cursor: pointer;" onclick="editTransaction(${txn.id}, ${txn.bank_account_id})" class="transaction-row">
                <td>${txn.transaction_date}</td>
                <td>${txn.transaction_number || 'N/A'}</td>
                <td>${txn.item_type || txn.transaction_type}</td>
                <td>${txn.description || 'No description'}</td>
                <td class="${amountClass}">${amountDisplay}</td>
                <td>${txn.source || 'Manual Entry'}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    }).join('');

    // Add hover effect styling
    const style = document.createElement('style');
    style.textContent = `
        .transaction-row:hover {
            background-color: #f8f9fa !important;
        }
    `;
    if (!document.getElementById('transaction-row-style')) {
        style.id = 'transaction-row-style';
        document.head.appendChild(style);
    }
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge bg-warning">Pending</span>',
        'cleared': '<span class="badge bg-success">Cleared</span>',
        'reconciled': '<span class="badge bg-primary">Reconciled</span>',
        'voided': '<span class="badge bg-danger">Voided</span>'
    };
    return badges[status.toLowerCase()] || `<span class="badge bg-secondary">${status}</span>`;
}

// Show recommendations based on percentage
function showRecommendations(data) {
    const section = document.getElementById('recommendationsSection');
    const percentage = data.unallocated_percentage;
    const amount = data.unallocated_amount;

    let html = '';

    if (percentage === 0) {
        html = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle me-2"></i>Perfect Allocation</h6>
                <p>All funds in the trust account are allocated to clients. Excellent record keeping!</p>
            </div>
        `;
    } else if (percentage > 0 && percentage <= 5) {
        html = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle me-2"></i>Healthy Range (0-5%)</h6>
                <p>Unallocated funds are within the normal range. This is acceptable for most trust accounts.</p>
                <ul>
                    <li>Review recent deposits and assign to clients if needed</li>
                    <li>Check for accumulated interest that needs allocation</li>
                </ul>
            </div>
        `;
    } else if (percentage > 5 && percentage <= 15) {
        html = `
            <div class="alert alert-warning">
                <h6><i class="fas fa-exclamation-triangle me-2"></i>Moderate Unallocated Funds (5-15%)</h6>
                <p>You have ${formatCurrency(amount)} (${percentage.toFixed(2)}%) unallocated. This requires attention.</p>
                <ul>
                    <li><strong>Action Required:</strong> Review all unallocated transactions above</li>
                    <li>Assign recent deposits to appropriate clients</li>
                    <li>Allocate accumulated interest to clients (per your state rules)</li>
                    <li>Investigate any bank fees or adjustments</li>
                    <li>Consider creating suspense cases for funds pending allocation</li>
                </ul>
            </div>
        `;
    } else if (percentage > 15) {
        html = `
            <div class="alert alert-danger">
                <h6><i class="fas fa-times-circle me-2"></i>High Unallocated Funds (>15%)</h6>
                <p>You have ${formatCurrency(amount)} (${percentage.toFixed(2)}%) unallocated. This is a compliance risk!</p>
                <ul>
                    <li><strong>Urgent:</strong> Review all transactions in the table above immediately</li>
                    <li>Assign ALL deposits to specific clients or create suspense cases</li>
                    <li>Verify bank reconciliation is up to date</li>
                    <li>Check for data entry errors or missing client assignments</li>
                    <li>Contact your compliance officer if needed</li>
                    <li><strong>IOLTA Rule:</strong> All client funds must be properly allocated</li>
                </ul>
            </div>
        `;
    } else {
        // Negative (deficit)
        html = `
            <div class="alert alert-danger">
                <h6><i class="fas fa-exclamation-circle me-2"></i>Trust Account Deficit</h6>
                <p><strong>CRITICAL:</strong> Client balances exceed bank balance by ${formatCurrency(Math.abs(amount))}!</p>
                <ul>
                    <li><strong>Immediate Action Required:</strong> This is a serious compliance violation</li>
                    <li>Review all client balances and transactions immediately</li>
                    <li>Verify bank reconciliation is accurate</li>
                    <li>Check for duplicate entries or data errors</li>
                    <li>Contact your compliance officer and banking advisor</li>
                    <li><strong>Do not issue any new checks or payments until resolved</strong></li>
                </ul>
            </div>
        `;
    }

    section.innerHTML = html;
}

// Edit transaction - redirect to bank transactions page with transaction ID
function editTransaction(transactionId, bankAccountId) {
    // Redirect to bank transactions page with both account_id and edit parameters
    window.location.href = `/bank-transactions?account_id=${bankAccountId}&edit=${transactionId}`;
}

// Load data on page load
document.addEventListener('DOMContentLoaded', loadUnallocatedFunds);
