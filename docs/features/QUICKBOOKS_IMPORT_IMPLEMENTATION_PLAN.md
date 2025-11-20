# QuickBooks Import Implementation Plan

**Date:** November 10, 2025
**Status:** Implementation Ready
**Strategy:** Finalized based on user decisions

---

## ✅ User Decisions (Finalized)

### 0. Case Naming Convention
**Format:** `"{Client Name} Case"`

**Examples:**
- Client: "Jerry Patel" → Case: "Jerry Patel Case"
- Client: "Kevin Nelson" → Case: "Kevin Nelson Case"

### 1. Import Strategy
**Selected:** Strategy A - One case per client

### 2. Journal Entries Without Client
**Solution:** Create "Unassigned" client for orphaned transactions

### 3. Existing Clients
**Solution:** If client already exists in IOLTA Guard:
- Don't skip
- Don't update client
- **Create new case** for that client: "{Client Name} Case"
- Import transactions to the new case

### 4. Error Handling
**Approach:** Validation-first with complete error report
1. Validate entire CSV file
2. Report ALL errors found
3. Show detailed error list to user
4. User fixes errors or chooses to proceed (skipping error rows)
5. Then import valid rows

### 5. UI Location
**Location:** New "Import" page in main navigation

---

## 🏗️ Implementation Architecture

### Backend Components

#### 1. CSV Parser (`quickbooks_parser.py`)
```python
class QuickBooksParser:
    """Parse and validate QuickBooks CSV file."""

    def parse(csv_file):
        """Parse CSV and return structured data."""

    def validate(data):
        """Validate data and return errors."""

    def extract_clients(data):
        """Extract unique clients from data."""

    def group_by_client(data):
        """Group transactions by client."""
```

#### 2. Import Service (`quickbooks_importer.py`)
```python
class QuickBooksImporter:
    """Handle QuickBooks import logic."""

    def import_clients(clients):
        """Create or find clients."""

    def create_cases(clients):
        """Create one case per client."""

    def import_transactions(data):
        """Import all transactions."""

    def generate_report():
        """Generate import summary report."""
```

#### 3. API Endpoint (`/api/quickbooks/import/`)
```python
POST /api/quickbooks/import/
    - Upload CSV file
    - Validate
    - Return validation errors OR import

Response:
{
    "success": true,
    "summary": {
        "clients_created": 193,
        "cases_created": 193,
        "transactions_imported": 1258,
        "errors": []
    }
}
```

### Frontend Components

#### 1. Import Page (`import-quickbooks.html`)
```
┌──────────────────────────────────────────┐
│  Import QuickBooks Data                  │
├──────────────────────────────────────────┤
│                                          │
│  Step 1: Upload CSV File                 │
│  [Choose File] quickbooks.csv  [Validate]│
│                                          │
│  Step 2: Review Validation Results       │
│  ┌────────────────────────────────────┐  │
│  │ ✓ 193 clients found                │  │
│  │ ✓ 1,263 transactions found         │  │
│  │ ⚠ 5 validation warnings            │  │
│  │                                    │  │
│  │ Errors:                            │  │
│  │ • Row 742: Missing client name     │  │
│  │ • Row 855: Invalid date format     │  │
│  │ ...                                │  │
│  └────────────────────────────────────┘  │
│                                          │
│  Import Options:                         │
│  ☑ Create "Unassigned" client           │
│  ☑ Skip rows with errors                │
│                                          │
│  [Cancel]         [Import Data]          │
└──────────────────────────────────────────┘
```

#### 2. Import JavaScript (`import-quickbooks.js`)
- File upload handler
- Validation trigger
- Error display
- Import progress
- Success/error reporting

---

## 📋 Detailed Implementation Spec

### Data Processing Flow

```
1. User uploads quickbooks.csv
   ↓
2. Backend validates entire file
   ├─ Check column headers
   ├─ Validate each row
   ├─ Check data formats
   └─ Detect issues
   ↓
3. Return validation results
   ├─ Valid rows count
   ├─ Error list (all errors)
   └─ Preview data
   ↓
4. User reviews errors
   ├─ Fix file and re-upload?
   └─ Or proceed (skip error rows)?
   ↓
5. User clicks "Import"
   ↓
6. Backend imports data
   ├─ Create/find clients
   ├─ Create cases
   ├─ Import transactions
   └─ Generate report
   ↓
7. Show success summary
   ├─ Clients created
   ├─ Cases created
   ├─ Transactions imported
   └─ Errors skipped
```

---

## 🔍 Validation Rules

### File-Level Validation

1. **Required Columns Present:**
   ```python
   REQUIRED_COLUMNS = [
       'Date', 'Type', 'Account', 'Payee',
       'Memo', 'Payment', 'Deposit'
   ]
   ```

2. **Not Empty:**
   - File has at least 1 data row

3. **Encoding:**
   - UTF-8, UTF-8-sig, latin-1, or cp1252

### Row-Level Validation

For each row:

1. **Date Field:**
   - Not empty
   - Valid date format (MM/DD/YYYY)
   - Reasonable date range (2020-2030)

2. **Type Field:**
   - One of: Check, Deposit, Expense, Journal

3. **Account Field:**
   - Not empty (except Journal entries)
   - If Journal and empty: Will use "Unassigned" client

4. **Amount Fields:**
   - Has either Payment OR Deposit (not both)
   - Valid number format
   - Positive amount

5. **Payee Field:**
   - Can be empty (optional)

---

## 💾 Data Mapping Specification

### Client Creation

**For each unique Account value:**

```python
# If Account is empty (Journal entry)
if not account_name:
    account_name = "Unassigned"

# Check if client exists
existing_client = Client.objects.filter(
    firm=current_firm,
    name=account_name
).first()

if existing_client:
    # Use existing client (don't create new)
    client = existing_client
else:
    # Create new client
    client = Client.objects.create(
        firm=current_firm,
        name=account_name,
        status='Active',
        notes=f'Imported from QuickBooks on {today}'
    )
```

### Case Creation

**For each client (new or existing):**

```python
# Case naming: "{Client Name} Case"
case_title = f"{client.name} Case"

# Get date of first transaction for this client
first_transaction_date = min(
    t['Date'] for t in transactions
    if t['Account'] == client.name
)

# Create case
case = Case.objects.create(
    firm=current_firm,
    client=client,
    title=case_title,
    case_number=f'QB-{timestamp}-{client.id}',
    status='Open',
    opened_date=first_transaction_date,
    description=f'Imported from QuickBooks on {today}'
)
```

### Transaction Mapping

**For each transaction row:**

```python
# Determine transaction type
if row['Type'] in ['Check', 'Expense']:
    if row['Payment']:
        transaction_type = 'Withdrawal'
        amount = parse_amount(row['Payment'])
elif row['Type'] in ['Deposit', 'Journal']:
    if row['Deposit']:
        transaction_type = 'Deposit'
        amount = parse_amount(row['Deposit'])

# Map to IOLTA Guard transaction
Transaction.objects.create(
    firm=current_firm,
    case=case,
    transaction_date=parse_date(row['Date']),
    transaction_type=transaction_type,
    amount=amount,
    payee=row['Payee'] or '',
    check_number=row['Ref No.'] or None,
    description=row['Memo'] or '',
    is_cleared=(row['Reconciliation Status'] in ['Reconciled', 'Cleared']),
    created_by=request.user
)
```

---

## 🎨 UI/UX Details

### Navigation Addition

Add to main navigation menu:

```html
<li>
    <a href="/import-quickbooks.html">
        <i class="fas fa-file-import"></i>
        Import QuickBooks
    </a>
</li>
```

### Import Page Sections

#### Section 1: File Upload
```html
<div class="upload-section">
    <h3>Step 1: Upload QuickBooks CSV</h3>
    <input type="file" id="csvFile" accept=".csv">
    <button id="validateBtn">Validate File</button>
</div>
```

#### Section 2: Validation Results
```html
<div id="validationResults" style="display:none;">
    <h3>Step 2: Validation Results</h3>

    <div class="stats">
        <span id="clientCount">0 clients</span>
        <span id="transactionCount">0 transactions</span>
        <span id="errorCount">0 errors</span>
    </div>

    <div id="errorList" class="error-list">
        <!-- Errors displayed here -->
    </div>

    <button id="importBtn">Import Data</button>
</div>
```

#### Section 3: Import Progress
```html
<div id="importProgress" style="display:none;">
    <h3>Importing...</h3>
    <div class="progress-bar">
        <div id="progressFill"></div>
    </div>
    <p id="progressText">Processing...</p>
</div>
```

#### Section 4: Success Summary
```html
<div id="importSummary" style="display:none;">
    <h3>Import Complete!</h3>
    <ul>
        <li>Clients created: <span id="clientsCreated">0</span></li>
        <li>Cases created: <span id="casesCreated">0</span></li>
        <li>Transactions imported: <span id="transactionsImported">0</span></li>
        <li>Errors skipped: <span id="errorsSkipped">0</span></li>
    </ul>
    <a href="/clients.html" class="btn">View Clients</a>
</div>
```

---

## 🔧 API Specification

### Endpoint 1: Validate CSV

**Request:**
```http
POST /api/quickbooks/validate/
Content-Type: multipart/form-data

file: quickbooks.csv
```

**Response (Success):**
```json
{
    "valid": true,
    "summary": {
        "total_rows": 1263,
        "valid_rows": 1258,
        "error_rows": 5,
        "unique_clients": 193,
        "date_range": {
            "start": "2025-03-01",
            "end": "2025-09-24"
        }
    },
    "errors": [
        {
            "row": 742,
            "field": "Account",
            "error": "Missing client name (Journal entry)",
            "value": ""
        },
        {
            "row": 855,
            "field": "Date",
            "error": "Invalid date format",
            "value": "invalid"
        }
    ],
    "warnings": [
        {
            "message": "5 Journal entries have no Account (will use 'Unassigned')"
        }
    ]
}
```

**Response (Validation Failed):**
```json
{
    "valid": false,
    "errors": [
        {
            "row": null,
            "field": null,
            "error": "Missing required column: Date"
        }
    ]
}
```

### Endpoint 2: Import Data

**Request:**
```http
POST /api/quickbooks/import/
Content-Type: multipart/form-data

file: quickbooks.csv
skip_errors: true
```

**Response:**
```json
{
    "success": true,
    "summary": {
        "clients_created": 150,
        "clients_existing": 43,
        "cases_created": 193,
        "transactions_imported": 1258,
        "transactions_skipped": 5,
        "duration_seconds": 12.5
    },
    "errors": [
        {
            "row": 742,
            "error": "Skipped: Invalid date"
        }
    ]
}
```

---

## 📝 Implementation Files

### Backend Files to Create/Modify

1. **`/app/apps/clients/utils/quickbooks_parser.py`** (NEW)
   - CSV parsing logic
   - Validation rules
   - Data extraction

2. **`/app/apps/clients/utils/quickbooks_importer.py`** (NEW)
   - Import orchestration
   - Client/Case/Transaction creation
   - Error handling

3. **`/app/apps/clients/api/views.py`** (MODIFY)
   - Add `/api/quickbooks/validate/` endpoint
   - Add `/api/quickbooks/import/` endpoint

4. **`/app/apps/clients/api/serializers.py`** (MODIFY)
   - Add QuickBooksImportSerializer
   - Add validation serializers

### Frontend Files to Create/Modify

1. **`/usr/share/nginx/html/html/import-quickbooks.html`** (NEW)
   - Import page UI

2. **`/usr/share/nginx/html/js/import-quickbooks.js`** (NEW)
   - Import page logic
   - File upload
   - Validation handling
   - Import progress

3. **`/usr/share/nginx/html/html/index.html`** (MODIFY)
   - Add navigation link to Import page

---

## 🧪 Testing Plan

### Test Data
- Use `quickbooks.csv` (1,263 transactions)
- Use `test_quickbooks_sample.csv` (5 transactions)

### Test Cases

1. **Validation Tests:**
   - Valid CSV → Should show preview
   - Missing columns → Should show error
   - Invalid dates → Should list all invalid rows
   - Empty file → Should show error

2. **Import Tests:**
   - New clients → Should create clients
   - Existing clients → Should create new cases
   - Journal entries → Should create "Unassigned" client
   - Transactions → Should import with correct amounts

3. **Error Handling:**
   - Skip invalid rows
   - Continue after errors
   - Report all errors

---

## 🚀 Implementation Order

### Phase 1: Backend (Today)
1. ✅ Create `quickbooks_parser.py`
2. ✅ Create `quickbooks_importer.py`
3. ✅ Add API endpoints
4. ✅ Test with sample data

### Phase 2: Frontend (Today)
5. ✅ Create import page HTML
6. ✅ Create import page JS
7. ✅ Add navigation link
8. ✅ Test UI flow

### Phase 3: Testing (Today)
9. ✅ Test with quickbooks.csv (1,263 transactions)
10. ✅ Verify data integrity
11. ✅ Create user documentation

---

**Ready to implement!** Starting with backend parser and validator.
