/**
 * Approval Badge Notification System
 *
 * COMPLIANCE CONTROL #3: Two-Person Approval Workflow
 *
 * Features:
 * - Polls /approvals/pending_count/ every 60 seconds
 * - Updates badge count in header
 * - Shows/hides badge based on count
 * - Animates badge on count change
 * - Plays notification sound (optional)
 *
 * Usage:
 * - Include this script on ALL pages
 * - Requires header element with id="approvalBadge" and id="approvalBadgeLink"
 */

class ApprovalBadge {
    constructor() {
        this.badge = document.getElementById('approvalBadge');
        this.link = document.getElementById('approvalBadgeLink');

        // Don't initialize if elements don't exist
        if (!this.badge || !this.link) {
            console.log('Approval badge elements not found - skipping initialization');
            return;
        }

        this.pollInterval = 300000; // 5 minutes
        this.lastCount = 0;
        this.isFirstLoad = true;

        this.init();
    }

    async init() {
        console.log('Initializing approval badge notification system...');

        // Initial load
        await this.updateCount();

        // Poll for updates every 60 seconds
        setInterval(() => this.updateCount(), this.pollInterval);
    }

    async updateCount() {
        try {
            const response = await fetch('/api/v1/bank-accounts/approvals/pending_count/', {
                credentials: 'include',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Not authenticated - hide badge
                    this.hideBadge();
                    return;
                }
                console.error('Failed to fetch pending count:', response.status);
                return;
            }

            const data = await response.json();
            const count = data.pending_count || 0;

            this.updateBadge(count);
        } catch (error) {
            console.error('Error fetching approval count:', error);
        }
    }

    updateBadge(count) {
        if (count === 0) {
            // Hide badge if no pending approvals
            this.hideBadge();
        } else {
            // Show badge with count
            this.showBadge(count);

            // Animate if count changed (and not first load)
            if (count !== this.lastCount && !this.isFirstLoad) {
                this.animateBadge();

                // If count increased, show notification
                if (count > this.lastCount) {
                    this.showNotification(count - this.lastCount);
                }
            }
        }

        this.lastCount = count;
        this.isFirstLoad = false;
    }

    showBadge(count) {
        this.badge.textContent = count;
        this.badge.style.display = 'inline-block';

        // Update link styling
        this.link.classList.remove('btn-outline-secondary');
        this.link.classList.add('btn-warning');

        // Update title for accessibility
        this.link.title = `${count} pending approval${count !== 1 ? 's' : ''}`;
    }

    hideBadge() {
        this.badge.style.display = 'none';

        // Update link styling
        this.link.classList.remove('btn-warning');
        this.link.classList.add('btn-outline-secondary');

        // Update title
        this.link.title = 'No pending approvals';
    }

    animateBadge() {
        // Remove animation class if it exists
        this.badge.classList.remove('badge-pulse');

        // Trigger reflow to restart animation
        void this.badge.offsetWidth;

        // Add animation class
        this.badge.classList.add('badge-pulse');

        // Remove class after animation completes
        setTimeout(() => {
            this.badge.classList.remove('badge-pulse');
        }, 1000);
    }

    showNotification(newCount) {
        // Browser notification (if permission granted)
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('New Approval Request', {
                body: `${newCount} new transaction${newCount !== 1 ? 's' : ''} require${newCount === 1 ? 's' : ''} approval`,
                icon: '/favicon.ico',
                badge: '/favicon.ico',
                tag: 'approval-notification',
                renotify: true
            });
        }

        // Console log for debugging
        console.log(`New approval requests: ${newCount}`);
    }

    // Method to request notification permission
    static async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    }
}

// Global instance
let approvalBadge;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Singleton pattern to prevent multiple pollers
    if (!window.approvalBadgeInstance) {
        window.approvalBadgeInstance = new ApprovalBadge();
    }
});

// Request notification permission when user first interacts with page
document.addEventListener('click', () => {
    ApprovalBadge.requestNotificationPermission();
}, { once: true });
