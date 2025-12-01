// Negative Balances Report Logic

document.addEventListener('DOMContentLoaded', async function() {
    await checkAuth();
    await loadNegativeBalances();
});

async function checkAuth() {
    const isAuth = await api.isAuthenticated();
    if (!isAuth) {
        window.location.href = '/login';
    }
}

async function loadNegativeBalances() {
    try {
        // Fetch all clients
        const response = await api.get('/v1/clients/?page_size=10000');
        const clients = response.results || [];

        // Filter clients with negative balances
        const negativeClients = clients.filter(client => {
            const balance = parseFloat(client.current_balance);
            return balance < 0;
        });

        // Sort by balance (worst first)
        negativeClients.sort((a, b) => parseFloat(a.current_balance) - parseFloat(b.current_balance));

        // Fetch case information for each client
        const clientsWithCases = await Promise.all(
            negativeClients.map(async (client) => {
                try {
                    // Fetch cases for this client
                    const casesResponse = await api.get(`/v1/clients/${client.id}/cases/`);
                    // API returns {client_id, client_name, cases: [...]}
                    const cases = casesResponse.cases || casesResponse || [];

                    // Calculate total transactions across all cases
                    let totalTransactions = 0;
                    const caseTitles = [];

                    for (const caseItem of cases) {
                        // Use case_title, fallback to case_number if title is empty
                        const caseDisplay = caseItem.case_title || caseItem.case_number || 'Untitled Case';
                        caseTitles.push(caseDisplay);

                        // Count transactions for each case
                        try {
                            const txnResponse = await api.get(`/v1/cases/${caseItem.id}/transactions/`);
                            // Handle different response structures
                            let transactions = [];
                            if (txnResponse && typeof txnResponse === 'object') {
                                if (Array.isArray(txnResponse.transactions)) {
                                    transactions = txnResponse.transactions;
                                } else if (Array.isArray(txnResponse)) {
                                    transactions = txnResponse;
                                } else if (txnResponse.results && Array.isArray(txnResponse.results)) {
                                    transactions = txnResponse.results;
                                }
                            }
                            totalTransactions += transactions.length;
                            console.log(`Case ${caseItem.id} (${caseDisplay}): ${transactions.length} transactions`);
                        } catch (e) {
                            console.warn(`Could not load transactions for case ${caseItem.id}:`, e);
                        }
                    }

                    console.log(`Client ${client.full_name}: ${caseTitles.length} cases, ${totalTransactions} total transactions`);

                    return {
                        ...client,
                        cases: caseTitles,
                        transaction_count: totalTransactions
                    };
                } catch (error) {
                    console.warn(`Could not load cases for client ${client.id}:`, error);
                    return {
                        ...client,
                        cases: [],
                        transaction_count: 0
                    };
                }
            })
        );

        // Update summary cards
        const totalCount = clientsWithCases.length;
        const totalNegative = clientsWithCases.reduce((sum, client) => sum + parseFloat(client.current_balance), 0);
        const worstBalance = clientsWithCases.length > 0 ? parseFloat(clientsWithCases[0].current_balance) : 0;

        document.getElementById('totalClientsCount').textContent = totalCount;
        document.getElementById('totalNegativeAmount').textContent = formatCurrency(totalNegative);
        document.getElementById('worstBalance').textContent = formatCurrency(worstBalance);

        // Render table
        renderNegativeBalancesTable(clientsWithCases);

    } catch (error) {
        console.error('Error loading negative balances:', error);
        document.getElementById('negativeBalancesTable').innerHTML =
            '<tr><td colspan="6" class="text-center text-danger">Error loading data</td></tr>';
    }
}

function renderNegativeBalancesTable(clients) {
    const tbody = document.getElementById('negativeBalancesTable');

    if (clients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-success">No clients with negative balances found!</td></tr>';
        return;
    }

    let html = '';
    clients.forEach(client => {
        const balance = parseFloat(client.current_balance);
        const transactionCount = client.transaction_count || 0;
        const dataSource = client.data_source || 'unknown';
        const caseTitles = client.cases || [];

        const sourceBadge = dataSource === 'csv'
            ? '<span class="badge bg-warning">CSV Import</span>'
            : '<span class="badge bg-primary">Webapp</span>';

        // Display case titles or "No cases"
        const caseTitlesDisplay = caseTitles.length > 0
            ? caseTitles.join(', ')
            : '<span class="text-muted">No cases</span>';

        html += `
            <tr>
                <td>
                    <a href="/clients/${client.id}" class="text-decoration-none">
                        ${client.full_name}
                    </a>
                </td>
                <td>${caseTitlesDisplay}</td>
                <td class="text-danger fw-bold">${client.formatted_balance}</td>
                <td>${transactionCount}</td>
                <td>${sourceBadge}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewClient(${client.id})" title="View Client">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="viewTransactions(${client.id})" title="View Transactions">
                            <i class="fas fa-list"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

function viewClient(clientId) {
    window.location.href = `/clients/${clientId}`;
}

function viewTransactions(clientId) {
    window.location.href = `/clients/${clientId}#transactions`;
}

function formatCurrency(value) {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';

    const formatted = Math.abs(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    return num < 0 ? `($${formatted})` : `$${formatted}`;
}

function logout() {
    window.location.href = '/logout';
}
