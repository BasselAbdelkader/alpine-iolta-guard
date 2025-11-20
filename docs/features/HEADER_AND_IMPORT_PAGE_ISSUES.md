# Header Information & Import Audit Page

**Date:** November 13, 2025
**Issues:**
1. Hardcoded header showing demo firm information
2. Import Audit page doesn't exist yet

---

## Issue #1: Header Showing Demo Firm Info

### **What You're Seeing:**
```
1200 Insurance Plaza, New York, NY 10004 | (212) 555-0100 | contact@ioltaguard.com
```

### **Root Cause:**
This is **NOT hardcoded** - it's coming from the **LawFirm** database table!

**Database Check:**
```
Active Law Firm: IOLTA Guard Insurance Law
Address: 1200 Insurance Plaza
City: New York, NY 10004
Phone: (212) 555-0100
Email: contact@ioltaguard.com
```

### **This is Actually CORRECT Design:**
✅ Header pulls from LawFirm settings (dynamic)
❌ Problem is the data is **demo/placeholder data**

---

## ✅ Solution #1: Update Law Firm Information

### **Option A: Update via Django Admin**

1. Go to: `http://localhost/admin/`
2. Login with admin credentials
3. Navigate to: **Settings → Law Firm Information**
4. Update:
   - Firm Name
   - Address
   - City, State, ZIP
   - Phone
   - Email
   - Website
5. Save

### **Option B: Update via Database**

```python
docker exec iolta_backend_alpine python -c "
import django
django.setup()
from apps.settings.models import LawFirm

firm = LawFirm.get_active_firm()
if firm:
    firm.firm_name = 'Your Law Firm Name'
    firm.address_line1 = 'Your Address'
    firm.city = 'Your City'
    firm.state = 'NY'
    firm.zip_code = '10001'
    firm.phone = '(555) 123-4567'
    firm.email = 'your@email.com'
    firm.save()
    print('✅ Law firm information updated!')
"
```

### **Option C: Create Settings UI Page**

Create a settings page where users can update firm information via the web interface.

**Recommended Page:** `settings.html` (already exists)

**Add Section:**
```html
<div class="card">
    <div class="card-header">
        <h5>Law Firm Information</h5>
    </div>
    <div class="card-body">
        <form id="firmInfoForm">
            <div class="mb-3">
                <label>Firm Name</label>
                <input type="text" class="form-control" id="firmName">
            </div>
            <div class="mb-3">
                <label>Address</label>
                <input type="text" class="form-control" id="firmAddress">
            </div>
            <!-- More fields... -->
            <button type="submit" class="btn btn-primary">Save</button>
        </form>
    </div>
</div>
```

---

## Issue #2: Import Audit Page Doesn't Exist

### **Current State:**
✅ Backend API created and working:
- `POST /api/v1/settings/csv/preview/`
- `POST /api/v1/settings/csv/import/`
- `GET /api/v1/settings/import-audits/`
- `DELETE /api/v1/settings/import-audits/{id}/delete/`

❌ Frontend UI not created yet

### **What Exists:**
- `import-quickbooks.html` - QuickBooks import page (different feature)
- `settings.html` - General settings page

### **What's Missing:**
- Import Management page (CSV import + history)
- Import Audit page (view past imports)

---

## ✅ Solution #2: Create Import Management Page

### **Recommended Approach:**

**Option A: Add to Settings Page**

Update `settings.html` to include import management as a tab:

```html
<ul class="nav nav-tabs">
    <li class="nav-item">
        <a class="nav-link" href="#general">General Settings</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="#firm">Firm Information</a>
    </li>
    <li class="nav-item">
        <a class="nav-link active" href="#import">Import Management</a>
    </li>
</ul>

<div class="tab-content">
    <div id="import" class="tab-pane active">
        <!-- CSV Import Section -->
        <!-- Import History Section -->
    </div>
</div>
```

**Option B: Create New Page**

Create `/usr/share/nginx/html/html/import-management.html`

**Page Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Import Management - IOLTA Guard</title>
    <!-- Bootstrap CSS -->
</head>
<body>
    <div class="container-fluid">
        <h2>Import Management</h2>

        <!-- Tab Navigation -->
        <ul class="nav nav-tabs">
            <li class="nav-item">
                <a class="nav-link active" data-bs-toggle="tab" href="#csv-import">
                    CSV Import
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#import-history">
                    Import History
                </a>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content">
            <!-- Tab 1: CSV Import -->
            <div id="csv-import" class="tab-pane active">
                <div class="card mt-3">
                    <div class="card-header">
                        <h5>Upload CSV File</h5>
                    </div>
                    <div class="card-body">
                        <!-- File Upload -->
                        <input type="file" id="csvFile" accept=".csv">
                        <button id="previewBtn" class="btn btn-primary">
                            Preview CSV
                        </button>

                        <!-- Preview Results -->
                        <div id="previewResults" style="display:none;">
                            <h6>Preview Summary</h6>
                            <table class="table">
                                <tr>
                                    <th>Entity</th>
                                    <th>Total in CSV</th>
                                    <th>New</th>
                                    <th>Existing</th>
                                    <th>Duplicates</th>
                                </tr>
                                <tr>
                                    <td>Clients</td>
                                    <td id="totalClients"></td>
                                    <td id="newClients"></td>
                                    <td id="existingClients"></td>
                                    <td id="dupClients"></td>
                                </tr>
                                <!-- More rows... -->
                            </table>

                            <button id="confirmImportBtn" class="btn btn-success">
                                Confirm Import
                            </button>
                            <button id="cancelBtn" class="btn btn-secondary">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab 2: Import History -->
            <div id="import-history" class="tab-pane">
                <div class="card mt-3">
                    <div class="card-header">
                        <h5>Import History</h5>
                    </div>
                    <div class="card-body">
                        <table class="table" id="importHistoryTable">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>File</th>
                                    <th>Status</th>
                                    <th>Total Rows</th>
                                    <th>Created</th>
                                    <th>Skipped</th>
                                    <th>Success Rate</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Populated via JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/js/import-management.js"></script>
</body>
</html>
```

**JavaScript File:** `/usr/share/nginx/html/js/import-management.js`

```javascript
// Preview CSV
document.getElementById('previewBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a CSV file');
        return;
    }

    const formData = new FormData();
    formData.append('csv_file', file);

    try {
        const response = await fetch('/api/v1/settings/csv/preview/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Display preview results
        document.getElementById('previewResults').style.display = 'block';
        document.getElementById('totalClients').textContent = data.preview_summary.total_clients_in_csv;
        document.getElementById('newClients').textContent = data.preview_summary.expected_clients;
        document.getElementById('existingClients').textContent = data.preview_summary.existing_clients;
        document.getElementById('dupClients').textContent = data.preview_summary.duplicate_clients_in_csv;
        // ... more fields

    } catch (error) {
        alert('Error previewing CSV: ' + error.message);
    }
});

// Confirm Import
document.getElementById('confirmImportBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('csv_file', file);

    try {
        const response = await fetch('/api/v1/settings/csv/import/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        alert('Import completed successfully!');
        loadImportHistory(); // Refresh history

    } catch (error) {
        alert('Error importing CSV: ' + error.message);
    }
});

// Load Import History
async function loadImportHistory() {
    try {
        const response = await fetch('/api/v1/settings/import-audits/');
        const imports = await response.json();

        const tbody = document.querySelector('#importHistoryTable tbody');
        tbody.innerHTML = '';

        imports.forEach(imp => {
            const row = `
                <tr>
                    <td>${new Date(imp.import_date).toLocaleString()}</td>
                    <td>${imp.file_name}</td>
                    <td>${imp.status}</td>
                    <td>${imp.total_records}</td>
                    <td>${imp.clients_created + imp.cases_created + imp.transactions_created}</td>
                    <td>${imp.clients_skipped + imp.cases_skipped}</td>
                    <td>${((imp.successful_records / imp.total_records) * 100).toFixed(1)}%</td>
                    <td>
                        <button onclick="deleteImport(${imp.id})" class="btn btn-sm btn-danger">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });

    } catch (error) {
        console.error('Error loading import history:', error);
    }
}

// Delete Import
async function deleteImport(id) {
    if (!confirm('Delete this import batch? All imported data will be removed.')) {
        return;
    }

    try {
        await fetch(`/api/v1/settings/import-audits/${id}/delete/`, {
            method: 'DELETE'
        });

        alert('Import batch deleted successfully');
        loadImportHistory();

    } catch (error) {
        alert('Error deleting import: ' + error.message);
    }
}

// Load history on page load
document.addEventListener('DOMContentLoaded', loadImportHistory);
```

---

## 📋 Quick Implementation Checklist

### **For Law Firm Header:**
- [ ] Access Django admin
- [ ] Update law firm information
- [ ] Verify header changes on pages

**OR**

- [ ] Add firm settings section to settings.html
- [ ] Create API endpoint for updating firm info
- [ ] Allow users to update from UI

### **For Import Audit Page:**
- [ ] Create `import-management.html` page
- [ ] Create `import-management.js` JavaScript
- [ ] Add navigation link in menu
- [ ] Test CSV preview
- [ ] Test CSV import
- [ ] Test import history display
- [ ] Test delete import batch

---

## 🎯 Priority Recommendation

### **High Priority:**
1. **Update Law Firm Info** (5 minutes via admin)
   - Removes demo data immediately
   - Users see correct firm name/address

### **Medium Priority:**
2. **Create Import Management Page** (2-3 hours)
   - Essential for using CSV import feature
   - Provides visibility into imports
   - Allows batch deletion

### **Low Priority:**
3. **Add Firm Settings UI** (1-2 hours)
   - Nice to have for self-service
   - Can be done via admin for now

---

## 📁 Files Referenced

**Backend (Existing):**
- `/app/apps/settings/models.py` - LawFirm model (line 24-118)
- `/app/apps/settings/api/views.py` - Import API endpoints
- `/app/apps/settings/api/serializers.py` - Import serializers

**Frontend (To Create):**
- `/usr/share/nginx/html/html/import-management.html` - Main page
- `/usr/share/nginx/html/js/import-management.js` - JavaScript logic

**Frontend (Existing):**
- `/usr/share/nginx/html/html/settings.html` - Could add firm settings here

---

## ✅ Summary

**Issue #1 (Header):**
- ✅ Design is correct (uses LawFirm model)
- ❌ Data is demo/placeholder
- **Fix:** Update via admin or create settings UI

**Issue #2 (Import Page):**
- ✅ Backend API complete and working
- ❌ Frontend UI doesn't exist
- **Fix:** Create import-management.html page

**Next Steps:**
1. Update law firm information (quick fix)
2. Create import management page (complete the feature)

---

**Documentation:** Complete
**APIs:** Ready
**Frontend:** Needs to be built
