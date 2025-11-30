/**
 * Dashboard Approval Widget
 *
 * COMPLIANCE CONTROL #3: Two-Person Approval Workflow
 *
 * Shows top 3 pending approvals on main dashboard
 * Updates every 2 minutes
 *
 * Usage:
 * - Include this script on dashboard.html
 * - Requires div with id="approvalWidgetBody"
 * - Requires span with id="widgetPendingCount"
 */

class ApprovalWidget {
    constructor() {
        this.countBadge = document.getElementById('widgetPendingCount');
        this.body = document.getElementById('approvalWidgetBody');

        // Don't initialize if elements don't exist
        if (!this.countBadge || !this.body) {
            console.log('Approval widget elements not found - skipping initialization');
            return;
        }

        this.init();
    }

    async init() {
        console.log('Initializing approval widget...');

        // Initial load
        await this.loadPendingApprovals();

        // Refresh every 2 minutes
        setInterval(() => this.loadPendingApprovals(), 120000);
    }

    async loadPendingApprovals() {
        try {
            const response = await fetch('/api/v1/bank-accounts/approvals/pending/?page_size=3', {
                credentials: 'include',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Not authenticated
                    this.renderError('Authentication required');
                    return;
                }
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.renderApprovals(data);
        } catch (error) {
            console.error('Error loading approvals:', error);
            this.renderError('Error loading approvals');
        }
    }

    renderApprovals(data) {
        const count = data.count || 0;
        const approvals = data.results || [];

        // Update count badge
        this.countBadge.textContent = count;

        if (approvals.length === 0) {
            this.body.innerHTML = `
                <p class="text-muted text-center mb-0 py-3">
                    <i class="bi bi-check-circle text-success" style="font-size: 2rem;"></i>
                    <br>
                    <small>No pending approvals</small>
                </p>
            `;
            return;
        }

        // Render approval list (top 3)
        const html = approvals.map(approval => this.renderApprovalItem(approval)).join('');

        this.body.innerHTML = html;

        // Show "and X more" if count > 3
        if (count > 3) {
            this.body.innerHTML += `
                <p class="text-center mb-0 mt-2">
                    <small class="text-muted">and ${count - 3} more...</small>
                </p>
            `;
        }
    }

    renderApprovalItem(approval) {
        const amount = Number(approval.transaction_amount);
        const daysClass = approval.days_pending > 2 ? 'bg-danger' :
                         approval.days_pending > 1 ? 'bg-warning text-dark' : 'bg-success';

        return `
            <div class="approval-item mb-3 pb-3 border-bottom">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <strong class="text-danger text-amount">
                            $${amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                        </strong>
                        <br>
                        <small class="text-muted">
                            <i class="bi bi-person"></i>
                            ${approval.client_name}
                        </small>
                        <br>
                        <small class="text-muted">
                            <i class="bi bi-briefcase"></i>
                            ${approval.case_number}
                        </small>
                    </div>
                    <div class="text-end">
                        <span class="badge ${daysClass} days-pending-badge">
                            ${approval.days_pending}d
                        </span>
                        <br>
                        <small class="text-muted mt-1 d-block">
                            by ${approval.created_by_name}
                        </small>
                    </div>
                </div>
            </div>
        `;
    }

    renderError(message) {
        this.body.innerHTML = `
            <p class="text-danger text-center mb-0 py-3">
                <i class="bi bi-exclamation-triangle" style="font-size: 2rem;"></i>
                <br>
                <small>${message}</small>
            </p>
        `;

        this.countBadge.textContent = '!';
    }
}

// Global instance
let approvalWidget;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    approvalWidget = new ApprovalWidget();
});
