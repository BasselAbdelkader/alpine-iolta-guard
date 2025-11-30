// Vendors Page JavaScript
let allVendors = [];
let currentVendorId = null;

// Pagination state
let currentPage = 1;
let pageSize = 50; // Show 50 records per page
let totalCount = 0;
let nextPageUrl = null;
let previousPageUrl = null;

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

    // Load vendors
    loadVendors();

    // Setup filter form
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            currentPage = 1; // Reset to page 1 when filters change
            loadVendors();
        });
    }

    // Live search: filter as you type (with debounce)
    const searchInput = document.getElementById('search');
    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            currentPage = 1;

            // Clear previous timeout
            clearTimeout(searchTimeout);

            // Debounce: wait 300ms after user stops typing
            searchTimeout = setTimeout(() => {
                loadVendors();
            }, 300);
        });
    }

    // Reset to page 1 when status changes
    const statusSelect = document.getElementById('status');
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            currentPage = 1;
            loadVendors();
        });
    }

    // Phone formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', formatPhoneInput);
        phoneInput.addEventListener('blur', validatePhone);
    }

    // Email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', validateEmail);
    }

    // Zip code validation
    const zipInput = document.getElementById('zip_code');
    if (zipInput) {
        zipInput.addEventListener('input', validateZipCode);
        zipInput.addEventListener('blur', validateZipCode);
    }

    // Vendor form submit handler
    const vendorForm = document.getElementById('vendorForm');
    if (vendorForm) {
        vendorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitVendorForm();
        });
    }
});

async function loadFirmInfo() {
    try {
        const data = await api.get('/v1/dashboard/law-firm/');
        const firm = data;

        // Sidebar firm info
        document.getElementById('firmNameSidebar').textContent = firm.firm_name;
        document.getElementById('firmLocation').textContent = `${firm.city}, ${firm.state}`;
        document.getElementById('firmPhone').textContent = firm.phone;
        document.getElementById('firmEmail').textContent = firm.email;

        // Header firm info
        document.getElementById('firmNameHeader').textContent = firm.firm_name;
        document.getElementById('firmAddressFull').textContent = `${firm.address}, ${firm.city}, ${firm.state} ${firm.zip_code} | ${firm.phone} | ${firm.email}`;
    } catch (error) {
        // console.error('Error loading firm info:', error);
    }
}

async function loadVendors() {
    try {
        // Build query params from filters
        const params = new URLSearchParams();

        const search = document.getElementById('search').value;
        const status = document.getElementById('status').value;

        if (search) params.append('search', search);
        if (status === 'active') params.append('is_active', 'true');
        if (status === 'inactive') params.append('is_active', 'false');

        // PAGINATION: Use page_size=50 for proper pagination with UI controls
        params.append('page_size', pageSize.toString());
        params.append('page', currentPage.toString());

        const response = await api.get(`/v1/vendors/?${params.toString()}`);

        // Store pagination info from API response
        totalCount = response.count || 0;
        nextPageUrl = response.next;
        previousPageUrl = response.previous;
        allVendors = response.results || [];

        renderVendors(allVendors);
        updatePaginationUI();
    } catch (error) {
        // console.error('Error loading vendors:', error);
        showError('Failed to load vendors');
    }
}

function renderVendors(vendors) {
    const tbody = document.getElementById('vendorsTableBody');

    if (!vendors || vendors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No vendors found</td></tr>';
        return;
    }

    tbody.innerHTML = vendors.map(vendor => {
        const statusBadge = vendor.is_active
            ? '<span class="badge bg-success">Active</span>'
            : '<span class="badge bg-secondary">Inactive</span>';

        const phone = formatPhone(vendor.phone);
        const createdDate = new Date(vendor.created_at).toLocaleDateString('en-US');

        return `
            <tr>
                <td>
                    <a href="/vendors/${vendor.id}" class="text-decoration-none">
                        ${vendor.vendor_name}
                    </a>
                </td>
                <td>${vendor.contact_person || '-'}</td>
                <td>${vendor.email || '-'}</td>
                <td>${phone}</td>
                <td>${statusBadge}</td>
                <td>${createdDate}</td>
            </tr>
        `;
    }).join('');
}

function formatPhone(phone) {
    if (!phone) return '-';

    // Remove all non-digit characters
    const cleaned = phone.replace(/\D/g, '');

    // Format as (XXX) XXX-XXXX
    if (cleaned.length === 10) {
        return `(${cleaned.substring(0, 3)}) ${cleaned.substring(3, 6)}-${cleaned.substring(6, 10)}`;
    }

    return phone;
}

function formatPhoneInput(e) {
    let value = e.target.value.replace(/\D/g, '');
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
}

function validateZipCode(e) {
    const zipInput = e.target;
    const zipError = document.getElementById('zip-error');
    const value = zipInput.value.trim();

    // Remove non-digits
    const digitsOnly = value.replace(/\D/g, '');
    zipInput.value = digitsOnly;

    // Clear error initially
    zipInput.classList.remove('is-invalid');
    zipError.style.display = 'none';

    // If empty, it's valid (not required)
    if (!value) {
        return true;
    }

    // Check if exactly 5 digits
    if (digitsOnly.length !== 5) {
        zipInput.classList.add('is-invalid');
        zipError.textContent = 'Zip code must be exactly 5 digits';
        zipError.style.display = 'block';
        return false;
    }

    return true;
}

function validateEmail(e) {
    const emailInput = e.target;
    const emailError = document.getElementById('email-error');
    const value = emailInput.value.trim();

    // Clear error initially
    emailInput.classList.remove('is-invalid');
    emailError.style.display = 'none';

    // If empty, it's valid (not required)
    if (!value) {
        return true;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
        emailInput.classList.add('is-invalid');
        emailError.textContent = 'Please enter a valid email address';
        emailError.style.display = 'block';
        return false;
    }

    return true;
}

function validatePhone(e) {
    const phoneInput = e.target;
    const phoneError = document.getElementById('phone-error');
    const value = phoneInput.value.trim();

    // Clear error initially
    phoneInput.classList.remove('is-invalid');
    phoneError.style.display = 'none';

    // If empty, it's valid (not required)
    if (!value) {
        return true;
    }

    // Check if phone has exactly 10 digits
    const digitsOnly = value.replace(/\D/g, '');
    if (digitsOnly.length !== 10) {
        phoneInput.classList.add('is-invalid');
        phoneError.textContent = 'Phone number must be 10 digits';
        phoneError.style.display = 'block';
        return false;
    }

    return true;
}

function clearFilters() {
    document.getElementById('search').value = '';
    document.getElementById('status').value = '';
    loadVendors();
}

function addNewVendor() {
    currentVendorId = null;
    document.getElementById('vendorModalTitle').textContent = 'Add New Vendor';

    // Reset form
    document.getElementById('vendorForm').reset();
    document.getElementById('is_active').checked = true;

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('vendorModal'));
    modal.show();
}

async function editVendor(vendorId) {
    currentVendorId = vendorId;
    document.getElementById('vendorModalTitle').textContent = 'Edit Vendor';

    try {
        const vendor = await api.get(`/v1/vendors/${vendorId}/`);

        // Populate form
        document.getElementById('vendor_name').value = vendor.vendor_name || '';
        document.getElementById('contact_person').value = vendor.contact_person || '';
        document.getElementById('email').value = vendor.email || '';
        document.getElementById('phone').value = formatPhone(vendor.phone);
        document.getElementById('address').value = vendor.address || '';
        document.getElementById('city').value = vendor.city || '';
        document.getElementById('state').value = vendor.state || '';
        document.getElementById('zip_code').value = vendor.zip_code || '';
        document.getElementById('is_active').checked = vendor.is_active;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('vendorModal'));
        modal.show();
    } catch (error) {
        // console.error('Error loading vendor:', error);
        // alert('Failed to load vendor details');
    }
}

async function submitVendorForm() {
    // Validate all fields
    const zipInput = document.getElementById('zip_code');
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');

    let isValid = true;

    // Validate zip code
    if (zipInput.value.trim()) {
        const zipValid = validateZipCode({ target: zipInput });
        if (!zipValid) isValid = false;
    }

    // Validate email
    if (emailInput.value.trim()) {
        const emailValid = validateEmail({ target: emailInput });
        if (!emailValid) isValid = false;
    }

    // Validate phone
    if (phoneInput.value.trim()) {
        const phoneValid = validatePhone({ target: phoneInput });
        if (!phoneValid) isValid = false;
    }

    // If validation fails, stop submission
    if (!isValid) {
        return;
    }

    // Get form values
    const vendorData = {
        vendor_name: document.getElementById('vendor_name').value.trim(),
        contact_person: document.getElementById('contact_person').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.replace(/\D/g, ''), // Remove formatting
        address: document.getElementById('address').value.trim(),
        city: document.getElementById('city').value.trim(),
        state: document.getElementById('state').value,
        zip_code: document.getElementById('zip_code').value.trim(),
        is_active: document.getElementById('is_active').checked
    };

    // Validate
    if (!vendorData.vendor_name) {
        // alert('Vendor name is required');
        return;
    }

    try {
        let response;
        if (currentVendorId) {
            // Update existing vendor
            response = await api.put(`/v1/vendors/${currentVendorId}/`, vendorData);
        } else {
            // Create new vendor
            response = await api.post('/v1/vendors/', vendorData);
        }

        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('vendorModal')).hide();

        // Show success message
        showSuccessMessage(currentVendorId ? 'Vendor updated successfully' : 'Vendor created successfully');

        // Reload vendors
        loadVendors();
    } catch (error) {
        console.error('Error saving vendor:', error);
        showErrorMessage('Failed to save vendor: ' + (error.message || 'Unknown error'));
    }
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

async function deleteVendor(vendorId, vendorName) {
    if (!confirm(`Are you sure you want to delete vendor "${vendorName}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        await api.delete(`/v1/vendors/${vendorId}/`);
        // alert('Vendor deleted successfully');
        loadVendors();
    } catch (error) {
        // console.error('Error deleting vendor:', error);
        // alert('Failed to delete vendor: ' + (error.message || 'Unknown error'));
    }
}

function showError(message) {
    // alert('Error: ' + message);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/login';
    }
}

// ===== PAGINATION FUNCTIONS =====

function updatePaginationUI() {
    // Calculate start, end, and total
    const start = totalCount > 0 ? ((currentPage - 1) * pageSize) + 1 : 0;
    const end = Math.min(currentPage * pageSize, totalCount);

    // Update count info
    document.getElementById('vendors-start').textContent = start;
    document.getElementById('vendors-end').textContent = end;
    document.getElementById('vendors-total').textContent = totalCount;

    // Update Previous button
    const prevButton = document.getElementById('prev-page-vendors');
    if (previousPageUrl) {
        prevButton.classList.remove('disabled');
    } else {
        prevButton.classList.add('disabled');
    }

    // Update Next button
    const nextButton = document.getElementById('next-page-vendors');
    if (nextPageUrl) {
        nextButton.classList.remove('disabled');
    } else {
        nextButton.classList.add('disabled');
    }
}

function previousPageVendors() {
    if (previousPageUrl && currentPage > 1) {
        currentPage--;
        loadVendors();
    }
}

function nextPageVendors() {
    if (nextPageUrl) {
        currentPage++;
        loadVendors();
    }
}
