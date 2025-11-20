// Clients page logic
let allClients = [];
let allCases = {};
let currentSort = { column: 'name', direction: 'asc' }; // REQUIREMENT: Default sort by name
let searchTimeout;

// Pagination state
let currentPage = 1;
let pageSize = 50; // Show 50 records per page
let totalCount = 0;
let nextPageUrl = null;
let previousPageUrl = null;

// Load clients on page load
document.addEventListener('DOMContentLoaded', async function() {
    // BUG #11 FIX: Setup page protection against back button after logout
    if (!api.setupPageProtection()) {
        return; // User was logged out, redirect handled
    }

    await checkAuth();
    await loadLawFirmInfo();
    await loadStaticTrustBalance(); // REQUIREMENT: Load static trust balance
    await loadClients();

    // Setup search input listener
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', handleSearch);

    // Setup filter form submission
    document.getElementById('filterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 1; // Reset to page 1 when filters change
        loadClients();
    });

    // Reset to page 1 when balance filter changes
    document.getElementById('balance_filter').addEventListener('change', function() {
        currentPage = 1;
        loadClients();
    });

    // Reset to page 1 when status filter changes
    document.getElementById('status_filter').addEventListener('change', function() {
        currentPage = 1;
        loadClients();
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

            // Format: "123 Legal Plaza, New York, NY 10001 | 555-LAW-FIRM | admin@samplelawfirm.com"
            const details = `${firm.address}, ${firm.city}, ${firm.state} ${firm.zip_code} | ${firm.phone} | ${firm.email}`;
            document.getElementById('lawFirmDetails').textContent = details;
            document.getElementById('headerFirmDetails').textContent = details;
        }
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

// REQUIREMENT: Load static trust balance (unaffected by filters/search)
async function loadStaticTrustBalance() {
    try {
        // Call dedicated endpoint for total trust balance
        const data = await api.get('/v1/clients/trust_summary/');

        const totalBalance = parseFloat(data.total_trust_balance) || 0;
        const formatted = totalBalance.toLocaleString('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        document.getElementById('totalTrustBalance').textContent = formatted;
        document.getElementById('balanceDate').textContent = 'Current';

        // Update color based on balance
        const balanceEl = document.getElementById('totalTrustBalance');
        if (totalBalance < 0) {
            balanceEl.classList.add('text-danger');
        } else {
            balanceEl.classList.remove('text-danger');
        }
    } catch (error) {
        console.error('Error loading static trust balance:', error);
        document.getElementById('totalTrustBalance').textContent = 'Error loading';
    }
}

// REQUIREMENT: Load historical trust balance for specific date
async function loadHistoricalTrustBalance() {
    const dateInput = document.getElementById('trustBalanceDate');
    const selectedDate = dateInput.value;

    console.log('loadHistoricalTrustBalance called with date:', selectedDate);

    if (!selectedDate) {
        // If no date, reload current balance
        console.log('No date selected, loading current balance');
        await loadStaticTrustBalance();
        return;
    }

    try {
        // Call API with as_of_date parameter
        console.log('Calling API with date:', selectedDate);
        const data = await api.get(`/v1/clients/trust_summary/?as_of_date=${selectedDate}`);
        console.log('Historical balance API response:', data);

        const totalBalance = parseFloat(data.total_trust_balance) || 0;
        const formatted = totalBalance.toLocaleString('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        console.log('Updating totalTrustBalance to:', formatted);
        const balanceElement = document.getElementById('totalTrustBalance');
        console.log('Balance element found:', balanceElement);
        balanceElement.textContent = formatted;

        // Format date for display
        const dateObj = new Date(selectedDate + 'T00:00:00');
        const formattedDate = dateObj.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        document.getElementById('balanceDate').textContent = `as of ${formattedDate}`;

        // Update color based on balance
        const balanceEl = document.getElementById('totalTrustBalance');
        if (totalBalance < 0) {
            balanceEl.classList.add('text-danger');
        } else {
            balanceEl.classList.remove('text-danger');
        }
    } catch (error) {
        console.error('Error loading historical trust balance:', error);
        console.error('Error details:', error.message, error.stack);
        document.getElementById('totalTrustBalance').textContent = 'Error loading';
        document.getElementById('balanceDate').textContent = 'Error';
    }
}

// REQUIREMENT: Clear historical date filter and show current balance
function clearHistoricalDate() {
    document.getElementById('trustBalanceDate').value = '';
    loadStaticTrustBalance();
}

async function loadClients() {
    try {
        const searchQuery = document.getElementById('search').value.trim();
        const balanceFilter = document.getElementById('balance_filter').value;
        const statusFilter = document.getElementById('status_filter').value;

        // Build query parameters
        let params = new URLSearchParams();

        // REQUIREMENT: When searching, include ALL clients (active and inactive)
        // Status filter only applies when NOT searching
        if (searchQuery.length < 2) {
            // Status filter only when not searching
            if (statusFilter === 'active') {
                params.append('is_active', 'true');
            } else if (statusFilter === 'inactive') {
                params.append('is_active', 'false');
            }
            // 'all' means no status filter
        }

        // BUG #8 FIX: Use page_size parameter for pagination (limit is deprecated)
        // PAGINATION: Use page_size=50 for proper pagination with UI controls
        // For search, use the search endpoint with filters
        let endpoint = searchQuery.length >= 2
            ? `/v1/clients/search/?q=${encodeURIComponent(searchQuery)}&page_size=${pageSize}&page=${currentPage}`
            : `/v1/clients/?${params.toString()}&page_size=${pageSize}&page=${currentPage}`;

        console.log('Loading clients from:', endpoint);
        const data = await api.get(endpoint);

        // Store pagination info from API response
        totalCount = data.count || 0;
        nextPageUrl = data.next;
        previousPageUrl = data.previous;
        console.log('API response:', data);
        console.log('data.results:', data.results);
        console.log('data.clients:', data.clients);

        // Extract clients from response
        allClients = searchQuery.length >= 2 ? data.clients : data.results;

        if (!allClients || !Array.isArray(allClients)) {
            console.error('Invalid API response - clients is not an array:', allClients);
            console.error('Full data object:', JSON.stringify(data, null, 2));
            throw new Error('Invalid API response format');
        }

        // Apply balance filter client-side ONLY when NOT searching (global search)
        let filteredClients = allClients;
        if (searchQuery.length < 2) {
            // Only apply balance filter when NOT searching
            filteredClients = allClients.filter(client => {
                const balance = parseFloat(client.current_balance);
                if (balanceFilter === 'zero') {
                    return balance === 0;
                } else if (balanceFilter === 'non_zero') {
                    return balance !== 0;
                }
                return true; // 'all' or no filter
            });
        }

        // Apply sorting if active
        if (currentSort.column) {
            filteredClients = sortClientsArray(filteredClients, currentSort.column, currentSort.direction);
        }

        // Store cases from client data (already included in response)
        filteredClients.forEach(client => {
            allCases[client.id] = client.cases || [];
        });

        // Calculate and display total trust balance
        const totalBalance = filteredClients.reduce((sum, client) => {
            return sum + parseFloat(client.current_balance);
        }, 0);
        displayTotalBalance(totalBalance);

        // Display clients
        displayClients(filteredClients);

        // Update pagination UI
        updatePaginationUI();

    } catch (error) {
        console.error('Error loading clients:', error);
        console.error('Error stack:', error.stack);
        document.querySelector('#clientsTable tbody').innerHTML =
            '<tr><td colspan="6" class="text-center text-danger">Error loading clients: ' + error.message + '</td></tr>';
    }
}

function displayClients(clients) {
    const tbody = document.querySelector('#clientsTable tbody');

    if (clients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No clients found</td></tr>';
        return;
    }

    // REQUIREMENT: Apply sorting before displaying
    const sortedClients = sortClientsArray(clients, currentSort.column, currentSort.direction);

    let html = '';

    sortedClients.forEach(client => {
        const cases = client.cases || [];
        const hasCases = client.has_cases || cases.length > 0;

        // Status badge
        const statusBadge = client.is_active
            ? '<span class="badge bg-success">Active</span>'
            : '<span class="badge bg-secondary">Inactive</span>';

        // Expand button for cases
        const expandButton = hasCases
            ? `<button class="btn btn-sm btn-outline-secondary me-2 toggle-cases" data-client-id="${client.id}" title="Show/Hide Cases" style="width: 30px; height: 30px; padding: 0;">
                   <i class="fas fa-chevron-down" id="expand-icon-${client.id}"></i>
               </button>`
            : '<div style="width: 30px; height: 30px; margin-right: 0.5rem;"></div>';

        // Balance class
        const balanceClass = getBalanceClass(parseFloat(client.current_balance));

        // Client row
        html += `
            <tr class="client-row">
                <td>
                    <div class="d-flex align-items-center">
                        ${expandButton}
                        <a href="#" class="text-decoration-none" onclick="viewClient(${client.id}); return false;">
                            ${client.full_name}
                        </a>
                    </div>
                </td>
                <td>${client.email || '-'}</td>
                <td>${formatPhone(client.phone)}</td>
                <td class="${balanceClass}">${client.formatted_balance}</td>
                <td>${statusBadge}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-primary" title="View Details" onclick="viewClient(${client.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary" title="Edit Client" onclick="editClient(${client.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-success" title="Add Case" onclick="addCase(${client.id})">
                            <i class="fas fa-briefcase"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" title="Delete Client" onclick="smartDeleteClient(${client.id}, '${client.full_name.replace(/'/g, "\\'")}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;

        // Cases rows
        if (hasCases) {
            cases.forEach(caseItem => {
                const caseStatusBadge = getCaseStatusBadge(caseItem.case_status);
                const caseBalanceClass = getBalanceClass(parseFloat(caseItem.current_balance));

                html += `
                    <tr class="cases-row cases-${client.id}" style="display: none;">
                        <td class="ps-5">
                            <a href="#" class="text-decoration-none text-muted" onclick="viewCase(${caseItem.id}); return false;">
                                <i class="fas fa-level-up-alt fa-rotate-90 me-2"></i>${caseItem.case_title}
                            </a>
                        </td>
                        <td class="text-muted">${truncate(caseItem.case_description || '-', 50)}</td>
                        <td></td>
                        <td class="${caseBalanceClass}">${caseItem.formatted_balance}</td>
                        <td>${caseStatusBadge}</td>
                        <td></td>
                    </tr>
                `;
            });
        }
    });

    tbody.innerHTML = html;

    // Setup toggle cases event listeners
    document.querySelectorAll('.toggle-cases').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const clientId = this.dataset.clientId;
            toggleCases(clientId);
        });
    });
}

function toggleCases(clientId) {
    const casesRows = document.querySelectorAll(`.cases-${clientId}`);
    const icon = document.getElementById(`expand-icon-${clientId}`);

    const isVisible = casesRows[0].style.display !== 'none';

    casesRows.forEach(row => {
        row.style.display = isVisible ? 'none' : '';
    });

    if (icon) {
        if (isVisible) {
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        } else {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        }
    }
}

function handleSearch() {
    const spinner = document.getElementById('search-spinner');

    // Clear previous timeout
    clearTimeout(searchTimeout);

    // Show spinner
    spinner.style.display = 'block';

    // Debounce search by 300ms
    searchTimeout = setTimeout(function() {
        currentPage = 1; // Reset to page 1 when searching
        loadClients();
        spinner.style.display = 'none';
    }, 300);
}

function sortTable(column) {
    // Toggle sort direction or set to asc if different column
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }

    // Update visual indicators
    updateSortIcons(column, currentSort.direction);

    // Reload clients with sorting
    loadClients();
}

function sortClients(clients, column, direction) {
    return clients.sort((a, b) => {
        let aVal, bVal;

        if (column === 'name') {
            aVal = a.full_name.toLowerCase();
            bVal = b.full_name.toLowerCase();
        } else if (column === 'balance') {
            aVal = parseFloat(a.current_balance);
            bVal = parseFloat(b.current_balance);
        }

        if (direction === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
}

function updateSortIcons(activeColumn, direction) {
    // Clear all icons
    document.getElementById('name-sort-icon').innerHTML = '';
    document.getElementById('balance-sort-icon').innerHTML = '';

    // Set active icon
    const icon = direction === 'asc'
        ? '<i class="fas fa-chevron-up"></i>'
        : '<i class="fas fa-chevron-down"></i>';
    document.getElementById(activeColumn + '-sort-icon').innerHTML = icon;
}

function displayTotalBalance(total) {
    const element = document.getElementById('totalTrustBalance');

    if (total < 0) {
        element.className = 'h5 mb-0 text-danger fw-bold';
        element.textContent = `(${formatCurrency(Math.abs(total))})`;
    } else if (total === 0) {
        element.className = 'h5 mb-0 text-muted';
        element.textContent = formatCurrency(total);
    } else {
        element.className = 'h5 mb-0 text-success';
        element.textContent = formatCurrency(total);
    }
}

function clearFilters() {
    document.getElementById('search').value = '';
    document.getElementById('balance_filter').value = 'non_zero';
    document.getElementById('status_filter').value = 'active';
    loadClients();
}

function viewClient(clientId) {
    window.location.href = `/clients/${clientId}`;
}

// BUG #9 FIX: Redirect to case detail page
function viewCase(caseId) {
    window.location.href = `/cases/${caseId}`;
}

function getCaseStatusBadge(status) {
    const statusMap = {
        'Open': '<span class="badge bg-primary">Open</span>',
        'Pending Settlement': '<span class="badge bg-warning">Pending Settlement</span>',
        'Settled': '<span class="badge bg-success">Settled</span>',
        'Closed': '<span class="badge bg-secondary">Closed</span>',
    };
    return statusMap[status] || `<span class="badge bg-secondary">${status}</span>`;
}

function getBalanceClass(balance) {
    if (balance < 0) {
        return 'text-danger fw-bold';
    } else if (balance === 0) {
        return 'text-muted';
    } else {
        return 'text-success';
    }
}

function formatCurrency(value) {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';
    return '$' + num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatPhone(phone) {
    if (!phone) return '-';

    // Remove all non-numeric characters
    const cleaned = ('' + phone).replace(/\D/g, '');

    // Format as (XXX) XXX-XXXX for 10-digit US numbers
    if (cleaned.length === 10) {
        return `(${cleaned.substring(0, 3)}) ${cleaned.substring(3, 6)}-${cleaned.substring(6)}`;
    }

    return phone;
}

function truncate(str, length) {
    if (!str || str.length <= length) return str;
    return str.substring(0, length - 3) + '...';
}

// BUG #10 FIX: Print only searched clients
function printClients() {
    const searchQuery = document.getElementById('search').value.trim();
    const balanceFilter = document.getElementById('balance_filter').value;
    const statusFilter = document.getElementById('status_filter').value;

    // Build query parameters
    let params = new URLSearchParams();

    if (searchQuery) {
        params.append('search', searchQuery);
    }
    if (balanceFilter && balanceFilter !== 'all') {
        params.append('balance_filter', balanceFilter);
    }
    if (statusFilter && statusFilter !== 'all') {
        params.append('status_filter', statusFilter);
    }

    const queryString = params.toString();
    const printUrl = queryString
        ? `${window.location.origin}/clients/print-with-cases/?${queryString}`
        : `${window.location.origin}/clients/print-with-cases/`;

    window.open(printUrl, '_blank');
}

// Global variable to track current client being edited
let currentClientId = null;
let currentDeleteClientId = null;

function addNewClient() {
    currentClientId = null;
    document.getElementById('clientModalLabel').textContent = 'New Client';
    document.getElementById('clientSubmitBtn').textContent = 'Save Client';

    // Reset form
    document.getElementById('clientForm').reset();
    document.getElementById('is_active').checked = true;

    // Clear all validation errors
    document.querySelectorAll('#clientForm .is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
    document.querySelectorAll('#clientForm .invalid-feedback').forEach(el => {
        el.textContent = '';
    });

    // Show modal
    new bootstrap.Modal(document.getElementById('clientModal')).show();
}

async function editClient(clientId) {
    currentClientId = clientId;
    document.getElementById('clientModalLabel').textContent = 'Edit Client';
    document.getElementById('clientSubmitBtn').textContent = 'Update Client';

    try {
        // Get client data from API
        const client = await api.get(`/v1/clients/${clientId}/`);

        // Populate form
        const fullName = `${client.first_name || ''} ${client.last_name || ''}`.trim();
        document.getElementById('client_name').value = fullName;
        document.getElementById('phone').value = client.phone || '';
        document.getElementById('email').value = client.email || '';
        document.getElementById('address').value = client.address || '';
        document.getElementById('city').value = client.city || '';
        document.getElementById('state').value = client.state || '';
        document.getElementById('zip_code').value = client.zip_code || '';
        document.getElementById('is_active').checked = client.is_active;

        // Clear validation errors
        document.querySelectorAll('#clientForm .is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        document.querySelectorAll('#clientForm .invalid-feedback').forEach(el => {
            el.textContent = '';
        });

        // Show modal
        new bootstrap.Modal(document.getElementById('clientModal')).show();
    } catch (error) {
        // console.error('Error loading client:', error);
        // alert('Error loading client data. Please try again.');
    }
}

// Handle client form submission
document.getElementById('clientForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Split client_name into first_name and last_name
    const clientName = document.getElementById('client_name').value.trim();
    const nameParts = clientName.split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';

    const formData = {
        first_name: firstName,
        last_name: lastName,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        zip_code: document.getElementById('zip_code').value,
        is_active: document.getElementById('is_active').checked
    };

    try {
        // Clear previous errors
        document.querySelectorAll('#clientForm .is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        document.querySelectorAll('#clientForm .invalid-feedback').forEach(el => {
            el.textContent = '';
        });

        if (currentClientId) {
            // Update existing client
            await api.put(`/v1/clients/${currentClientId}/`, formData);
        } else {
            // Create new client
            await api.post('/v1/clients/', formData);
        }

        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('clientModal')).hide();

        // Reload clients
        await loadClients();

    } catch (error) {
        // BUG #6 FIX: Check for network errors
        if (!navigator.onLine) {
            alert('No internet connection. Please check your network and try again.');
            return;
        }

        // console.error('Error saving client:', error);

        // Handle validation errors
        if (error.validationErrors) {
            const errors = error.validationErrors;

            // BUG #4 FIX: Handle non_field_errors (like duplicate name)
            if (errors.non_field_errors) {
                alert('Error: ' + (Array.isArray(errors.non_field_errors) ? errors.non_field_errors[0] : errors.non_field_errors));
            }

            // Display field-specific errors
            for (const [field, messages] of Object.entries(errors)) {
                if (field === 'non_field_errors') continue;

                const input = document.getElementById(field);
                if (input) {
                    input.classList.add('is-invalid');
                    const feedback = input.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.textContent = Array.isArray(messages) ? messages[0] : messages;
                    }
                }
            }
        } else {
            alert('Error saving client: ' + error.message);
        }
    }
});

async function addCase(clientId) {
    // Reset form
    document.getElementById('caseForm').reset();

    // Clear case_id for new case
    document.getElementById('case_id').value = '';
    document.getElementById('case_client_id').value = clientId;
    document.getElementById('case_status').value = 'Open';

    // Update modal title
    document.getElementById('caseModalLabel').textContent = 'Add New Case';
    document.getElementById('caseSubmitBtn').textContent = 'Save Case';

    // Clear validation errors
    document.querySelectorAll('#caseForm .is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });

    // Show modal
    new bootstrap.Modal(document.getElementById('caseModal')).show();
}

async function editCase(caseId) {
    try {
        // Fetch case data
        const caseData = await api.get(`/v1/cases/${caseId}/`);

        // Populate form
        document.getElementById('case_id').value = caseData.id;
        document.getElementById('case_client_id').value = caseData.client;
        document.getElementById('case_title').value = caseData.case_title || '';
        document.getElementById('case_description').value = caseData.case_description || '';
        document.getElementById('case_status').value = caseData.case_status || 'Open';
        document.getElementById('case_amount').value = caseData.case_amount || '';
        document.getElementById('opened_date').value = caseData.opened_date || '';
        document.getElementById('closed_date').value = caseData.closed_date || '';

        // Update modal title
        document.getElementById('caseModalLabel').textContent = 'Edit Case';
        document.getElementById('caseSubmitBtn').textContent = 'Update Case';

        // Clear validation errors
        document.querySelectorAll('#caseForm .is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });

        // Show modal
        new bootstrap.Modal(document.getElementById('caseModal')).show();

    } catch (error) {
        // console.error('Error loading case:', error);
        // alert('Error loading case: ' + error.message);
    }
}

// Handle case form submission
document.getElementById('caseForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const caseId = document.getElementById('case_id').value;
    const isEdit = caseId !== '';

    const formData = {
        client: document.getElementById('case_client_id').value,
        case_title: document.getElementById('case_title').value,
        case_description: document.getElementById('case_description').value,
        case_status: document.getElementById('case_status').value,
        case_amount: document.getElementById('case_amount').value || null,
        opened_date: document.getElementById('opened_date').value || null,
        closed_date: document.getElementById('closed_date').value || null,
    };

    try {
        if (isEdit) {
            // Update existing case
            await api.put(`/v1/cases/${caseId}/`, formData);
        } else {
            // Create new case
            await api.post('/v1/cases/', formData);
        }

        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('caseModal')).hide();

        // Reload clients
        await loadClients();

    } catch (error) {
        // BUG #6 FIX: Check for network errors
        if (!navigator.onLine) {
            alert('No internet connection. Please check your network and try again.');
            return;
        }

        // BUG #17, #18, #20, #21 FIX: Display backend validation errors
        if (error.validationErrors) {
            const errors = error.validationErrors;

            // Display errors
            let errorMessage = 'Error saving case:\n\n';
            for (const [field, messages] of Object.entries(errors)) {
                const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                const message = Array.isArray(messages) ? messages[0] : messages;
                errorMessage += `• ${fieldName}: ${message}\n`;

                // Also mark field as invalid if it exists
                const input = document.getElementById(field === 'client' ? 'case_client_id' : field);
                if (input) {
                    input.classList.add('is-invalid');
                }
            }
            alert(errorMessage);
        } else {
            alert('Error saving case: ' + error.message);
        }
    }
});

async function smartDeleteClient(clientId, clientName) {
    currentDeleteClientId = clientId;

    const message = `Are you sure you want to delete "${clientName}"?\n\n` +
                   `• Clients with a balance CANNOT be deleted.\n` +
                   `• Clients with transactions but $0 balance will be set to INACTIVE.\n` +
                   `• Clients with no transactions will be permanently deleted.`;

    document.getElementById('deleteMessage').innerHTML = message.replace(/\n/g, '<br>');

    // Show modal
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

// Handle delete confirmation
document.getElementById('confirmDeleteBtn').addEventListener('click', async function() {
    if (!currentDeleteClientId) return;

    try {
        const response = await api.delete(`/v1/clients/${currentDeleteClientId}/`);

        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();

        // Show success notification
        showNotification(response.message || 'Client updated successfully.', 'success');

        // Reload clients
        await loadClients();

    } catch (error) {
        console.error('Error deleting client:', error);

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
        if (modal) modal.hide();

        // Show error notification (rejection toast)
        const errorMessage = error.error || error.message || 'Cannot delete client with balance';
        showNotification(errorMessage, 'danger');
    }
});

// Toast notification function
function showNotification(message, type = 'success') {
    // Create toast element if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999;';
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toastId = 'toast-' + Date.now();
    const bgColor = type === 'success' ? '#28a745' : type === 'danger' ? '#dc3545' : '#17a2b8';
    const icon = type === 'success' ? 'fa-check-circle' : type === 'danger' ? 'fa-times-circle' : 'fa-info-circle';

    const toastHTML = `
        <div id="${toastId}" class="alert alert-dismissible fade show" role="alert"
             style="min-width: 400px; max-width: 500px; margin-top: 10px; background-color: ${bgColor}; color: white; border: none; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.25); padding: 16px 20px; font-size: 15px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas ${icon}" style="font-size: 20px;"></i>
                <span style="flex: 1; font-weight: 500;">${message}</span>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close" style="font-size: 14px; opacity: 0.9;"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 150);
        }
    }, 4000);
}

function logout() {
    api.logout();
}

// REQUIREMENT: Client sorting functionality
function sortClientsArray(clients, column, direction) {
    const sorted = [...clients]; // Create copy to avoid mutation

    sorted.sort((a, b) => {
        let aVal, bVal;

        if (column === 'name') {
            // Sort by full name as displayed (first name + last name)
            aVal = (a.full_name || '').toLowerCase().trim();
            bVal = (b.full_name || '').toLowerCase().trim();
        } else if (column === 'balance') {
            // Sort by balance (numeric)
            aVal = parseFloat(a.current_balance) || 0;
            bVal = parseFloat(b.current_balance) || 0;
        } else {
            return 0;
        }

        if (aVal < bVal) return direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return direction === 'asc' ? 1 : -1;
        return 0;
    });

    return sorted;
}

function sortClients(column) {
    // Toggle direction if clicking same column, otherwise default to desc for balance, asc for name
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = column === 'balance' ? 'desc' : 'asc'; // Balance defaults to highest first
    }

    // Update table header icons
    const nameIcon = document.getElementById('name-sort-icon');
    const balanceIcon = document.getElementById('balance-sort-icon');

    // Reset both icons
    nameIcon.className = 'fas fa-sort text-muted ms-1';
    balanceIcon.className = 'fas fa-sort text-muted ms-1';

    // Update active column icon
    if (column === 'name') {
        nameIcon.className = currentSort.direction === 'asc'
            ? 'fas fa-sort-up text-primary ms-1'
            : 'fas fa-sort-down text-primary ms-1';
    } else if (column === 'balance') {
        balanceIcon.className = currentSort.direction === 'asc'
            ? 'fas fa-sort-up text-primary ms-1'
            : 'fas fa-sort-down text-primary ms-1';
    }

    // Re-display clients with new sort
    displayClients(allClients);
}

// ===== PAGINATION FUNCTIONS =====

function updatePaginationUI() {
    // Calculate start, end, and total
    const start = totalCount > 0 ? ((currentPage - 1) * pageSize) + 1 : 0;
    const end = Math.min(currentPage * pageSize, totalCount);

    // Update count info
    document.getElementById('clients-start').textContent = start;
    document.getElementById('clients-end').textContent = end;
    document.getElementById('clients-total').textContent = totalCount;

    // Update Previous button
    const prevButton = document.getElementById('prev-page');
    if (previousPageUrl) {
        prevButton.classList.remove('disabled');
    } else {
        prevButton.classList.add('disabled');
    }

    // Update Next button
    const nextButton = document.getElementById('next-page');
    if (nextPageUrl) {
        nextButton.classList.remove('disabled');
    } else {
        nextButton.classList.add('disabled');
    }
}

function previousPage() {
    if (previousPageUrl && currentPage > 1) {
        currentPage--;
        loadClients();
    }
}

function nextPage() {
    if (nextPageUrl) {
        currentPage++;
        loadClients();
    }
}
