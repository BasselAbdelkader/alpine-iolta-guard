// Populate outstanding checks
function populateOutstandingChecks(checks) {
    const checksTable = document.getElementById('outstandingChecksTable');

    document.getElementById('outstandingChecksBadge').textContent = checks.length;

    if (checks.length === 0) {
        checksTable.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No outstanding checks over 90 days</td></tr>';
    } else {
        // Clear table first
        checksTable.innerHTML = '';

        // Build rows safely to prevent XSS
        checks.forEach(check => {
            const row = document.createElement('tr');

            // Create cells with safe text content
            const cells = [
                check.reference_number || '',
                check.date_issued || '',
                check.client_name || '',
                check.payee || '',
                check.description || '',
                `(${formatCurrency(check.amount).replace('$', '')})`,
                `${check.days_outstanding} days`
            ];

            // Add text cells safely
            cells.forEach((content, index) => {
                const cell = document.createElement('td');
                if (index === 4) { // Description cell
                    const small = document.createElement('small');
                    small.textContent = content;
                    cell.appendChild(small);
                } else if (index === 5) { // Amount cell
                    const span = document.createElement('span');
                    span.className = 'text-dark';
                    span.textContent = content;
                    cell.appendChild(span);
                } else if (index === 6) { // Days cell
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-danger';
                    badge.textContent = content;
                    cell.appendChild(badge);
                } else {
                    cell.textContent = content;
                }
                row.appendChild(cell);
            });

            // Add action buttons cell
            const actionCell = document.createElement('td');
            const btnGroup = document.createElement('div');
            btnGroup.className = 'btn-group btn-group-sm';
            btnGroup.setAttribute('role', 'group');

            // Edit button
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-outline-primary btn-sm';
            editBtn.setAttribute('title', 'Edit');
            editBtn.onclick = () => editTransaction(check.id);
            editBtn.innerHTML = '<i class="fas fa-edit"></i>';

            // Reissue button
            const reissueBtn = document.createElement('button');
            reissueBtn.className = 'btn btn-outline-warning btn-sm';
            reissueBtn.setAttribute('title', 'Reissue');
            reissueBtn.onclick = () => reissueCheck(check.id, check.reference_number);
            reissueBtn.innerHTML = '<i class="fas fa-redo"></i>';

            // Void button
            const voidBtn = document.createElement('button');
            voidBtn.className = 'btn btn-outline-danger btn-sm';
            voidBtn.setAttribute('title', 'Void');
            voidBtn.onclick = () => voidCheck(check.id, check.reference_number);
            voidBtn.innerHTML = '<i class="fas fa-ban"></i>';

            btnGroup.appendChild(editBtn);
            btnGroup.appendChild(reissueBtn);
            btnGroup.appendChild(voidBtn);
            actionCell.appendChild(btnGroup);
            row.appendChild(actionCell);

            checksTable.appendChild(row);
        });
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
            showSuccessMessage(`Check #${checkNumber} reissued successfully. New check #${response.new_reference_number}`);
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
