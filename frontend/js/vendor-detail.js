// Vendor Detail Page JavaScript
const vendorId = window.location.pathname.split('/').pop();
let allPayments = [];
let clientBreakdown = [];

document.addEventListener('DOMContentLoaded', async function() {
    await loadFirmInfo();
    await loadVendorDetails();

    // Setup client search
    document.getElementById('clientSearch').addEventListener('input', filterClientBreakdown);
});

async function loadFirmInfo() {
    try {
        const data = await api.get('/v1/dashboard/law-firm/');
        const firm = data;
        document.getElementById('firmNameSidebar').textContent = firm.firm_name;
        document.getElementById('firmLocation').textContent = firm.city + ', ' + firm.state;
        document.getElementById('firmPhone').textContent = firm.phone;
        document.getElementById('firmEmail').textContent = firm.email;
        document.getElementById('firmNameHeader').textContent = firm.firm_name;
        document.getElementById('firmAddressFull').textContent = firm.address + ', ' + firm.city + ', ' + firm.state + ' ' + firm.zip_code + ' | ' + firm.phone + ' | ' + firm.email;
    } catch (error) {
        // console.error('Error:', error);
    }
}

async function loadVendorDetails() {
    try {
        // Get date filters
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;

        // console.log('Loading vendor details with filters:', { dateFrom, dateTo });

        let url = `/v1/vendors/${vendorId}/payments/`;
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        if (params.toString()) url += '?' + params.toString();

        // console.log('Fetching URL:', url);

        const data = await api.get(url);

        // Update page title
        document.getElementById('vendorPageTitle').textContent = 'Vendor Details: ' + data.vendor.vendor_name;

        // Display vendor details in 3 columns
        displayVendorDetails(data.vendor);

        // Display payment register
        allPayments = data.payments || [];
        displayPaymentRegister(allPayments);

        // Update summary
        document.getElementById('totalPayments').textContent = formatCurrency(data.total_payments);
        document.getElementById('paymentCount').textContent = data.payment_count;

        // Display client breakdown
        clientBreakdown = data.client_breakdown || [];
        displayClientBreakdown(clientBreakdown);

    } catch (error) {
        // console.error('Error loading vendor details:', error);
        // alert('Error loading vendor details. Please try again.');
    }
}

function displayVendorDetails(vendor) {
    // Column 1: Name, Email, Phone
    const col1 = `
        <tr>
            <td>Name:</td>
            <td>${escapeHtml(vendor.vendor_name)}</td>
        </tr>
        <tr>
            <td>Email:</td>
            <td>${escapeHtml(vendor.email || '-')}</td>
        </tr>
        <tr>
            <td>Phone:</td>
            <td>${formatPhone(vendor.phone) || '-'}</td>
        </tr>
    `;
    document.getElementById('vendorDetailsCol1').innerHTML = col1;

    // Column 2: Address, City, State, Zip
    const col2 = `
        <tr>
            <td>Address:</td>
            <td>${escapeHtml(vendor.address || '-')}</td>
        </tr>
        <tr>
            <td>City:</td>
            <td>${escapeHtml(vendor.city || '-')}</td>
        </tr>
        <tr>
            <td>State:</td>
            <td>${escapeHtml(vendor.state || '-')}</td>
        </tr>
        <tr>
            <td>Zip Code:</td>
            <td>${escapeHtml(vendor.zip_code || '-')}</td>
        </tr>
    `;
    document.getElementById('vendorDetailsCol2').innerHTML = col2;

    // Column 3: Status, Created, Updated
    const statusBadge = vendor.is_active ?
        '<span class="badge bg-success">Active</span>' :
        '<span class="badge bg-secondary">Inactive</span>';

    const col3 = `
        <tr>
            <td>Status:</td>
            <td>${statusBadge}</td>
        </tr>
        <tr>
            <td>Created:</td>
            <td>${formatDate(vendor.created_at)}</td>
        </tr>
        <tr>
            <td>Updated:</td>
            <td>${formatDate(vendor.updated_at)}</td>
        </tr>
    `;
    document.getElementById('vendorDetailsCol3').innerHTML = col3;
}

function displayPaymentRegister(payments) {
    const tbody = document.getElementById('paymentRegisterBody');

    if (!payments || payments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No payments found</td></tr>';
        return;
    }

    let html = '';
    payments.forEach(payment => {
        html += `
            <tr>
                <td>${formatDate(payment.date)}</td>
                <td>
                    <a href="/clients/${payment.client_id}" class="text-decoration-none">
                        ${escapeHtml(payment.client_name)}
                    </a>
                </td>
                <td>${escapeHtml(payment.description)}</td>
                <td>${escapeHtml(payment.reference || '-')}</td>
                <td class="text-end">${formatCurrency(payment.amount)}</td>
                <td class="text-end fw-bold text-primary">${formatCurrency(payment.running_total)}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

function displayClientBreakdown(breakdown) {
    const tbody = document.getElementById('clientBreakdownBody');

    if (!breakdown || breakdown.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-4">No client breakdown available</td></tr>';
        return;
    }

    let html = '';
    breakdown.forEach(item => {
        html += `
            <tr>
                <td>${escapeHtml(item.client_name)}</td>
                <td class="text-end">${formatCurrency(item.amount)}</td>
                <td class="text-end">${item.percentage}%</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

function filterClientBreakdown() {
    const searchTerm = document.getElementById('clientSearch').value.toLowerCase();
    const filtered = clientBreakdown.filter(item =>
        item.client_name.toLowerCase().includes(searchTerm)
    );
    displayClientBreakdown(filtered);
}

function filterPayments() {
    // console.log('Filter button clicked!');
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    // console.log('Date filters:', { dateFrom, dateTo });
    loadVendorDetails();
}

function clearFilters() {
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    loadVendorDetails();
}

function editVendor() {
    // TODO: Implement edit modal
    // alert('Edit vendor functionality coming soon!');
}

async function exportToExcel() {
    try {
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;

        // Build export URL with authentication
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);

        const queryString = params.toString() ? '?' + params.toString() : '';
        const url = `/api/v1/vendors/${vendorId}/payments/export/${queryString}`;

        // Use fetch with credentials to download file (proxy through nginx)
        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) {
            const errorText = await response.text();
            // console.error('Export failed:', response.status, errorText);
            throw new Error(`Export failed: ${response.status} ${response.statusText}`);
        }

        // Get filename from header or use default
        const disposition = response.headers.get('Content-Disposition');
        let filename = 'vendor_payments.csv';
        if (disposition && disposition.includes('filename=')) {
            filename = disposition.split('filename=')[1].replace(/"/g, '').replace(/;$/, '');
        }

        // Download the file
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);

        // Show success message
        // alert('Export completed successfully!');

    } catch (error) {
        // console.error('Error exporting:', error);
        // alert('Error exporting to Excel: ' + error.message);
    }
}

// Utility functions
function formatCurrency(amount) {
    if (!amount && amount !== 0) return '$0.00';
    const num = parseFloat(amount);
    if (num < 0) {
        return `($${Math.abs(num).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})})`;
    }
    return `$${num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return (date.getMonth() + 1).toString().padStart(2, '0') + '/' +
           date.getDate().toString().padStart(2, '0') + '/' +
           date.getFullYear();
}

function formatPhone(phone) {
    if (!phone) return null;
    // Remove all non-digits
    const cleaned = phone.replace(/\D/g, '');
    // Format as (555) 123-4567
    if (cleaned.length === 10) {
        return `(${cleaned.substr(0,3)}) ${cleaned.substr(3,3)}-${cleaned.substr(6,4)}`;
    }
    return phone;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        api.post('/auth/logout/').then(() => {
            window.location.href = '/login';
        });
    }
}
