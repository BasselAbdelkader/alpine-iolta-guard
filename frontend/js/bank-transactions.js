// Bank Transactions Page JavaScript
let allTransactions = [];
let currentVoidTransactionId = null;
let validPayeeSelected = false; // Track if selected payee is valid
let validClientSelected = false; // Track if selected client is valid

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load firm info
    loadFirmInfo();

    // Setup menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Check if we need to auto-open edit modal (from query parameter)
    const urlParams = new URLSearchParams(window.location.search);
    const editTransactionId = urlParams.get('edit');

    // Load transactions
    if (editTransactionId) {
        // If we need to auto-open modal, wait for loadTransactions to complete first
        loadTransactions().then(() => {
            // Give a brief moment for DOM to update, then open modal
            setTimeout(() => {
                editTransaction(parseInt(editTransactionId));
            }, 300);
        }).catch(error => {
            console.error('Error loading transactions before opening modal:', error);
        });
    } else {
        // Normal load without auto-open
        loadTransactions();
    }

    // Setup search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loadTransactions();
        });
    }
});

async function loadFirmInfo() {
    try {
        const data = await api.get('/v1/dashboard/law-firm/');
        const firm = data;

        // Sidebar
        document.getElementById('firmNameSidebar').textContent = firm.firm_name;
        document.getElementById('firmLocation').textContent = `${firm.city}, ${firm.state}`;
        document.getElementById('firmPhone').textContent = firm.phone;
        document.getElementById('firmEmail').textContent = firm.email;

        // Header
        document.getElementById('firmNameHeader').textContent = firm.firm_name;
        document.getElementById('firmAddressFull').textContent = `${firm.address}, ${firm.city}, ${firm.state} ${firm.zip_code} | ${firm.phone} | ${firm.email}`;
    } catch (error) {
        // console.error('Error loading firm info:', error);
    }
}

// Global variable to store running balances for all transactions
let runningBalanceMap = {};

async function loadTransactions() {
    try {
        // Check URL for account_id parameter
        const urlParams = new URLSearchParams(window.location.search);
        const accountId = urlParams.get('account_id');
        console.log('Account ID from URL:', accountId);

        if (!accountId) {
            showError('No account ID specified');
            return;
        }

        // STEP 1: Fetch ALL transactions for this account (no filters) to calculate running balance
        console.log('Fetching ALL transactions for running balance calculation...');
        const allParams = new URLSearchParams();
        allParams.append('bank_account', accountId);
        allParams.append('page_size', '10000'); // Get all transactions

        const allResponse = await api.get(`/v1/bank-accounts/bank-transactions/?${allParams.toString()}`);
        const allTxns = Array.isArray(allResponse) ? allResponse : (allResponse.results || []);
        console.log('Total transactions for balance calculation:', allTxns.length);

        // Calculate running balance for ALL transactions
        runningBalanceMap = calculateRunningBalances(allTxns);
        console.log('Running balance map created, final balance:', runningBalanceMap[Object.keys(runningBalanceMap).pop()]);

        // STEP 2: Fetch filtered transactions for display
        // Build query params from filters
        const params = new URLSearchParams();
        params.append('bank_account', accountId);

        const search = document.getElementById('searchInput').value;
        const type = document.getElementById('transactionTypeFilter').value;
        const status = document.getElementById('statusFilter').value;
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;

        if (search) params.append('search', search);
        if (type) params.append('transaction_type', type);
        if (status) params.append('status', status);
        if (dateFrom) params.append('start_date', dateFrom);
        if (dateTo) params.append('end_date', dateTo);

        // CRITICAL: Get ALL transactions (no pagination limit)
        params.append('page_size', '10000');

        console.log('Fetching filtered transactions with params:', params.toString());
        const response = await api.get(`/v1/bank-accounts/bank-transactions/?${params.toString()}`);
        console.log('API Response:', response);

        // Handle both array and paginated responses
        allTransactions = Array.isArray(response) ? response : (response.results || []);
        console.log('Filtered transactions loaded:', allTransactions.length);

        renderTransactions(allTransactions);
        // updateSummaryCards(allTransactions); // REMOVED: Summary cards no longer displayed
    } catch (error) {
        console.error('Error loading transactions:', error);
        showError('Failed to load transactions: ' + (error.message || 'Unknown error'));
        // Show empty state
        document.getElementById('transactionsTableBody').innerHTML = '<tr><td colspan="10" class="text-center text-danger">Error loading transactions. Please try again.</td></tr>';
    }
}

// NEW FUNCTION: Calculate running balance for all transactions
function calculateRunningBalances(transactions) {
    const balanceMap = {};

    // Sort transactions by date (oldest first), then by ID for consistency
    const sorted = [...transactions].sort((a, b) => {
        const dateA = new Date(a.transaction_date);
        const dateB = new Date(b.transaction_date);
        if (dateA - dateB !== 0) return dateA - dateB;
        // If same date, sort by ID to maintain consistency
        return a.id - b.id;
    });

    let runningBalance = 0;

    sorted.forEach(txn => {
        const amount = parseFloat(txn.amount);
        // Only count non-voided transactions
        if (txn.status !== 'voided') {
            if (txn.transaction_type === 'DEPOSIT') {
                runningBalance += amount;
            } else {
                runningBalance -= amount;
            }
        }
        // Store the running balance for this transaction ID
        balanceMap[txn.id] = runningBalance;
    });

    return balanceMap;
}

function renderTransactions(transactions) {
    // Update count info
    const countInfo = document.getElementById('transactions-count-info');
    if (countInfo && transactions) {
        countInfo.innerHTML = `<small>Showing <strong>${transactions.length}</strong> transactions</small>`;
    }
    const tbody = document.getElementById('transactionsTableBody');

    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">No bank transactions found</td></tr>';
        return;
    }

    // REQUIREMENT: Display transactions with pre-calculated running balance
    // Sort by date (newest first for display)
    const sorted = [...transactions].sort((a, b) => {
        const dateA = new Date(a.transaction_date);
        const dateB = new Date(b.transaction_date);
        if (dateB - dateA !== 0) return dateB - dateA;
        // If same date, sort by ID descending
        return b.id - a.id;
    });

    // Add running balance from the pre-calculated map
    const displayTransactions = sorted.map(txn => {
        return {
            ...txn,
            runningBalance: runningBalanceMap[txn.id] || 0
        };
    });

    tbody.innerHTML = displayTransactions.map(txn => {
        const date = new Date(txn.transaction_date).toLocaleDateString('en-US');
        const isVoided = txn.status.toLowerCase() === 'voided';

        // Type badge
        let typeBadge = '';
        if (isVoided) {
            // REQUIREMENT: Display voided transactions as simply "VOIDED"
            typeBadge = `<span class="badge bg-danger">VOIDED</span>`;
        } else if (txn.transaction_type === 'DEPOSIT') {
            typeBadge = `<span class="badge bg-success">${txn.transaction_type_display}</span>`;
        } else {
            typeBadge = `<span class="badge bg-danger">${txn.transaction_type_display}</span>`;
        }

        // Status badge
        let statusBadge = '';

        if (txn.status.toLowerCase() === 'voided') {
            statusBadge = '<span class="badge bg-danger">VOIDED</span>';
        } else if (txn.status.toLowerCase() === 'pending') {
            statusBadge = '<span class="badge bg-warning text-dark">Pending</span>';
        } else if (txn.status.toLowerCase() === 'cleared') {
            statusBadge = '<span class="badge bg-success">Cleared</span>';
        } else if (txn.status.toLowerCase() === 'reconciled') {
            // REQUIREMENT: Add Reconciled status display
            statusBadge = '<span class="badge bg-primary">Reconciled</span>';
        } else {
            statusBadge = `<span class="badge bg-secondary">${txn.status}</span>`;
        }

        // Amount formatting
        let amountDisplay = '';
        const amount = parseFloat(txn.amount);
        if (isVoided) {
            amountDisplay = `<span class="text-muted" style="text-decoration: line-through;">
                ${txn.transaction_type === 'DEPOSIT' ? '+' : '-'}$${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                <small>(VOIDED)</small>
            </span>`;
        } else if (txn.transaction_type === 'DEPOSIT') {
            amountDisplay = `<span class="text-success fw-medium">+$${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>`;
        } else {
            amountDisplay = `<span class="text-danger fw-medium">-$${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>`;
        }

        // Get client name - use client_name field from serializer
        const clientName = txn.client_name || '-';

        // Payee - use payee or vendor_name from serializer
        const payee = txn.payee || txn.vendor_name || '-';

        // REQUIREMENT: Format running balance
        const balance = txn.runningBalance || 0;
        const balanceClass = balance >= 0 ? 'text-success' : 'text-danger';
        const balanceDisplay = `<span class="${balanceClass} fw-bold">$${Math.abs(balance).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>`;

        // Action buttons
        let actionsHtml = '';
        if (isVoided) {
            // For voided transactions, only show audit trail
            const voidReason = txn.void_reason ? ` - ${txn.void_reason}` : '';
            actionsHtml = `
                <div class="d-flex justify-content-center" style="gap: 4px;">
                    <button type="button" class="btn btn-outline-info btn-sm" onclick="viewAuditHistory(${txn.id})" title="View Audit Trail" style="min-width: 36px; padding: 4px 6px;">
                        <i class="fas fa-file-alt"></i>
                    </button>
                </div>
            `;
        } else {
            // For active transactions, show all action buttons
            actionsHtml = `
                <div class="d-flex justify-content-center" style="gap: 4px;">
                    <button type="button" class="btn btn-outline-primary btn-sm" onclick="editTransaction(${txn.id})" title="Edit Transaction" style="min-width: 36px; padding: 4px 6px;">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-outline-warning btn-sm" onclick="voidTransaction(${txn.id})" title="Void Transaction" style="min-width: 36px; padding: 4px 6px;">
                        <i class="fas fa-ban"></i>
                    </button>
                    <button type="button" class="btn btn-outline-success btn-sm" onclick="reissueTransaction(${txn.id})" title="Re-issue Payment" style="min-width: 36px; padding: 4px 6px;">
                        <i class="fas fa-redo"></i>
                    </button>
                    <button type="button" class="btn btn-outline-info btn-sm" onclick="viewAuditHistory(${txn.id})" title="View Audit Trail" style="min-width: 36px; padding: 4px 6px;">
                        <i class="fas fa-file-alt"></i>
                    </button>
                </div>
            `;
        }

        return `
            <tr>
                <td class="text-center"><span class="fw-medium">${date}</span></td>
                <td class="text-center">${typeBadge}</td>
                <td class="text-center"><span class="text-dark">${txn.reference_number || '-'}</span></td>
                <td><span class="fw-medium">${payee}</span></td>
                <td><span class="fw-medium">${clientName}</span></td>
                <td><span class="text-dark">${txn.description || '-'}</span></td>
                <td class="text-end">${amountDisplay}</td>
                <td class="text-end">${balanceDisplay}</td>
                <td class="text-center">${statusBadge}</td>
                <td class="text-center">${actionsHtml}</td>
            </tr>
        `;
    }).join('');
}

function updateSummaryCards(transactions) {
    const deposits = transactions.filter(t => t.transaction_type === 'DEPOSIT' && t.status !== 'voided');
    const withdrawals = transactions.filter(t => t.transaction_type === 'WITHDRAWAL' && t.status !== 'voided');
    const unmatched = transactions.filter(t => t.status.toLowerCase() === 'pending');
    const matched = transactions.filter(t => t.status.toLowerCase() === 'cleared');

    const depositsSum = deposits.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const withdrawalsSum = withdrawals.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const unmatchedSum = unmatched.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    const matchedSum = matched.reduce((sum, t) => sum + parseFloat(t.amount), 0);

    document.getElementById('depositsCount').textContent = deposits.length;
    document.getElementById('depositsAmount').textContent = depositsSum.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

    document.getElementById('withdrawalsCount').textContent = withdrawals.length;
    document.getElementById('withdrawalsAmount').textContent = withdrawalsSum.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

    document.getElementById('unmatchedCount').textContent = unmatched.length;
    document.getElementById('unmatchedAmount').textContent = unmatchedSum.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

    document.getElementById('matchedCount').textContent = matched.length;
    document.getElementById('matchedAmount').textContent = matchedSum.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

    // Missing is always 0 for now
    document.getElementById('missingCount').textContent = '0';
    document.getElementById('missingAmount').textContent = '0.00';
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('transactionTypeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    loadTransactions();
}

async function addBankTransaction() {
    // Reset modal title and clear editing mode
    document.querySelector('#transactionModal .modal-title').textContent = 'Add New Transaction';
    window.editingTransactionId = null;
    validPayeeSelected = false; // Reset payee validation for new transaction
    validClientSelected = false; // Reset client validation for new transaction

    // Show the unified transaction modal without client/case context
    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    modal.show();

    try {
        // Fetch required data for the form
        const [bankAccountsData, clientsData, vendorsData] = await Promise.all([
            api.get('/v1/bank-accounts/accounts/'),
            api.get('/v1/clients/'),
            api.get('/v1/vendors/')
        ]);

        const bankAccounts = bankAccountsData.results || [];
        const clients = (clientsData.results || []).sort((a, b) => {
            const nameA = a.full_name.toLowerCase();
            const nameB = b.full_name.toLowerCase();
            return nameA.localeCompare(nameB);
        });
        const vendors = vendorsData.results || [];

        // Populate global clientList for autocomplete
        clientList = clients.map(c => ({
            id: c.id,
            full_name: c.full_name
        }));
        console.log('Clients populated for autocomplete:', clientList.length, 'clients');

        // Build form HTML
        const formHtml = buildTransactionFormHTML(bankAccounts, clients, vendors);
        document.getElementById('transactionModalContent').innerHTML = formHtml;

        // Initialize form functionality
        initializeTransactionForm();

        // Attach case dropdown handler AFTER modal content is loaded
        attachCaseDropdownHandler();
    } catch (error) {
        // console.error('Error loading transaction form:', error);
        document.getElementById('transactionModalContent').innerHTML = '<div class="alert alert-danger">Error loading form. Please try again.</div>';
    }
}

function buildTransactionFormHTML(bankAccounts, clients, vendors) {
    const currentBankAccountId = new URLSearchParams(window.location.search).get('account_id') || bankAccounts[0]?.id || '';
    const today = new Date().toISOString().split('T')[0];

    return `
        <!-- Available Funds Display - Top Right - GREEN AND PROMINENT -->
        <div class="d-flex justify-content-end align-items-center mb-3">
            <div class="text-end">
                <!-- GREEN, BOLD, LARGE available funds display -->
                <span id="available-funds-display" style="color: #28a745; font-weight: bold; font-size: 1.25rem; display: none;">
                    Available Funds: $<span id="available-funds">0.00</span>
                </span>

                <!-- Show message in dynamic mode until both client and case are selected -->
                <div id="funds-message" class="text-muted" style="display: block; font-size: 0.875rem;">
                    Select client and case to see available funds
                </div>
            </div>
        </div>

        <form id="transactionForm" method="post">
            <!-- Hidden status field with default value -->
            <input type="hidden" name="status" value="pending">
            <input type="hidden" id="form-mode" value="dynamic">

            <!-- First Line: Bank Account (Half Page) -->
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="id_bank_account" class="form-label">
                            Bank Account <span class="text-danger">*</span>
                        </label>
                        <select name="bank_account" class="form-select" required id="id_bank_account">
                            <option value="">Select Bank Account</option>
                            ${bankAccounts.map(acc => `
                                <option value="${acc.id}" ${acc.id == currentBankAccountId ? 'selected' : ''}>
                                    ${acc.bank_name} - ${acc.account_name}
                                </option>
                            `).join('')}
                        </select>
                        <small class="form-text text-muted">Select the bank account for this transaction</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <!-- Empty space for half page layout -->
                </div>
            </div>

            <!-- Second Line: Client and Case -->
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3" style="position: relative;">
                        <label for="id_client_text" class="form-label">Client <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="id_client_text" placeholder="Type client name..." autocomplete="off" required>
                        <input type="hidden" name="client" id="id_client_hidden">
                        <div id="client-suggestions" class="dropdown-menu" style="display: none; position: absolute; z-index: 1000; width: 100%; max-height: 300px; overflow-y: auto;"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="id_case" class="form-label">Case <span class="text-danger">*</span></label>
                        <select name="case" class="form-select" id="id_case" required>
                            <option value="">Select Case</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Third Line: Transaction Date, Transaction Type, Reference Number, Payee, Amount -->
            <div class="row">
                <div class="col-md-2" style="max-width: 180px;">
                    <div class="mb-3">
                        <label for="id_transaction_date" class="form-label">
                            Date <span class="text-danger">*</span>
                        </label>
                        <input type="date" name="transaction_date" value="${today}" class="form-control" required id="id_transaction_date">
                    </div>
                </div>
                <div class="col-md-2" style="max-width: 170px;">
                    <div class="mb-3">
                        <label for="id_transaction_type" class="form-label">
                            Type <span class="text-danger">*</span>
                        </label>
                        <select name="transaction_type" class="form-select" required id="id_transaction_type">
                            <option value="">---------</option>
                            <option value="DEPOSIT">Deposit</option>
                            <option value="WITHDRAWAL">Withdrawal</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-2" style="max-width: 130px;">
                    <div class="mb-3">
                        <label for="id_reference_number" class="form-label">Ref <span class="text-danger">*</span></label>
                        <input type="text" name="reference_number" class="form-control" placeholder="Wire reference, ACH number, etc." maxlength="100" required id="id_reference_number">
                    </div>
                </div>
                <div class="col-md-1" id="to-print-container" style="display: none; max-width: 120px;">
                    <div class="mb-3">
                        <label class="form-label">&nbsp;</label>
                        <div class="form-check mt-2">
                            <input type="checkbox" class="form-check-input" id="id_to_print" style="transform: scale(0.9);">
                            <label class="form-check-label" for="id_to_print" style="font-size: 0.875rem; white-space: nowrap;">
                                To Print
                            </label>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="mb-3" style="position: relative;">
                        <label for="id_payee_text" class="form-label">Payee <span class="text-danger">*</span></label>
                        <input type="text" name="payee" class="form-control" id="id_payee_text" placeholder="Type payee name..." autocomplete="off" required>
                        <div id="payee-suggestions" class="dropdown-menu" style="display: none; position: absolute; z-index: 1000; width: 100%; max-height: 300px; overflow-y: auto;"></div>
                        <div id="payee-error" class="text-danger small mt-1" style="display: none;">Please add a valid payee or create new.</div>
                    </div>
                </div>
                <div class="col-md-2" style="max-width: 180px;">
                    <div class="mb-3">
                        <label for="id_amount_display" class="form-label">
                            Amount <span class="text-danger">*</span>
                        </label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="text" name="amount_display" class="form-control" id="id_amount_display" placeholder="0.00" required>
                            <input type="hidden" name="amount" id="id_amount_hidden" required>
                        </div>
                        <div id="amount-error" class="text-danger" style="display: none; font-size: 0.875rem; margin-top: 2px;">
                            Transaction not permitted - insufficient funds
                        </div>
                    </div>
                </div>
            </div>

            <!-- Fourth Line: Description -->
            <div class="row">
                <div class="col-md-12">
                    <div class="mb-3">
                        <label for="id_description" class="form-label">
                            Description <span class="text-danger">*</span>
                        </label>
                        <textarea name="description" rows="3" class="form-control" placeholder="Enter transaction description" required id="id_description"></textarea>
                    </div>
                </div>
            </div>

            <!-- Fifth Line: Check Memo -->
            <div class="row">
                <div class="col-md-12">
                    <div class="mb-3">
                        <label for="id_check_memo" class="form-label">Check Memo</label>
                        <textarea name="check_memo" rows="2" class="form-control" placeholder="Check memo (appears on check)" maxlength="500" id="id_check_memo"></textarea>
                    </div>
                </div>
            </div>
        </form>
    `;
}

async function editTransaction(transactionId) {
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));

    // Update modal title
    document.querySelector('#transactionModal .modal-title').textContent = 'Edit Transaction';

    modal.show();

    try {
        // Fetch required data
        const [transaction, bankAccountsData, clientsData, vendorsData] = await Promise.all([
            api.get(`/v1/bank-accounts/bank-transactions/${transactionId}/`),
            api.get('/v1/bank-accounts/accounts/'),
            api.get('/v1/clients/'),
            api.get('/v1/vendors/')
        ]);

        const bankAccounts = bankAccountsData.results || [];
        const clients = (clientsData.results || []).sort((a, b) => {
            const nameA = a.full_name.toLowerCase();
            const nameB = b.full_name.toLowerCase();
            return nameA.localeCompare(nameB);
        });
        const vendors = vendorsData.results || [];

        // Populate global clientList for autocomplete
        clientList = clients.map(c => ({
            id: c.id,
            full_name: c.full_name
        }));
        console.log('Clients populated for edit autocomplete:', clientList.length, 'clients');

        // Build form HTML with transaction data pre-filled
        const formHtml = buildEditTransactionFormHTML(transaction, bankAccounts, clients, vendors);
        document.getElementById('transactionModalContent').innerHTML = formHtml;

        // Initialize form functionality
        initializeTransactionForm();
        attachCaseDropdownHandler();

        // Store transaction ID for update
        window.editingTransactionId = transactionId;

        // Load cases for the selected client
        if (transaction.client) {
            await loadCasesForClient(transaction.client, transaction.case);
            validClientSelected = true; // Mark client as valid since it's from existing transaction
        }

        // Mark payee as valid since it's from existing transaction
        if (transaction.payee) {
            validPayeeSelected = true;
        }

        // Check if transaction can be fully edited
        const status = (transaction.status || '').toLowerCase();
        if (status.toLowerCase() === 'cleared' || status.toLowerCase() === 'reconciled') {
            // Disable fields except description
            document.getElementById('id_transaction_date').disabled = true;
            document.getElementById('id_transaction_type').disabled = true;
            document.getElementById('id_reference_number').readOnly = true;
            document.getElementById('id_reference_number').style.backgroundColor = '#e9ecef';
            document.getElementById('id_payee_text').readOnly = true;
            document.getElementById('id_payee_text').style.backgroundColor = '#e9ecef';
            document.getElementById('id_amount_display').readOnly = true;
            document.getElementById('id_amount_display').style.backgroundColor = '#e9ecef';
            document.getElementById('id_bank_account').disabled = true;
            const clientTextField = document.getElementById('id_client_text');
            if (clientTextField) {
                clientTextField.readOnly = true;
                clientTextField.style.backgroundColor = '#e9ecef';
            }
            document.getElementById('id_case').disabled = true;
            document.getElementById('id_check_memo').readOnly = true;
            document.getElementById('id_check_memo').style.backgroundColor = '#e9ecef';

            const toPrintCheckbox = document.getElementById('id_to_print');
            if (toPrintCheckbox) toPrintCheckbox.disabled = true;
        }

    } catch (error) {
        console.error('Error loading transaction:', error);
        document.getElementById('transactionModalContent').innerHTML = '<div class="alert alert-danger">Error loading form. Please try again.</div>';
    }
}

function buildEditTransactionFormHTML(transaction, bankAccounts, clients, vendors) {
    const today = new Date().toISOString().split('T')[0];

    return `
        <!-- Available Funds Display - Top Right - GREEN AND PROMINENT -->
        <div class="d-flex justify-content-end align-items-center mb-3">
            <div class="text-end">
                <span id="available-funds-display" style="color: #28a745; font-weight: bold; font-size: 1.25rem;">
                    Available Funds: $<span id="available-funds">${transaction.case_balance || '0.00'}</span>
                </span>
            </div>
        </div>

        <form id="transactionForm" method="post">
            <input type="hidden" name="status" value="${transaction.status || 'pending'}">
            <input type="hidden" id="form-mode" value="edit">

            <!-- First Line: Bank Account (Half Page) -->
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="id_bank_account" class="form-label">
                            Bank Account <span class="text-danger">*</span>
                        </label>
                        <select name="bank_account" class="form-select" required id="id_bank_account">
                            <option value="">Select Bank Account</option>
                            ${bankAccounts.map(acc => `
                                <option value="${acc.id}" ${acc.id == transaction.bank_account ? 'selected' : ''}>
                                    ${acc.bank_name} - ${acc.account_name}
                                </option>
                            `).join('')}
                        </select>
                    </div>
                </div>
                <div class="col-md-6"></div>
            </div>

            <!-- Second Line: Client and Case -->
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3" style="position: relative;">
                        <label for="id_client_text" class="form-label">Client <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="id_client_text" value="${transaction.client_name || ''}" placeholder="Type client name..." autocomplete="off" required>
                        <input type="hidden" name="client" id="id_client_hidden" value="${transaction.client || ''}">
                        <div id="client-suggestions" class="dropdown-menu" style="display: none; position: absolute; z-index: 1000; width: 100%; max-height: 300px; overflow-y: auto;"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="id_case" class="form-label">Case <span class="text-danger">*</span></label>
                        <select name="case" class="form-select" id="id_case" required>
                            <option value="">Select Case</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Third Line: Transaction Date, Type, Ref, To Print, Payee, Amount -->
            <div class="row">
                <div class="col-md-2" style="max-width: 180px;">
                    <div class="mb-3">
                        <label for="id_transaction_date" class="form-label">Date <span class="text-danger">*</span></label>
                        <input type="date" name="transaction_date" value="${transaction.transaction_date}" class="form-control" required id="id_transaction_date">
                    </div>
                </div>
                <div class="col-md-2" style="max-width: 170px;">
                    <div class="mb-3">
                        <label for="id_transaction_type" class="form-label">Type <span class="text-danger">*</span></label>
                        <select name="transaction_type" class="form-select" required id="id_transaction_type">
                            <option value="">---------</option>
                            <option value="DEPOSIT" ${transaction.transaction_type === 'DEPOSIT' ? 'selected' : ''}>Deposit</option>
                            <option value="WITHDRAWAL" ${transaction.transaction_type === 'WITHDRAWAL' ? 'selected' : ''}>Withdrawal</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-2" style="max-width: 130px;">
                    <div class="mb-3">
                        <label for="id_reference_number" class="form-label">Ref <span class="text-danger">*</span></label>
                        <input type="text" name="reference_number" value="${transaction.reference_number || ''}" class="form-control" maxlength="100" required id="id_reference_number">
                    </div>
                </div>
                <div class="col-md-1" id="to-print-container" style="${transaction.transaction_type === 'WITHDRAWAL' ? '' : 'display: none;'} max-width: 120px;">
                    <div class="mb-3">
                        <label class="form-label">&nbsp;</label>
                        <div class="form-check mt-2">
                            <input type="checkbox" class="form-check-input" id="id_to_print" ${transaction.reference_number === 'TO PRINT' ? 'checked' : ''} style="transform: scale(0.9);">
                            <label class="form-check-label" for="id_to_print" style="font-size: 0.875rem; white-space: nowrap;">To Print</label>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <div class="mb-3" style="position: relative;">
                        <label for="id_payee_text" class="form-label">Payee <span class="text-danger">*</span></label>
                        <input type="text" name="payee" value="${transaction.payee || ''}" class="form-control" id="id_payee_text" placeholder="Type payee name..." autocomplete="off" required>
                        <div id="payee-suggestions" class="dropdown-menu" style="display: none; position: absolute; z-index: 1000; width: 100%; max-height: 300px; overflow-y: auto;"></div>
                    </div>
                </div>
                <div class="col-md-2" style="max-width: 180px;">
                    <div class="mb-3">
                        <label for="id_amount_display" class="form-label">Amount <span class="text-danger">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="text" name="amount_display" value="${transaction.amount}" class="form-control" id="id_amount_display" required>
                            <input type="hidden" name="amount" value="${transaction.amount}" id="id_amount_hidden" required>
                        </div>
                        <div id="amount-error" class="text-danger" style="display: none; font-size: 0.875rem; margin-top: 2px;">
                            Transaction not permitted - insufficient funds
                        </div>
                    </div>
                </div>
            </div>

            <!-- Fourth Line: Description -->
            <div class="row">
                <div class="col-md-12">
                    <div class="mb-3">
                        <label for="id_description" class="form-label">Description <span class="text-danger">*</span></label>
                        <textarea name="description" rows="3" class="form-control" required id="id_description">${transaction.description || ''}</textarea>
                    </div>
                </div>
            </div>

            <!-- Fifth Line: Check Memo -->
            <div class="row">
                <div class="col-md-12">
                    <div class="mb-3">
                        <label for="id_check_memo" class="form-label">Check Memo</label>
                        <textarea name="check_memo" rows="2" class="form-control" maxlength="500" id="id_check_memo">${transaction.check_memo || ''}</textarea>
                    </div>
                </div>
            </div>
        </form>
    `;
}

async function loadCasesForClient(clientId, selectedCaseId = null) {
    const caseSelect = document.getElementById('id_case');
    if (!caseSelect) return;

    // Clear existing options
    caseSelect.innerHTML = '<option value="">Select Case</option>';

    try {
        const response = await api.get(`/v1/clients/${clientId}/cases/`);
        const cases = response.cases || [];

        cases.forEach(caseObj => {
            const option = document.createElement('option');
            option.value = caseObj.id;  // Backend uses ID for API calls
            option.textContent = `${caseObj.case_title || caseObj.case_description}`;  // Display only case title
            option.setAttribute('data-balance', caseObj.current_balance || 0);
            option.setAttribute('data-formatted-balance', caseObj.formatted_balance || '0.00');

            if (selectedCaseId && caseObj.id == selectedCaseId) {
                option.selected = true;
            }

            caseSelect.appendChild(option);
        });

        // Update available funds if a case is selected
        if (selectedCaseId) {
            updateAvailableFunds();
        }
    } catch (error) {
        console.error('Error loading cases:', error);
    }
}

async function voidTransaction(transactionId) {
    const reason = prompt('Please enter a reason for voiding this transaction:');
    if (!reason || !reason.trim()) {
        return;
    }

    if (!confirm('Are you sure you want to void this transaction? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await api.post(`/v1/bank-accounts/bank-transactions/${transactionId}/void/`, {
            void_reason: reason.trim()
        });

        if (response.success) {
            showSuccessMessage('Transaction voided successfully!');
            setTimeout(() => location.reload(), 1000);
        } else {
            showErrorMessage(response.message || 'Failed to void transaction');
        }
    } catch (error) {
        console.error('Error voiding transaction:', error);
        showErrorMessage(error.message || 'Failed to void transaction');
    }
}

// Store current transaction ID for printing
let currentAuditTransactionId = null;

async function viewAuditHistory(transactionId) {
    try {
        // Store transaction ID for print function
        currentAuditTransactionId = transactionId;

        // Check if modal exists (in case of cache issues)
        const modalElement = document.getElementById('auditTrailModal');
        const contentElement = document.getElementById('auditTrailContent');

        if (!modalElement || !contentElement) {
            alert('⚠️ Page cache detected!\n\nPlease do a HARD REFRESH to load the latest version:\n\n• Mac: Cmd + Shift + R\n• Windows: Ctrl + Shift + R\n\nOr press Ctrl+F5');
            console.error('Modal elements not found. Current page version is cached. Hard refresh required.');
            return;
        }

        // Show modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();

        // Show loading state
        contentElement.innerHTML = `
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

            contentElement.innerHTML = html;
        } else {
            contentElement.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load audit history
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading audit history:', error);
        const contentElement = document.getElementById('auditTrailContent');
        if (contentElement) {
            contentElement.innerHTML = `
                <div class="alert alert-danger">
                    Error loading audit history: ${error.message}
                </div>
            `;
        }
    }
}

function printAuditTrail() {
    // Open the PDF in a new tab (like professional websites - Chrome PDF viewer with grey toolbar)
    if (currentAuditTransactionId) {
        window.open(`/api/v1/bank-accounts/bank-transactions/${currentAuditTransactionId}/audit_history_pdf/`, '_blank');
    } else {
        alert('No transaction selected for printing');
    }
}

async function reissueTransaction(transactionId) {
    console.log('🔄 Reissue button clicked - Transaction ID:', transactionId);

    // First, get transaction details to check status
    try {
        const txnResponse = await api.get(`/v1/bank-accounts/bank-transactions/${transactionId}/`);
        const transaction = txnResponse;

        // Check if transaction is cleared or reconciled
        if (transaction.status.toLowerCase() === 'cleared' || transaction.status.toLowerCase() === 'reconciled') {
            // Show error notification immediately without confirmation dialog
            showErrorMessage(`Cannot reissue ${transaction.status.toLowerCase() === 'cleared' ? 'Cleared' : 'Reconciled'} transactions.`);
            return;
        }

        // If not cleared/reconciled, show confirmation dialog
        if (!confirm('Are you sure you want to reissue this check?\n\nThis will:\n1. VOID the original check\n2. Create a reversal deposit (cleared)\n3. Create a new pending check\n\nContinue?')) {
            console.log('❌ User cancelled reissue');
            return;
        }

        console.log('✅ User confirmed reissue, calling API...');

        // Proceed with reissue
        const response = await api.post(`/v1/bank-accounts/bank-transactions/${transactionId}/reissue/`);
        console.log('📥 API Response:', response);

        if (response.success) {
            showSuccessMessage(
                `Check reissued successfully!\n\n` +
                `Original: ${response.original_transaction_number} (VOIDED)\n` +
                `Reversal: ${response.reversal_transaction_number} (CLEARED)\n` +
                `New Check: ${response.new_check_transaction_number} (PENDING)`
            );
            // Reload transactions after short delay
            setTimeout(() => location.reload(), 1500);
        } else {
            showErrorMessage(response.message || 'Failed to reissue check');
        }
    } catch (error) {
        console.error('❌ Error reissuing check:', error);
        showErrorMessage(error.message || 'Failed to reissue check');
    }
}

// Use unified toast notification system
function showSuccess(message) {
    showSuccessMessage(message);
}

function showError(message) {
    showErrorMessage(message);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        api.post('/auth/logout/').then(() => {
            window.location.href = '/login';
        });
    }
}

// Transaction form functions
// Global vendor list for payee autocomplete
var vendorList = [];
// Global client list for client autocomplete
var clientList = [];

// Function to update available funds display - MUST BE GLOBAL
function updateAvailableFunds() {
    const caseSelect = document.getElementById('id_case');
    const selectedCaseId = caseSelect?.value;

    console.log('🔄 updateAvailableFunds called - Case:', selectedCaseId);

    const availableFundsElement = document.getElementById('available-funds');
    const availableFundsDisplay = document.getElementById('available-funds-display');
    const fundsMessage = document.getElementById('funds-message');

    if (selectedCaseId && caseSelect) {
        // Get balance from the selected option's data attribute (already loaded from cases API)
        const selectedOption = caseSelect.options[caseSelect.selectedIndex];
        const rawBalance = parseFloat(selectedOption.getAttribute('data-balance')) || 0;
        const formattedBalance = selectedOption.getAttribute('data-formatted-balance') || '0.00';

        console.log('💰 Balance from dropdown data:', rawBalance, 'Formatted:', formattedBalance);

        // Display the balance with thousands separators
        // For negative numbers, use parentheses: ($2,000.00) instead of $-2,000.00
        let displayBalance;
        if (rawBalance < 0) {
            const absBalance = Math.abs(rawBalance).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            displayBalance = `(${absBalance})`;
        } else {
            displayBalance = rawBalance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }

        if (availableFundsElement) {
            availableFundsElement.textContent = displayBalance;
        }

        // Show available funds display and hide message (if elements exist)
        if (availableFundsDisplay) {
            availableFundsDisplay.style.display = 'inline';
            // Set color based on balance: red if negative, green if positive/zero
            if (rawBalance < 0) {
                availableFundsDisplay.style.color = '#dc3545'; // Bootstrap danger red
            } else {
                availableFundsDisplay.style.color = '#28a745'; // Bootstrap success green
            }
        }
        if (fundsMessage) {
            fundsMessage.style.display = 'none';
        }
        console.log('✅ Available funds displayed: $' + displayBalance);
    } else {
        console.log('⏸️  Case not selected, hiding available funds');

        // Hide available funds and show selection message (if elements exist)
        if (availableFundsDisplay) {
            availableFundsDisplay.style.display = 'none';
        }
        if (fundsMessage) {
            fundsMessage.style.display = 'block';
            fundsMessage.textContent = 'Select client and case to see available funds';
        }
    }
}

function initializeTransactionForm() {
    // Show/hide "To Print" checkbox based on transaction type
    const transactionTypeSelect = document.getElementById('id_transaction_type');
    const toPrintContainer = document.getElementById('to-print-container');

    if (transactionTypeSelect && toPrintContainer) {
        transactionTypeSelect.addEventListener('change', function() {
            if (this.value === 'WITHDRAWAL') {
                toPrintContainer.style.display = '';
            } else {
                toPrintContainer.style.display = 'none';
                // Uncheck the checkbox if it was checked
                const toPrintCheckbox = document.getElementById('id_to_print');
                if (toPrintCheckbox && toPrintCheckbox.checked) {
                    toPrintCheckbox.checked = false;
                    // Trigger the change event to reset the ref field
                    toPrintCheckbox.dispatchEvent(new Event('change'));
                }
            }
        });
    }

    // "To Print" checkbox functionality - Lock Ref field when checked
    const toPrintCheckbox = document.getElementById('id_to_print');
    const refField = document.getElementById('id_reference_number');

    if (toPrintCheckbox && refField) {
        toPrintCheckbox.addEventListener('change', function() {
            if (this.checked) {
                refField.value = 'TO PRINT';
                refField.readOnly = true;
                refField.style.backgroundColor = '#e9ecef';
                refField.style.color = '#6c757d';
                refField.style.cursor = 'not-allowed';
                refField.style.opacity = '0.7';
            } else {
                refField.value = '';
                refField.readOnly = false;
                refField.style.backgroundColor = '';
                refField.style.color = '';
                refField.style.cursor = '';
                refField.style.opacity = '';
            }
        });
    }

    // Load vendors for payee autocomplete
    function loadVendorList() {
        api.get('/v1/vendors/')
            .then(data => {
                vendorList = (data.results || []).map(v => ({
                    id: v.id,
                    vendor_name: v.vendor_name
                }));
            })
            .catch(error => console.log('Failed to load vendors:', error));
    }

    // Load clients for client autocomplete
    function loadClientList() {
        api.get('/v1/clients/')
            .then(data => {
                console.log('Raw client API response:', data);
                console.log('data.results:', data.results);
                console.log('Array.isArray(data):', Array.isArray(data));

                // Handle both array and paginated response formats
                const clientsArray = Array.isArray(data) ? data : (data.results || []);

                clientList = clientsArray.map(c => ({
                    id: c.id,
                    full_name: c.full_name
                })).sort((a, b) => a.full_name.localeCompare(b.full_name));
                console.log('Clients loaded:', clientList.length, 'clients');
            })
            .catch(error => console.log('Failed to load clients:', error));
    }

    // Client autocomplete functionality
    const clientInput = document.getElementById('id_client_text');
    const clientHidden = document.getElementById('id_client_hidden');
    const clientSuggestions = document.getElementById('client-suggestions');

    if (clientInput && clientSuggestions) {
        // Load client list
        loadClientList();

        // Show all clients when field is focused (empty)
        clientInput.addEventListener('focus', function() {
            if (!this.value || this.value.trim() === '') {
                showAllClients();
            }
        });

        // Handle input for autocomplete
        clientInput.addEventListener('input', function() {
            const query = this.value;
            const queryLower = query.toLowerCase().trim();

            // Clear hidden field if user is typing and mark as invalid
            if (clientHidden) clientHidden.value = '';
            validClientSelected = false;

            if (query.length < 1) {
                clientSuggestions.style.display = 'none';
                return;
            }

            // Check for exact match (case-insensitive)
            const exactMatch = clientList.find(client =>
                client.full_name && client.full_name.toLowerCase() === queryLower
            );

            if (exactMatch) {
                // Auto-fill with proper capitalization and set hidden ID
                clientInput.value = exactMatch.full_name;
                if (clientHidden) clientHidden.value = exactMatch.id;
                validClientSelected = true; // Mark as valid
                clientSuggestions.style.display = 'none';
                // Trigger case dropdown update
                const event = new Event('change', { bubbles: true });
                clientInput.dispatchEvent(event);
                return;
            }

            // Filter clients that match the query and sort alphabetically
            const matches = clientList.filter(client =>
                client.full_name && client.full_name.toLowerCase().includes(queryLower)
            ).sort((a, b) => a.full_name.localeCompare(b.full_name));

            console.log('Client search query:', query, '- Matches found:', matches.length);

            // Clear previous suggestions
            clientSuggestions.innerHTML = '';

            if (matches.length > 0) {
                // Add matching clients (already sorted alphabetically)
                matches.forEach(client => {
                    const item = document.createElement('a');
                    item.className = 'dropdown-item';
                    item.href = '#';
                    item.textContent = client.full_name;
                    item.onclick = function(e) {
                        e.preventDefault();
                        clientInput.value = client.full_name;
                        if (clientHidden) clientHidden.value = client.id;
                        validClientSelected = true; // Mark as valid when selected from list
                        clientSuggestions.style.display = 'none';
                        // Trigger case dropdown update
                        loadCasesForClient(client.id);
                    };
                    clientSuggestions.appendChild(item);
                });

                clientSuggestions.style.display = 'block';
            } else {
                clientSuggestions.style.display = 'none';
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (e.target !== clientInput && e.target !== clientSuggestions) {
                clientSuggestions.style.display = 'none';
            }
        });

        // Function to show all clients (already sorted alphabetically when loaded)
        function showAllClients() {
            clientSuggestions.innerHTML = '';

            clientList.forEach(client => {
                const item = document.createElement('a');
                item.className = 'dropdown-item';
                item.href = '#';
                item.textContent = client.full_name;
                item.onclick = function(e) {
                    e.preventDefault();
                    clientInput.value = client.full_name;
                    if (clientHidden) clientHidden.value = client.id;
                    validClientSelected = true; // Mark as valid when selected from list
                    clientSuggestions.style.display = 'none';
                    // Trigger case dropdown update
                    loadCasesForClient(client.id);
                };
                clientSuggestions.appendChild(item);
            });

            clientSuggestions.style.display = 'block';
        }
    }

    // Payee autocomplete functionality (copied from case-detail.js working implementation)
    const payeeInput = document.getElementById('id_payee_text');
    const suggestions = document.getElementById('payee-suggestions');
    const payeeError = document.getElementById('payee-error');

    if (payeeInput && suggestions) {
        // Show random vendors when field is focused (empty)
        payeeInput.addEventListener('focus', function() {
            if (!this.value || this.value.trim() === '') {
                showRandomVendors();
            }
        });

        // Handle input for autocomplete
        payeeInput.addEventListener('input', function() {
            const query = this.value;
            const queryLower = query.toLowerCase().trim();

            // Mark payee as invalid when user types (will be revalidated on exact match or selection)
            validPayeeSelected = false;

            if (query.length < 1) {
                suggestions.style.display = 'none';
                if (payeeError) payeeError.style.display = 'none';
                return;
            }

            // Check for exact match (case-insensitive)
            const exactMatch = vendorList.find(vendor =>
                vendor.vendor_name && vendor.vendor_name.toLowerCase() === queryLower
            );

            if (exactMatch) {
                // Auto-fill with proper capitalization and mark as valid
                payeeInput.value = exactMatch.vendor_name;
                validPayeeSelected = true;
                suggestions.style.display = 'none';
                if (payeeError) payeeError.style.display = 'none';
                return;
            }

            // Filter vendors that match the query (alphabetical search)
            const matches = vendorList.filter(vendor =>
                vendor.vendor_name && vendor.vendor_name.toLowerCase().includes(queryLower)
            ).sort((a, b) => a.vendor_name.localeCompare(b.vendor_name));

            // Clear previous suggestions
            suggestions.innerHTML = '';

            if (matches.length > 0) {
                // Add matching vendors
                matches.forEach(vendor => {
                    const item = document.createElement('a');
                    item.className = 'dropdown-item';
                    item.href = '#';
                    item.textContent = vendor.vendor_name;
                    item.onclick = function(e) {
                        e.preventDefault();
                        payeeInput.value = vendor.vendor_name;
                        validPayeeSelected = true; // Mark as valid when selected from list
                        suggestions.style.display = 'none';
                        if (payeeError) payeeError.style.display = 'none';
                    };
                    suggestions.appendChild(item);
                });

                // Add "Add as new payee" option at the end
                const addNewItem = document.createElement('a');
                addNewItem.className = 'dropdown-item add-new';
                addNewItem.href = '#';
                addNewItem.innerHTML = `<i class="fas fa-plus"></i> Add "${query}" as new payee`;
                addNewItem.onclick = function(e) {
                    e.preventDefault();
                    showAddPayeeModal(query);
                    suggestions.style.display = 'none';
                };
                suggestions.appendChild(addNewItem);

                suggestions.style.display = 'block';
                if (payeeError) payeeError.style.display = 'none';
            } else {
                // No matches found - show "Add as new payee" option
                const separator = document.createElement('div');
                separator.className = 'dropdown-divider';
                suggestions.appendChild(separator);

                const addNewItem = document.createElement('a');
                addNewItem.className = 'dropdown-item add-new';
                addNewItem.href = '#';
                addNewItem.innerHTML = `<i class="fas fa-plus"></i> Add "${query}" as new payee`;
                addNewItem.onclick = function(e) {
                    e.preventDefault();
                    showAddPayeeModal(query);
                    suggestions.style.display = 'none';
                };
                suggestions.appendChild(addNewItem);
                suggestions.style.display = 'block';
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('#id_payee_text') && !e.target.closest('#payee-suggestions')) {
                suggestions.style.display = 'none';
            }
        });
    }

    // Helper function to show random vendors
    function showRandomVendors() {
        if (!suggestions) return;

        suggestions.innerHTML = '';

        if (vendorList.length === 0) {
            // Show "Add new payee" option when no vendors exist
            const addNewItem = document.createElement('a');
            addNewItem.className = 'dropdown-item add-new';
            addNewItem.href = '#';
            addNewItem.innerHTML = '<i class="fas fa-plus"></i> Add new payee';
            addNewItem.onclick = function(e) {
                e.preventDefault();
                suggestions.style.display = 'none';
                showAddPayeeModal('');
            };
            suggestions.appendChild(addNewItem);
            suggestions.style.display = 'block';
            return;
        }

        // Get 5 random vendors
        const shuffled = [...vendorList].sort(() => 0.5 - Math.random());
        const randomVendors = shuffled.slice(0, Math.min(5, vendorList.length));

        // Display random vendors
        randomVendors.forEach(vendor => {
            const item = document.createElement('a');
            item.className = 'dropdown-item';
            item.href = '#';
            item.textContent = vendor.vendor_name;
            item.onclick = function(e) {
                e.preventDefault();
                if (payeeInput) {
                    payeeInput.value = vendor.vendor_name;
                    validPayeeSelected = true; // Mark as valid when selected from list
                }
                suggestions.style.display = 'none';
            };
            suggestions.appendChild(item);
        });

        // Add separator
        const separator = document.createElement('div');
        separator.className = 'dropdown-divider';
        suggestions.appendChild(separator);

        // Add "Add new payee" option
        const addNewItem = document.createElement('a');
        addNewItem.className = 'dropdown-item add-new';
        addNewItem.href = '#';
        addNewItem.innerHTML = '<i class="fas fa-plus"></i> Add new payee';
        addNewItem.onclick = function(e) {
            e.preventDefault();
            showAddPayeeModal('');
            suggestions.style.display = 'none';
        };
        suggestions.appendChild(addNewItem);

        suggestions.style.display = 'block';
    }

    // Helper function to show ALL vendors
    function showAllVendors() {
        if (!suggestions) return;

        suggestions.innerHTML = '';

        if (vendorList.length === 0) {
            const noVendorsItem = document.createElement('div');
            noVendorsItem.className = 'dropdown-item text-muted';
            noVendorsItem.textContent = 'No vendors found';
            suggestions.appendChild(noVendorsItem);
        } else {
            // Display ALL vendors (sorted alphabetically)
            const sortedVendors = [...vendorList].sort((a, b) =>
                a.vendor_name.localeCompare(b.vendor_name)
            );

            sortedVendors.forEach(vendor => {
                const item = document.createElement('a');
                item.className = 'dropdown-item';
                item.href = '#';
                item.textContent = vendor.vendor_name;
                item.onclick = function(e) {
                    e.preventDefault();
                    if (payeeInput) payeeInput.value = vendor.vendor_name;
                    suggestions.style.display = 'none';
                };
                suggestions.appendChild(item);
            });
        }

        // Add separator
        const separator = document.createElement('div');
        separator.className = 'dropdown-divider';
        suggestions.appendChild(separator);

        // Add "Add new payee" option at bottom
        const addNewItem = document.createElement('a');
        addNewItem.className = 'dropdown-item add-new';
        addNewItem.href = '#';
        addNewItem.innerHTML = '<i class="fas fa-plus"></i> Add new payee';
        addNewItem.onclick = function(e) {
            e.preventDefault();
            showAddPayeeModal('');
            suggestions.style.display = 'none';
        };
        suggestions.appendChild(addNewItem);

        suggestions.style.display = 'block';
    }

    // Format amount with commas as user types and validate against balance
    const amountDisplay = document.getElementById('id_amount_display');
    const amountHidden = document.getElementById('id_amount_hidden');
    const amountError = document.getElementById('amount-error');

    if (amountDisplay && amountHidden) {
        amountDisplay.addEventListener('input', function() {
            let value = this.value.replace(/[^\d.]/g, ''); // Remove all non-digit and non-decimal
            const parts = value.split('.');

            // Add commas to integer part
            if (parts[0]) {
                parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            }

            // Limit to 2 decimal places
            if (parts[1]) {
                parts[1] = parts[1].substring(0, 2);
            }

            const displayValue = parts.join('.');
            this.value = displayValue;

            // Store raw value without commas in hidden field
            amountHidden.value = value;

            // Validate against available balance
            validateTransactionAmount();
        });
    }

    // Function to validate transaction amount against available balance
    function validateTransactionAmount() {
        const transactionType = document.getElementById('id_transaction_type')?.value;
        const amount = parseFloat(amountHidden?.value) || 0;
        const availableFundsText = document.getElementById('available-funds')?.textContent || '0';
        const cleanFundsText = availableFundsText.replace(/,/g, '');
        const availableBalance = parseFloat(cleanFundsText) || 0;

        if (transactionType === 'WITHDRAWAL' && amount > 0) {
            if (availableBalance < 0 || amount > availableBalance) {
                amountError.style.display = 'block';
                amountDisplay.classList.add('is-invalid');
                return false;
            } else {
                amountError.style.display = 'none';
                amountDisplay.classList.remove('is-invalid');
                return true;
            }
        } else {
            amountError.style.display = 'none';
            amountDisplay.classList.remove('is-invalid');
            return true;
        }
    }

    // Case dropdown handler moved to attachCaseDropdownHandler() - called after modal loads

    // Validate amount when transaction type changes
    const transactionType = document.getElementById('id_transaction_type');
    if (transactionType) {
        transactionType.addEventListener('change', validateTransactionAmount);
    }

    // Initialize everything
    loadVendorList();
    updateAvailableFunds();
}

// Attach case dropdown handler - call this AFTER modal content is loaded
function attachCaseDropdownHandler() {
    console.log('[CASE DROPDOWN] Attaching handler...');

    // Note: Client field is now an autocomplete text input, not a dropdown
    // Case loading is handled by the client autocomplete calling loadCasesForClient()
    // We only need to attach the case dropdown change handler here

    const caseSelect = document.getElementById('id_case');

    if (caseSelect) {
        console.log('[CASE DROPDOWN] Case dropdown found, attaching change handler');

        // Case dropdown change handler - THIS is where we update available funds
        caseSelect.addEventListener('change', function() {
            console.log('[CASE DROPDOWN] Case changed, updating available funds...');
            updateAvailableFunds();
        });

        console.log('[CASE DROPDOWN] Handler attached successfully!');
    } else {
        console.error('[CASE DROPDOWN] Could not find case select element!');
    }
}

// Flag to prevent duplicate submissions
let isSubmittingTransaction = false;

async function submitTransactionForm() {
    // Prevent duplicate submissions
    if (isSubmittingTransaction) {
        console.log('Transaction already being submitted, ignoring duplicate call');
        return;
    }

    isSubmittingTransaction = true;

    const form = document.querySelector('#transactionModalContent form');
    if (!form) {
        isSubmittingTransaction = false;
        return;
    }

    // Get form data
    const formData = new FormData(form);

    // Convert to JSON - use hidden amount field for actual value
    const data = {
        bank_account: formData.get('bank_account'),
        transaction_date: formData.get('transaction_date'),
        transaction_type: formData.get('transaction_type'),
        amount: document.getElementById('id_amount_hidden')?.value || formData.get('amount'),
        description: formData.get('description'),
        reference_number: formData.get('reference_number'),
        payee: formData.get('payee'),
        check_memo: formData.get('check_memo') || '',
        client: formData.get('client') || null,
        case: formData.get('case') || null,
        status: 'pending'
    };

    // Validate ALL required fields
    if (!data.bank_account) {
        showErrorMessage('Please select a Bank Account before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.client) {
        showErrorMessage('Please select a Client before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    // REQUIREMENT: Validate that client is from valid client list (not random string)
    if (!validClientSelected) {
        showErrorMessage('Please select a valid Client from the list.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.case) {
        showErrorMessage('Please select a Case before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.transaction_date) {
        showErrorMessage('Please enter a Transaction Date before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.transaction_type) {
        showErrorMessage('Please select a Transaction Type before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.reference_number || data.reference_number.trim() === '') {
        showErrorMessage('Please enter a Reference Number before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.payee || data.payee.trim() === '') {
        showErrorMessage('Please enter a Payee before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    // REQUIREMENT: Validate that payee is from valid vendor list (not random string)
    if (!validPayeeSelected) {
        showErrorMessage('Please select a valid Payee from the list or click "Add as new payee" to create one.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.amount || parseFloat(data.amount) <= 0) {
        showErrorMessage('Please enter a valid Amount before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    if (!data.description || data.description.trim() === '') {
        showErrorMessage('Please enter a Description before saving the transaction.');
        isSubmittingTransaction = false;
        return;
    }

    try {
        let response;
        const transactionType = data.transaction_type === 'DEPOSIT' ? 'Deposit' : 'Withdrawal';

        // Check if we're editing or creating
        if (window.editingTransactionId) {
            // Update existing transaction
            response = await api.put(`/v1/bank-accounts/bank-transactions/${window.editingTransactionId}/`, data);
            showSuccessMessage(`${transactionType} transaction updated successfully!`);
            // Clear the editing ID
            window.editingTransactionId = null;
        } else {
            // Create new transaction
            response = await api.post('/v1/bank-accounts/bank-transactions/', data);
            showSuccessMessage(`${transactionType} transaction added successfully!`);
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
        modal.hide();

        // Reload transactions
        loadTransactions();

        // Reset submission flag
        isSubmittingTransaction = false;
    } catch (error) {
        console.error('Error submitting form:', error);

        // Extract clean error message from validation errors
        let errorMessage = 'Error saving transaction. Please try again.';

        if (error.validationErrors) {
            // DRF validation errors format: {field: [messages]}
            const errors = error.validationErrors;

            // Extract the first error message from any field
            for (const field in errors) {
                if (Array.isArray(errors[field]) && errors[field].length > 0) {
                    errorMessage = errors[field][0];
                    break;
                } else if (typeof errors[field] === 'string') {
                    errorMessage = errors[field];
                    break;
                }
            }
        } else if (error.message) {
            errorMessage = error.message;
        }

        showErrorMessage(errorMessage);

        // Reset submission flag
        isSubmittingTransaction = false;
    }
}

// Function to show add payee modal - IDENTICAL TO CASE-DETAIL.JS IMPLEMENTATION
function showAddPayeeModal(payeeName) {
    // Create modal dynamically
    const modalHtml = `
        <div class="modal fade" id="addPayeeModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered" style="max-width: 60%;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Payee/Vendor</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="payeeForm">
                            <div class="row">
                                <div class="col-md-12 mb-3">
                                    <label class="form-label">Vendor Name <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" id="payee_vendor_name" name="vendor_name" value="${payeeName || ''}" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Contact Person</label>
                                    <input type="text" class="form-control" id="payee_contact_person" name="contact_person">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Phone</label>
                                    <input type="tel" class="form-control" id="payee_phone" name="phone" placeholder="(555) 123-4567">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-12 mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" id="payee_email" name="email">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-12 mb-3">
                                    <label class="form-label">Address</label>
                                    <textarea class="form-control" id="payee_address" name="address" rows="2"></textarea>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">City</label>
                                    <input type="text" class="form-control" id="payee_city" name="city">
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">State</label>
                                    <select class="form-select" id="payee_state" name="state">
                                        <option value="">Select State</option>
                                        ${getStateOptions()}
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">Zip Code</label>
                                    <input type="text" class="form-control" id="payee_zip_code" name="zip_code" maxlength="5">
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="savePayeeBtn">
                            <i class="fas fa-save"></i> Save Payee
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if present
    const existing = document.getElementById('addPayeeModal');
    if (existing) existing.remove();

    // Add modal to DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Get field references
    const nameField = document.getElementById('payee_vendor_name');
    const phoneField = document.getElementById('payee_phone');
    const zipField = document.getElementById('payee_zip_code');

    // Lock vendor name field if provided from autocomplete
    if (payeeName && payeeName.trim() !== '') {
        nameField.readOnly = true;
        nameField.style.backgroundColor = '#e9ecef';
        nameField.style.cursor = 'not-allowed';
    } else {
        nameField.readOnly = false;
        nameField.style.backgroundColor = '';
        nameField.style.cursor = '';
    }

    // Setup US phone number formatting: (XXX) XXX-XXXX
    phoneField.addEventListener('input', function(e) {
        let cleaned = this.value.replace(/\D/g, '');
        cleaned = cleaned.substring(0, 10);

        let formatted = '';
        if (cleaned.length > 0) {
            formatted = '(' + cleaned.substring(0, 3);
        }
        if (cleaned.length > 3) {
            formatted += ') ' + cleaned.substring(3, 6);
        }
        if (cleaned.length > 6) {
            formatted += '-' + cleaned.substring(6, 10);
        }

        this.value = formatted;
    });

    // Setup zip code formatting (5 digits only)
    zipField.addEventListener('input', function(e) {
        this.value = this.value.replace(/\D/g, '').substring(0, 5);
    });

    // Track save success for cleanup
    let saveSuccessful = false;

    // Setup save button handler
    document.getElementById('savePayeeBtn').onclick = async function() {
        const result = await saveNewPayee(payeeName);
        if (result === true) {
            saveSuccessful = true;
        }
    };

    // Show modal
    const modalEl = document.getElementById('addPayeeModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    // Clear payee field ONLY when cancelled (not when saved successfully)
    modalEl.addEventListener('hidden.bs.modal', function() {
        // Only clear if save was NOT successful
        if (!saveSuccessful) {
            const payeeField = document.getElementById('id_payee_text');
            if (payeeField) {
                payeeField.value = '';
            }
        }
        // Remove modal from DOM
        this.remove();
    }, { once: true });
}

// Save new payee/vendor - IDENTICAL TO CASE-DETAIL.JS IMPLEMENTATION
async function saveNewPayee(originalName) {
    const form = document.getElementById('payeeForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return false;
    }

    const vendorData = {
        vendor_name: document.getElementById('payee_vendor_name').value,
        contact_person: document.getElementById('payee_contact_person').value,
        phone: document.getElementById('payee_phone').value,
        email: document.getElementById('payee_email').value,
        address: document.getElementById('payee_address').value,
        city: document.getElementById('payee_city').value,
        state: document.getElementById('payee_state').value,
        zip_code: document.getElementById('payee_zip_code').value
    };

    // Validate email format if provided
    if (vendorData.email && vendorData.email.trim() !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(vendorData.email)) {
            alert('Please enter a valid email address (e.g., example@domain.com)');
            return false;
        }
    }

    // Validate US phone format if provided (must be 10 digits)
    if (vendorData.phone && vendorData.phone.trim() !== '') {
        const digitsOnly = vendorData.phone.replace(/\D/g, '');
        if (digitsOnly.length !== 10) {
            alert('Please enter a valid US phone number with 10 digits (e.g., (555) 123-4567)');
            return false;
        }
    }

    try {
        // Show loading state
        const saveBtn = document.getElementById('savePayeeBtn');
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

        // Submit to API
        const response = await api.post('/v1/vendors/', vendorData);

        // Success - update payee field with saved vendor name
        document.getElementById('id_payee_text').value = vendorData.vendor_name;
        validPayeeSelected = true; // Mark as valid after successful vendor creation

        // Add to vendor list for autocomplete
        vendorList.push({
            id: response.id,
            vendor_name: vendorData.vendor_name
        });

        // Show success message
        showSuccessMessage(`Vendor "${vendorData.vendor_name}" added successfully!`);

        // Close modal
        const modalEl = document.getElementById('addPayeeModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        return true;

    } catch (error) {
        console.error('Error saving vendor:', error);
        alert('Error saving payee: ' + (error.message || 'Please try again'));

        // Restore button state
        const saveBtn = document.getElementById('savePayeeBtn');
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Payee';

        return false;
    }
}

function getStateOptions() {
    const states = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'];
    return states.map(s => `<option value="${s}">${s}</option>`).join('');
}

// Success/Error message functions
function showSuccessMessage(message) {
    // Remove any existing toast
    const existingToast = document.getElementById('successToast');
    if (existingToast) existingToast.remove();

    // Create toast HTML
    const toastHTML = `
        <div id="successToast" class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true" style="position: fixed; top: 80px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    // Add to page
    document.body.insertAdjacentHTML('beforeend', toastHTML);

    // Show toast
    const toastElement = document.getElementById('successToast');
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();

    // Remove from DOM after hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function showErrorMessage(message) {
    // Remove any existing toast
    const existingToast = document.getElementById('errorToast');
    if (existingToast) existingToast.remove();

    // Create toast HTML
    const toastHTML = `
        <div id="errorToast" class="toast align-items-center text-white bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true" style="position: fixed; top: 80px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-circle me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    // Add to page
    document.body.insertAdjacentHTML('beforeend', toastHTML);

    // Show toast
    const toastElement = document.getElementById('errorToast');
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();

    // Remove from DOM after hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}
