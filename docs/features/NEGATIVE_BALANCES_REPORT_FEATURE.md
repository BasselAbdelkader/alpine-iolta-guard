# Negative Balances Report Feature

**Date:** November 10, 2025
**Feature:** Dedicated page to view and monitor clients with negative trust account balances
**URL:** `http://localhost/negative-balances`

---

## 🎯 PURPOSE

This feature provides a dedicated report page for monitoring clients with negative trust account balances.

### Use Cases:

1. **Compliance Monitoring:** Track IOLTA violations (negative balances not allowed)
2. **Fraud Detection:** Identify potentially fraudulent withdrawals
3. **Data Validation:** Review historical import issues
4. **Audit Trail:** Document negative balances for correction

---

## 📊 WHAT IT SHOWS

### Summary Cards:

1. **Total Clients Affected:** Count of clients with negative balances
2. **Total Negative Amount:** Sum of all negative balances (e.g., -$826,104.13)
3. **Worst Balance:** Most negative balance (e.g., -$77,911.77)

### Detailed Table:

| Column          | Description                                      |
|-----------------|--------------------------------------------------|
| Client Number   | Client's unique identifier (e.g., QB-0021)       |
| Client Name     | Full name (clickable link to client detail)      |
| Balance         | Negative balance amount (in red, bold)           |
| Transactions    | Count of transactions for this client            |
| Source          | Data source badge (CSV Import or Webapp)         |
| Actions         | View client or view transactions buttons         |

---

## 🔗 HOW TO ACCESS

### Direct URL:
```
http://localhost/negative-balances
```

### From Dashboard (TO BE ADDED):

The dashboard should show a warning card with negative balance statistics. Add this link:

**Current Display:**
```
75 clients with negative balances ($826,104.13)
```

**Should Become:**
```html
<a href="/negative-balances" class="text-decoration-none">
    <div class="alert alert-danger">
        <i class="fas fa-exclamation-triangle"></i>
        75 clients with negative balances ($826,104.13)
        <i class="fas fa-arrow-right ms-2"></i>
        View Details
    </div>
</a>
```

---

## 📁 FILES CREATED

### Frontend:

1. **`/usr/share/nginx/html/html/negative-balances.html`**
   - HTML page with layout and structure
   - Includes alert box explaining the issue
   - Summary cards for statistics
   - Table for detailed listing

2. **`/usr/share/nginx/html/js/negative-balances.js`**
   - Fetches all clients from API
   - Filters clients with negative balances
   - Sorts by balance (worst first)
   - Renders the table dynamically

---

## 🎨 FEATURES

### 1. Alert Box

```
⚠️ Trust Account Compliance Alert

The following clients have negative trust account balances.
Trust accounts should never have negative balances as this violates IOLTA regulations.

Possible Causes: Historical data import issues, missing deposits, fraudulent withdrawals,
or data from systems that don't validate insufficient funds.

Action Required: Review each case, verify against bank statements, and add correcting
transactions if needed.
```

### 2. Color Coding

- **Red text** for negative balances
- **Bold** formatting for emphasis
- **Danger border** on summary cards
- **Warning badges** for CSV imported data

### 3. Quick Actions

- **View Client:** Opens client detail page
- **View Transactions:** Opens client page with transactions tab
- **Print Report:** Browser print function

---

## 🔍 TECHNICAL DETAILS

### Data Flow:

1. Page loads → Calls `/v1/clients/?page_size=10000`
2. JavaScript filters `current_balance < 0`
3. Sorts by balance ascending (worst first)
4. Calculates summary statistics
5. Renders table with formatted data

### API Endpoint Used:

```
GET /v1/clients/?page_size=10000
```

Response includes:
- `current_balance`: Calculated balance for each client
- `formatted_balance`: Pre-formatted currency string
- `transaction_count`: Number of transactions
- `data_source`: Origin of data (csv/webapp)

### Performance:

- Loads all clients in one request (up to 10,000)
- Client-side filtering (fast for <1,000 clients)
- No pagination needed (usually <100 negative balances)

---

## 📈 EXAMPLE OUTPUT

### Summary:
```
Total Clients Affected: 75
Total Negative Amount: ($826,104.13)
Worst Balance: ($77,911.77)
```

### Table Sample:
```
Client Number | Client Name      | Balance       | Transactions | Source     | Actions
QB-0021       | Daniel Gonzales  | ($77,911.77)  | 1            | CSV Import | 👁️ 📋
QB-0138       | Pamela Ramos     | ($71,792.80)  | 2            | CSV Import | 👁️ 📋
QB-0094       | Jessica Russell  | ($67,561.66)  | 8            | CSV Import | 👁️ 📋
```

---

## 🔗 INTEGRATION WITH DASHBOARD

### Option 1: Add Link to Existing Alert

If dashboard already shows negative balance count, make it clickable:

**Before:**
```html
<div class="alert alert-danger">
    75 clients with negative balances ($826,104.13)
</div>
```

**After:**
```html
<a href="/negative-balances" class="text-decoration-none">
    <div class="alert alert-danger alert-link">
        <div class="d-flex justify-content-between align-items-center">
            <span>
                <i class="fas fa-exclamation-triangle me-2"></i>
                75 clients with negative balances ($826,104.13)
            </span>
            <span>
                View Report <i class="fas fa-arrow-right"></i>
            </span>
        </div>
    </div>
</a>
```

### Option 2: Add to Reports Menu

Add to navigation sidebar:

```html
<li class="nav-item">
    <a href="/negative-balances" class="nav-link">
        <i class="fas fa-exclamation-triangle text-danger me-2"></i>
        Negative Balances
        <span class="badge bg-danger ms-2">75</span>
    </a>
</li>
```

### Option 3: Add to Dashboard Cards

Create a dedicated dashboard card:

```html
<div class="col-md-3">
    <div class="card border-danger">
        <div class="card-body">
            <h6 class="text-muted">Negative Balances</h6>
            <h3 class="text-danger">75 Clients</h3>
            <p class="mb-0">($826,104.13)</p>
            <a href="/negative-balances" class="btn btn-sm btn-outline-danger mt-2">
                View Report
            </a>
        </div>
    </div>
</div>
```

---

## ✅ TESTING

### Test Cases:

1. **Access Page:**
   - Navigate to `http://localhost/negative-balances`
   - Verify page loads without errors

2. **Summary Cards:**
   - Check "Total Clients" shows 75
   - Check "Total Negative" shows ($826,104.13)
   - Check "Worst Balance" shows ($77,911.77)

3. **Table Display:**
   - Verify 75 rows displayed
   - Check balances shown in red
   - Verify sorting (worst first)

4. **Links Work:**
   - Click client name → Opens client detail page
   - Click "View" button → Opens client page
   - Click "View Transactions" → Opens with transactions

5. **Print Function:**
   - Click "Print Report" button
   - Verify browser print dialog opens

---

## 🚀 FUTURE ENHANCEMENTS

### 1. Export to Excel
```javascript
function exportToExcel() {
    // Convert table to CSV
    // Download as Excel file
}
```

### 2. Email Alerts
```python
# Send email when new negative balance detected
if client.calculate_balance() < 0:
    send_alert_email(admin_emails, client)
```

### 3. Correction Workflow
```
Add "Correct Balance" button that:
1. Shows modal with current balance
2. Calculates needed deposit amount
3. Creates correcting transaction
4. Adds note: "Balance correction for historical data"
```

### 4. Historical Tracking
```sql
-- Track when balance went negative
CREATE TABLE negative_balance_history (
    client_id INT,
    first_detected DATE,
    amount NUMERIC,
    corrected_date DATE,
    correction_note TEXT
);
```

---

## 📝 DOCUMENTATION

### For Users:

**Purpose:** This report helps you identify and monitor clients with negative trust account balances.

**What to Do:**
1. Review each client on the list
2. Click the client name to see their full transaction history
3. Verify against bank statements
4. Add correcting transactions if needed
5. Document the reason for the negative balance

**Why This Matters:**
- Trust accounts legally cannot have negative balances
- Negative balances indicate data issues or potential fraud
- IOLTA audits will flag these as violations

### For Developers:

**Adding New Features:**
1. Update `negative-balances.js` to add new functionality
2. Use existing `api.get('/v1/clients/')` endpoint
3. Filter/sort data client-side for performance
4. Follow existing styling conventions

**Modifying Display:**
1. Edit `negative-balances.html` for layout changes
2. Update `renderNegativeBalancesTable()` for table modifications
3. Modify `formatCurrency()` for number formatting changes

---

## ✅ STATUS

**Implementation:** ✅ COMPLETE
**Testing:** ⏳ PENDING USER VERIFICATION
**Dashboard Link:** ⏳ TO BE ADDED

**Files Created:**
- ✅ `/usr/share/nginx/html/html/negative-balances.html`
- ✅ `/usr/share/nginx/html/js/negative-balances.js`

**Next Steps:**
1. Test the page at `http://localhost/negative-balances`
2. Add link from dashboard
3. Optional: Add to navigation menu
4. Optional: Add email alerts for new negatives

---

**Feature Status:** ✅ READY FOR USE
**User Guide:** This document
**Technical Documentation:** Complete

