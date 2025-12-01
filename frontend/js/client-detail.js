// Client Detail Page Logic
let currentClient = null;
let clientId = null;

// Extract client ID from URL
function getClientIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    // URL format: /clients/123
    const id = pathParts[2];
    return id ? parseInt(id) : null;
}

// Load page on startup
document.addEventListener('DOMContentLoaded', async function() {
    // BUG #11 FIX: Setup page protection against back button after logout
    if (!api.setupPageProtection()) {
        return; // User was logged out, redirect handled
    }

    await checkAuth();

    clientId = getClientIdFromUrl();

    if (!clientId) {
        // alert('Invalid client ID');
        window.location.href = '/clients';
        return;
    }

    await loadLawFirmInfo();
    await loadClientDetails();
    await loadClientCases();

    // BUG #2 FIX: Setup event listeners - open modal instead of redirect
    document.getElementById('editClientBtn').addEventListener('click', function() {
        editClient(clientId);
    });

    // BUG #3 FIX: Add case button opens modal
    document.getElementById('addCaseBtn').addEventListener('click', function() {
        addCase(clientId);
    });
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
            document.getElementById('headerLawFirmName').textContent = firm.firm_name;
            const details = `${firm.address}, ${firm.city}, ${firm.state} ${firm.zip_code} | ${firm.phone} | ${firm.email}`;
            document.getElementById('lawFirmDetails').textContent = details;
            document.getElementById('headerFirmDetails').textContent = details;
        }
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

async function loadClientDetails() {
    try {
        // console.log('Loading client ID:', clientId);
        const client = await api.get(`/v1/clients/${clientId}/`);
        // console.log('Client data received:', client);
        currentClient = client;

        // Update page titles
        const fullName = client.client_name || client.full_name || '';
        document.getElementById('cardClientName').textContent = `Client Details: ${fullName}`;

        // Populate details - safely access all fields
        document.getElementById('detail-name').textContent = fullName || '-';
        document.getElementById('detail-phone').textContent = client.phone ? formatPhone(client.phone) : '-';
        document.getElementById('detail-email').textContent = client.email || '-';
        document.getElementById('detail-address').textContent = client.address || '-';
        document.getElementById('detail-city').textContent = client.city || '-';
        document.getElementById('detail-state').textContent = client.state || '-';
        document.getElementById('detail-zip').textContent = client.zip_code || '-';

        // Status badge
        const statusBadge = client.is_active
            ? '<span class="badge bg-success">Active</span>'
            : '<span class="badge bg-secondary">Inactive</span>';
        document.getElementById('detail-status').innerHTML = statusBadge;

        // Trust Account Status
        const trustStatus = getTrustAccountBadge(
            client.calculated_trust_status || client.trust_account_status,
            client.formatted_balance
        );
        document.getElementById('detail-trust-status').innerHTML = trustStatus;

        // Created date
        if (client.created_at) {
            const createdDate = new Date(client.created_at);
            document.getElementById('detail-created').textContent = createdDate.toLocaleDateString('en-US');
        } else {
            document.getElementById('detail-created').textContent = '-';
        }

        // Updated date
        if (client.updated_at) {
            const updatedDate = new Date(client.updated_at);
            document.getElementById('detail-updated').textContent = updatedDate.toLocaleDateString('en-US');
        } else {
            document.getElementById('detail-updated').textContent = '-';
        }

    } catch (error) {
        // console.error('Error loading client details:', error);
        // console.error('Error message:', error.message);
        // console.error('Error stack:', error.stack);
        // Show error in page instead of redirect
        document.getElementById('cardClientName').textContent = 'Error Loading Client';
    }
}

async function toggleTransactions(caseId) {
    const transactionsDiv = document.getElementById(`transactions-${caseId}`);
    const icon = document.getElementById(`expand-icon-${caseId}`);
    const contentDiv = document.getElementById(`transactions-content-${caseId}`);

    if (transactionsDiv.style.display === 'none') {
        // Show transactions
        transactionsDiv.style.display = '';
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');

        // Load transactions if not loaded yet
        if (contentDiv.querySelector('.fa-spinner')) {
            await loadTransactions(caseId);
        }
    } else {
        // Hide transactions
        transactionsDiv.style.display = 'none';
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
    }
}

async function loadTransactions(caseId) {
    const contentDiv = document.getElementById(`transactions-content-${caseId}`);

    try {
        const data = await api.get(`/v1/cases/${caseId}/transactions/`);
        const transactions = data.transactions || [];

        if (transactions.length === 0) {
            contentDiv.innerHTML = `
                <div class="text-center py-3 text-muted">
                    <i class="fas fa-receipt fa-2x mb-2"></i><br>
                    No transactions found for this case.
                </div>
            `;
            return;
        }

        let html = `
            <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                    <thead class="table-secondary">
                        <tr>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Reference</th>
                            <th>Payee</th>
                            <th>Description</th>
                            <th>Amount</th>
                            <th>Balance</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        // Calculate running balance (start from 0, go through transactions in chronological order)
        // Transactions are already sorted newest first, so we need to reverse, calculate, then display
        let runningBalance = 0;
        const txnsWithBalance = [];

        // Process transactions in reverse (oldest first) to calculate running balance
        for (let i = transactions.length - 1; i >= 0; i--) {
            const txn = transactions[i];
            const amount = parseFloat(txn.amount || 0);
            const type = txn.transaction_type || txn.type || '';

            // Add to running balance based on type
            if (type === 'DEPOSIT' || type === 'Deposit') {
                runningBalance += amount;
            } else if (type === 'WITHDRAWAL' || type === 'Withdrawal') {
                runningBalance -= amount;
            }

            txnsWithBalance.unshift({
                ...txn,
                balance: runningBalance
            });
        }

        txnsWithBalance.forEach(txn => {
            // Handle voided transactions - check status field
            const isVoided = txn.status.toLowerCase() === 'voided';

            // Type badge
            let typeClass = 'bg-secondary';
            let typeText = txn.transaction_type || txn.type || 'UNKNOWN';
            if (typeText === 'DEPOSIT' || typeText === 'Deposit') {
                typeClass = 'bg-success';
                typeText = 'DEPOSIT';
            } else if (typeText === 'WITHDRAWAL' || typeText === 'Withdrawal') {
                typeClass = 'bg-danger';
                typeText = 'WITHDRAWAL';
            }

            // Amount class - voided transactions show differently
            let amountClass = typeText === 'DEPOSIT' ? 'text-success' : 'text-danger';
            let displayAmount = txn.amount;

            // For voided transactions, show as $0.00 with strikethrough on original amount
            if (isVoided) {
                amountClass = 'text-muted';
                // Amount should already be 0.00 from API, but ensure it
                displayAmount = '0.00';
            }

            // Get payee name - check multiple possible fields
            let payeeName = txn.payee || txn.payee_name || txn.vendor_name || txn.client_name;
            if (!payeeName && txn.vendor) {
                payeeName = txn.vendor;
            }
            if (!payeeName && txn.client) {
                payeeName = txn.client;
            }
            payeeName = payeeName || '-';

            // Status badge - handle voided, cleared, pending
            let statusClass = 'bg-warning';
            let statusText = 'Pending';

            // Check status field directly
            if (txn.status.toLowerCase() === 'voided') {
                statusClass = 'bg-danger';
                statusText = 'Voided';
            } else if (txn.status.toLowerCase() === 'cleared') {
                statusClass = 'bg-success';
                statusText = 'Cleared';
            } else if (txn.status.toLowerCase() === 'pending') {
                statusClass = 'bg-warning';
                statusText = 'Pending';
            }

            // Balance color - positive green, negative red, zero gray
            let balanceClass = 'text-success fw-bold';
            if (txn.balance < 0) {
                balanceClass = 'text-danger fw-bold';
            } else if (txn.balance === 0) {
                balanceClass = 'text-muted';
            }

            html += `
                <tr ${isVoided ? 'class="text-muted"' : ''}>
                    <td ${isVoided ? 'style="text-decoration: line-through;"' : ''}>${formatDate(txn.transaction_date || txn.date)}</td>
                    <td ${isVoided ? 'style="text-decoration: line-through;"' : ''}><span class="badge ${typeClass}">${typeText}</span></td>
                    <td ${isVoided ? 'style="text-decoration: line-through;"' : ''}>${txn.reference_number || txn.transaction_number || '-'}</td>
                    <td ${isVoided ? 'style="text-decoration: line-through;"' : ''}>${payeeName}</td>
                    <td ${isVoided ? 'style="text-decoration: line-through;"' : ''}>${txn.description || '-'}</td>
                    <td class="${amountClass}" ${isVoided ? 'style="text-decoration: line-through;"' : ''}>${formatCurrency(displayAmount)}</td>
                    <td class="${balanceClass}">${formatCurrency(txn.balance)}</td>
                    <td><span class="badge ${statusClass}">${statusText}</span></td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        contentDiv.innerHTML = html;

    } catch (error) {
        // console.error('Error loading transactions:', error);
        contentDiv.innerHTML = `
            <div class="alert alert-danger">
                Error loading transactions.
            </div>
        `;
    }
}

function addCase(clientId) {
    console.log('========================================');
    console.log('➕ ADD NEW CASE - CLIENT DETAIL');
    console.log('Client ID:', clientId);
    console.log('========================================');

    // Reset form
    document.getElementById('edit_case_id').value = '';
    document.getElementById('edit_case_client').value = clientId;
    document.getElementById('edit_case_title').value = '';
    document.getElementById('edit_case_description').value = '';
    document.getElementById('edit_case_status').value = 'Open';

    // Hide case status for new cases (it's set automatically)
    document.getElementById('edit_case_status_container').style.display = 'none';

    // Update modal title
    document.getElementById('caseModalTitle').textContent = 'Add New Case';
    document.getElementById('saveCaseBtn').innerHTML = '<i class="fas fa-plus"></i> Add Case';

    // Show modal
    const modalEl = document.getElementById('caseModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    console.log('✅ Add case modal shown');
}

// Edit case function
async function editCase(caseId) {
    console.log('========================================');
    console.log('🔧 EDIT CASE CLICKED - CLIENT DETAIL');
    console.log('Case ID:', caseId);
    console.log('========================================');

    try {
        console.log('📡 Fetching case data from API...');
        const response = await fetch(`/api/v1/cases/${caseId}/`, {
            credentials: 'include'
        });
        console.log('✅ API Response received:', response.status);

        if (!response.ok) {
            throw new Error('Failed to load case');
        }

        const caseData = await response.json();
        console.log('📦 Case data loaded:', caseData);

        // Populate form fields
        document.getElementById('edit_case_id').value = caseData.id;
        document.getElementById('edit_case_client').value = caseData.client;
        document.getElementById('edit_case_title').value = caseData.case_title || '';
        document.getElementById('edit_case_description').value = caseData.case_description || '';
        document.getElementById('edit_case_status').value = caseData.case_status || 'Open';

        // Show case status field when editing (in case it was hidden from add mode)
        document.getElementById('edit_case_status_container').style.display = 'block';

        // Update modal title
        document.getElementById('caseModalTitle').textContent = 'Edit Case';
        document.getElementById('saveCaseBtn').innerHTML = '<i class="fas fa-save"></i> Save Changes';

        console.log('✅ Form fields populated');

        // Show modal
        const modalEl = document.getElementById('caseModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
        console.log('✅ Modal shown');

    } catch (error) {
        console.error('❌ Error loading case:', error);
        showErrorMessage('Error loading case: ' + error.message);
    }
}

// Save case changes (handles both add and edit)
async function saveCaseChanges() {
    const caseId = document.getElementById('edit_case_id').value;
    const isNewCase = !caseId;

    // Validate required fields
    const caseTitle = document.getElementById('edit_case_title').value.trim();
    if (!caseTitle) {
        showErrorMessage('Case title is required');
        return;
    }

    const formData = {
        client: parseInt(document.getElementById('edit_case_client').value),
        case_title: caseTitle,
        case_description: document.getElementById('edit_case_description').value,
        case_status: document.getElementById('edit_case_status').value,
    };

    console.log('💾 Saving case:', isNewCase ? 'NEW' : caseId, formData);

    try {
        let response;

        if (isNewCase) {
            // POST to create new case
            response = await fetch('/api/v1/cases/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': api.getCsrfToken()
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
        } else {
            // PUT to update existing case
            response = await fetch(`/api/v1/cases/${caseId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': api.getCsrfToken()
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            // Throw error with full error data for proper handling
            const error = new Error((isNewCase ? 'Failed to create case' : 'Failed to update case'));
            error.validationErrors = errorData;
            throw error;
        }

        console.log('✅ Case saved successfully');

        // Close modal
        const modalEl = document.getElementById('caseModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        // Show success message
        showSuccessMessage(isNewCase ? 'Case created successfully!' : 'Case updated successfully!');

        // Reload cases
        await loadClientCases();

    } catch (error) {
        console.error('Error saving case:', error);

        // BUG #17, #18, #20, #21 FIX: Properly display validation errors
        if (error.validationErrors) {
            let errorMessage = 'Please fix the following errors:\n\n';
            const errors = error.validationErrors;

            for (const [field, messages] of Object.entries(errors)) {
                const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                const message = Array.isArray(messages) ? messages[0] : messages;
                errorMessage += `• ${fieldName}: ${message}\n`;
            }

            showErrorMessage(errorMessage);
        } else {
            showErrorMessage('Error saving case: ' + error.message);
        }
    }
}

function viewCase(caseId) {
    window.location.href = `/cases/${caseId}`;
}

function deleteCase(caseId, caseTitle) {
    if (confirm(`Are you sure you want to delete case "${caseTitle}"?`)) {
        api.delete(`/v1/cases/${caseId}/`)
            .then(() => {
                // alert('Case deleted successfully');
                loadClientCases();
            })
            .catch(error => {
                // console.error('Error deleting case:', error);
                // alert('Error deleting case: ' + error.message);
            });
    }
}

function getCaseStatusBadge(status) {
    const statusMap = {
        'Open': 'bg-primary',
        'Pending Settlement': 'bg-warning',
        'Settled': 'bg-success',
        'Closed': 'bg-secondary',
    };
    const badgeClass = statusMap[status] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${status}</span>`;
}

function getBalanceClass(balance) {
    if (balance < 0) return 'text-danger fw-bold';
    if (balance === 0) return 'text-muted';
    return 'text-success';
}

function formatCurrency(value) {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';

    if (num < 0) {
        return `($${Math.abs(num).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})})`;
    }
    return `$${num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

function formatPhone(phone) {
    if (!phone) return null;
    const cleaned = ('' + phone).replace(/\D/g, '');
    if (cleaned.length === 10) {
        return `(${cleaned.substring(0, 3)}) ${cleaned.substring(3, 6)}-${cleaned.substring(6)}`;
    }
    return phone;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US');
}

function getTrustAccountBadge(status, balance) {
    const statusMap = {
        'ACTIVE_WITH_FUNDS': { class: 'bg-success', text: 'Active with Funds' },
        'ACTIVE_ZERO_BALANCE': { class: 'bg-info', text: 'Active - Zero Balance' },
        'NEGATIVE_BALANCE': { class: 'bg-danger', text: 'Negative Balance' },
        'DORMANT': { class: 'bg-warning', text: 'Dormant' },
        'CLOSED': { class: 'bg-secondary', text: 'Closed/Inactive' }
    };

    const statusInfo = statusMap[status] || { class: 'bg-secondary', text: status };
    return `<span class="badge ${statusInfo.class}">${statusInfo.text}</span>`;
}

let allCasesData = [];

async function loadClientCases() {
    try {
        const data = await api.get(`/v1/clients/${clientId}/cases/`);
        allCasesData = data.cases || [];
        displayFilteredCases();
    } catch (error) {
        // console.error('Error loading cases:', error);
        document.getElementById('casesContainer').innerHTML = `
            <div class="alert alert-danger">
                Error loading cases. Please try again.
            </div>
        `;
    }
}

function filterCases() {
    displayFilteredCases();
}

function displayFilteredCases() {
    const filter = document.getElementById('caseFilter').value;

    let filteredCases = allCasesData;

    if (filter === 'active') {
        filteredCases = allCasesData.filter(c => c.is_active);
    } else if (filter === 'inactive') {
        filteredCases = allCasesData.filter(c => !c.is_active);
    }

    if (filteredCases.length === 0) {
        document.getElementById('casesContainer').innerHTML = `
            <div class="text-center py-4">
                <div class="text-muted mb-3">
                    <i class="fas fa-briefcase fa-3x"></i>
                </div>
                <p class="text-muted">No cases found.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="row border-bottom bg-light py-2 mb-2 fw-bold">
            <div class="col-1"></div>
            <div class="col-5">Case Title</div>
            <div class="col-2">Current Balance</div>
            <div class="col-2">Status</div>
            <div class="col-2">Actions</div>
        </div>
    `;

    filteredCases.forEach(caseItem => {
        const caseStatusBadge = getCaseStatusBadge(caseItem.case_status);
        const balanceClass = getBalanceClass(parseFloat(caseItem.current_balance));
        const inactiveClass = caseItem.is_active ? '' : 'opacity-50';

        html += `
            <div class="row border-bottom py-2 align-items-center ${inactiveClass}">
                <div class="col-1">
                    <button class="btn btn-sm btn-outline-secondary" onclick="toggleTransactions(${caseItem.id})" title="Show/Hide Transactions">
                        <i class="fas fa-chevron-down" id="expand-icon-${caseItem.id}"></i>
                    </button>
                </div>
                <div class="col-5">
                    <a href="#" onclick="viewCase(${caseItem.id}); return false;" class="text-decoration-none">
                        ${caseItem.case_title}${!caseItem.is_active ? ' <small class="text-muted">(Inactive)</small>' : ''}
                    </a>
                </div>
                <div class="col-2">
                    <span class="${balanceClass}">${caseItem.formatted_balance}</span>
                </div>
                <div class="col-2">
                    ${caseStatusBadge}
                </div>
                <div class="col-2">
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-primary" title="View Case" onclick="viewCase(${caseItem.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" title="Edit Case" onclick="console.log('🔧 BUTTON CLICKED! Case ID:', ${caseItem.id}); editCase(${caseItem.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" title="Delete Case" onclick="deleteCase(${caseItem.id}, '${caseItem.case_title.replace(/'/g, "\\'")}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
            <div id="transactions-${caseItem.id}" class="row" style="display: none;">
                <div class="col-12">
                    <div class="bg-light border-start border-end border-bottom ms-5 me-3 p-3">
                        <div id="transactions-content-${caseItem.id}">
                            <div class="text-center py-2">
                                <i class="fas fa-spinner fa-spin"></i> Loading transactions...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    document.getElementById('casesContainer').innerHTML = html;
}

// Success/Error toast message functions
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

// BUG #2 FIX: Edit client function - opens modal instead of redirecting
async function editClient(clientId) {
    try {
        // Fetch client data
        const client = await api.get(`/v1/clients/${clientId}/`);

        // Check if we have a client modal in this page, if not, redirect
        const clientModal = document.getElementById('clientModal');
        if (!clientModal) {
            // Modal doesn't exist on this page, redirect to clients page
            window.location.href = `/clients?edit=${clientId}`;
            return;
        }

        // Populate form - combine first and last name into single field
        document.getElementById('client_id').value = client.id;
        const fullName = client.client_name || client.full_name || '';
        document.getElementById('client_name').value = fullName;
        document.getElementById('phone').value = client.phone || '';
        document.getElementById('email').value = client.email || '';
        document.getElementById('address').value = client.address || '';
        document.getElementById('city').value = client.city || '';
        document.getElementById('state').value = client.state || '';
        document.getElementById('zip_code').value = client.zip_code || '';
        document.getElementById('is_active').checked = client.is_active;

        // Update modal title
        document.getElementById('clientModalLabel').textContent = 'Edit Client';
        document.getElementById('clientSubmitBtn').textContent = 'Update Client';

        // Clear validation errors
        document.querySelectorAll('#clientForm .is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        document.querySelectorAll('#clientForm .invalid-feedback').forEach(el => {
            el.textContent = '';
        });

        // Show modal
        new bootstrap.Modal(clientModal).show();

    } catch (error) {
        // BUG #6 FIX: Check for network errors
        if (!navigator.onLine) {
            showErrorMessage('No internet connection. Please check your network and try again.');
        } else {
            console.error('Error loading client:', error);
            showErrorMessage('Error loading client: ' + error.message);
        }
    }
}

// Handle client form submission
document.getElementById('clientForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
        client_name: document.getElementById("client_name").value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        zip_code: document.getElementById('zip_code').value,
        is_active: document.getElementById('is_active').checked
    };

    try {
        const clientId = document.getElementById('client_id').value;

        // Update client
        const response = await api.put(`/v1/clients/${clientId}/`, formData);

        if (response.success || response.id) {
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('clientModal')).hide();

            // Show success message
            showSuccessMessage('Client updated successfully');

            // Reload client details
            await loadClientDetails();
        }
    } catch (error) {
        // Handle validation errors
        if (error.errors) {
            // Clear previous errors
            document.querySelectorAll('#clientForm .is-invalid').forEach(el => {
                el.classList.remove('is-invalid');
            });
            document.querySelectorAll('#clientForm .invalid-feedback').forEach(el => {
                el.textContent = '';
            });

            // Show new errors
            Object.keys(error.errors).forEach(field => {
                const input = document.getElementById(field);
                if (input) {
                    input.classList.add('is-invalid');
                    const feedback = input.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.textContent = error.errors[field][0];
                    }
                }
            });
        } else {
            showErrorMessage(error.message || 'Error updating client');
        }
    }
});

function logout() {
    api.logout();
}

// Phone number auto-formatting
const phoneInput = document.getElementById('phone');
if (phoneInput) {
    phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, ''); // Remove all non-digits
        
        // Limit to 10 digits
        if (value.length > 10) {
            value = value.slice(0, 10);
        }
        
        // Format as (XXX) XXX-XXXX
        let formatted = '';
        if (value.length > 0) {
            formatted = '(' + value.substring(0, 3);
        }
        if (value.length >= 4) {
            formatted += ') ' + value.substring(3, 6);
        }
        if (value.length >= 7) {
            formatted += '-' + value.substring(6, 10);
        }
        
        e.target.value = formatted;
    });

    // Prevent non-numeric input
    phoneInput.addEventListener('keypress', function(e) {
        const char = String.fromCharCode(e.which);
        if (!/[0-9]/.test(char)) {
            e.preventDefault();
        }
    });
}
