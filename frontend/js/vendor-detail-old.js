let vendorId = null;

document.addEventListener('DOMContentLoaded', async function() {
    vendorId = window.location.pathname.split('/')[2];
    await loadFirmInfo();
    await loadVendorDetails();
});

async function loadFirmInfo() {
    try {
        const firm = await api.get('/v1/dashboard/law-firm/');
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
        const data = await api.get('/v1/vendors/' + vendorId + '/payments/');
        document.getElementById('vendorTitle').textContent = 'Vendor Details: ' + data.vendor.vendor_name;
        renderVendorDetails(data);
    } catch (error) {
        document.getElementById('vendorContent').innerHTML = '<div class="alert alert-danger">Error loading vendor</div>';
    }
}

function renderVendorDetails(data) {
    const v = data.vendor;
    let html = '<div class="row"><div class="col-md-4 detail-column"><table class="vendor-details-table">';
    html += '<tr><td>Name:</td><td>' + v.vendor_name + '</td></tr>';
    html += '<tr><td>Email:</td><td>' + (v.email || '-') + '</td></tr>';
    html += '<tr><td>Phone:</td><td>' + (v.phone ? formatPhone(v.phone) : '-') + '</td></tr>';
    html += '</table></div><div class="col-md-4 detail-column"><table class="vendor-details-table">';
    html += '<tr><td>Address:</td><td>' + (v.address || '-') + '</td></tr>';
    html += '<tr><td>City:</td><td>' + (v.city || '-') + '</td></tr>';
    html += '<tr><td>State:</td><td>' + (v.state || '-') + '</td></tr>';
    html += '<tr><td>Zip Code:</td><td>' + (v.zip_code || '-') + '</td></tr>';
    html += '</table></div><div class="col-md-4 detail-column"><table class="vendor-details-table">';
    html += '<tr><td>Status:</td><td>' + (v.is_active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>') + '</td></tr>';
    html += '<tr><td>Created:</td><td>' + v.created_at + '</td></tr>';
    html += '<tr><td>Updated:</td><td>' + v.updated_at + '</td></tr>';
    html += '</table></div></div><div class="border-top my-4"></div>';
    html += '<h5 class="mb-3"><i class="fas fa-money-check-alt me-2 text-primary"></i>Payment Register <small>(Total: ' + fm(data.total_payments) + ' • ' + data.payment_count + ' payments)</small></h5>';
    html += renderPaymentTable(data.payments);
    if (data.client_breakdown && data.client_breakdown.length > 0) {
        html += '<div class="border-top my-4"></div><h5 class="mb-3"><i class="fas fa-chart-pie me-2"></i>Client Breakdown</h5>';
        html += renderClientBreakdown(data.client_breakdown);
    }
    document.getElementById('vendorContent').innerHTML = html;
}

function renderPaymentTable(payments) {
    if (!payments || !payments.length) return '<p>No payments</p>';
    let html = '<div class="table-responsive"><table class="table table-sm table-hover"><thead class="table-light"><tr><th>Date</th><th>Client</th><th>Description</th><th>Reference</th><th class="text-end">Amount</th><th class="text-end">Running Total</th></tr></thead><tbody>';
    payments.forEach(p => {
        html += '<tr><td>' + p.date + '</td><td>' + p.client_name + '</td><td>' + p.description + '</td><td>' + (p.reference || '-') + '</td><td class="text-end">' + fm(p.amount) + '</td><td class="text-end">' + fm(p.running_total) + '</td></tr>';
    });
    return html + '</tbody></table></div>';
}

function renderClientBreakdown(breakdown) {
    let html = '<div class="table-responsive"><table class="table table-sm table-striped"><thead class="table-light"><tr><th>Client</th><th class="text-end">Amount</th><th class="text-end">Count</th><th class="text-end">%</th></tr></thead><tbody>';
    breakdown.forEach(c => {
        html += '<tr><td>' + c.client_name + '</td><td class="text-end">' + fm(c.amount) + '</td><td class="text-end">' + c.count + '</td><td class="text-end">' + c.percentage + '%</td></tr>';
    });
    return html + '</tbody></table></div>';
}

function fm(amount) {
    return parseFloat(amount).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function formatPhone(phone) {
    const c = ('' + phone).replace(/\D/g, '');
    return c.length === 10 ? '(' + c.substring(0, 3) + ') ' + c.substring(3, 6) + '-' + c.substring(6, 10) : phone;
}

function editVendor() {
    // alert('Edit - Coming soon');
}
