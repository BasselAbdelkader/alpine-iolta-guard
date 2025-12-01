// Uncleared Transactions Page Logic

document.addEventListener('DOMContentLoaded', async function() {
    await checkAuth();
    await loadLawFirmInfo();
    await loadUnclearedTransactions();
});

async function checkAuth() {
    const isAuth = await api.isAuthenticated();
    if (!isAuth) {
        window.location.href = '/login';
    }
}

async function loadLawFirmInfo() {
    try {
        const firm = await api.get('/v1/dashboard/law-firm/');
        if (firm) {
            document.getElementById('lawFirmName').textContent = firm.firm_name;
            const details = `${firm.address}, ${firm.city}, ${firm.state} ${firm.zip_code} | ${firm.phone} | ${firm.email}`;
            document.getElementById('lawFirmDetails').textContent = details;
            document.getElementById('headerFirmDetails').textContent = details;
        }
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

async function loadUnclearedTransactions() {
    try {
        // Get uncleared transactions from dedicated API endpoint
        const data = await api.get('/v1/dashboard/uncleared-transactions/');

        // Update summary cards
        document.getElementById('totalCount').textContent = data.total_count || 0;
        document.getElementById('totalDeposits').textContent = formatCurrency(data.total_deposits || 0);
        document.getElementById('totalWithdrawals').textContent = formatCurrency(data.total_withdrawals || 0);

        const netAmount = parseFloat(data.net_amount || 0);
        document.getElementById('netAmount').textContent = formatCurrency(netAmount);

        // Update net amount card color
        const netCard = document.getElementById('netAmountCard');
        if (netAmount >= 0) {
            netCard.className = 'card text-white bg-info';
        } else {
            netCard.className = 'card text-white bg-warning';
        }

        // Update age group counts
        document.getElementById('recentCount').textContent = data.recent_count || 0;
        document.getElementById('moderateCount').textContent = data.moderate_count || 0;
        document.getElementById('oldCount').textContent = data.old_count || 0;
        document.getElementById('veryOldCount').textContent = data.very_old_count || 0;

        // Render transaction tables
        const ageGroups = data.age_groups || {};
        renderTransactionTable('recentContent', ageGroups.recent || [], 'bg-success');
        renderTransactionTable('moderateContent', ageGroups.moderate || [], 'bg-warning');
        renderTransactionTable('oldContent', ageGroups.old || [], 'bg-danger');
        renderTransactionTable('veryOldContent', ageGroups.very_old || [], 'bg-dark');

    } catch (error) {
        // console.error('Error loading uncleared transactions:', error);
        document.getElementById('recentContent').innerHTML = '<div class="alert alert-danger">Error loading transactions</div>';
    }
}

function renderTransactionTable(containerId, transactions, badgeClass) {
    const container = document.getElementById(containerId);

    if (transactions.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="text-muted mb-3">
                    <i class="fas fa-check-circle fa-3x"></i>
                </div>
                <h5 class="text-muted">No uncleared transactions in this category</h5>
                <p class="text-muted">All transactions in this age group have been cleared.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Reference</th>
                        <th>Amount</th>
                        <th>Client</th>
                        <th>Case</th>
                        <th>Payee</th>
                        <th>Description</th>
                        <th>Days Old</th>
                    </tr>
                </thead>
                <tbody>
    `;

    transactions.forEach(txn => {
        const typeClass = txn.transaction_type === 'DEPOSIT' ? 'bg-success' : 'bg-danger';
        const amountClass = txn.transaction_type === 'DEPOSIT' ? 'text-success' : 'text-danger';

        html += `
            <tr>
                <td><span class="fw-medium">${txn.transaction_date || '-'}</span></td>
                <td><span class="badge ${typeClass}">${txn.transaction_type}</span></td>
                <td><span class="text-muted">${txn.reference_number || '-'}</span></td>
                <td><span class="${amountClass} fw-medium">${formatCurrency(txn.amount)}</span></td>
                <td>${txn.client || '-'}</td>
                <td>${txn.case || '-'}</td>
                <td>${txn.payee || '-'}</td>
                <td title="${txn.description}">${truncate(txn.description, 40)}</td>
                <td><span class="badge ${badgeClass}">${txn.days_old} days</span></td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

async function markCleared(transactionId) {
    if (!confirm('Mark this transaction as cleared?')) {
        return;
    }

    try {
        await api.patch(`/v1/bank-accounts/bank-transactions/${transactionId}/`, {
            status: 'cleared'
        });
        showToast('Transaction cleared successfully!', 'success');
        await loadUnclearedTransactions();
    } catch (error) {
        // console.error('Error marking transaction as cleared:', error);
        showToast('Error marking transaction as cleared: ' + error.message, 'error');
    }
}

function showToast(message, type = 'success') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-success' : 'bg-danger';
    toast.className = `toast align-items-center text-white ${bgClass} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function formatCurrency(value) {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';
    return '$' + num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US');
}

function truncate(str, maxLength) {
    if (!str) return '';
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength - 3) + '...';
}

function logout() {
    api.logout();
}
