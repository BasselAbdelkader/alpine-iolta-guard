/**
 * Client Ledger Report JavaScript
 * Handles report generation and display
 */

// Initialize API client
const api = new TAMSApiClient();

let clients = [];
let cases = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', async function() {
    // console.log('Client Ledger page loaded');

    // Load law firm info
    await loadLawFirmInfo();

    // Load clients for dropdown
    await loadClients();

    // Set default date range (last 12 months)
    setDefaultDateRange();

    // Handle form submission
    document.getElementById('filterForm').addEventListener('submit', handleGenerateReport);

    // Handle client selection change
    document.getElementById('clientSelect').addEventListener('change', handleClientChange);
});

/**
 * Load law firm information
 */
async function loadLawFirmInfo() {
    try {
        const firm = await api.get('/v1/dashboard/law-firm/');

        if (firm) {

            // Update sidebar
            document.getElementById('lawFirmName').textContent = firm.firm_name || 'Law Firm';
            document.getElementById('lawFirmLocation').textContent = `${firm.city || ''}, ${firm.state || ''}`;
            document.getElementById('lawFirmPhone').textContent = firm.phone || '';
            document.getElementById('lawFirmEmail').textContent = firm.email || '';

            // Update header
            const addressLine = [firm.address, firm.city, firm.state, firm.zip_code]
                .filter(Boolean)
                .join(', ');
            document.getElementById('headerFirmAddress').textContent = addressLine;

            // Update report header (for printing)
            document.getElementById('reportFirmName').textContent = firm.firm_name || 'Law Firm';
            document.getElementById('reportFirmAddress').textContent = addressLine;
        }
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

/**
 * Load clients for dropdown
 */
async function loadClients() {
    try {
        const response = await api.get('/v1/clients/?page_size=1000');

        if (response && response.results) {
            clients = response.results;

            const clientSelect = document.getElementById('clientSelect');
            clientSelect.innerHTML = '<option value="">-- Select Client --</option>';

            clients.forEach(client => {
                const option = document.createElement('option');
                option.value = client.id;
                option.textContent = `${client.full_name} (Balance: $${client.formatted_balance})`;
                clientSelect.appendChild(option);
            });
        }
    } catch (error) {
        // console.error('Error loading clients:', error);
        // alert('Error loading clients. Please refresh the page.');
    }
}

/**
 * Handle client selection change - load cases for selected client
 */
async function handleClientChange(e) {
    const clientId = e.target.value;
    const caseSelect = document.getElementById('caseSelect');

    // Reset case dropdown
    caseSelect.innerHTML = '<option value="">-- All Cases --</option>';

    if (!clientId) {
        return;
    }

    try {
        // Load cases for this client
        const response = await api.get(`/v1/clients/${clientId}/cases/`);

        if (response && response.length > 0) {
            response.forEach(caseItem => {
                const option = document.createElement('option');
                option.value = caseItem.id;
                option.textContent = `${caseItem.case_number} - ${caseItem.case_title}`;
                caseSelect.appendChild(option);
            });
        }
    } catch (error) {
        // console.error('Error loading cases:', error);
    }
}

/**
 * Set default date range (last 12 months)
 */
function setDefaultDateRange() {
    const today = new Date();
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(today.getMonth() - 12);

    document.getElementById('dateTo').valueAsDate = today;
    document.getElementById('dateFrom').valueAsDate = twelveMonthsAgo;
}

/**
 * Reset filters
 */
function resetFilters() {
    document.getElementById('clientSelect').value = '';
    document.getElementById('caseSelect').innerHTML = '<option value="">-- All Cases --</option>';
    setDefaultDateRange();
    document.getElementById('reportDisplay').style.display = 'none';
}

/**
 * Handle report generation
 */
async function handleGenerateReport(e) {
    e.preventDefault();

    const clientId = document.getElementById('clientSelect').value;
    const caseId = document.getElementById('caseSelect').value;
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;

    if (!clientId) {
        // alert('Please select a client');
        return;
    }

    // Show loading
    const reportDisplay = document.getElementById('reportDisplay');
    const transactionsBody = document.getElementById('transactionsBody');
    transactionsBody.innerHTML = '<tr><td colspan="7" class="text-center py-4"><i class="fas fa-spinner fa-spin me-2"></i>Loading transactions...</td></tr>';
    reportDisplay.style.display = 'block';

    try {
        // Build API URL with parameters
        const params = new URLSearchParams({
            client_id: clientId,
            date_from: dateFrom,
            date_to: dateTo
        });

        if (caseId) {
            params.append('case_id', caseId);
        }

        // For now, we'll use the transaction API to get client transactions
        // In production, you'd create a dedicated report API endpoint
        const response = await api.get(`/v1/clients/${clientId}/cases/`);

        // Get client info
        const selectedClient = clients.find(c => c.id == clientId);

        // Display report
        displayReport(selectedClient, response, dateFrom, dateTo);

    } catch (error) {
        // console.error('Error generating report:', error);
        transactionsBody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4"><i class="fas fa-exclamation-triangle me-2"></i>Error loading report data</td></tr>';
    }
}

/**
 * Display report data
 */
function displayReport(client, casesData, dateFrom, dateTo) {
    // Update report header
    document.getElementById('reportClientName').textContent = client.full_name;
    document.getElementById('reportDateRange').textContent = `${formatDate(dateFrom)} to ${formatDate(dateTo)}`;
    document.getElementById('reportGenerated').textContent = new Date().toLocaleString();
    document.getElementById('reportBalance').textContent = `$${client.formatted_balance}`;

    // For this demo, we'll show a simplified version
    // In production, you'd have a dedicated API endpoint that returns transactions with running balances
    const transactionsBody = document.getElementById('transactionsBody');

    if (!casesData || casesData.length === 0) {
        transactionsBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No transactions found for selected date range</td></tr>';
        updateSummary([], 0);
        return;
    }

    // Build transactions table
    let html = '';
    let runningBalance = 0;
    let totalDeposits = 0;
    let totalWithdrawals = 0;
    let transactionCount = 0;

    // This is a simplified display - in production you'd get actual transactions from API
    casesData.forEach(caseItem => {
        html += `
            <tr class="table-secondary">
                <td colspan="7"><strong>Case: ${caseItem.case_number} - ${caseItem.case_title}</strong></td>
            </tr>
            <tr>
                <td colspan="6" class="text-end"><strong>Case Balance:</strong></td>
                <td class="text-end"><strong>$${caseItem.formatted_balance}</strong></td>
            </tr>
        `;
        transactionCount++;
    });

    transactionsBody.innerHTML = html || '<tr><td colspan="7" class="text-center text-muted py-4">No transactions found</td></tr>';

    // Update summary
    updateSummary(casesData, client.current_balance);
}

/**
 * Update summary section
 */
function updateSummary(transactions, currentBalance) {
    // In production, these would be calculated from actual transaction data
    document.getElementById('totalDeposits').textContent = '$0.00';
    document.getElementById('totalWithdrawals').textContent = '$0.00';
    document.getElementById('netChange').textContent = '$0.00';
    document.getElementById('transactionCount').textContent = transactions.length;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' });
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Logout function
 */
function logout() {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/login';
}
