/**
 * Bank Accounts List Page
 * Handles loading and displaying bank accounts with DataTables
 */

// Global variables
let bankAccountsTable;
let deleteAccountId = null;

/**
 * Initialize page on load
 */
$(document).ready(function() {
    // Check authentication
    checkAuth();

    // Load law firm info (for sidebar and header)
    loadLawFirmInfo();

    // Load bank accounts
    loadBankAccounts();

    // Setup delete confirmation
    setupDeleteModal();
});

/**
 * Check if user is authenticated
 */
async function checkAuth() {
    const isAuth = await api.isAuthenticated();
    if (!isAuth) {
        window.location.href = '/login';
    }
}

/**
 * Load law firm information for sidebar and header
 */
async function loadLawFirmInfo() {
    try {
        // Try to get law firm info from dashboard endpoint or settings
        // For now, use placeholder - you can enhance this later
        $('#lawFirmName').text('Trust Account System');
        $('#headerFirmName').text('Bank Accounts Management');
        $('#userName').text('admin');
        $('#headerUserName').text('admin');
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

/**
 * Load bank accounts from API
 */
async function loadBankAccounts() {
    try {
        // Show loading state
        const tbody = $('#bankAccountsTable tbody');
        tbody.html('<tr><td colspan="5" class="text-center">Loading bank accounts...</td></tr>');

        // Fetch bank accounts
        const response = await api.get('/v1/bank-accounts/accounts/');

        // Check if we have results
        if (!response.results || response.results.length === 0) {
            tbody.html('<tr><td colspan="5" class="text-center">No bank accounts found</td></tr>');
            return;
        }

        // Build table rows
        let rows = '';
        response.results.forEach(account => {
            rows += buildAccountRow(account);
        });

        tbody.html(rows);

        // Initialize DataTables
        initializeDataTable();

    } catch (error) {
        // console.error('Error loading bank accounts:', error);
        const tbody = $('#bankAccountsTable tbody');
        tbody.html(`<tr><td colspan="5" class="text-center text-danger">Error loading bank accounts: ${error.message}</td></tr>`);
    }
}

/**
 * Build a table row for a bank account
 */
function buildAccountRow(account) {
    const accountNumber = escapeHtml(account.account_number || 'N/A');
    const bankName = escapeHtml(account.bank_name || 'N/A');
    const balance = account.register_balance || 0;
    const formattedBalance = formatBalance(balance);
    const balanceClass = getBalanceClass(balance);
    const statusBadge = account.is_active
        ? '<span class="badge bg-success">Active</span>'
        : '<span class="badge bg-secondary">Inactive</span>';
    const createdDate = formatDate(account.created_at);

    return `
        <tr>
            <td>
                <a href="/bank-transactions?account_id=${account.id}" class="text-decoration-none">
                    ${accountNumber}
                </a>
            </td>
            <td>${bankName}</td>
            <td class="${balanceClass}">${formattedBalance}</td>
            <td>${statusBadge}</td>
            <td>${createdDate}</td>
        </tr>
    `;
}

/**
 * Initialize DataTables with exact same settings as v3
 */
function initializeDataTable() {
    // Destroy existing table if it exists
    if (bankAccountsTable) {
        bankAccountsTable.destroy();
    }

    // Initialize with v3 settings
    bankAccountsTable = $('#bankAccountsTable').DataTable({
        "pageLength": 25,
        "order": [[ 4, "desc" ]], // Sort by created date descending
        "searching": false,  // Disable DataTables search box
        "lengthChange": false,  // Disable "Show X entries" dropdown
        "paging": false,  // Disable pagination
        "info": false  // Disable "Showing 1 to 1 of 1 entries" info
    });
}

/**
 * Format balance with accounting notation
 */
function formatBalance(balance) {
    const amount = parseFloat(balance);
    if (isNaN(amount)) {
        return '$0.00';
    }

    // Use accounting notation: negative values in parentheses
    if (amount < 0) {
        return `($${Math.abs(amount).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})})`;
    } else {
        return `$${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }
}

/**
 * Get CSS class for balance based on value
 */
function getBalanceClass(balance) {
    const amount = parseFloat(balance);
    if (isNaN(amount)) {
        return '';
    }

    if (amount < 0) {
        return 'text-danger'; // Negative balance - red
    } else if (amount === 0) {
        return 'text-muted'; // Zero balance - gray
    } else {
        return 'text-success'; // Positive balance - green
    }
}

/**
 * Format date to MM/DD/YYYY
 */
function formatDate(dateString) {
    if (!dateString) {
        return 'N/A';
    }

    try {
        const date = new Date(dateString);
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const year = date.getFullYear();
        return `${month}/${day}/${year}`;
    } catch (error) {
        return 'Invalid Date';
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Setup delete modal event handlers
 */
function setupDeleteModal() {
    $('#confirmDeleteBtn').on('click', async function() {
        if (!deleteAccountId) {
            return;
        }

        try {
            // Disable button during deletion
            $(this).prop('disabled', true).text('Deleting...');

            // Call delete API
            await api.delete(`/v1/bank-accounts/${deleteAccountId}/`);

            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            modal.hide();

            // Reload accounts
            await loadBankAccounts();

            // Show success message (you can add a toast notification here)
            // alert('Bank account deleted successfully');

        } catch (error) {
            // console.error('Error deleting bank account:', error);
            // alert(`Error deleting bank account: ${error.message}`);
        } finally {
            // Re-enable button
            $(this).prop('disabled', false).text('Delete');
            deleteAccountId = null;
        }
    });
}

/**
 * Show delete confirmation modal
 */
function confirmDelete(accountId, accountName) {
    deleteAccountId = accountId;
    document.getElementById('accountName').textContent = accountName;
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

/**
 * Logout function
 */
async function logout() {
    try {
        await api.logout();
    } catch (error) {
        // console.error('Logout error:', error);
        window.location.href = '/login';
    }
}
