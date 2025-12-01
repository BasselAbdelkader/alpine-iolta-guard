// Case Detail Page Logic
let currentCase = null;
let caseId = null;
let clientId = null;
let validPayeeSelected = false; // Track if selected payee is valid

// Show success notification with auto-fade
function showSuccessNotification(message = 'Transaction saved successfully!') {
    const notification = document.getElementById('successNotification');
    const messageSpan = document.getElementById('notificationMessage');

    // Set message
    messageSpan.textContent = message;

    // Show notification with fade-in
    notification.style.display = 'block';
    notification.style.opacity = '0';

    // Fade in
    setTimeout(() => {
        notification.style.transition = 'opacity 0.3s ease-in';
        notification.style.opacity = '1';
    }, 10);

    // Auto-hide after 3 seconds with fade-out
    setTimeout(() => {
        notification.style.transition = 'opacity 0.5s ease-out';
        notification.style.opacity = '0';

        // Hide completely after fade-out
        setTimeout(() => {
            notification.style.display = 'none';
        }, 500);
    }, 3000);
}

// Show error notification (top-right)
function showErrorNotification(message) {
    showToast(message, 'error');
}

// Show centered error notification (same style as top-right, but centered)
function showCenteredError(message) {
    showToast(message, 'error', 'center');
}

function showToast(message, type = 'success', position = 'top-right') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        // Position based on parameter
        if (position === 'center') {
            toastContainer.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999;';
        } else {
            toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        }
        document.body.appendChild(toastContainer);
    } else {
        // Update position if it changed
        if (position === 'center') {
            toastContainer.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999;';
        } else {
            toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        }
    }

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-success' : 'bg-danger';
    toast.className = `toast align-items-center text-white ${bgClass} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Extract case ID from URL
function getCaseIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    // URL format: /cases/123
    const id = pathParts[2];
    return id ? parseInt(id) : null;
}

// Load page on startup
document.addEventListener('DOMContentLoaded', async function() {
    await checkAuth();

    caseId = getCaseIdFromUrl();

    if (!caseId) {
        // alert('Invalid case ID');
        window.location.href = '/clients';
        return;
    }

    await loadLawFirmInfo();
    await loadCaseDetails();
    await loadTransactions();

    // Setup event listeners
    // BUG #24 FIX: All Cases button should go to client detail page (shows all cases for that client)
    const allCasesBtn = document.getElementById('allCasesBtn');
    if (allCasesBtn) {
        allCasesBtn.addEventListener('click', function() {
            if (clientId) {
                window.location.href = `/clients/${clientId}`;
            } else {
                window.location.href = '/clients';
            }
        });
    }

    const viewClientBtn = document.getElementById('viewClientBtn');
    if (viewClientBtn) {
        viewClientBtn.addEventListener('click', function() {
            if (clientId) {
                window.location.href = `/clients/${clientId}`;
            } else {
                window.location.href = '/clients';
            }
        });
    }

    const editCaseBtn = document.getElementById('editCaseBtn');
    if (editCaseBtn) {
        editCaseBtn.addEventListener('click', function() {
            console.log('========================================');
            console.log('🖱️  EDIT CASE BUTTON CLICKED - CASE DETAIL PAGE');
            console.log('========================================');
            // Open edit case modal
            editCaseFromDetail();
        });
    }

    const addTransactionBtn = document.getElementById('addTransactionBtn');
    if (addTransactionBtn) {
        addTransactionBtn.addEventListener('click', function() {
            openTransactionModal();
        });
    }

    const printLedgerBtn = document.getElementById('printLedgerBtn');
    if (printLedgerBtn) {
        printLedgerBtn.addEventListener('click', function() {
            printCaseLedger();
        });
    }

    // Handle To Print checkbox - disable/enable reference field
    const toPrintCheckbox = document.getElementById('to_print');
    const refField = document.getElementById('transaction_ref');

    if (toPrintCheckbox && refField) {
        // Initial state - if checkbox already checked on modal open
        if (toPrintCheckbox.checked) {
            refField.value = '';
            refField.disabled = true;
        }

        // Listen for checkbox changes
        toPrintCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // When To Print is checked, clear and disable reference field
                refField.value = '';
                refField.disabled = true;
            } else {
                // When To Print is unchecked, enable reference field
                refField.disabled = false;
                refField.focus();  // Focus on field for user convenience
            }
        });
    }
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
            document.getElementById('printFirmName').textContent = firm.firm_name;
            const details = `${firm.address}, ${firm.city}, ${firm.state} ${firm.zip_code} | ${firm.phone} | ${firm.email}`;
            document.getElementById('lawFirmDetails').textContent = details;
            document.getElementById('headerFirmDetails').textContent = details;
        }
    } catch (error) {
        // console.error('Error loading law firm info:', error);
    }
}

async function loadCaseDetails() {
    try {
        console.log('Loading case ID:', caseId);
        const caseData = await api.get(`/v1/cases/${caseId}/`);
        console.log('Case data received:', caseData);
        console.log('Client name from API:', caseData.client_name);
        console.log('Case title from API:', caseData.case_title);
        currentCase = caseData;
        clientId = caseData.client;

        // Update page title with client name and reduced font size
        const cardTitle = document.getElementById('cardCaseTitle');
        if (cardTitle) {
            const clientName = caseData.client_name || 'Unknown Client';
            const caseTitle = caseData.case_title || 'Case Details';
            cardTitle.innerHTML = `<strong style="font-size: 0.9rem;">${clientName}: ${caseTitle}</strong>`;
        }

        // Update print header (may not exist on all pages)
        const fullName = caseData.client_name || 'Unknown Client';
        const caseTitle = caseData.case_title || 'Unknown Case';
        const printClientCase = document.getElementById('printClientCase');
        if (printClientCase) {
            printClientCase.textContent = `Client: ${fullName} | Case: ${caseTitle}`;
        }

        // Populate print case details table
        const printCaseDetailsHTML = `
            <h3 style="font-size: 14pt; font-weight: bold; margin-bottom: 10px;">${caseTitle}</h3>
            <table style="width: 100%; margin-bottom: 20px; border-collapse: collapse; font-size: 10pt;">
                <tr>
                    <td style="width: 20%; font-weight: bold; padding: 5px; border: 1px solid #ddd;">Case Title:</td>
                    <td style="width: 30%; padding: 5px; border: 1px solid #ddd;">${caseTitle}</td>
                    <td style="width: 20%; font-weight: bold; padding: 5px; border: 1px solid #ddd;">Status:</td>
                    <td style="width: 30%; padding: 5px; border: 1px solid #ddd;">${caseData.case_status || '-'}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; padding: 5px; border: 1px solid #ddd;">Client:</td>
                    <td style="padding: 5px; border: 1px solid #ddd;">${fullName}</td>
                    <td style="font-weight: bold; padding: 5px; border: 1px solid #ddd;">Case Balance:</td>
                    <td style="padding: 5px; border: 1px solid #ddd;">${caseData.formatted_balance || '$0.00'}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; padding: 5px; border: 1px solid #ddd;">Opened Date:</td>
                    <td style="padding: 5px; border: 1px solid #ddd;">${caseData.opened_date ? formatDate(caseData.opened_date) : '-'}</td>
                    <td style="font-weight: bold; padding: 5px; border: 1px solid #ddd;"></td>
                    <td style="padding: 5px; border: 1px solid #ddd;"></td>
                </tr>
                <tr>
                    <td style="font-weight: bold; padding: 5px; border: 1px solid #ddd;">Description:</td>
                    <td colspan="3" style="padding: 5px; border: 1px solid #ddd;">${caseData.case_description || '-'}</td>
                </tr>
            </table>
        `;
        const printCaseDetails = document.getElementById('printCaseDetails');
        if (printCaseDetails) {
            printCaseDetails.innerHTML = printCaseDetailsHTML;
        }

        // Populate case details table
        const detailCaseTitle = document.getElementById('detail-case-title');
        if (detailCaseTitle) {
            detailCaseTitle.textContent = caseData.case_title || '-';
        }

        const detailStatus = document.getElementById('detail-status');
        if (detailStatus) {
            detailStatus.innerHTML = getCaseStatusBadge(caseData.case_status);
        }

        // Client link
        const clientLink = document.getElementById('detail-client-link');
        if (clientLink) {
            clientLink.textContent = caseData.client_name || '-';
            clientLink.href = `/clients/${caseData.client}`;
        }

        // Case balance with color coding
        const balance = parseFloat(caseData.current_balance || 0);
        const balanceEl = document.getElementById('detail-case-balance');
        if (balanceEl) {
            balanceEl.textContent = formatAccountingAmount(balance);
            balanceEl.className = 'h6 mb-0 ' + getBalanceClass(balance);
        }

        // Opened date
        const openedDate = document.getElementById('detail-opened-date');
        if (openedDate) {
            openedDate.textContent = caseData.opened_date ? formatDate(caseData.opened_date) : '-';
        }

        // BUG #22 FIX: Closed date - only show if case is closed and has closed date
        const closedDateEl = document.getElementById('detail-closed-date');
        const closedDateRow = document.getElementById('closed-date-row');
        if (caseData.closed_date && closedDateEl && closedDateRow) {
            closedDateEl.textContent = formatDate(caseData.closed_date);
            closedDateRow.style.display = '';
        } else if (closedDateRow) {
            closedDateRow.style.display = 'none';
        }

        // Description - only show row if description exists
        const descEl = document.getElementById('detail-description');
        const descRow = document.getElementById('description-row');
        if (caseData.case_description && caseData.case_description.trim() && descEl && descRow) {
            descEl.textContent = caseData.case_description;
            descRow.style.display = '';
        }

        // Update ledger subtitle
        const subtitleElement = document.getElementById('ledger-subtitle');
        console.log('ledger-subtitle element:', subtitleElement);
        if (subtitleElement) {
            subtitleElement.textContent = `Client: ${caseData.client_name || '-'} | Case: ${caseData.case_title || '-'}`;
            console.log('Updated ledger-subtitle to:', subtitleElement.textContent);
        } else {
            console.error('ledger-subtitle element not found!');
        }

        // Update print header
        const printElement = document.getElementById('printClientCase');
        console.log('printClientCase element:', printElement);
        if (printElement) {
            printElement.textContent = `Client: ${caseData.client_name || '-'} | Case: ${caseData.case_title || '-'}`;
            console.log('Updated printClientCase to:', printElement.textContent);
        } else {
            console.error('printClientCase element not found!');
        }

    } catch (error) {
        // console.error('Error loading case details:', error);
        document.getElementById('cardCaseTitle').textContent = 'Error Loading Case';
        // alert('Error loading case details: ' + error.message);
    }
}

async function loadTransactions() {
    const container = document.getElementById('transactionsContainer');

    try {
        const data = await api.get(`/v1/cases/${caseId}/transactions/`);
        const transactions = data.transactions || [];

        // Update transaction count
        document.getElementById('transaction-count').textContent = transactions.length;

        if (transactions.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <div class="mb-3">
                        <i class="fas fa-receipt fa-3x"></i>
                    </div>
                    <p>No transactions found for this case.</p>
                    <button type="button" class="btn btn-success" onclick="document.getElementById('addTransactionBtn').click()">
                        <i class="fas fa-plus"></i> Add First Transaction
                    </button>
                </div>
            `;
            return;
        }

        // Sort transactions by date (oldest first) for correct balance calculation
        const sortedTransactions = [...transactions].sort((a, b) => {
            const dateA = new Date(a.transaction_date || a.date);
            const dateB = new Date(b.transaction_date || b.date);
            const dateDiff = dateA - dateB;
            // If dates are the same, sort by ID to maintain consistent order
            if (dateDiff === 0) {
                return (a.id || 0) - (b.id || 0);
            }
            return dateDiff;
        });

        // Calculate running balance
        let runningBalance = 0;
        const transactionsWithBalance = sortedTransactions.map(txn => {
            // Handle both old and new API formats
            const transactionType = txn.transaction_type || txn.type;
            const isVoided = txn.status.toLowerCase() === 'voided' || (txn.amount === '0.00' && txn.status === false);

            if (!isVoided) {
                const amount = parseFloat(txn.amount || 0);
                if (transactionType === 'DEPOSIT') {
                    runningBalance += amount;
                } else if (transactionType === 'WITHDRAWAL') {
                    runningBalance -= amount;
                }
            }
            return {
                ...txn,
                running_balance: runningBalance
            };
        });

        // Keep oldest first for display (chronological order)
        // transactionsWithBalance.reverse(); // REMOVED - now showing oldest-to-newest

        let html = `
            <div class="table-responsive">
                <table class="table table-striped table-hover align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th style="width: 90px;" class="text-center">Date</th>
                            <th style="width: 80px;" class="text-center">Type</th>
                            <th style="width: 100px;" class="text-center">Reference</th>
                            <th style="width: 150px;">Payee</th>
                            <th style="width: 160px;">Description</th>
                            <th style="width: 85px;" class="text-center">Status</th>
                            <th style="width: 110px;" class="text-end">Amount</th>
                            <th style="width: 110px;" class="text-end">Balance</th>
                            <th style="width: 200px;" class="text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        transactionsWithBalance.forEach(txn => {
            // Handle both old and new API formats
            const transactionType = txn.transaction_type || txn.type;
            const transactionDate = txn.transaction_date || txn.date;

            // Determine if voided (handle both formats)
            const isVoided = txn.status.toLowerCase() === 'voided' || (txn.amount === '0.00' && txn.status === false);

            // Type badge
            let typeClass = 'bg-secondary';
            let typeText = 'Unknown';
            if (transactionType === 'DEPOSIT') {
                typeClass = 'bg-success';
                typeText = 'Deposit';
            } else if (transactionType === 'WITHDRAWAL') {
                typeClass = 'bg-danger';
                typeText = 'Withdrawal';
            }

            // Get payee - try multiple fields
            let payeeName = txn.payee || txn.payee_name || txn.vendor_name || txn.client_name;
            if (!payeeName && currentCase) {
                payeeName = currentCase.client_name; // Fallback to case client
            }
            payeeName = payeeName || '-';

            // Status badge based on status field
            let statusClass = 'bg-warning text-dark';
            let statusText = 'Pending';
            if (txn.status.toLowerCase() === 'voided') {
                statusClass = 'bg-danger';
                statusText = 'Voided';
            } else if (txn.status.toLowerCase() === 'cleared') {
                statusClass = 'bg-success';
                statusText = 'Cleared';
            } else if (txn.status.toLowerCase() === 'pending') {
                statusClass = 'bg-warning text-dark';
                statusText = 'Pending';
            }

            // Amount formatting - deposits positive, withdrawals in parentheses
            const amount = parseFloat(txn.original_amount || txn.amount || 0);
            let amountDisplay = '';
            let amountClass = 'fw-medium';

            if (isVoided) {
                // Voided transactions show original amount with strikethrough and (VOIDED) text
                amountClass = 'text-muted';
                if (transactionType === 'DEPOSIT') {
                    amountDisplay = `<span class="text-muted" style="text-decoration: line-through;">${formatAccountingAmount(amount)} <small>(VOIDED)</small></span>`;
                } else {
                    amountDisplay = `<span class="text-muted" style="text-decoration: line-through;">(${formatAccountingAmount(amount)}) <small>(VOIDED)</small></span>`;
                }
            } else {
                if (transactionType === 'DEPOSIT') {
                    amountClass += ' text-success';
                    amountDisplay = formatAccountingAmount(amount);
                } else {
                    amountClass += ' text-danger';
                    amountDisplay = `(${formatAccountingAmount(amount)})`;
                }
            }

            // Balance styling
            const balanceClass = 'fw-bold ' + getBalanceClass(txn.running_balance);

            html += `
                <tr ${isVoided ? 'class="voided-transaction"' : ''}>
                    <td class="text-center" ${isVoided ? 'style="text-decoration: line-through;"' : ''}>
                        <span class="fw-medium">${formatDate(transactionDate)}</span>
                    </td>
                    <td class="text-center">
                        <span class="badge ${typeClass}">${typeText}</span>
                    </td>
                    <td class="text-center">
                        <span class="text-muted">${txn.reference_number || txn.transaction_number || '-'}</span>
                    </td>
                    <td>
                        <span class="fw-medium">${payeeName}</span>
                    </td>
                    <td>
                        <span class="text-dark">${truncate(txn.description || 'No description provided', 50)}</span>
                    </td>
                    <td class="text-center">
                        <span class="badge ${statusClass}">${statusText}</span>
                    </td>
                    <td class="text-end">
                        <span class="${amountClass}">${amountDisplay}</span>
                    </td>
                    <td class="text-end">
                        <span class="${balanceClass}">${formatAccountingAmount(txn.running_balance)}</span>
                    </td>
                    <td class="text-center" style="white-space: nowrap; padding: 8px;">
        `;

            if (isVoided) {
                // Voided transaction display
                const voidReason = txn.void_reason || txn.voided_reason || '';
                console.log('Voided transaction:', txn.id, 'void_reason:', txn.void_reason, 'voidReason:', voidReason);
                html += `
                        <div class="d-flex flex-column align-items-center" style="gap: 4px;">
                            <span class="badge bg-secondary">VOIDED</span>
                            ${voidReason ? `
                                <div class="text-muted text-center" title="${voidReason}" style="line-height: 1.3; max-width: 180px;">
                                    <strong>Reason:</strong> ${voidReason}
                                </div>
                            ` : ''}
                            <button type="button" class="btn btn-outline-info btn-sm" onclick="viewAuditHistory(${txn.id})" title="Print Audit Trail" style="min-width: 36px; padding: 4px 6px;">
                                <i class="fas fa-file-alt"></i>
                            </button>
                        </div>
                `;
            } else {
                // Active transaction actions
                html += `
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
                            <button type="button" class="btn btn-outline-info btn-sm" onclick="viewAuditHistory(${txn.id})" title="Print Audit Trail" style="min-width: 36px; padding: 4px 6px;">
                                <i class="fas fa-file-alt"></i>
                            </button>
                        </div>
                `;
            }

            html += `
                    </td>
                </tr>
            `;
        });

        // Add final balance row
        const finalBalance = transactionsWithBalance.length > 0
            ? transactionsWithBalance[transactionsWithBalance.length - 1].running_balance
            : 0;

        html += `
                    <tr class="print-only-row" style="border-top: 2px solid #000; font-weight: bold; display: none;">
                        <td colspan="6" class="text-end" style="padding: 8px; font-size: 11pt;">FINAL BALANCE:</td>
                        <td class="text-end" style="padding: 8px; font-size: 11pt;">${formatAccountingAmount(finalBalance)}</td>
                        <td></td>
                    </tr>
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        // console.error('Error loading transactions:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                Error loading transactions. Please try again.
            </div>
        `;
    }
}

async function editTransaction(transactionId) {
    try {
        // Load all transactions and find the one we want
        const txnData = await api.get(`/v1/cases/${caseId}/transactions/`);
        const transactions = txnData.transactions || [];
        const transaction = transactions.find(t => t.id === transactionId);

        if (!transaction) {
            // alert('Transaction not found');
            return;
        }

        // Handle both old and new API formats
        const transactionType = transaction.transaction_type || transaction.type;
        const transactionDate = transaction.transaction_date || transaction.date;

        // Set form to edit mode
        document.getElementById('transactionModalLabel').textContent = 'Edit Transaction';
        document.getElementById('transaction_id').value = transactionId;

        // Populate form fields (handle both API formats)
        document.getElementById('transaction_date').value = transactionDate;
        document.getElementById('transaction_type').value = transactionType;
        document.getElementById('transaction_ref').value = transaction.reference_number || '';
        document.getElementById('transaction_amount').value = transaction.amount;
        document.getElementById('transaction_description').value = transaction.description || '';
        document.getElementById('transaction_memo').value = transaction.check_memo || '';

        // Handle payee field
        const payeeField = document.getElementById('transaction_payee');
        const payee = transaction.payee || transaction.payee_name || transaction.vendor_name || transaction.client_name;
        if (payee) {
            payeeField.value = payee;
            validPayeeSelected = true; // Mark as valid since it's from existing transaction
        }

        // Set bank account (need to load bank accounts first)
        await loadBankAccounts();
        if (transaction.bank_account) {
            document.getElementById('transaction_bank_account').value = transaction.bank_account;
        }

        // Client and Case (locked)
        document.getElementById('transaction_client').value = currentCase.client_name || '';
        document.getElementById('transaction_case').value = currentCase.case_title || '';
        document.getElementById('transaction_client_id').value = clientId || '';
        document.getElementById('transaction_case_id').value = caseId || '';

        // Update available funds from case balance
        const balance = parseFloat(currentCase.current_balance || 0);
        updateAvailableFundsDisplay(balance);

        // Load vendor list for autocomplete
        await loadVendorList();

        // Set "To print" checkbox based on reference number
        const toPrintCheckbox = document.getElementById('to_print');
        const refField = document.getElementById('transaction_ref');
        if (transaction.reference_number === 'TO PRINT') {
            toPrintCheckbox.checked = true;
            refField.value = 'TO PRINT';
            refField.readOnly = true;
            refField.style.backgroundColor = '#e9ecef';
        } else {
            toPrintCheckbox.checked = false;
            refField.readOnly = false;
            refField.style.backgroundColor = '';
        }

        // REQUIREMENT: Lock fields for cleared/reconciled transactions (only description editable)
        const transactionStatus = (transaction.status || '').toLowerCase();
        console.log('Transaction status:', transactionStatus);

        if (transactionStatus.toLowerCase() === 'cleared' || transactionStatus.toLowerCase() === 'reconciled') {
            // Disable all fields except description
            document.getElementById('transaction_date').disabled = true;
            document.getElementById('transaction_type').disabled = true;
            document.getElementById('transaction_ref').readOnly = true;
            document.getElementById('transaction_ref').style.backgroundColor = '#e9ecef';
            document.getElementById('transaction_payee').readOnly = true;
            document.getElementById('transaction_payee').style.backgroundColor = '#e9ecef';
            document.getElementById('transaction_amount').readOnly = true;
            document.getElementById('transaction_amount').style.backgroundColor = '#e9ecef';
            document.getElementById('transaction_bank_account').disabled = true;
            document.getElementById('transaction_memo').readOnly = true;
            document.getElementById('transaction_memo').style.backgroundColor = '#e9ecef';

            if (toPrintCheckbox) {
                toPrintCheckbox.disabled = true;
            }

            console.log('Fields locked for', transactionStatus, 'transaction');
        } else {
            // Enable all fields for pending/voided transactions
            document.getElementById('transaction_date').disabled = false;
            document.getElementById('transaction_type').disabled = false;
            document.getElementById('transaction_ref').readOnly = false;
            document.getElementById('transaction_ref').style.backgroundColor = '';
            document.getElementById('transaction_payee').readOnly = false;
            document.getElementById('transaction_payee').style.backgroundColor = '';
            document.getElementById('transaction_amount').readOnly = false;
            document.getElementById('transaction_amount').style.backgroundColor = '';
            document.getElementById('transaction_bank_account').disabled = false;
            document.getElementById('transaction_memo').readOnly = false;
            document.getElementById('transaction_memo').style.backgroundColor = '';

            if (toPrintCheckbox) {
                toPrintCheckbox.disabled = false;
            }

            console.log('Fields unlocked for', transactionStatus || 'pending', 'transaction');
        }

        // Setup Save button click handler
        const saveBtn = document.getElementById('saveTransactionBtn');
        // console.log('Setting up Save button for edit:', saveBtn);
        if (!saveBtn) {
            // console.error('ERROR: Save button not found!');
            // alert('ERROR: Save button not found!');
            return;
        }
        saveBtn.onclick = function(e) {
            e.preventDefault();
            // console.log('Save button clicked (from edit)!');
            // alert('Save button was clicked! Check console for details.');
            submitTransaction();
        };

        // Open modal
        const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
        modal.show();

    } catch (error) {
        // console.error('Error loading transaction:', error);
        // alert('Error loading transaction details: ' + (error.message || 'Please try again'));
    }
}

let currentVoidTransactionId = null;

async function voidTransaction(transactionId) {
    // First, get transaction details to check status
    try {
        const txnResponse = await api.get(`/v1/bank-accounts/bank-transactions/${transactionId}/`);
        const transaction = txnResponse;

        // Check if transaction is cleared or reconciled - BEFORE asking for reason
        if (transaction.status.toLowerCase() === 'cleared' || transaction.status.toLowerCase() === 'reconciled') {
            // Show centered red error toast
            showCenteredError(`Cannot void ${transaction.status.toLowerCase() === 'cleared' ? 'cleared' : 'reconciled'} transactions.`);
            return;
        }

        // If not cleared/reconciled, proceed with void flow
        const reason = prompt('Please enter a reason for voiding this transaction:');
        if (!reason || !reason.trim()) {
            return;
        }

        if (!confirm('Are you sure you want to void this transaction? This action cannot be undone.')) {
            return;
        }

        const response = await api.post(`/v1/bank-accounts/bank-transactions/${transactionId}/void/`, {
            void_reason: reason.trim()
        });

        if (response.success) {
            showSuccessNotification('Transaction voided successfully!');
            setTimeout(() => location.reload(), 1000);
        } else {
            showErrorNotification(response.message || 'Failed to void transaction');
        }
    } catch (error) {
        // console.error('Error voiding transaction:', error);
        showErrorNotification(error.message || 'Failed to void transaction');
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
            // Show centered red error toast
            showCenteredError(`Cannot reissue ${transaction.status.toLowerCase() === 'cleared' ? 'cleared' : 'reconciled'} transactions.`);
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
            showErrorNotification(response.message || 'Failed to reissue check');
        }
    } catch (error) {
        console.error('❌ Error reissuing check:', error);
        showErrorNotification(error.message || 'Failed to reissue check');
    }
}

// Store current transaction ID for printing
let currentAuditTransactionId = null;

async function viewAuditHistory(transactionId) {
    try {
        // Store transaction ID for print function
        currentAuditTransactionId = transactionId;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('auditTrailModal'));
        modal.show();

        // Show loading state
        document.getElementById('auditTrailContent').innerHTML = `
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

            document.getElementById('auditTrailContent').innerHTML = html;
        } else {
            document.getElementById('auditTrailContent').innerHTML = `
                <div class="alert alert-danger">
                    Failed to load audit history.
                </div>
            `;
        }
    } catch (error) {
        // console.error('Error loading audit history:', error);
        document.getElementById('auditTrailContent').innerHTML = `
            <div class="alert alert-danger">
                Error loading audit history: ${error.message}
            </div>
        `;
    }
}

function printAuditTrail() {
    // Open the PDF in a new tab (like professional websites - Chrome PDF viewer with grey toolbar)
    if (currentAuditTransactionId) {
        window.open(`/api/v1/bank-accounts/bank-transactions/${currentAuditTransactionId}/audit_history_pdf/`, '_blank');
    } else {
        // alert('No transaction selected for printing');
    }
}

function getCaseStatusBadge(status) {
    const statusMap = {
        'Open': 'bg-primary',
        'Pending Settlement': 'bg-warning text-dark',
        'Settled': 'bg-success',
        'Closed': 'bg-secondary',
    };
    const badgeClass = statusMap[status] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${status}</span>`;
}

function getBalanceClass(balance) {
    if (balance < 0) return 'text-danger';
    if (balance === 0) return 'text-muted';
    return 'text-success';
}

// Format amount in accounting format (parentheses for negative)
function formatAccountingAmount(value) {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';

    if (num < 0) {
        return `(${Math.abs(num).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})})`;
    }
    return num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function updateAvailableFundsDisplay(balance) {
    const fundsElement = document.getElementById('available-funds');
    const containerElement = document.getElementById('available-funds-container');

    if (fundsElement) {
        fundsElement.textContent = formatAccountingAmount(balance);
    }

    if (containerElement) {
        // Set color based on balance: red if negative, green if positive/zero
        if (balance < 0) {
            containerElement.style.color = '#dc3545'; // Bootstrap danger red
        } else {
            containerElement.style.color = '#28a745'; // Bootstrap success green
        }
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US');
}

function truncate(str, maxLength) {
    if (!str) return '';
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength - 3) + '...';
}

function logout() {
    api.logout();
}

// Global vendor list
let vendorList = [];

// Transaction Modal Functions
async function openTransactionModal() {
    try {
        // Reset form first (before setting values)
        document.getElementById('transactionForm').reset();
        document.getElementById('amount-error').style.display = 'none';
        document.getElementById('transaction_amount').classList.remove('is-invalid');

        // Reset payee validation for new transaction
        validPayeeSelected = false;

        // Clear transaction ID (for new transaction)
        document.getElementById('transaction_id').value = '';
        document.getElementById('transactionModalLabel').textContent = 'Add New Transaction';

        // ALWAYS set client and case (LOCKED to current context)
        if (currentCase) {
            // Set display names (locked fields)
            document.getElementById('transaction_client').value = currentCase.client_name || '';
            document.getElementById('transaction_case').value = currentCase.case_title || '';

            // Set hidden IDs for submission
            document.getElementById('transaction_client_id').value = clientId || '';
            document.getElementById('transaction_case_id').value = caseId || '';

            // Update available funds from case balance
            const balance = parseFloat(currentCase.current_balance || 0);
            updateAvailableFundsDisplay(balance);
        }

        // Set today's date
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('transaction_date').value = today;

        // Load bank accounts and vendors
        await loadBankAccounts();
        await loadVendorList();

        // Setup To Print checkbox listener
        setupToPrintCheckbox();

        // Setup amount validation
        setupAmountValidation();

        // Setup payee autocomplete
        setupPayeeAutocomplete();

        // Setup Save button
        const saveBtn = document.getElementById('saveTransactionBtn');
        // console.log('Setting up Save button:', saveBtn);
        if (!saveBtn) {
            // console.error('ERROR: Save button not found!');
            // alert('ERROR: Save button not found!');
            return;
        }
        saveBtn.onclick = function(e) {
            e.preventDefault();
            // console.log('Save button clicked!');
            // alert('Save button was clicked! Check console for details.');
            submitTransaction();
        };

        // Show modal
        const modalEl = document.getElementById('transactionModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

    } catch (error) {
        // console.error('Error opening transaction modal:', error);
        // alert('Error loading transaction form. Please try again.');
    }
}

async function loadBankAccounts() {
    try {
        // Using the bank accounts API - correct endpoint
        const data = await api.get('/v1/bank-accounts/accounts/');
        const select = document.getElementById('transaction_bank_account');
        select.innerHTML = '<option value="">Select Bank Account</option>';

        // API returns paginated results
        const accounts = data.results || data.bank_accounts || [];

        // console.log('Loaded bank accounts:', accounts);

        if (accounts.length > 0) {
            accounts.forEach(account => {
                const option = document.createElement('option');
                option.value = account.id;
                // Format: "Account Name - Bank Name (Type)"
                const typeLabel = account.account_type ? ` (${account.account_type})` : '';
                option.textContent = `${account.account_name || account.bank_name}${typeLabel}`;
                select.appendChild(option);
            });

            // Auto-select first active account if available
            const firstActive = accounts.find(a => a.is_active) || accounts[0];
            if (firstActive) {
                select.value = firstActive.id;
            }

            // Disable bank account selection when in case context (locked to case)
            select.disabled = true;
            select.style.backgroundColor = '#f8f9fa';  // Light grey background
            select.style.cursor = 'not-allowed';
        } else {
            // console.warn('No bank accounts found');
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No bank accounts available';
            option.disabled = true;
            select.appendChild(option);
        }
    } catch (error) {
        // console.error('Error loading bank accounts:', error);
        // alert('Error loading bank accounts: ' + (error.message || 'Please try again'));
    }
}

function setupToPrintCheckbox() {
    const checkbox = document.getElementById('to_print');
    const refField = document.getElementById('transaction_ref');

    if (!checkbox || !refField) {
        console.error('To Print checkbox or reference field not found');
        return;
    }

    checkbox.addEventListener('change', function() {
        console.log('To Print checkbox changed. Checked:', this.checked);
        if (this.checked) {
            refField.value = 'TO PRINT';
            refField.readOnly = true;
            refField.style.backgroundColor = '#e9ecef';
            refField.style.color = '#6c757d';
            refField.style.cursor = 'not-allowed';
            refField.style.opacity = '0.7';
            console.log('Set reference field to TO PRINT');
        } else {
            refField.value = '';
            refField.readOnly = false;
            refField.style.backgroundColor = '';
            refField.style.color = '';
            refField.style.cursor = '';
            refField.style.opacity = '';
            console.log('Cleared reference field');
        }
    });
}

function setupAmountValidation() {
    const amountField = document.getElementById('transaction_amount');
    const typeField = document.getElementById('transaction_type');

    function validateAmount() {
        const amount = parseFloat(amountField.value.replace(/[^\d.]/g, '')) || 0;
        const type = typeField.value;
        const availableFundsText = document.getElementById('available-funds').textContent;
        const availableFunds = parseFloat(availableFundsText.replace(/[^\d.-]/g, '')) || 0;

        if (type === 'WITHDRAWAL' && amount > 0) {
            if (availableFunds < 0 || amount > availableFunds) {
                document.getElementById('amount-error').style.display = 'block';
                amountField.classList.add('is-invalid');
                return false;
            } else {
                document.getElementById('amount-error').style.display = 'none';
                amountField.classList.remove('is-invalid');
                return true;
            }
        } else {
            document.getElementById('amount-error').style.display = 'none';
            amountField.classList.remove('is-invalid');
            return true;
        }
    }

    amountField.addEventListener('input', function() {
        // Format with commas as user types
        let value = this.value.replace(/[^\d.]/g, '');
        const parts = value.split('.');
        if (parts[0]) {
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        }
        if (parts[1]) {
            parts[1] = parts[1].substring(0, 2);
        }
        this.value = parts.join('.');
        validateAmount();
    });

    typeField.addEventListener('change', validateAmount);

    // REQUIREMENT: Setup To Print visibility based on transaction type
    setupToPrintVisibility();
}

// REQUIREMENT: Hide "To Print" option until Withdrawal is chosen
// REQUIREMENT: Handle To Print checkbox - disable reference requirement
document.addEventListener('DOMContentLoaded', function() {
    const toPrintCheckbox = document.getElementById('to_print');
    const refField = document.getElementById('transaction_ref');
    
    if (toPrintCheckbox && refField) {
        toPrintCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // When To Print is checked, reference is not needed
                refField.removeAttribute('required');
                refField.value = '';  // Clear the field
                refField.disabled = true;  // Disable it
            } else {
                // When To Print is unchecked, reference is required
                refField.disabled = false;  // Enable it
            }
        });
    }
});


function setupToPrintVisibility() {
    const typeField = document.getElementById('transaction_type');
    const toPrintContainer = document.getElementById('to-print-container'); // Container for "To Print" checkbox
    const toPrintCheckbox = document.getElementById('to_print');
    const refField = document.getElementById('transaction_ref');

    function toggleToPrintVisibility() {
        const transactionType = typeField.value;

        console.log('Toggle To Print visibility, type:', transactionType);

        // Only show "To Print" for WITHDRAWAL transactions
        if (transactionType === 'WITHDRAWAL') {
            if (toPrintContainer) {
                toPrintContainer.style.display = 'block';
                console.log('Showing To Print checkbox');
            }
        } else {
            if (toPrintContainer) {
                toPrintContainer.style.display = 'none';
                console.log('Hiding To Print checkbox');
            }
            // If hiding, also uncheck and clear the TO PRINT value
            if (toPrintCheckbox) {
                toPrintCheckbox.checked = false;
            }
            if (refField && refField.value === 'TO PRINT') {
                refField.value = '';
                refField.readOnly = false;
                refField.style.backgroundColor = '';
            }
        }
    }

    // Set initial visibility
    toggleToPrintVisibility();

    // Update visibility when transaction type changes
    typeField.addEventListener('change', toggleToPrintVisibility);
}

async function loadVendorList() {
    try {
        // Correct endpoint: /v1/vendors/
        const data = await api.get('/v1/vendors/');
        // API returns paginated results
        vendorList = data.results || data.vendors || [];
        // console.log('Loaded vendors:', vendorList.length);
    } catch (error) {
        // console.error('Error loading vendors:', error);
        vendorList = [];
    }
}

function setupPayeeAutocomplete() {
    const payeeField = document.getElementById('transaction_payee');
    const suggestions = document.getElementById('payee-suggestions');

    // Remove any existing listeners
    payeeField.removeEventListener('input', handlePayeeInput);
    payeeField.removeEventListener('focus', handlePayeeFocus);

    // Add input listener for autocomplete
    payeeField.addEventListener('input', handlePayeeInput);

    // Add focus listener to show 5 random vendors
    payeeField.addEventListener('focus', handlePayeeFocus);

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#transaction_payee') && !e.target.closest('#payee-suggestions')) {
            suggestions.style.display = 'none';
        }
    });
}

function handlePayeeFocus(e) {
    const payeeField = e.target;
    const suggestions = document.getElementById('payee-suggestions');

    // Only show random suggestions if field is empty
    if (!payeeField.value || payeeField.value.trim() === '') {
        showRandomVendors();
    }
}

function showRandomVendors() {
    const suggestions = document.getElementById('payee-suggestions');
    suggestions.innerHTML = '';

    if (vendorList.length === 0) {
        // Show "Add as new payee" option when no vendors exist
        const payeeField = document.getElementById('transaction_payee');
        const currentValue = payeeField ? payeeField.value.trim() : '';

        const addNewItem = document.createElement('a');
        addNewItem.className = 'dropdown-item add-new';
        addNewItem.href = '#';
        addNewItem.innerHTML = currentValue ?
            '<i class="fas fa-plus"></i> Add "' + currentValue + '" as new payee' :
            '<i class="fas fa-plus"></i> Add new payee';
        addNewItem.onclick = function(e) {
            e.preventDefault();
            suggestions.style.display = 'none';
            showAddPayeeModal(currentValue);
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
            document.getElementById('transaction_payee').value = vendor.vendor_name;
            validPayeeSelected = true; // Mark as valid when selected from list
            suggestions.style.display = 'none';
        };
        suggestions.appendChild(item);
    });

    // Add "Add new payee" option at the bottom
    const payeeField = document.getElementById('transaction_payee');
    const currentValue = payeeField ? payeeField.value.trim() : '';

    const addNewItem = document.createElement('a');
    addNewItem.className = 'dropdown-item add-new';
    addNewItem.href = '#';
    addNewItem.innerHTML = currentValue ?
        '<i class="fas fa-plus"></i> Add "' + currentValue + '" as new payee' :
        '<i class="fas fa-plus"></i> Add new payee';
    addNewItem.onclick = function(e) {
        e.preventDefault();
        suggestions.style.display = 'none';
        showAddPayeeModal(currentValue);
    };
    suggestions.appendChild(addNewItem);

    suggestions.style.display = 'block';
}

function handlePayeeInput(e) {
    const query = e.target.value;
    const queryLower = query.toLowerCase().trim();
    const suggestions = document.getElementById('payee-suggestions');

    // Mark payee as invalid when user types (will be revalidated on exact match or selection)
    validPayeeSelected = false;

    if (query.length < 1) {
        suggestions.style.display = 'none';
        return;
    }

    // Check for exact match (case-insensitive)
    const exactMatch = vendorList.find(vendor =>
        vendor.vendor_name && vendor.vendor_name.toLowerCase() === queryLower
    );

    if (exactMatch) {
        // Auto-fill with proper capitalization and mark as valid
        document.getElementById('transaction_payee').value = exactMatch.vendor_name;
        validPayeeSelected = true;
        suggestions.style.display = 'none';
        return;
    }

    // Filter vendors that match the query (alphabetical search)
    const matches = vendorList.filter(vendor =>
        vendor.vendor_name && vendor.vendor_name.toLowerCase().includes(queryLower)
    ).sort((a, b) => a.vendor_name.localeCompare(b.vendor_name)); // Sort alphabetically

    // Clear previous suggestions
    suggestions.innerHTML = '';

    if (matches.length > 0) {
        // Add matching vendors (alphabetically sorted)
        matches.forEach(vendor => {
            const item = document.createElement('a');
            item.className = 'dropdown-item';
            item.href = '#';
            item.textContent = vendor.vendor_name;
            item.onclick = function(e) {
                e.preventDefault();
                document.getElementById('transaction_payee').value = vendor.vendor_name;
                validPayeeSelected = true; // Mark as valid when selected from list
                suggestions.style.display = 'none';
            };
            suggestions.appendChild(item);
        });

        // Add "Add new payee" option at the bottom
        const addNewItem = document.createElement('a');
        addNewItem.className = 'dropdown-item add-new';
        addNewItem.href = '#';
        addNewItem.innerHTML = '<i class="fas fa-plus"></i> Add "' + query + '" as new payee';
        addNewItem.onclick = function(e) {
            e.preventDefault();
            suggestions.style.display = 'none';
            showAddPayeeModal(query);
        };
        suggestions.appendChild(addNewItem);

        suggestions.style.display = 'block';
    } else {
        // Show "Add as new payee" option when no matches
        const addNewItem = document.createElement('a');
        addNewItem.className = 'dropdown-item add-new';
        addNewItem.href = '#';
        addNewItem.innerHTML = '<i class="fas fa-plus"></i> Add "' + query + '" as new payee';
        addNewItem.onclick = function(e) {
            e.preventDefault();
            suggestions.style.display = 'none';
            showAddPayeeModal(query);
        };
        suggestions.appendChild(addNewItem);
        suggestions.style.display = 'block';
    }
}

function showAddPayeeModal(vendorName) {
    // Pre-fill vendor name
    const nameField = document.getElementById('payee_vendor_name');
    nameField.value = vendorName;
    // Only lock the field if a vendor name was provided
    if (vendorName && vendorName.trim() !== '') {
        nameField.readOnly = true;
        nameField.style.backgroundColor = '#e9ecef';
        nameField.style.color = '#495057';
        nameField.style.cursor = 'not-allowed';
    } else {
        // Unlock the field when opened from "+ Add new payee" button
        nameField.readOnly = false;
        nameField.style.backgroundColor = '';
        nameField.style.cursor = '';
    }

    // Reset other fields
    document.getElementById('payee_contact_person').value = '';
    document.getElementById('payee_phone').value = '';
    document.getElementById('payee_email').value = '';
    document.getElementById('payee_address').value = '';
    document.getElementById('payee_city').value = '';
    document.getElementById('payee_state').value = '';
    document.getElementById('payee_zip_code').value = '';

    // Setup zip code formatting (only 5 digits)
    const zipField = document.getElementById('payee_zip_code');
    zipField.addEventListener('input', function(e) {
        this.value = this.value.replace(/\D/g, '').substring(0, 5);
    });

    // Setup US phone number formatting
    const phoneField = document.getElementById('payee_phone');
    phoneField.addEventListener('input', function(e) {
        // Remove all non-digits
        let cleaned = this.value.replace(/\D/g, '');

        // Limit to 10 digits
        cleaned = cleaned.substring(0, 10);

        // Format as (XXX) XXX-XXXX
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

    // Track whether save was successful
    let saveSuccessful = false;

    // Setup save button
    document.getElementById('savePayeeBtn').onclick = async function() {
        const result = await saveNewPayee(vendorName);
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
            const payeeField = document.getElementById('transaction_payee');
            if (payeeField) {
                payeeField.value = '';
            }
        }
    }, { once: true }); // Use 'once' so it only fires for this modal instance
}

async function saveNewPayee(originalName) {
    const form = document.getElementById('payeeForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
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
            return;
        }
    }

    // Validate US phone format if provided
    if (vendorData.phone && vendorData.phone.trim() !== '') {
        // Remove all non-digits to check length
        const digitsOnly = vendorData.phone.replace(/\D/g, '');
        if (digitsOnly.length !== 10) {
            alert('Please enter a valid US phone number with 10 digits (e.g., (555) 123-4567)');
            return;
        }
    }

    try {
        // Show loading
        const saveBtn = document.getElementById('savePayeeBtn');
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

        // Submit to API - correct endpoint
        const response = await api.post('/v1/vendors/', vendorData);

        // Success - update payee field
        document.getElementById('transaction_payee').value = vendorData.vendor_name;
        validPayeeSelected = true; // Mark as valid after successful vendor creation

        // Add to vendor list
        vendorList.push({
            id: response.id,
            vendor_name: vendorData.vendor_name
        });

        // Close modal
        const modalEl = document.getElementById('addPayeeModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        // Show success notification after modal is fully hidden
        setTimeout(() => {
            showSuccessNotification('Vendor added successfully!');
        }, 300);

        // Reset button
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;

        // Return success
        return true;

    } catch (error) {
        // console.error('Error saving payee:', error);
        // alert('Error saving payee: ' + (error.message || 'Please try again'));

        // Restore button
        const saveBtn = document.getElementById('savePayeeBtn');
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Payee';

        // Return failure
        return false;
    }
}

// Clear payee field when modal is cancelled
document.addEventListener('DOMContentLoaded', function() {
    const payeeModal = document.getElementById('addPayeeModal');
    if (payeeModal) {
        payeeModal.addEventListener('hidden.bs.modal', function() {
            // Only clear if vendor name was pre-filled (readonly)
            const nameField = document.getElementById('payee_vendor_name');
    nameField.value = vendorName;
            if (nameField && nameField.readOnly) {
                // Reset readonly state
                nameField.readOnly = false;
                nameField.style.backgroundColor = '';
                nameField.style.cursor = '';
            }
        });
    }
});

// Flag to prevent duplicate submissions
let isSubmittingCaseTransaction = false;

async function submitTransaction() {
    // Prevent duplicate submissions
    if (isSubmittingCaseTransaction) {
        console.log('Transaction already being submitted, ignoring duplicate call');
        return;
    }

    isSubmittingCaseTransaction = true;

    // console.log('=== submitTransaction called ===');
    const form = document.getElementById('transactionForm');
    // console.log('Form element:', form);

    // Validate form
    if (!form.checkValidity()) {
        // console.log('Form validation failed');
        form.reportValidity();
        isSubmittingCaseTransaction = false;
        return;
    }
    // console.log('Form validation passed');

    // Validate amount
    const amountField = document.getElementById('transaction_amount');
    const typeField = document.getElementById('transaction_type');
    const amount = parseFloat(amountField.value.replace(/[^\d.]/g, ''));
    const transactionId = document.getElementById('transaction_id').value;

    if (typeField.value === 'WITHDRAWAL' && !transactionId) {
        // Only validate available funds for NEW withdrawals (not edits)
        const availableFundsText = document.getElementById('available-funds').textContent;
        const availableFunds = parseFloat(availableFundsText.replace(/[^\d.-]/g, '')) || 0;

        if (availableFunds < 0 || amount > availableFunds) {
            // Show toast notification for insufficient funds
            const formattedBalance = availableFunds.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            const formattedAmount = amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            showErrorMessage(`Insufficient funds. Case balance: $${formattedBalance}. Cannot withdraw $${formattedAmount}.`);
            isSubmittingCaseTransaction = false;
            return;
        }
    }

    // Check To Print checkbox and set reference_number accordingly
    const toPrintCheckbox = document.getElementById('to_print');
    let referenceNumber = document.getElementById('transaction_ref').value;

    console.log('=== SUBMIT TRANSACTION DEBUG ===');
    console.log('To Print checkbox exists:', !!toPrintCheckbox);
    console.log('To Print checkbox checked:', toPrintCheckbox ? toPrintCheckbox.checked : 'N/A');
    console.log('Reference field value:', referenceNumber);
    console.log('Transaction type:', typeField.value);

    // If To Print is checked, set reference to TO PRINT
    if (toPrintCheckbox && toPrintCheckbox.checked) {
        referenceNumber = 'TO PRINT';
        console.log('Checkbox is checked, setting reference to TO PRINT');
    } else if (typeField.value === 'WITHDRAWAL' && !referenceNumber) {
        // If withdrawal and not To Print, reference is required
        console.log('Validation failed: withdrawal requires reference or To Print checkbox');
        showErrorMessage('Please enter a Reference Number or check "To Print"');
        isSubmittingCaseTransaction = false;
        return;
    }

    console.log('Final reference number:', referenceNumber);

    // REQUIREMENT: Validate that payee is from valid vendor list (not random string)
    const payeeValue = document.getElementById('transaction_payee').value;
    if (!payeeValue || payeeValue.trim() === '') {
        showErrorMessage('Please enter a Payee before saving the transaction.');
        isSubmittingCaseTransaction = false;
        return;
    }

    if (!validPayeeSelected) {
        showErrorMessage('Please select a valid Payee from the list or click "Add as new payee" to create one.');
        isSubmittingCaseTransaction = false;
        return;
    }

    // Prepare data - use hidden IDs for client/case
    const transactionData = {
        bank_account: document.getElementById('transaction_bank_account').value,
        client: document.getElementById('transaction_client_id').value,
        case: document.getElementById('transaction_case_id').value,
        transaction_date: document.getElementById('transaction_date').value,
        transaction_type: typeField.value,
        reference_number: referenceNumber,
        payee: document.getElementById('transaction_payee').value,
        amount: amount,
        description: document.getElementById('transaction_description').value,
        check_memo: document.getElementById('transaction_memo').value || '',
        status: 'pending'
    };

    console.log('Transaction data being sent:', JSON.stringify(transactionData, null, 2));

    try {
        // Show loading state
        const saveBtn = document.getElementById('saveTransactionBtn');
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

        // Check if editing or creating
        const editTransactionId = document.getElementById('transaction_id').value;
        let response;

        // console.log('Submitting transaction:', { editTransactionId, transactionData });

        if (editTransactionId) {
            // Edit existing transaction
            // console.log(`Updating transaction ${editTransactionId}`);
            response = await api.put(`/v1/bank-accounts/bank-transactions/${editTransactionId}/`, transactionData);
        } else {
            // Create new transaction
            // console.log('Creating new transaction');
            response = await api.post('/v1/bank-accounts/bank-transactions/', transactionData);
        }

        // BUG #25 FIX: Reset button state before closing modal
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;

        // Close modal
        const modalEl = document.getElementById('transactionModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        // BUG #25 FIX: Clear form for next transaction
        document.getElementById('transactionForm').reset();
        document.getElementById('transaction_id').value = '';

        // Show success message (only ONE message)
        const transactionType = transactionData.transaction_type === 'DEPOSIT' ? 'Deposit' : 'Withdrawal';
        const action = editTransactionId ? 'updated' : 'added';
        showSuccessMessage(`${transactionType} transaction ${action} successfully!`);

        // Reload transactions and case details
        await loadCaseDetails();
        await loadTransactions();

        // Reset submission flag
        isSubmittingCaseTransaction = false;

    } catch (error) {
        console.error('Error saving transaction:', error);

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

        // Restore button
        const saveBtn = document.getElementById('saveTransactionBtn');
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Transaction';

        // Reset submission flag
        isSubmittingCaseTransaction = false;
    }
}

function printCaseLedger() {
    // Open case ledger PDF in new window with grey Chrome toolbar
    window.open(`/clients/cases/${caseId}/print/`, '_blank');
}

// Success/Error toast message functions (matching bank-transactions.js)
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

// Edit case from case detail page
async function editCaseFromDetail() {
    console.log('========================================');
    console.log('🔧 EDIT CASE FROM DETAIL - Function Called');
    console.log('Current caseId variable:', caseId);
    console.log('========================================');

    if (!caseId) {
        console.error('❌ ERROR: Case ID not found!');
        showErrorMessage('Case ID not found');
        return;
    }

    try {
        console.log('📡 Fetching case data from API for case:', caseId);
        // Fetch case data from API
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
        console.log('📝 Populating form fields...');
        console.log('Looking for element: edit_case_id');
        const editCaseIdEl = document.getElementById('edit_case_id');
        console.log('Element found:', editCaseIdEl ? 'YES' : 'NO');

        document.getElementById('edit_case_id').value = caseData.id;
        document.getElementById('edit_case_client').value = caseData.client;
        document.getElementById('edit_case_title').value = caseData.case_title || '';
        document.getElementById('edit_case_description').value = caseData.case_description || '';
        document.getElementById('edit_case_status').value = caseData.case_status || 'Open';
        document.getElementById('edit_case_amount').value = caseData.case_amount || '';
        // BUG #23 FIX: Include date fields so closed cases can be edited
        document.getElementById('edit_case_opened_date').value = caseData.opened_date || '';
        document.getElementById('edit_case_closed_date').value = caseData.closed_date || '';
        console.log('✅ All form fields populated');

        // Show modal
        console.log('🎭 Looking for modal element: caseEditModal');
        const modalEl = document.getElementById('caseEditModal');
        console.log('Modal element found:', modalEl ? 'YES' : 'NO');

        if (!modalEl) {
            console.error('❌ MODAL ELEMENT NOT FOUND IN DOM!');
            alert('Error: Modal element not found in page');
            return;
        }

        console.log('🚀 Creating Bootstrap modal instance...');
        const modal = new bootstrap.Modal(modalEl);
        console.log('📣 Showing modal...');
        modal.show();
        console.log('✅ Modal.show() called successfully');

    } catch (error) {
        console.error('Error loading case:', error);
        showErrorMessage('Error loading case: ' + error.message);
    }
}

// Save case edits
async function saveCaseEdits() {
    const caseIdToSave = document.getElementById('edit_case_id').value;

    // BUG #23 FIX: Include all fields including dates for proper validation
    const formData = {
        client: document.getElementById('edit_case_client').value,
        case_title: document.getElementById('edit_case_title').value,
        case_description: document.getElementById('edit_case_description').value,
        case_status: document.getElementById('edit_case_status').value,
        case_amount: document.getElementById('edit_case_amount').value || null,
        opened_date: document.getElementById('edit_case_opened_date').value || null,
        closed_date: document.getElementById('edit_case_closed_date').value || null,
    };

    console.log('Saving case:', caseIdToSave, formData);

    try {
        // Get CSRF token
        const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

        const response = await fetch(`/api/v1/cases/${caseIdToSave}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const error = new Error('Failed to update case');
            error.validationErrors = errorData;
            throw error;
        }

        // Close modal
        const modalEl = document.getElementById('caseEditModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal.hide();

        // Show success message
        showSuccessMessage('Case updated successfully!');

        // Reload case details and transactions
        await loadCaseDetails();
        await loadTransactions();

    } catch (error) {
        console.error('Error saving case:', error);

        // BUG #23 FIX: Properly display validation errors when editing closed cases
        if (error.validationErrors) {
            let errorMessage = 'Please fix the following errors:\n\n';
            const errors = error.validationErrors;

            for (const [field, messages] of Object.entries(errors)) {
                const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                const message = Array.isArray(messages) ? messages[0] : messages;
                errorMessage += `• ${fieldName}: ${message}\n`;
            }

            alert(errorMessage);
        } else {
            showErrorMessage('Error saving case: ' + error.message);
        }
    }
}
