/**
 * Settlements Page JavaScript
 * Handles 3-way settlements display and management
 */

// Initialize API client
const api = new TAMSApiClient();

let settlements = [];
let clients = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', async function() {
    // console.log('Settlements page loaded');

    // Load law firm info
    await loadLawFirmInfo();

    // Load clients for filter dropdown
    await loadClients();

    // Load settlements
    await loadSettlements();

    // Initialize Select2 on dropdowns
    $('#clientFilter').select2({
        theme: 'bootstrap-5',
        placeholder: 'All Clients'
    });

    // Handle filter form submission
    document.getElementById('filterForm').addEventListener('submit', handleFilter);
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
        }
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

/**
 * Load clients for filter dropdown
 */
async function loadClients() {
    try {
        const response = await api.get('/v1/clients/?page_size=1000');

        if (response && response.results) {
            clients = response.results;

            const clientFilter = document.getElementById('clientFilter');
            clientFilter.innerHTML = '<option value="">All Clients</option>';

            clients.forEach(client => {
                const option = document.createElement('option');
                option.value = client.id;
                option.textContent = client.full_name;
                clientFilter.appendChild(option);
            });
        }
    } catch (error) {
        // console.error('Error loading clients:', error);
    }
}

/**
 * Load settlements from API
 */
async function loadSettlements(filters = {}) {
    try {
        // Build query parameters
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.client) params.append('client', filters.client);

        const queryString = params.toString();
        const url = queryString ? `/v1/settlements/?${queryString}` : '/v1/settlements/';

        const response = await api.get(url);

        if (response) {
            // Handle both paginated and non-paginated responses
            settlements = response.results || response || [];
            displaySettlements(settlements);
        }
    } catch (error) {
        // console.error('Error loading settlements:', error);
        // Show error message in table
        const tbody = document.getElementById('settlementsTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading settlements. ${error.message || 'Please try again.'}
                </td>
            </tr>
        `;
    }
}

/**
 * Display settlements in table
 */
function displaySettlements(settlementsData) {
    const tbody = document.getElementById('settlementsTableBody');

    if (!settlementsData || settlementsData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    No settlements found
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    settlementsData.forEach(settlement => {
        const statusBadge = getStatusBadge(settlement.status);
        const balancedBadge = settlement.is_balanced
            ? '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Yes</span>'
            : '<span class="badge bg-warning text-dark"><i class="fas fa-times me-1"></i>No</span>';

        html += `
            <tr>
                <td><strong>${settlement.settlement_number || '-'}</strong></td>
                <td>${formatDate(settlement.settlement_date || settlement.created_at)}</td>
                <td>${settlement.client_name || settlement.client?.full_name || '-'}</td>
                <td>${settlement.case_number || settlement.case?.case_number || '-'}</td>
                <td><strong>${formatCurrency(settlement.total_amount || 0)}</strong></td>
                <td>${statusBadge}</td>
                <td>${balancedBadge}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary" onclick="viewSettlement(${settlement.id})" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="editSettlement(${settlement.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="reconcileSettlement(${settlement.id})" title="Reconcile">
                            <i class="fas fa-balance-scale"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status) {
    const badges = {
        'PENDING': '<span class="badge bg-warning text-dark">Pending</span>',
        'IN_PROGRESS': '<span class="badge bg-info">In Progress</span>',
        'COMPLETED': '<span class="badge bg-success">Completed</span>',
        'CANCELLED': '<span class="badge bg-danger">Cancelled</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
}

/**
 * Handle filter form submission
 */
function handleFilter(e) {
    e.preventDefault();

    const filters = {
        status: document.getElementById('statusFilter').value,
        client: document.getElementById('clientFilter').value
    };

    loadSettlements(filters);
}

/**
 * Clear filters
 */
function clearFilters() {
    document.getElementById('statusFilter').value = '';
    $('#clientFilter').val('').trigger('change');
    loadSettlements();
}

/**
 * Create new settlement
 */
function createSettlement() {
    // In a full implementation, this would open a modal or navigate to create page
    // alert('Create Settlement feature coming soon!\n\nThis would open a form to create a new 3-way settlement.');
}

/**
 * View settlement details
 */
function viewSettlement(id) {
    // Navigate to settlement detail page (when implemented)
    window.location.href = `/settlements/${id}`;
}

/**
 * Edit settlement
 */
function editSettlement(id) {
    // Navigate to edit page (when implemented)
    window.location.href = `/settlements/${id}/edit`;
}

/**
 * Reconcile settlement
 */
function reconcileSettlement(id) {
    // Navigate to reconciliation page (when implemented)
    window.location.href = `/settlements/${id}/reconcile`;
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
    if (amount === null || amount === undefined) return '$0.00';
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
