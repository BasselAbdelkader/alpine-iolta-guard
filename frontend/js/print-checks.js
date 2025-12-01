// Print Checks Page JavaScript
let allChecks = [];
let selectedCheckIds = [];
let currentBankAccountId = null; // Store the bank account ID

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load firm info
    loadFirmInfo();

    // REQUIREMENT: Load next check number
    loadNextCheckNumber();

    // Load checks
    loadChecks();

    // Setup search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loadChecks();
        });
    }

    // Select all checkbox
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            document.querySelectorAll('.check-item').forEach(cb => {
                cb.checked = this.checked;
                updateSelectedChecks();
            });
        });
    }

    // Preview selected button
    const previewSelectedBtn = document.getElementById('previewSelectedBtn');
    if (previewSelectedBtn) {
        previewSelectedBtn.addEventListener('click', previewSelected);
    }
});

async function loadFirmInfo() {
    try {
        const firm = await api.get('/v1/dashboard/law-firm/');

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

async function loadChecks() {
    try {
        // Build query params from filters
        const params = new URLSearchParams();

        // Note: checkNumber field was removed (replaced with Next Check # display)
        const payee = document.getElementById('payee')?.value;
        const fromDate = document.getElementById('fromDate')?.value;
        const toDate = document.getElementById('toDate')?.value;

        if (payee) params.append('payee', payee);
        if (fromDate) params.append('from_date', fromDate);
        if (toDate) params.append('to_date', toDate);

        // Call API to get checks to print
        const response = await api.get(`/v1/checks/?${params.toString()}`);

        // API returns { checks: [...], count: N }
        allChecks = response.checks || [];

        renderChecks(allChecks);
        updateCheckCount(response.count || allChecks.length);
    } catch (error) {
        // console.error('Error loading checks:', error);
        document.getElementById('checksTableBody').innerHTML = '<tr><td colspan="9" class="text-center text-danger">Error loading checks. Please try again.</td></tr>';
        updateCheckCount(0);
    }
}

function renderChecks(checks) {
    const tbody = document.getElementById('checksTableBody');

    if (!checks || checks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No checks to print</td></tr>';
        return;
    }

    tbody.innerHTML = checks.map(check => {
        const date = formatDate(check.transaction_date);
        const amount = parseFloat(check.amount).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        const clientName = check.client_name || '-';
        const caseNumber = check.case_title || '-';
        const checkMemo = check.check_memo || '-';
        const payee = check.payee || check.vendor_name || '-';

        return `
            <tr>
                <td>
                    <input type="checkbox" class="check-item" data-check-id="${check.id}" onchange="updateSelectedChecks()">
                </td>
                <td><strong>${check.reference_number || check.reference_number}</strong></td>
                <td>${date}</td>
                <td>${escapeHtml(payee)}</td>
                <td class="text-center">${amount}</td>
                <td><small>${escapeHtml(clientName)}</small></td>
                <td><small>${escapeHtml(caseNumber)}</small></td>
                <td><small>${escapeHtml(checkMemo)}</small></td>
                <td class="text-center">
                    <small class="text-muted">Select & preview to print</small>
                </td>
            </tr>
        `;
    }).join('');
}

function updateSelectedChecks() {
    selectedCheckIds = [];
    document.querySelectorAll('.check-item:checked').forEach(cb => {
        // Convert to number to match check.id type
        selectedCheckIds.push(parseInt(cb.dataset.checkId));
    });
}

function updateCheckCount(count) {
    document.getElementById('checkCountBadge').textContent = `${count} check${count !== 1 ? 's' : ''}`;
}

function clearFilters() {
    document.getElementById('checkNumber').value = '';
    document.getElementById('payee').value = '';
    document.getElementById('fromDate').value = '';
    document.getElementById('toDate').value = '';
    loadChecks();
}

async function printCheck(checkId) {
    // Get the check from the list
    const check = allChecks.find(c => c.id == checkId);
    if (!check) {
        // alert('Check not found');
        return;
    }

    // If check already has a real number (not "TO PRINT"), show preview first
    if (check.reference_number && check.reference_number !== 'TO PRINT') {
        // REQUIREMENT: Show preview before printing
        const confirmed = await showCheckPreview(check, check.reference_number);
        if (confirmed) {
            window.open(`/api/v1/checks/print-batch-pdf/?check_ids=${checkId}`, '_blank');
        }
        return;
    }

    // Check needs a number assigned - use the same workflow as "Print Selected"
    selectedCheckIds = [checkId];
    await printSelected();
}

async function printSelected() {
    if (selectedCheckIds.length === 0) {
        // alert('Please select at least one check to print');
        return;
    }

    // Step 1: Get the next check number from backend
    let nextCheckNumber = '1001'; // Default fallback
    try {
        const checkNumberInfo = await api.get('/v1/checks/next-check-number/');
        nextCheckNumber = checkNumberInfo.next_check_number;
    } catch (error) {
        // console.error('Error fetching next check number:', error);
    }

    // Step 2: Immediately open PDF preview in new tab (shows "TO PRINT" as placeholder)
    const ids = selectedCheckIds.join(',');
    // console.log('Opening preview PDF for check IDs:', ids);
    const previewWindow = window.open(`/api/v1/checks/print-batch-pdf/?check_ids=${ids}`, '_blank');

    // Step 3: Show professional confirmation modal
    const modal = new bootstrap.Modal(document.getElementById('checkConfirmModal'));

    // Update modal content with ACTUAL next check number
    const checkCount = selectedCheckIds.length;

    // Update check count with proper singular/plural
    const checkCountText = checkCount === 1 ? '1 check' : `${checkCount} checks`;
    document.getElementById('modalCheckCount').textContent = checkCountText;

    // Update check number range text
    const checkNumberElement = document.getElementById('checkNumberRange');
    if (checkCount === 1) {
        // Singular: "Check number 1008 will be assigned"
        checkNumberElement.innerHTML = `Check number <strong>${nextCheckNumber}</strong> will be assigned`;
    } else {
        // Plural: "Check numbers 1007 through 1008 will be assigned"
        const endingCheckNumber = parseInt(nextCheckNumber) + checkCount - 1;
        checkNumberElement.innerHTML = `Check numbers <strong>${nextCheckNumber}</strong> through <strong>${endingCheckNumber}</strong> will be assigned`;
    }

    // Show modal
    modal.show();

    // Set up button handlers
    return new Promise((resolve) => {
        const confirmBtn = document.getElementById('confirmCheckAssignment');
        const cancelBtn = document.getElementById('cancelCheckAssignment');

        const handleConfirm = async () => {
            modal.hide();

            // Close the preview window to avoid user printing "TO PRINT" by accident
            if (previewWindow && !previewWindow.closed) {
                previewWindow.close();
            }

            await assignCheckNumbers();
            cleanup();
        };

        const handleCancel = () => {
            modal.hide();
            showToast('Print cancelled. No check numbers were assigned.', 'info');
            cleanup();
        };

        const cleanup = () => {
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
    });
}

async function previewSelected() {
    if (selectedCheckIds.length === 0) {
        alert('Please select at least one check to preview');
        return;
    }

    console.log('Selected check IDs:', selectedCheckIds);
    console.log('All checks:', allChecks);

    // Get the next check number from backend
    let nextCheckNumber = '1001';
    try {
        const checkNumberInfo = await api.get('/v1/checks/next-check-number/');
        nextCheckNumber = checkNumberInfo.next_check_number;
    } catch (error) {
        console.error('Error fetching next check number:', error);
    }

    // Get selected check transactions
    const selectedTransactions = allChecks.filter(check => selectedCheckIds.includes(check.id));
    console.log('Selected transactions:', selectedTransactions);
    console.log('Next check number:', nextCheckNumber);

    // Show preview modal
    const modal = new bootstrap.Modal(document.getElementById('checkPreviewModal'));

    // Update modal title
    const checkCount = selectedCheckIds.length;
    const checkCountText = checkCount === 1 ? '1 check' : `${checkCount} checks`;
    document.querySelector('#checkPreviewModal .modal-title').innerHTML =
        `<i class="fas fa-eye me-2"></i>Check Preview - ${checkCountText}`;

    // Generate preview HTML with check numbers
    let previewHTML = '';
    let currentCheckNum = parseInt(nextCheckNumber);

    selectedTransactions.forEach((check) => {
        console.log('Generating preview for check:', check, 'with number:', currentCheckNum);
        const html = generateCheckPreviewHTML(check, currentCheckNum);
        console.log('Generated HTML:', html);
        previewHTML += html;
        currentCheckNum++;
    });

    console.log('Total preview HTML:', previewHTML);

    // Insert preview into modal
    const container = document.getElementById('checkPreviewContainer');
    console.log('Container element:', container);
    container.innerHTML = previewHTML;

    // Show modal
    modal.show();

    // Handle "Looks Good, Continue" button
    const confirmBtn = document.getElementById('confirmCheckPreview');
    const handleConfirm = async () => {
        modal.hide();
        // Assign check numbers and open PDF
        await assignCheckNumbers();
        confirmBtn.removeEventListener('click', handleConfirm);
    };
    confirmBtn.addEventListener('click', handleConfirm);
}

function generateCheckPreviewHTML(check, checkNumber) {
    const amount = parseFloat(check.amount || 0);
    const amountText = amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    const dateParts = (check.transaction_date || '').split('-');
    const formattedDate = dateParts.length === 3 ? `${dateParts[1]}/${dateParts[2]}/${dateParts[0]}` : check.transaction_date;

    return `
        <div class="border rounded p-3 mb-3" style="background: white; font-family: 'Courier New', monospace;">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <small class="text-muted">Check Number</small>
                    <h5 class="mb-0"><strong>${checkNumber}</strong></h5>
                </div>
                <div class="text-end">
                    <small class="text-muted">Date</small>
                    <div>${formattedDate}</div>
                </div>
            </div>
            <div class="mb-2">
                <small class="text-muted">Pay to the Order of:</small>
                <div class="fw-bold">${check.payee || 'N/A'}</div>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div style="flex: 1;">
                    <small class="text-muted">Amount</small>
                    <div class="fw-bold fs-5">${amountText}</div>
                </div>
                <div class="text-end" style="flex: 1;">
                    <small class="text-muted">Memo</small>
                    <div>${check.check_memo || '-'}</div>
                </div>
            </div>
            <div class="mt-2 pt-2 border-top">
                <div class="row">
                    <div class="col-md-6">
                        <small class="text-muted">Client:</small> ${check.client_name || 'N/A'}
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">Case:</small> ${check.case_title || 'N/A'}
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function assignCheckNumbers() {
    // Save the IDs before any async operations
    const idsToAssign = [...selectedCheckIds];

    try {
        // console.log('Assigning check numbers for IDs:', idsToAssign);

        const response = await api.post('/v1/checks/assign-check-numbers/', {
            check_ids: idsToAssign
        });

        if (response.success) {
            // console.log('Check numbers assigned successfully:', response.checks);

            showToast(
                `Success! ${response.message}. ` +
                `${response.checks.length} check(s) have been assigned numbers. ` +
                `Next check number will be: ${response.next_check_number}`,
                'success'
            );

            // Update the next check number display
            if (response.next_check_number) {
                document.getElementById('nextCheckNumberDisplay').value = response.next_check_number;
            }

            // Open the final PDF with actual check numbers in a new tab
            // Use the SAME IDs we sent to the backend
            const ids = idsToAssign.join(',');
            // console.log('Opening PDF for check IDs:', ids);
            window.open(`/api/v1/checks/print-batch-pdf/?check_ids=${ids}`, '_blank');

            // Clear selection and reload
            selectedCheckIds = [];
            loadChecks();
        } else {
            showToast('Error: ' + (response.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        // console.error('Error assigning check numbers:', error);
        showToast('Failed to assign check numbers: ' + error.message, 'error');
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    const toastContainer = document.createElement('div');
    toastContainer.innerHTML = toastHtml;
    document.body.appendChild(toastContainer);

    const toastElement = toastContainer.querySelector('.toast');
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();

    // Remove from DOM after hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastContainer.remove();
    });
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return (date.getMonth() + 1).toString().padStart(2, '0') + '/' +
           date.getDate().toString().padStart(2, '0') + '/' +
           date.getFullYear();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    // alert('Error: ' + message);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        api.post('/auth/logout/').then(() => {
            window.location.href = '/login';
        });
    }
}

// REQUIREMENT: Load next check number from bank account
async function loadNextCheckNumber() {
    try {
        console.log('Loading next check number...');

        // Get all bank accounts to determine the bank account ID
        const accountsResponse = await api.get('/v1/bank-accounts/accounts/');
        console.log('Bank accounts response:', accountsResponse);

        // Handle different response formats to get accounts
        let accounts = [];
        if (Array.isArray(accountsResponse)) {
            accounts = accountsResponse;
        } else if (accountsResponse.results && Array.isArray(accountsResponse.results)) {
            accounts = accountsResponse.results;
        } else if (accountsResponse.data && Array.isArray(accountsResponse.data)) {
            accounts = accountsResponse.data;
        }

        console.log('Accounts found:', accounts.length);

        if (accounts.length > 0) {
            currentBankAccountId = accounts[0].id;
            console.log('Account ID:', currentBankAccountId);
        } else {
            console.warn('No bank accounts found!');
        }

        // Get the next check number from the check_sequences table via the proper endpoint
        const checkNumberInfo = await api.get('/v1/checks/next-check-number/');
        console.log('Check number info:', checkNumberInfo);

        const nextCheckNumber = checkNumberInfo.next_check_number || 1001;
        console.log('Next check number from check_sequences:', nextCheckNumber);

        document.getElementById('nextCheckNumberDisplay').value = nextCheckNumber;
    } catch (error) {
        console.error('Error loading next check number:', error);
        console.error('Error details:', error.message, error.stack);
        document.getElementById('nextCheckNumberDisplay').value = '1001';
    }
}

// REQUIREMENT: Show edit next check number modal
function editNextCheckNumber() {
    // Get current value
    const currentValue = document.getElementById('nextCheckNumberDisplay').value;

    if (currentValue === 'N/A' || currentValue === 'Error' || currentValue === 'Loading...') {
        alert('Cannot edit check number at this time. Please refresh the page.');
        return;
    }

    // Set input value
    document.getElementById('editCheckNumberInput').value = currentValue;

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editCheckNumberModal'));
    modal.show();
}

// REQUIREMENT: Save updated next check number
async function saveNextCheckNumber() {
    const newCheckNumber = document.getElementById('editCheckNumberInput').value;

    if (!newCheckNumber || newCheckNumber < 1) {
        alert('Please enter a valid check number (must be 1 or greater).');
        return;
    }

    try {
        // Update check sequence with new next_check_number
        const response = await api.post('/v1/checks/update-next-check-number/', {
            next_check_number: parseInt(newCheckNumber)
        });

        console.log('Check number updated:', response);

        // Update display
        document.getElementById('nextCheckNumberDisplay').value = newCheckNumber;

        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('editCheckNumberModal')).hide();

        // Show success message
        showToast(`Next check number updated to ${newCheckNumber}`, 'success');
    } catch (error) {
        console.error('Error saving next check number:', error);
        alert('Error saving next check number: ' + (error.message || 'Unknown error'));
    }
}

// REQUIREMENT: Convert number to words for check amount
function numberToWords(num) {
    const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
    const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
    const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];

    if (num === 0) return 'Zero';

    function convertLessThanThousand(n) {
        if (n === 0) return '';

        if (n < 10) return ones[n];
        if (n < 20) return teens[n - 10];
        if (n < 100) return tens[Math.floor(n / 10)] + (n % 10 !== 0 ? ' ' + ones[n % 10] : '');

        return ones[Math.floor(n / 100)] + ' Hundred' + (n % 100 !== 0 ? ' ' + convertLessThanThousand(n % 100) : '');
    }

    if (num < 1000) return convertLessThanThousand(num);
    if (num < 1000000) {
        return convertLessThanThousand(Math.floor(num / 1000)) + ' Thousand' +
               (num % 1000 !== 0 ? ' ' + convertLessThanThousand(num % 1000) : '');
    }

    return convertLessThanThousand(Math.floor(num / 1000000)) + ' Million' +
           (num % 1000000 !== 0 ? ' ' + convertLessThanThousand(Math.floor((num % 1000000) / 1000)) + ' Thousand' : '') +
           (num % 1000 !== 0 ? ' ' + convertLessThanThousand(num % 1000) : '');
}

// REQUIREMENT: Generate check preview HTML
function generateCheckPreview(check, checkNumber) {
    const amount = parseFloat(check.amount);
    const dollars = Math.floor(amount);
    const cents = Math.round((amount - dollars) * 100);

    // Convert amount to words
    const amountWords = numberToWords(dollars) + ' and ' + cents.toString().padStart(2, '0') + '/100 Dollars';

    // Format amount with commas (no $ sign per requirement)
    const amountFormatted = amount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const date = new Date(check.transaction_date);
    const dateFormatted = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();

    return `
        <div style="background: white; border: 2px solid #000; padding: 30px; font-family: 'Courier New', monospace; max-width: 800px; margin: 0 auto;">
            <!-- Check Header -->
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div>
                    <div style="font-size: 10px; color: #666;">YOUR LAW FIRM NAME</div>
                    <div style="font-size: 10px; color: #666;">123 Main Street</div>
                    <div style="font-size: 10px; color: #666;">City, State 12345</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 14px; font-weight: bold;">Check #${escapeHtml(checkNumber)}</div>
                </div>
            </div>

            <!-- Date -->
            <div style="text-align: right; margin-bottom: 30px;">
                <span style="font-size: 12px;">Date: </span>
                <span style="border-bottom: 1px solid #000; padding: 0 20px; font-size: 12px;">${dateFormatted}</span>
            </div>

            <!-- Pay to the order of -->
            <div style="margin-bottom: 15px;">
                <span style="font-size: 12px;">Pay to the order of: </span>
                <span style="border-bottom: 1px solid #000; padding: 0 20px; font-size: 14px; font-weight: bold; display: inline-block; min-width: 400px;">
                    ${escapeHtml(check.payee || check.vendor_name || 'PAYEE NAME')}
                </span>
            </div>

            <!-- Amount -->
            <div style="margin-bottom: 20px; display: flex; justify-content: flex-end;">
                <div style="border: 2px solid #000; padding: 8px 15px; font-size: 16px; font-weight: bold; background: #f9f9f9;">
                    <span class="check-amount-formatted">${amountFormatted}</span>
                </div>
            </div>

            <!-- Amount in words -->
            <div style="margin-bottom: 30px;">
                <div style="border-bottom: 1px solid #000; padding: 5px 0; font-size: 12px; min-height: 25px; text-transform: uppercase;">
                    ${amountWords}
                </div>
                <div style="font-size: 10px; color: #666; margin-top: 5px;">DOLLARS</div>
            </div>

            <!-- Memo -->
            <div style="margin-bottom: 30px;">
                <span style="font-size: 11px;">Memo: </span>
                <span style="border-bottom: 1px solid #000; padding: 0 10px; font-size: 11px; display: inline-block; min-width: 300px;">
                    ${escapeHtml(check.check_memo || check.description || '')}
                </span>
            </div>

            <!-- Signature line -->
            <div style="display: flex; justify-content: flex-end; margin-top: 40px;">
                <div style="border-top: 1px solid #000; width: 250px; text-align: center; padding-top: 5px; font-size: 10px;">
                    Authorized Signature
                </div>
            </div>

            <!-- Bank info (bottom) -->
            <div style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 9px; color: #666;">
                <div style="text-align: center;">
                    ⑈1234⑈ ⑆567890123⑆ 1234
                </div>
            </div>
        </div>
    `;
}

// REQUIREMENT: Show check preview modal
async function showCheckPreview(check, checkNumber) {
    const previewHtml = generateCheckPreview(check, checkNumber);
    document.getElementById('checkPreviewContainer').innerHTML = previewHtml;

    const modal = new bootstrap.Modal(document.getElementById('checkPreviewModal'));
    modal.show();

    return new Promise((resolve) => {
        const confirmBtn = document.getElementById('confirmCheckPreview');
        const modalEl = document.getElementById('checkPreviewModal');

        const handleConfirm = () => {
            modal.hide();
            resolve(true);
            cleanup();
        };

        const handleClose = () => {
            resolve(false);
            cleanup();
        };

        const cleanup = () => {
            confirmBtn.removeEventListener('click', handleConfirm);
            modalEl.removeEventListener('hidden.bs.modal', handleClose);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        modalEl.addEventListener('hidden.bs.modal', handleClose, { once: true });
    });
}
