// Populate outstanding checks
function populateOutstandingChecks(checks) {
    const checksTable = document.getElementById('outstandingChecksTable');

    document.getElementById('outstandingChecksBadge').textContent = checks.length;

    if (checks.length === 0) {
        checksTable.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No outstanding checks over 90 days</td></tr>';
    } else {
        checksTable.innerHTML = checks.map(check => `
            <tr>
                <td>${check.check_number}</td>
                <td>${check.date_issued}</td>
                <td>${check.client_name}</td>
                <td>${check.payee}</td>
                <td><small>${check.description || ''}</small></td>
                <td><span class="text-dark">(${formatCurrency(check.amount).replace('$', '')})</span></td>
                <td><span class="badge bg-danger">${check.days_outstanding} days</span></td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary btn-sm" onclick="editTransaction(${check.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-warning btn-sm" onclick="reissueCheck(${check.id}, '${check.check_number}')" title="Reissue">
                            <i class="fas fa-redo"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="voidCheck(${check.id}, '${check.check_number}')" title="Void">
                            <i class="fas fa-ban"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

// Edit transaction - redirect to bank transactions page with transaction ID
function editTransaction(transactionId) {
    // Get the bank account ID (assume first/only account for now)
    window.location.href = `/bank-transactions?account_id=1&edit=${transactionId}`;
}

// Reissue check
async function reissueCheck(transactionId, checkNumber) {
    if (!confirm(`Reissue check #${checkNumber}?\n\nThis will:\n1. Void the current check\n2. Create a new check with a new check number`)) {
        return;
    }

    try {
        const response = await api.post(`/api/v1/bank-accounts/transactions/${transactionId}/reissue/`, {});

        if (response.success) {
            showSuccessMessage(`Check #${checkNumber} reissued successfully. New check #${response.new_check_number}`);
            // Reload dashboard
            loadDashboard();
        }
    } catch (error) {
        showErrorMessage(error.message || 'Failed to reissue check');
    }
}

// Void check
async function voidCheck(transactionId, checkNumber) {
    const reason = prompt(`Void check #${checkNumber}?\n\nPlease enter the reason for voiding:`);

    if (!reason) {
        return; // User cancelled
    }

    try {
        const response = await api.post(`/api/v1/bank-accounts/transactions/${transactionId}/void/`, {
            void_reason: reason
        });

        if (response.success) {
            showSuccessMessage(`Check #${checkNumber} voided successfully`);
            // Reload dashboard
            loadDashboard();
        }
    } catch (error) {
        showErrorMessage(error.message || 'Failed to void check');
    }
}
