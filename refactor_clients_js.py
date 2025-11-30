import sys

file_path = '/root/ve_demo/frontend/js/clients.js'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Update loadClients to perform filtering locally
old_load_clients = """async function loadClients() {
    try {
        const searchQuery = document.getElementById('search').value.trim();
        const balanceFilter = document.getElementById('balance_filter').value;
        const statusFilter = document.getElementById('status_filter').value;

        // Build query parameters for BACKEND filtering/sorting
        let params = new URLSearchParams();

        // Balance filter (backend handles this now)
        if (balanceFilter && balanceFilter !== '') {
            params.append('balance_filter', balanceFilter);
        }

        // Status filter
        if (searchQuery.length < 2) {
            if (statusFilter === 'active') {
                params.append('is_active', 'true');
            } else if (statusFilter === 'inactive') {
                params.append('is_active', 'false');
            }
        }

        // Sorting (backend handles this now)
        if (currentSort.column) {
            let orderingField = currentSort.column === 'balance' ? 'current_balance' : 'client_name';
            let orderingDirection = currentSort.direction === 'desc' ? '-' : '';
            params.append('ordering', orderingDirection + orderingField);
        }

        // Build endpoint URL
        let endpoint = searchQuery.length >= 2
            ? `/v1/clients/search/?q=${encodeURIComponent(searchQuery)}&${params.toString()}`
            : `/v1/clients/?${params.toString()}`;

        console.log('Fetching ALL clients from:', endpoint);
        const data = await api.get(endpoint);

        // Backend returns ALL filtered and sorted clients (no pagination)
        // Extract clients from response based on API structure
        if (Array.isArray(data)) {
            allClients = data;
        } else if (data.results && Array.isArray(data.results)) {
            allClients = data.results;
        } else if (data.clients && Array.isArray(data.clients)) {
            allClients = data.clients;
        } else {
            console.error('Invalid API response structure:', data);
            throw new Error('Invalid API response format');
        }

        console.log(`Loaded ${allClients.length} clients from backend`);

        // Store cases
        allClients.forEach(client => {
            allCases[client.id] = client.cases || [];
        });

        // Update total count for pagination
        totalCount = allClients.length;

        // Paginate in FRONTEND only (slice the array)
        paginateAndDisplay();

    } catch (error) {
        console.error('Error loading clients:', error);
        console.error('Error stack:', error.stack);
        document.querySelector('#clientsTable tbody').innerHTML =
            '<tr><td colspan="6" class="text-center text-danger">Error loading clients. Please try again.</td></tr>';
    }
}"""

new_load_clients = """// Global variable to store ALL clients fetched from server
let cachedClients = [];
let isInitialLoad = true;

async function loadClients() {
    try {
        // Only fetch from server on initial load or explicit refresh
        if (isInitialLoad || cachedClients.length === 0) {
            console.log('Fetching ALL clients from backend (Initial Load)...');
            const data = await api.get('/v1/clients/'); // Fetch ALL clients, no filters

            if (Array.isArray(data)) {
                cachedClients = data;
            } else if (data.results && Array.isArray(data.results)) {
                cachedClients = data.results;
            } else {
                console.error('Invalid API response structure:', data);
                throw new Error('Invalid API response format');
            }
            isInitialLoad = false;
            console.log(`Cached ${cachedClients.length} clients.`);
        }

        // Apply filters locally
        applyLocalFilters();

    } catch (error) {
        console.error('Error loading clients:', error);
        document.querySelector('#clientsTable tbody').innerHTML =
            '<tr><td colspan="6" class="text-center text-danger">Error loading clients. Please try again.</td></tr>';
    }
}

function applyLocalFilters() {
    const searchQuery = document.getElementById('search').value.trim().toLowerCase();
    const balanceFilter = document.getElementById('balance_filter').value;
    const statusFilter = document.getElementById('status_filter').value;

    // Start with all cached clients
    let filtered = [...cachedClients];

    // 1. Filter by Search (Name, Email, Phone, Client Number)
    if (searchQuery.length >= 1) {
        filtered = filtered.filter(client => {
            return (client.full_name && client.full_name.toLowerCase().includes(searchQuery)) ||
                   (client.email && client.email.toLowerCase().includes(searchQuery)) ||
                   (client.phone && client.phone.replace(/\D/g, '').includes(searchQuery)) ||
                   (client.client_number && client.client_number.toLowerCase().includes(searchQuery));
        });
    }

    // 2. Filter by Status
    if (statusFilter !== 'all') {
        const isActive = statusFilter === 'active';
        filtered = filtered.filter(client => client.is_active === isActive);
    }

    // 3. Filter by Balance
    if (balanceFilter !== 'all') {
        filtered = filtered.filter(client => {
            const balance = parseFloat(client.current_balance || 0);
            if (balanceFilter === 'zero') return balance === 0;
            if (balanceFilter === 'non_zero') return balance !== 0;
            if (balanceFilter === 'positive') return balance > 0;
            if (balanceFilter === 'negative') return balance < 0;
            return true;
        });
    }

    // 4. Sort
    if (currentSort.column) {
        filtered = sortClientsArray(filtered, currentSort.column, currentSort.direction);
    }

    // Update global filtered list for pagination
    allClients = filtered;
    totalCount = allClients.length;
    
    // Reset to page 1 if filtering changed results significantly (optional, but good UX)
    // We usually want to reset page on filter change, which is handled by event listeners calling loadClients
    // But since loadClients now calls this, we might want to ensure page is valid.
    const maxPage = Math.ceil(totalCount / pageSize) || 1;
    if (currentPage > maxPage) currentPage = 1;

    console.log(`Filtered down to ${allClients.length} clients locally.`);
    paginateAndDisplay();
}
"""

# We need to replace the old loadClients function.
# Finding exact match might be hard due to whitespace.
# I'll use a robust marker approach.

# Start marker
start_marker = "async function loadClients() {"
# End marker - searching for the end of the function is tricky.
# The function ends before "function paginateAndDisplay() {"

end_marker = "// NEW: Frontend-only pagination (slice array)"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_load_clients + "\n\n" + content[end_idx:]
    
    # Also need to update event listeners to NOT reset currentPage inside the listener, 
    # but let applyLocalFilters handle logic or just keep as is (resetting is fine).
    # The existing listeners call loadClients(), which now calls applyLocalFilters().
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("Successfully refactored clients.js for client-side filtering.")
else:
    print("Could not find loadClients function block.")
    sys.exit(1)
