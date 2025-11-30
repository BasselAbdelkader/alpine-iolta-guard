/**
 * Sidebar Loader
 * Loads the sidebar HTML and sets the active link based on current page
 */

async function loadSidebar() {
    try {
        // Try to get cached sidebar from sessionStorage
        let sidebarHTML = sessionStorage.getItem('cachedSidebarHTML');
        
        if (!sidebarHTML) {
            // Fetch the sidebar HTML if not cached
            console.log('Fetching sidebar from server...');
            const response = await fetch('/html/sidebar.html');
            if (!response.ok) {
                console.error('Failed to load sidebar');
                return;
            }
            sidebarHTML = await response.text();
            
            // Cache it
            sessionStorage.setItem('cachedSidebarHTML', sidebarHTML);
        } else {
            console.log('Loaded sidebar from cache');
        }

        // Find the sidebar container and inject the HTML
        const sidebarContainer = document.getElementById('sidebar-container');
        if (sidebarContainer) {
            sidebarContainer.innerHTML = sidebarHTML;

            // Set active link based on current page
            setActiveSidebarLink();

            // Initialize law firm info after sidebar is loaded
            if (typeof initLawFirmInfo === 'function') {
                initLawFirmInfo();
            }

            // Initialize approval badge after sidebar is loaded
            if (typeof ApprovalBadge !== 'undefined') {
                // Using the global instance check we added earlier in approval-badge.js
                if (!window.approvalBadgeInstance) {
                    window.approvalBadgeInstance = new ApprovalBadge();
                }
            }
        }
    } catch (error) {
        console.error('Error loading sidebar:', error);
    }
}

function setActiveSidebarLink() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.sidebar .nav-link');
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath.includes(href) || (currentPath === '/' && href.includes('dashboard'))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Load sidebar when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSidebar);
} else {
    loadSidebar();
}
