// User Management JavaScript
// Handles user CRUD operations, role management, and permissions

const API_BASE = '/api/v1/settings';
let allUsers = [];
let createUserModalInstance = null;
let editUserModalInstance = null;

// Role descriptions
const ROLE_DESCRIPTIONS = {
    'managing_attorney': 'Full access to all functions. Can approve high-value transactions, reconcile accounts, and manage users.',
    'staff_attorney': 'Create/edit own cases and clients. View assigned cases only. Cannot approve high-value transactions.',
    'paralegal': 'Limited data entry. Create/edit clients and cases. Enter transactions (require approval). No financial reports.',
    'bookkeeper': 'Financial operations. Enter transactions, reconcile accounts, generate reports. Cannot approve own transactions.',
    'system_admin': 'Technical access only. User management and system configuration. No access to client data or transactions.'
};

// Initialize user management
function initUserManagement() {
    console.log('User Management: Initializing...');

    // Initialize modals
    createUserModalInstance = new bootstrap.Modal(document.getElementById('createUserModal'));
    editUserModalInstance = new bootstrap.Modal(document.getElementById('editUserModal'));

    // Load users
    loadUsers();

    // Set up event listeners
    setupEventListeners();
}

// Set up event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('searchInput').addEventListener('input', filterUsers);

    // Role filter
    document.getElementById('roleFilter').addEventListener('change', filterUsers);

    // Status filter
    document.getElementById('statusFilter').addEventListener('change', filterUsers);

    // Role select changes (show descriptions)
    document.getElementById('createRoleSelect').addEventListener('change', function() {
        showRoleDescription('create', this.value);
    });

    document.getElementById('editRoleSelect').addEventListener('change', function() {
        showRoleDescription('edit', this.value);
    });
}

// Load all users from API
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users/`, {
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 403) {
                alert('You do not have permission to manage users.');
                window.location.href = '/dashboard';
                return;
            }
            throw new Error('Failed to load users');
        }

        const data = await response.json();
        allUsers = data.users || [];

        // Update stats
        updateStats();

        // Render table
        renderUsersTable(allUsers);

    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersTableBody').innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle me-2"></i>Error loading users: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Update statistics
function updateStats() {
    const totalUsers = allUsers.length;
    const activeUsers = allUsers.filter(u => u.is_active).length;
    const managingAttorneys = allUsers.filter(u => u.role === 'managing_attorney').length;
    const staffMembers = allUsers.filter(u => ['staff_attorney', 'paralegal', 'bookkeeper'].includes(u.role)).length;

    document.getElementById('totalUsers').textContent = totalUsers;
    document.getElementById('activeUsers').textContent = activeUsers;
    document.getElementById('managingAttorneys').textContent = managingAttorneys;
    document.getElementById('staffMembers').textContent = staffMembers;
}

// Render users table
function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');

    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    No users found.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr onclick="showEditUserModal(${user.id})">
            <td>
                <strong>${user.full_name || user.username}</strong>
                ${user.employee_id ? `<br><small class="text-muted">ID: ${user.employee_id}</small>` : ''}
            </td>
            <td>${user.username}</td>
            <td>${user.email || '<span class="text-muted">No email</span>'}</td>
            <td>
                <span class="role-badge role-${user.role}">
                    ${user.role_display}
                </span>
            </td>
            <td>
                ${getPermissionBadges(user)}
            </td>
            <td>
                ${user.is_active ?
                    '<span class="badge bg-success">Active</span>' :
                    '<span class="badge bg-secondary">Inactive</span>'
                }
            </td>
            <td>
                <small>${formatDate(user.created_at)}</small>
            </td>
            <td onclick="event.stopPropagation()">
                <button class="btn btn-sm btn-outline-primary" onclick="showEditUserModal(${user.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id}, '${user.username}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Get permission badges for user
function getPermissionBadges(user) {
    const badges = [];

    if (user.can_approve_transactions) {
        badges.push('<span class="badge bg-primary permission-badge">Approve</span>');
    }
    if (user.can_reconcile) {
        badges.push('<span class="badge bg-info permission-badge">Reconcile</span>');
    }
    if (user.can_print_checks) {
        badges.push('<span class="badge bg-warning permission-badge">Print Checks</span>');
    }
    if (user.can_manage_users) {
        badges.push('<span class="badge bg-danger permission-badge">Manage Users</span>');
    }

    return badges.length > 0 ? badges.join('') : '<span class="text-muted">Basic Access</span>';
}

// Filter users based on search and filters
function filterUsers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const roleFilter = document.getElementById('roleFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;

    let filtered = allUsers;

    // Search filter
    if (searchTerm) {
        filtered = filtered.filter(user =>
            user.username.toLowerCase().includes(searchTerm) ||
            user.full_name.toLowerCase().includes(searchTerm) ||
            (user.email && user.email.toLowerCase().includes(searchTerm)) ||
            (user.first_name && user.first_name.toLowerCase().includes(searchTerm)) ||
            (user.last_name && user.last_name.toLowerCase().includes(searchTerm))
        );
    }

    // Role filter
    if (roleFilter) {
        filtered = filtered.filter(user => user.role === roleFilter);
    }

    // Status filter
    if (statusFilter) {
        const isActive = statusFilter === 'true';
        filtered = filtered.filter(user => user.is_active === isActive);
    }

    renderUsersTable(filtered);
}

// Reset filters
function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('roleFilter').value = '';
    document.getElementById('statusFilter').value = '';
    filterUsers();
}

// Show create user modal
function showCreateUserModal() {
    document.getElementById('createUserForm').reset();
    document.getElementById('createRoleDescription').style.display = 'none';
    createUserModalInstance.show();
}

// Show role description
function showRoleDescription(type, role) {
    const descriptionDiv = document.getElementById(`${type}RoleDescription`);
    const descriptionText = document.getElementById(`${type}RoleDescriptionText`);

    if (role && ROLE_DESCRIPTIONS[role]) {
        descriptionText.textContent = ROLE_DESCRIPTIONS[role];
        descriptionDiv.style.display = 'block';
    } else {
        descriptionDiv.style.display = 'none';
    }
}

// Create new user
async function createUser() {
    const form = document.getElementById('createUserForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        first_name: formData.get('first_name') || '',
        last_name: formData.get('last_name') || '',
        password: formData.get('password'),
        role: formData.get('role'),
        phone: formData.get('phone') || '',
        employee_id: formData.get('employee_id') || '',
        department: formData.get('department') || '',
        is_active: formData.get('is_active') === 'on'
    };

    try {
        const response = await fetch(`${API_BASE}/users/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (!response.ok) {
            // Show validation errors
            if (data.username) {
                alert('Username: ' + data.username.join(', '));
            } else if (data.email) {
                alert('Email: ' + data.email.join(', '));
            } else {
                alert('Error creating user: ' + JSON.stringify(data));
            }
            return;
        }

        // Success
        alert('User created successfully!');
        createUserModalInstance.hide();
        loadUsers(); // Reload users list

    } catch (error) {
        console.error('Error creating user:', error);
        alert('Error creating user: ' + error.message);
    }
}

// Show edit user modal
async function showEditUserModal(userId) {
    try {
        const response = await fetch(`${API_BASE}/users/${userId}/`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to load user details');
        }

        const user = await response.json();

        // Populate form
        document.getElementById('editUserId').value = user.id;
        document.getElementById('editUsername').value = user.username;
        document.getElementById('editEmail').value = user.email || '';
        document.getElementById('editFirstName').value = user.first_name || '';
        document.getElementById('editLastName').value = user.last_name || '';
        document.getElementById('editPassword').value = '';
        document.getElementById('editRoleSelect').value = user.role;
        document.getElementById('editPhone').value = user.phone || '';
        document.getElementById('editEmployeeId').value = user.employee_id || '';
        document.getElementById('editDepartment').value = user.department || '';
        document.getElementById('editIsActive').checked = user.is_active;

        // Show role description
        showRoleDescription('edit', user.role);

        // Show modal
        editUserModalInstance.show();

    } catch (error) {
        console.error('Error loading user:', error);
        alert('Error loading user details: ' + error.message);
    }
}

// Update user
async function updateUser() {
    const form = document.getElementById('editUserForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const userId = document.getElementById('editUserId').value;
    const formData = new FormData(form);

    const userData = {
        email: formData.get('email'),
        first_name: formData.get('first_name') || '',
        last_name: formData.get('last_name') || '',
        role: formData.get('role'),
        phone: formData.get('phone') || '',
        employee_id: formData.get('employee_id') || '',
        department: formData.get('department') || '',
        is_active: formData.get('is_active') === 'on'
    };

    // Only include password if it was entered
    const password = formData.get('password');
    if (password) {
        userData.password = password;
    }

    try {
        const response = await fetch(`${API_BASE}/users/${userId}/update/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (!response.ok) {
            alert('Error updating user: ' + JSON.stringify(data));
            return;
        }

        // Success
        alert('User updated successfully!');
        editUserModalInstance.hide();
        loadUsers(); // Reload users list

    } catch (error) {
        console.error('Error updating user:', error);
        alert('Error updating user: ' + error.message);
    }
}

// Delete (deactivate) user
async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to deactivate user "${username}"?\n\nThis will prevent them from logging in but will preserve their record for audit purposes.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users/${userId}/delete/`, {
            method: 'DELETE',
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            alert('Error deactivating user: ' + (data.error || JSON.stringify(data)));
            return;
        }

        // Success
        alert('User deactivated successfully!');
        loadUsers(); // Reload users list

    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error deactivating user: ' + error.message);
    }
}

// Format date helper
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
