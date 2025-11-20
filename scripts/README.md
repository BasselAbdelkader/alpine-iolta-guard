# IOLTA Guard - Scripts

This directory contains scripts used for one-time modifications and fixes.

**Location:** `/home/amin/Projects/ve_demo/scripts/`

---

## 📁 Directory Structure

### **archive/**
Contains one-time fix scripts that have already been applied.

**Status:** Historical record (already executed)

**Purpose:** Keep for reference in case rollback or similar changes needed

---

## 📋 Archived Fix Scripts

All scripts in `archive/` have been **executed once** to apply fixes. They are kept for reference only.

### **1. fix_case_transactions_view.py** (1.5 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed missing $ sign in case transaction amounts and balances

**What it did:**
- Modified `/app/apps/clients/views.py`
- Updated `case_transactions()` function
- Added $ sign to deposit amounts
- Added $ sign to withdrawal amounts (inside parentheses)
- Added $ sign to balance displays

**Changes:**
```python
# BEFORE:
amount_display = f'{item.amount:,.2f}'
balance_display = f"{running_balance:,.2f}"

# AFTER:
amount_display = f'${item.amount:,.2f}'
balance_display = f"${running_balance:,.2f}"
```

**Related:** See `/docs/CASE_TRANSACTIONS_AMOUNT_BUG_FIX.md`

---

### **2. fix_double_parentheses.py** (890 bytes)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed double parentheses formatting in withdrawals

**What it did:**
- Modified `/app/apps/clients/views.py`
- Changed `($(14,850.00))` to `($14,850.00)`
- Fixed withdrawal amount display format
- Fixed negative balance display format

**Changes:**
```python
# BEFORE:
amount_display = f'($({item.amount:,.2f}))'

# AFTER:
amount_display = f'(${item.amount:,.2f})'
```

**Related:** See `/docs/CASE_TRANSACTIONS_AMOUNT_BUG_FIX.md`

---

### **3. fix_formatted_balance.py** (1.2 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed missing $ sign in `formatted_balance` field for Case and Client models

**What it did:**
- Modified `/app/apps/clients/models.py`
- Updated `get_formatted_balance()` in Client model
- Updated `get_formatted_balance()` in Case model
- Added $ sign to all balance formatting

**Changes:**
```python
# BEFORE:
return f"{balance:,.2f}"

# AFTER:
return f"${balance:,.2f}"
```

**Related:** See `/docs/FORMATTED_BALANCE_BUG_FIX.md`

---

### **4. modify_bank_views.py** (1.0 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Updated bank account views to use new field names

**What it did:**
- Modified `/app/apps/bank_accounts/api/views.py`
- Changed `transaction_number` to `RefNo` in custom views
- Removed `case_number` field (kept only `case_title`)
- Updated balance_history() and audit_history() methods

**Changes:**
```python
# BEFORE:
'transaction_number': transaction.transaction_number,
'case_number': transaction.case.case_number,

# AFTER:
'RefNo': transaction.transaction_number,
'case_title': transaction.case.case_title,
```

**Related:** See `/docs/FIELD_REPLACEMENT_SUMMARY.md`

---

### **5. modify_client_serializers.py** (1.6 KB)
**Date:** November 7, 2025
**Applied:** ❌ No (superseded by v3)

**Purpose:** Initial attempt to modify client serializers

**Status:** Superseded by `modify_client_serializers_v3.py`

---

### **6. modify_client_serializers_v2.py** (1.9 KB)
**Date:** November 7, 2025
**Applied:** ❌ No (superseded by v3)

**Purpose:** Second attempt to modify client serializers

**Status:** Superseded by `modify_client_serializers_v3.py` (syntax error)

---

### **7. modify_client_serializers_v3.py** (1.9 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Successfully modified client serializers for field replacement

**What it did:**
- Modified `/app/apps/clients/api/serializers.py`
- Added `to_representation()` to CaseSerializer
- Added `to_representation()` to CaseListSerializer
- Removed `case_number` from output (kept only `case_title`)

**Changes:**
```python
def to_representation(self, instance):
    """Override to remove case_number from output"""
    data = super().to_representation(instance)

    # Remove case_number (only return case_title)
    if 'case_number' in data:
        data.pop('case_number')

    return data
```

**Related:** See `/docs/FIELD_REPLACEMENT_SUMMARY.md`

---

### **8. modify_client_views.py** (1.3 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Updated client views for field replacement

**What it did:**
- Modified `/app/apps/clients/api/views.py`
- Changed `transaction_number` to `RefNo` in custom views
- Removed `case_number` from response dictionaries
- Updated balance_history() and transactions() methods

**Changes:**
```python
# BEFORE:
'transaction_number': txn.transaction_number,
'case_number': case.case_number,

# AFTER:
'RefNo': txn.transaction_number,
'case_title': case.case_title,
```

**Related:** See `/docs/FIELD_REPLACEMENT_SUMMARY.md`

---

### **9. modify_serializer.py** (2.7 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Updated BankTransactionSerializer for field replacement

**What it did:**
- Modified `/app/apps/bank_accounts/api/serializers.py`
- Updated `to_representation()` method in BankTransactionSerializer
- Renamed `transaction_number` to `RefNo`
- Replaced `case_number` with `case_title`

**Changes:**
```python
# Rename transaction_number to RefNo
if 'transaction_number' in data:
    data['RefNo'] = data.pop('transaction_number')

# Replace case_number with case_title
if 'case_number' in data:
    data.pop('case_number')
    if instance.case:
        data['case_title'] = instance.case.case_title
```

**Related:** See `/docs/FIELD_REPLACEMENT_SUMMARY.md`

---

### **10. fix_case_transactions_api.py** (1.9 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed case ledger showing $0.00 by changing API to return numeric amounts

**What it did:**
- Modified `/app/apps/clients/api/views.py`
- Changed `CaseViewSet.transactions()` method (line 364)
- Changed from `format_us_money()` to `float()` for amount field
- Frontend can now parse amounts for running balance calculation

**Changes:**
```python
# BEFORE:
amount = format_us_money(0) if txn.status == 'voided' else format_us_money(txn.amount)
# Returns: "$45,000.00" (STRING - parseFloat() fails)

# AFTER:
amount = float(0) if txn.status == 'voided' else float(txn.amount)
# Returns: 45000.0 (NUMBER - parseFloat() works)
```

**Related:** See `/docs/CASE_LEDGER_ZERO_AMOUNTS_FIX.md`

---

### **11. fix_bank_transaction_serializer.py** (1.3 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed bank transactions page showing NaN by removing amount formatting

**What it did:**
- Modified `/app/apps/bank_accounts/api/serializers.py`
- Removed `format_us_money()` from BankTransactionSerializer (lines 351-352)
- Amount field now returns parseable strings without $ signs
- Frontend parseFloat() can now work correctly

**Changes:**
```python
# BEFORE:
if data.get('amount') is not None:
    data['amount'] = format_us_money(data['amount'])
# Returns: "$34.78" (STRING - parseFloat() fails)

# AFTER:
# Removed formatting - amount returns as "34.78"
# Returns: "34.78" (STRING - parseFloat() works)
```

**Related:** See `/docs/BANK_TRANSACTIONS_NAN_FIX.md`

---

### **12. fix_bank_transactions_amount_display.sh** (BASH script, 1.2 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed Amount column missing $ sign (visual inconsistency)

**What it did:**
- Modified `/usr/share/nginx/html/js/bank-transactions.js` (FRONTEND)
- Added $ sign to deposit amount displays
- Added $ sign to withdrawal amount displays
- Added $ sign to voided transaction displays

**Changes:**
```javascript
// BEFORE:
amountDisplay = `...>+${amount.toLocaleString...`   // Shows: +34.78
amountDisplay = `...>-${amount.toLocaleString...`   // Shows: -500.00

// AFTER:
amountDisplay = `...>+$${amount.toLocaleString...`  // Shows: +$34.78
amountDisplay = `...>-$${amount.toLocaleString...`  // Shows: -$500.00
```

**Related:** See `/docs/BANK_TRANSACTIONS_AMOUNT_DOLLAR_SIGN_FIX.md`

---

### **13. fix_uncleared_transactions_ref_number.sh** (BASH script, 900 bytes)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Changed "Transaction #" to "Ref #" on uncleared transactions page

**What it did:**
- Modified `/usr/share/nginx/html/js/uncleared-transactions.js` (FRONTEND)
- Changed column header: "Transaction #" → "Ref #"
- Changed data field: `transaction_number` → `reference_number`
- Now displays check numbers instead of internal IDs

**Changes:**
```javascript
// BEFORE:
<th>Transaction #</th>
${txn.transaction_number || '-'}   // Shows: 263 (internal ID)

// AFTER:
<th>Ref #</th>
${txn.reference_number || '-'}     // Shows: CHK-1234 (check number)
```

**Related:** See `/docs/UNCLEARED_TRANSACTIONS_REF_NUMBER_FIX.md`

---

### **14. fix_uncleared_transactions_case_title.py** (1.5 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed uncleared transactions to show case title instead of case number

**What it did:**
- Modified `/app/apps/dashboard/api/views.py` (BACKEND)
- Changed variable: `case_number` → `case_title`
- Changed data source: `txn.case.case_number` → `txn.case.case_title`
- API now returns descriptive case titles

**Changes:**
```python
# BEFORE:
case_number = txn.case.case_number if txn.case else None
'case': case_number,  # Returns: "CASE-001"

# AFTER:
case_title = txn.case.case_title if txn.case else None
'case': case_title,   # Returns: "Slip and Fall - Commercial Property"
```

**Related:** See `/docs/UNCLEARED_TRANSACTIONS_CASE_TITLE_FIX.md`

---

### **15. fix_client_ledger_dropdown.sh** (BASH script, 1.0 KB)
**Date:** November 7, 2025
**Applied:** ✅ Yes

**Purpose:** Fixed client dropdown showing double $$ in balance display

**What it did:**
- Modified `/usr/share/nginx/html/js/client-ledger.js` (FRONTEND)
- Removed extra $ sign from balance display on line 78
- Frontend was adding $ to formatted_balance which already has $

**Changes:**
```javascript
// BEFORE:
option.textContent = `${client.full_name} (Balance: $${client.formatted_balance})`;
// Results in: "John Doe (Balance: $$1,234.56)"

// AFTER:
option.textContent = `${client.full_name} (Balance: ${client.formatted_balance})`;
// Results in: "John Doe (Balance: $1,234.56)"
```

**Related:** See `/docs/CLIENT_LEDGER_DROPDOWN_FIX.md`

---

## ⚠️ Important Notes

### **Do NOT Re-run These Scripts**
All scripts in `archive/` have already been executed. Running them again may:
- Cause errors (looking for fields that no longer exist)
- Duplicate changes
- Break functionality

### **Purpose of Keeping Them**
These scripts are kept for:
1. **Reference** - See exactly what changes were made
2. **Rollback** - Understand how to reverse changes if needed
3. **Similar Changes** - Use as templates for future modifications

### **Backup Files**
Original files were backed up before modifications:
- `/app/apps/bank_accounts/api/serializers.py.backup`
- `/app/apps/bank_accounts/api/views.py.backup`
- `/app/apps/clients/api/serializers.py.backup`
- `/app/apps/clients/api/views.py.backup`
- `/app/apps/clients/models.py.backup`

To restore a backup:
```bash
docker exec iolta_backend_alpine cp /app/path/to/file.py.backup /app/path/to/file.py
docker restart iolta_backend_alpine
```

---

## 🔗 Related Documentation

See `/home/amin/Projects/ve_demo/docs/` for:
- Complete implementation summaries
- Bug fix reports with before/after comparisons
- Test results

---

## 📊 Summary

| Script | Status | Files Modified |
|--------|--------|----------------|
| fix_case_transactions_view.py | ✅ Applied | views.py |
| fix_double_parentheses.py | ✅ Applied | views.py |
| fix_formatted_balance.py | ✅ Applied | models.py |
| modify_bank_views.py | ✅ Applied | bank views.py |
| modify_client_serializers_v3.py | ✅ Applied | client serializers.py |
| modify_client_views.py | ✅ Applied | client views.py |
| modify_serializer.py | ✅ Applied | bank serializers.py |
| fix_case_transactions_api.py | ✅ Applied | client api views.py |
| fix_bank_transaction_serializer.py | ✅ Applied | bank serializers.py |
| fix_bank_transactions_amount_display.sh | ✅ Applied | bank-transactions.js (frontend) |
| fix_uncleared_transactions_ref_number.sh | ✅ Applied | uncleared-transactions.js (frontend) |
| fix_uncleared_transactions_case_title.py | ✅ Applied | dashboard api views.py |
| fix_client_ledger_dropdown.sh | ✅ Applied | client-ledger.js (frontend) |

**Total Files Modified:** 9 unique files (6 backend, 3 frontend)
**All Changes:** Successfully applied and tested

---

**Last Updated:** November 7, 2025
