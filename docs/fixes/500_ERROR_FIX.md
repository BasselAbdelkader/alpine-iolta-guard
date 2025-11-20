# 500 Error Fix - Vendors and Transactions Pages

**Date:** November 10, 2025
**Status:** ✅ **FIXED**
**Issue:** Server Error (500) on vendors and transactions pages

---

## 🐛 Problem

**Error Message:**
```
django.db.utils.ProgrammingError: column bank_accounts.data_source does not exist
LINE 1: ..."next_check_number", "bank_accounts"."is_active", "bank_acco...
```

**Pages Affected:**
- `/vendors` - Vendors management page
- `/bank-accounts` - Bank transactions page (likely)
- Any page that queries BankAccount model

**Root Cause:**
When implementing data source tracking, we added the `data_source` field to:
- ✅ `clients` table
- ✅ `cases` table
- ✅ `vendors` table
- ✅ `bank_transactions` table
- ❌ **MISSING**: `bank_accounts` table

But we also added the field to the `BankAccount` Django model, creating a mismatch between the model definition and the actual database schema.

---

## ✅ Solution Applied

### 1. Added data_source Column to bank_accounts Table

```sql
ALTER TABLE bank_accounts
ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'webapp';

COMMENT ON COLUMN bank_accounts.data_source IS 'Source of data: webapp (default), csv, api';
```

### 2. Verified Django Model

The `BankAccount` model in `/app/apps/bank_accounts/models.py` already had the field added:

```python
class BankAccount(models.Model):
    # ... other fields ...
    is_active = models.BooleanField(default=True)
    data_source = models.CharField(
        max_length=20,
        choices=[
            ('webapp', 'Web Application'),
            ('csv', 'CSV Import'),
            ('api', 'API')
        ],
        default='webapp',
        help_text='Source of data entry'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3. Restarted Backend

```bash
docker restart iolta_backend_alpine
```

---

## ✅ Verification

### All Models Have data_source Field:
```
✅ BankAccount has data_source: True
✅ Client has data_source: True
✅ Case has data_source: True
✅ Vendor has data_source: True
✅ BankTransaction has data_source: True
```

### All Database Tables Have data_source Column:
```
Table              | Has Field
-------------------|----------
clients            | ✅ true
cases              | ✅ true
vendors            | ✅ true
bank_accounts      | ✅ true
bank_transactions  | ✅ true
```

### Current Data Distribution:
```
Table              | Source  | Count
-------------------|---------|------
bank_accounts      | webapp  | 1
bank_transactions  | webapp  | 100
cases              | webapp  | 81
clients            | webapp  | 79
vendors            | webapp  | 9
```

All existing data correctly marked as `webapp` source.

---

## 🎯 Result

**✅ Fixed:**
- Vendors page now loads without errors
- Transactions page now loads without errors
- All pages querying BankAccount work correctly
- Data source tracking is complete across ALL tables

**Pages Working:**
- ✅ `/vendors` - Loads successfully
- ✅ `/bank-accounts` - Loads successfully
- ✅ `/clients` - Loads successfully
- ✅ `/dashboard` - Loads successfully

---

## 📝 Lessons Learned

**When adding fields to Django models:**
1. ✅ Add column to database first (or use migrations)
2. ✅ Add field to Django model
3. ✅ Restart Django application
4. ✅ Verify both model AND database have the field
5. ✅ Test all affected pages

**Complete checklist for multi-table changes:**
- [ ] Identify ALL tables that need the new field
- [ ] Add column to ALL tables (not just some)
- [ ] Update ALL corresponding Django models
- [ ] Verify no model/database mismatches remain
- [ ] Test all pages that query those models

---

## 🔗 Related Files

**Modified:**
- `/app/apps/bank_accounts/models.py` - BankAccount model (data_source field)
- Database: `bank_accounts` table (data_source column)

**Related Documentation:**
- `DATA_SOURCE_TRACKING_GUIDE.md` - Complete guide to data source tracking
- `add_data_source_tracking.sql` - SQL script for all changes

---

**Status:** ✅ RESOLVED - All pages working correctly
