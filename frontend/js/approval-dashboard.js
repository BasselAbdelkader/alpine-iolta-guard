/**
 * Approval Dashboard Main Logic
 *
 * COMPLIANCE CONTROL #3: Two-Person Approval Workflow
 *
 * Features:
 * - Tabbed interface (Pending, My Requests, History)
 * - Approval detail modal
 * - Approve/Reject actions with confirmation
 * - Real-time updates
 * - Pagination support
 *
 * Usage:
 * - Include this script on approval-dashboard.html
 * - Requires Bootstrap 5 for modals and tabs
 */

class ApprovalDashboard {
    constructor() {
        this.currentTab = 'pending';
        this.currentPage = 1;
        this.canApprove = false;
        this.isLoading = false;

        this.init();
    }

    async init() {
        console.log('Initializing approval dashboard...');

        // Check if user has approval permission
        await this.checkPermission();

        // Load pending approvals
        await this.loadPendingApprovals();

        // Set up tab change handlers
        this.setupTabHandlers();

        // Set up history filter
        this.setupHistoryFilter();

        // Auto-refresh every 2 minutes (only for pending tab)
        setInterval(() => {
            if (this.currentTab === 'pending' && !this.isLoading) {
                this.loadPendingApprovals();
            }
        }, 120000);
    }

    setupTabHandlers() {
        document.querySelectorAll('#approvalTabs a[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const tabId = e.target.getAttribute('href').substring(1);
                this.currentTab = tabId;
                this.currentPage = 1;
                this.loadTabContent();
            });
        });
    }

    setupHistoryFilter() {
        const filter = document.getElementById('historyFilter');
        if (filter) {
            filter.addEventListener('change', () => {
                this.currentPage = 1;
                this.loadHistory();
            });
        }
    }

    async checkPermission() {
        try {
            const response = await fetch('/api/v1/bank-accounts/approvals/pending_count/', {
                credentials: 'include'
            });

            this.canApprove = response.ok;
        } catch (error) {
            this.canApprove = false;
        }
    }

    async loadTabContent() {
        switch (this.currentTab) {
            case 'pending':
                await this.loadPendingApprovals(this.currentPage);
                break;
            case 'my-requests':
                await this.loadMyRequests(this.currentPage);
                break;
            case 'history':
                await this.loadHistory(this.currentPage);
                break;
        }
    }

    async loadPendingApprovals(page = 1) {
        if (this.isLoading) return;

        const container = document.getElementById('pendingApprovalsContainer');
        if (!container) return;

        this.isLoading = true;
        container.innerHTML = this.renderLoading();

        try {
            const response = await fetch(
                `/api/v1/bank-accounts/approvals/pending/?page=${page}`,
                { credentials: 'include' }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.renderPendingApprovals(data);
            this.updateCounts(data.count);
        } catch (error) {
            console.error('Error loading pending approvals:', error);
            this.renderError(container, 'Failed to load pending approvals');
        } finally {
            this.isLoading = false;
        }
    }

    async loadMyRequests(page = 1) {
        if (this.isLoading) return;

        const container = document.getElementById('myRequestsContainer');
        if (!container) return;

        this.isLoading = true;
        container.innerHTML = this.renderLoading();

        try {
            const response = await fetch(
                `/api/v1/bank-accounts/approvals/my-requests/?page=${page}`,
                { credentials: 'include' }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.renderMyRequests(data);
        } catch (error) {
            console.error('Error loading my requests:', error);
            this.renderError(container, 'Failed to load your requests');
        } finally {
            this.isLoading = false;
        }
    }

    async loadHistory(page = 1) {
        if (this.isLoading) return;

        const container = document.getElementById('historyContainer');
        if (!container) return;

        this.isLoading = true;
        container.innerHTML = this.renderLoading();

        try {
            const filter = document.getElementById('historyFilter')?.value || '';
            let url = `/api/v1/bank-accounts/approvals/history/?page=${page}`;
            if (filter) {
                url += `&status=${filter}`;
            }

            const response = await fetch(url, { credentials: 'include' });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.renderHistory(data);
        } catch (error) {
            console.error('Error loading history:', error);
            this.renderError(container, 'Failed to load approval history');
        } finally {
            this.isLoading = false;
        }
    }

    renderPendingApprovals(data) {
        const container = document.getElementById('pendingApprovalsContainer');
        const approvals = data.results || [];

        if (approvals.length === 0) {
            container.innerHTML = this.renderEmptyState(
                'check-circle-fill',
                'No Pending Approvals',
                'All transactions have been reviewed'
            );
            return;
        }

        const html = approvals.map(approval => this.renderApprovalCard(approval)).join('');
        container.innerHTML = html + this.renderPagination(data);
    }

    renderApprovalCard(approval) {
        const amount = Number(approval.transaction_amount);
        const urgencyClass = approval.days_pending > 2 ? 'urgency-danger' :
                            approval.days_pending > 1 ? 'urgency-warning' : 'urgency-normal';

        const daysClass = approval.days_pending > 2 ? 'days-pending-danger' :
                         approval.days_pending > 1 ? 'days-pending-warning' : 'days-pending-normal';

        return `
            <div class="card approval-card ${urgencyClass} mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h5 class="card-title">
                                ${approval.transaction_number}
                                <span class="badge bg-danger ms-2 text-amount">
                                    $${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                </span>
                            </h5>
                            <p class="card-text">
                                <strong><i class="bi bi-person approval-icon"></i>Client:</strong> ${approval.client_name}<br>
                                <strong><i class="bi bi-briefcase approval-icon"></i>Case:</strong> ${approval.case_number}<br>
                                <strong><i class="bi bi-wallet approval-icon"></i>Payee:</strong> ${approval.payee}<br>
                                <strong><i class="bi bi-arrow-left-right approval-icon"></i>Type:</strong> ${approval.transaction_type}<br>
                                <strong><i class="bi bi-calendar approval-icon"></i>Date:</strong> ${approval.transaction_date}<br>
                                <strong><i class="bi bi-person-badge approval-icon"></i>Requested by:</strong> ${approval.created_by_name}
                                <span class="approval-timestamp">(${this.formatDate(approval.created_at)})</span>
                            </p>
                            ${approval.request_notes ? `
                                <p class="card-text">
                                    <small class="text-muted">
                                        <i class="bi bi-sticky approval-icon"></i>
                                        <em>${approval.request_notes}</em>
                                    </small>
                                </p>
                            ` : ''}
                        </div>
                        <div class="col-md-4">
                            <div class="approval-actions">
                                <div class="mb-3">
                                    <span class="badge ${daysClass} w-100">
                                        <i class="bi bi-clock"></i>
                                        ${approval.days_pending} day${approval.days_pending !== 1 ? 's' : ''} pending
                                    </span>
                                </div>
                                <button class="btn btn-sm btn-outline-primary w-100 mb-2" onclick="approvalDashboard.viewDetails(${approval.id})">
                                    <i class="bi bi-eye"></i>
                                    View Details
                                </button>
                                ${approval.can_approve ? `
                                    <button class="btn btn-sm btn-success w-100 mb-2" onclick="approvalDashboard.showApproveDialog(${approval.id})">
                                        <i class="bi bi-check-circle"></i>
                                        Approve
                                    </button>
                                    <button class="btn btn-sm btn-danger w-100" onclick="approvalDashboard.showRejectDialog(${approval.id})">
                                        <i class="bi bi-x-circle"></i>
                                        Reject
                                    </button>
                                ` : `
                                    <div class="alert alert-warning py-2 mb-0">
                                        <small><i class="bi bi-shield-x"></i> Cannot approve own request</small>
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderMyRequests(data) {
        const container = document.getElementById('myRequestsContainer');
        const requests = data.results || [];

        if (requests.length === 0) {
            container.innerHTML = this.renderEmptyState(
                'inbox',
                'No Requests',
                'You have not created any approval requests'
            );
            return;
        }

        const html = requests.map(approval => {
            const amount = Number(approval.transaction_amount);
            const statusBadgeClass = approval.status === 'approved' ? 'bg-success' :
                                    approval.status === 'rejected' ? 'bg-danger' : 'bg-warning text-dark';

            return `
                <div class="card approval-card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-9">
                                <h5 class="card-title">
                                    ${approval.transaction_number}
                                    <span class="badge ${statusBadgeClass} ms-2">
                                        ${approval.status_display}
                                    </span>
                                    <span class="badge bg-info text-dark ms-1 text-amount">
                                        $${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                    </span>
                                </h5>
                                <p class="card-text mb-0">
                                    <strong><i class="bi bi-person approval-icon"></i>Client:</strong> ${approval.client_name}<br>
                                    <strong><i class="bi bi-calendar approval-icon"></i>Created:</strong> ${this.formatDate(approval.created_at)}
                                    ${approval.reviewed_by_name ? `<br><strong><i class="bi bi-person-check approval-icon"></i>Reviewed by:</strong> ${approval.reviewed_by_name} (${this.formatDate(approval.reviewed_at)})` : ''}
                                </p>
                            </div>
                            <div class="col-md-3 text-end">
                                <button class="btn btn-sm btn-outline-primary w-100" onclick="approvalDashboard.viewDetails(${approval.id})">
                                    <i class="bi bi-eye"></i>
                                    View Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html + this.renderPagination(data);
    }

    renderHistory(data) {
        const container = document.getElementById('historyContainer');
        const items = data.results || [];

        if (items.length === 0) {
            container.innerHTML = this.renderEmptyState(
                'clock-history',
                'No History',
                'No approval history to display'
            );
            return;
        }

        // Group by date
        const grouped = {};
        items.forEach(item => {
            const date = new Date(item.reviewed_at).toLocaleDateString();
            if (!grouped[date]) grouped[date] = [];
            grouped[date].push(item);
        });

        let html = '';
        Object.keys(grouped).forEach(date => {
            html += `<div class="history-date-header"><i class="bi bi-calendar3"></i> ${date}</div>`;
            grouped[date].forEach(approval => {
                const amount = Number(approval.transaction_amount);
                const statusBadge = approval.status === 'approved' ?
                    '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Approved</span>' :
                    '<span class="badge bg-danger"><i class="bi bi-x-circle"></i> Rejected</span>';

                html += `
                    <div class="card history-item mb-2">
                        <div class="card-body py-2">
                            <div class="row align-items-center">
                                <div class="col-auto">
                                    ${statusBadge}
                                </div>
                                <div class="col">
                                    <strong>${approval.transaction_number}</strong>
                                    <span class="ms-2 text-amount">$${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                                    <small class="text-muted ms-2"><i class="bi bi-person"></i> ${approval.client_name}</small>
                                </div>
                                <div class="col-auto">
                                    <small class="text-muted approval-user">
                                        <i class="bi bi-person-check"></i>
                                        by ${approval.reviewed_by_name}
                                    </small>
                                </div>
                                <div class="col-auto">
                                    <button class="btn btn-sm btn-outline-secondary" onclick="approvalDashboard.viewDetails(${approval.id})">
                                        <i class="bi bi-eye"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        });

        container.innerHTML = html + this.renderPagination(data);
    }

    renderPagination(data) {
        if (!data.total_pages || data.total_pages <= 1) return '';

        let html = '<nav class="approval-pagination"><ul class="pagination justify-content-center mt-4">';

        // Previous button
        html += `
            <li class="page-item ${data.previous ? '' : 'disabled'}">
                <a class="page-link" href="#" onclick="approvalDashboard.loadPage(${data.current_page - 1}); return false;">
                    <i class="bi bi-chevron-left"></i> Previous
                </a>
            </li>
        `;

        // Page numbers (show max 5 pages)
        const startPage = Math.max(1, data.current_page - 2);
        const endPage = Math.min(data.total_pages, startPage + 4);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === data.current_page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="approvalDashboard.loadPage(${i}); return false;">${i}</a>
                </li>
            `;
        }

        // Next button
        html += `
            <li class="page-item ${data.next ? '' : 'disabled'}">
                <a class="page-link" href="#" onclick="approvalDashboard.loadPage(${data.current_page + 1}); return false;">
                    Next <i class="bi bi-chevron-right"></i>
                </a>
            </li>
        `;

        html += '</ul></nav>';
        return html;
    }

    renderLoading() {
        return `
            <div class="approval-loading">
                <i class="bi bi-hourglass-split"></i>
                <p class="mt-3">Loading...</p>
            </div>
        `;
    }

    renderEmptyState(icon, title, message) {
        return `
            <div class="approval-empty-state">
                <i class="bi bi-${icon}"></i>
                <h5>${title}</h5>
                <p>${message}</p>
            </div>
        `;
    }

    renderError(container, message) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                ${message}. Please refresh the page or try again later.
            </div>
        `;
    }

    loadPage(page) {
        this.currentPage = page;
        this.loadTabContent();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async viewDetails(approvalId) {
        try {
            const response = await fetch(
                `/api/v1/bank-accounts/approvals/${approvalId}/`,
                { credentials: 'include' }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const approval = await response.json();
            this.showDetailModal(approval);
        } catch (error) {
            console.error('Error loading approval details:', error);
            alert('Error loading approval details. Please try again.');
        }
    }

    showDetailModal(approval) {
        const modal = document.getElementById('approvalModal');
        const body = document.getElementById('approvalModalBody');
        const footer = document.getElementById('approvalModalFooter');

        if (!modal || !body || !footer) {
            console.error('Modal elements not found');
            return;
        }

        const amount = Number(approval.transaction.amount);
        const statusBadgeClass = approval.status === 'approved' ? 'bg-success' :
                                approval.status === 'rejected' ? 'bg-danger' : 'approval-status-pending';

        body.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="approval-detail-section">
                        <h6><i class="bi bi-receipt"></i> Transaction Details</h6>
                        <table class="table table-sm table-borderless">
                            <tr><th>Number:</th><td>${approval.transaction.transaction_number}</td></tr>
                            <tr><th>Type:</th><td>${approval.transaction.transaction_type}</td></tr>
                            <tr><th>Amount:</th><td class="text-danger fw-bold text-amount">$${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td></tr>
                            <tr><th>Date:</th><td>${approval.transaction.transaction_date}</td></tr>
                            <tr><th>Payee:</th><td>${approval.transaction.payee}</td></tr>
                            <tr><th>Reference:</th><td>${approval.transaction.reference_number}</td></tr>
                            <tr><th>Description:</th><td>${approval.transaction.description}</td></tr>
                        </table>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="approval-detail-section">
                        <h6><i class="bi bi-shield-check"></i> Approval Details</h6>
                        <table class="table table-sm table-borderless">
                            <tr><th>Status:</th><td><span class="badge ${statusBadgeClass}">${approval.status_display}</span></td></tr>
                            <tr><th>Client:</th><td>${approval.transaction.client_name}</td></tr>
                            <tr><th>Case:</th><td>${approval.transaction.case_number}</td></tr>
                            <tr><th>Created by:</th><td>${approval.created_by.full_name || approval.created_by.username}</td></tr>
                            <tr><th>Created at:</th><td>${this.formatDate(approval.created_at)}</td></tr>
                            ${approval.reviewed_by ? `
                                <tr><th>Reviewed by:</th><td>${approval.reviewed_by.full_name || approval.reviewed_by.username}</td></tr>
                                <tr><th>Reviewed at:</th><td>${this.formatDate(approval.reviewed_at)}</td></tr>
                            ` : ''}
                        </table>
                        ${approval.status === 'pending' && approval.days_pending !== null ? `
                            <div class="alert alert-warning">
                                <i class="bi bi-clock"></i>
                                Pending for ${approval.days_pending} day${approval.days_pending !== 1 ? 's' : ''}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
            <div class="approval-divider"></div>
            <div class="row">
                <div class="col-12">
                    <h6><i class="bi bi-sticky"></i> Request Notes</h6>
                    <div class="approval-notes">${approval.request_notes || 'No notes provided'}</div>
                </div>
                ${approval.review_notes ? `
                    <div class="col-12 mt-3">
                        <h6><i class="bi bi-chat-left-text"></i> Review Notes</h6>
                        <div class="approval-notes">${approval.review_notes}</div>
                    </div>
                ` : ''}
            </div>
        `;

        footer.innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="bi bi-x-lg"></i>
                Close
            </button>
            ${approval.status === 'pending' && approval.can_approve ? `
                <button type="button" class="btn btn-success" onclick="approvalDashboard.showApproveDialog(${approval.id})" data-bs-dismiss="modal">
                    <i class="bi bi-check-circle"></i>
                    Approve
                </button>
                <button type="button" class="btn btn-danger" onclick="approvalDashboard.showRejectDialog(${approval.id})" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle"></i>
                    Reject
                </button>
            ` : ''}
        `;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    showApproveDialog(approvalId) {
        const notes = prompt('Optional approval notes:\n\nEnter reason for approval (or leave blank):');

        if (notes !== null) {
            this.approveTransaction(approvalId, notes || 'Approved');
        }
    }

    showRejectDialog(approvalId) {
        const notes = prompt('⚠️ REQUIRED: Rejection reason\n\nEnter detailed reason for rejecting this transaction:');

        if (notes && notes.trim()) {
            if (confirm('⚠️ Are you sure you want to REJECT this transaction?\n\nThis will void the transaction permanently and cannot be undone.')) {
                this.rejectTransaction(approvalId, notes.trim());
            }
        } else if (notes !== null) {
            alert('❌ Rejection reason is required. Transaction was not rejected.');
        }
    }

    async approveTransaction(approvalId, notes) {
        try {
            const response = await fetch(
                `/api/v1/bank-accounts/approvals/${approvalId}/approve/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ review_notes: notes })
                }
            );

            const data = await response.json();

            if (response.ok) {
                alert('✅ ' + data.message + '\n\nThe transaction has been approved and will now affect the client balance.');
                this.loadTabContent(); // Refresh current tab
            } else {
                alert('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error approving transaction:', error);
            alert('❌ Error approving transaction. Please try again.');
        }
    }

    async rejectTransaction(approvalId, notes) {
        try {
            const response = await fetch(
                `/api/v1/bank-accounts/approvals/${approvalId}/reject/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ review_notes: notes })
                }
            );

            const data = await response.json();

            if (response.ok) {
                alert('✅ ' + data.message + '\n\nThe transaction has been voided and will not affect the client balance.');
                this.loadTabContent(); // Refresh current tab
            } else {
                alert('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error rejecting transaction:', error);
            alert('❌ Error rejecting transaction. Please try again.');
        }
    }

    updateCounts(count) {
        const totalCount = document.getElementById('totalPendingCount');
        const tabCount = document.getElementById('pendingTabCount');

        if (totalCount) totalCount.textContent = count;
        if (tabCount) tabCount.textContent = count;
    }

    formatDate(dateString) {
        if (!dateString) return '';

        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Global instance
let approvalDashboard;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    approvalDashboard = new ApprovalDashboard();
});
