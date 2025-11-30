/**
 * Frontend Permission Checker
 * Checks user role and redirects if user lacks permission for current page
 */

// Pages that require financial access (blocked for system_admin)
const FINANCIAL_PAGES = [
    '/dashboard',
    '/clients',
    '/vendors',
    '/bank-accounts',
    '/bank-transactions',
    '/uncleared-transactions',
    '/settlements',
    '/reports',
    '/checks',
    '/cases'
];

// Pages that require specific permissions
const PERMISSION_REQUIRED = {
    '/checks': 'can_print_checks',
    '/bank-accounts/reconciliations': 'can_reconcile',
    '/user-management': 'can_manage_users'
};

// Pages accessible to everyone (authenticated)
const PUBLIC_PAGES = [
    '/login',
    '/settings'
];

/**
 * Check if current user has permission to access current page
 * Redirects to appropriate page if no permission
 */
async function checkPagePermissions() {
    // Get current path
    const currentPath = window.location.pathname;

    // Skip check for login page
    if (currentPath === '/login' || currentPath === '/') {
        return;
    }

    try {
        // Get current user profile
        const response = await fetch('/api/v1/settings/users/me/', {
            credentials: 'include'
        });

        if (!response.ok) {
            // Not authenticated - redirect to login
            if (response.status === 401 || response.status === 403) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Failed to get user profile');
        }

        const data = await response.json();
        const userRole = data.role;
        const permissions = {
            can_manage_users: data.can_manage_users,
            can_approve_transactions: data.can_approve_transactions,
            can_reconcile: data.can_reconcile,
            can_print_checks: data.can_print_checks
        };

        console.log('User role:', userRole);
        console.log('Permissions:', permissions);

        // Check if system admin trying to access financial pages
        if (userRole === 'system_admin') {
            const isFinancialPage = FINANCIAL_PAGES.some(page =>
                currentPath.startsWith(page)
            );

            if (isFinancialPage) {
                console.warn('System Administrator blocked from financial page');
                showAccessDenied('System Administrators do not have access to client or financial data.');
                return;
            }
        }

        // Check specific permission requirements
        for (const [page, requiredPermission] of Object.entries(PERMISSION_REQUIRED)) {
            if (currentPath.startsWith(page)) {
                if (!permissions[requiredPermission]) {
                    console.warn(`User lacks ${requiredPermission} for ${page}`);
                    showAccessDenied(`You do not have permission to access this page. Required: ${requiredPermission.replace('can_', '').replace('_', ' ')}`);
                    return;
                }
            }
        }

    } catch (error) {
        console.error('Permission check error:', error);
        // On error, allow page load (fail open for better UX)
    }
}

/**
 * Show access denied message and redirect
 */
function showAccessDenied(message) {
    // Clear page content
    document.body.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background: #f8f9fa;">
            <div style="text-align: center; max-width: 600px; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <i class="fas fa-lock" style="font-size: 64px; color: #dc3545; margin-bottom: 1rem;"></i>
                <h2 style="color: #dc3545; margin-bottom: 1rem;">Access Denied</h2>
                <p style="color: #6c757d; margin-bottom: 2rem;">${message}</p>
                <div>
                    <a href="/settings" class="btn btn-primary" style="margin-right: 1rem; padding: 0.5rem 1.5rem; background: #0d6efd; color: white; text-decoration: none; border-radius: 4px; display: inline-block;">
                        Go to Settings
                    </a>
                    <a href="/user-management" class="btn btn-secondary" style="padding: 0.5rem 1.5rem; background: #6c757d; color: white; text-decoration: none; border-radius: 4px; display: inline-block;">
                        User Management
                    </a>
                </div>
            </div>
        </div>
    `;

    // Stop any JavaScript execution
    throw new Error('Access Denied');
}

// Run permission check when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkPagePermissions);
} else {
    checkPagePermissions();
}
