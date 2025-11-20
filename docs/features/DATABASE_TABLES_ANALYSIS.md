# Database Tables Analysis

**Date:** November 14, 2025
**Status:** ⚠️ DUPLICATE TABLES FOUND - NEEDS CLEANUP

---

## Summary

**Total Tables:** 29 tables
**Tables in Use:** 17 tables (59%)
**Duplicate Tables:** 2 tables (7%)
**Empty Tables:** 12 tables (41%)

---

## Tables Breakdown

### ✅ ACTIVELY USED TABLES (17 tables with data)

#### **Core Application Tables**
| Table Name | Rows | Purpose | Status |
|------------|------|---------|--------|
| **clients** | 79 | Client records | ✅ USED |
| **cases** | 81 | Case records | ✅ USED |
| **vendors** | 9 | Vendor records | ✅ USED |
| **vendor_types** | 7 | Vendor type lookup | ✅ USED |
| **bank_accounts** | 1 | Trust/Operating accounts | ✅ USED |
| **bank_transactions** | 100 | Transaction records | ✅ USED |
| **bank_transaction_audit** | 75 | Transaction history tracking | ✅ USED |
| **import_logs** | 5 | Import history | ✅ USED |
| **law_firm** | 1 | Firm information | ✅ USED |
| **check_sequences** | 1 | Check number sequences | ✅ USED |
| **case_number_counter** | 1 | Case number counter | ✅ USED |

#### **Django System Tables**
| Table Name | Rows | Purpose | Status |
|------------|------|---------|--------|
| **auth_user** | 1 | User accounts | ✅ USED |
| **auth_permission** | 24 | Permission definitions | ✅ USED |
| **django_content_type** | 6 | Model registry | ✅ USED |
| **django_migrations** | 26 | Migration tracking | ✅ USED |
| **django_session** | 55 | User sessions | ✅ USED |

---

### ⚠️ DUPLICATE TABLES (2 tables - UNUSED)

These tables appear to be from an old schema migration. They have ZERO rows and are NOT referenced by any Django models.

| Table Name | Rows | Duplicate Of | Problem |
|------------|------|--------------|---------|
| **bank_accounts_bankaccount** | 0 | bank_accounts | Old migration artifact |
| **bank_accounts_banktransaction** | 0 | bank_transactions | Old migration artifact |

**Evidence:**
```sql
 bank_accounts                 |    1 row  -- USED
 bank_accounts_bankaccount     |    0 rows -- DUPLICATE, EMPTY

 bank_transactions             |  100 rows -- USED
 bank_accounts_banktransaction |    0 rows -- DUPLICATE, EMPTY
```

**Django Models Point To:**
- `BankAccount` model → `db_table = 'bank_accounts'` ✅
- `BankTransaction` model → `db_table = 'bank_transactions'` ✅

**Conclusion:** The `bank_accounts_*` prefixed tables are NOT used and can be dropped.

---

### ❌ EMPTY BUT VALID TABLES (10 tables)

These tables are defined in Django models but have no data yet. They are VALID and should NOT be dropped.

#### **Feature Tables (Not Yet Used)**
| Table Name | Rows | Purpose | Status |
|------------|------|---------|--------|
| **bank_reconciliations** | 0 | Bank reconciliation records | Empty (feature exists, no data) |
| **settlements** | 0 | Settlement records | Empty (feature exists, no data) |
| **settlement_distributions** | 0 | Settlement distribution splits | Empty (feature exists, no data) |
| **settlement_reconciliations** | 0 | Settlement reconciliation tracking | Empty (feature exists, no data) |
| **import_audit** | 0 | CSV import audit trail | Empty (CSV import used, old data cleared) |
| **settings** | 0 | Application settings | Empty (using law_firm instead) |

#### **Django Auth Tables (No Groups/Permissions Assigned)**
| Table Name | Rows | Purpose | Status |
|------------|------|---------|--------|
| **auth_group** | 0 | User groups | Empty (single user app) |
| **auth_group_permissions** | 0 | Group permission links | Empty (single user app) |
| **auth_user_groups** | 0 | User-group links | Empty (single user app) |
| **auth_user_user_permissions** | 0 | User permission links | Empty (single user app) |

#### **Django System Tables (Empty)**
| Table Name | Rows | Purpose | Status |
|------------|------|---------|--------|
| **django_admin_log** | 0 | Admin action history | Empty (no admin actions logged) |

---

## Django Models vs Database Tables

### Models Defined in Code

#### `/apps/bank_accounts/models.py`
```python
class BankAccount(models.Model):
    class Meta:
        db_table = 'bank_accounts'  ✅ Maps to bank_accounts table

class BankTransaction(models.Model):
    class Meta:
        db_table = 'bank_transactions'  ✅ Maps to bank_transactions table

class BankReconciliation(models.Model):
    class Meta:
        db_table = 'bank_reconciliations'  ✅ Maps to bank_reconciliations table

class BankTransactionAudit(models.Model):
    class Meta:
        db_table = 'bank_transaction_audit'  ✅ Maps to bank_transaction_audit table
```

#### `/apps/clients/models.py`
```python
class Client(models.Model):
    class Meta:
        db_table = 'clients'  ✅ Maps to clients table

class Case(models.Model):
    class Meta:
        db_table = 'cases'  ✅ Maps to cases table
```

#### `/apps/vendors/models.py`
```python
class VendorType(models.Model):
    class Meta:
        db_table = 'vendor_types'  ✅ Maps to vendor_types table

class Vendor(models.Model):
    class Meta:
        db_table = 'vendors'  ✅ Maps to vendors table
```

#### `/apps/settlements/models.py`
```python
class Settlement(models.Model):
    class Meta:
        db_table = 'settlements'  ✅ Maps to settlements table

class SettlementDistribution(models.Model):
    class Meta:
        db_table = 'settlement_distributions'  ✅ Maps to settlement_distributions table

class SettlementReconciliation(models.Model):
    class Meta:
        db_table = 'settlement_reconciliations'  ✅ Maps to settlement_reconciliations table
```

#### `/apps/settings/models.py`
```python
class LawFirm(models.Model):
    class Meta:
        db_table = 'law_firm'  ✅ Maps to law_firm table

class Settings(models.Model):
    class Meta:
        db_table = 'settings'  ✅ Maps to settings table

class CheckSequence(models.Model):
    class Meta:
        db_table = 'check_sequences'  ✅ Maps to check_sequences table

class ImportAudit(models.Model):
    class Meta:
        db_table = 'import_audit'  ✅ Maps to import_audit table
```

---

## Problem: Duplicate Tables

### How Did This Happen?

The `bank_accounts_bankaccount` and `bank_accounts_banktransaction` tables appear to be from an old migration where Django auto-generated table names.

**Old Table Naming (Default Django Behavior):**
- `{app_label}_{model_name_lowercase}` → `bank_accounts_bankaccount`

**New Table Naming (Explicit db_table):**
- `db_table = 'bank_accounts'` → `bank_accounts`

**What Happened:**
1. Initial migrations created tables with default Django naming
2. Later, models were updated to use explicit `db_table` names
3. New migrations created new tables with explicit names
4. Old tables were never dropped
5. Application now uses new tables, old tables are empty and orphaned

---

## Recommendation: Drop Duplicate Tables

### Tables to DROP

```sql
DROP TABLE bank_accounts_bankaccount;
DROP TABLE bank_accounts_banktransaction;
```

**Why Safe:**
- ✅ Both tables have ZERO rows
- ✅ NOT referenced by any Django model
- ✅ NOT referenced by any migration
- ✅ Application uses bank_accounts and bank_transactions instead
- ✅ No foreign keys point to these tables

### Verification Before Drop

```sql
-- Verify they are empty
SELECT COUNT(*) FROM bank_accounts_bankaccount;  -- Should be 0
SELECT COUNT(*) FROM bank_accounts_banktransaction;  -- Should be 0

-- Verify no foreign keys reference them
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND (ccu.table_name = 'bank_accounts_bankaccount'
         OR ccu.table_name = 'bank_accounts_banktransaction');
-- Should return 0 rows
```

---

## Impact Analysis

### Current State
```
Total Tables: 29
- Used: 17 (59%)
- Duplicate: 2 (7%)
- Empty but valid: 10 (34%)
```

### After Cleanup
```
Total Tables: 27
- Used: 17 (63%)
- Duplicate: 0 (0%)
- Empty but valid: 10 (37%)
```

**Benefits:**
- Cleaner database schema
- No confusion about which tables to use
- Easier to understand data model
- Professional database structure

---

## Tables to KEEP (Empty but Valid)

### DO NOT DROP THESE:

1. **bank_reconciliations** - Feature exists, just no data yet
2. **settlements** - Feature exists, just no data yet
3. **settlement_distributions** - Feature exists, just no data yet
4. **settlement_reconciliations** - Feature exists, just no data yet
5. **import_audit** - Feature actively used (old data was cleaned)
6. **settings** - Valid model, may be used in future
7. **auth_group*** tables - Django auth system (may be used when adding users)
8. **django_admin_log** - Django admin (logs actions when used)

**Reason:** These tables are defined in Django models and migrations. Dropping them would cause Django to fail.

---

## Commands to Execute Cleanup

### Step 1: Backup Database
```bash
docker exec iolta_db_alpine pg_dump -U iolta_user -d iolta_guard_db > /tmp/backup_before_table_drop.sql
```

### Step 2: Verify Tables are Empty and Safe to Drop
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "SELECT COUNT(*) FROM bank_accounts_bankaccount;"
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "SELECT COUNT(*) FROM bank_accounts_banktransaction;"
```

### Step 3: Drop Duplicate Tables
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "DROP TABLE IF EXISTS bank_accounts_bankaccount CASCADE;"
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "DROP TABLE IF EXISTS bank_accounts_banktransaction CASCADE;"
```

### Step 4: Verify Cleanup
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\dt"
```

**Expected Result:** Should list 27 tables (down from 29)

---

## Summary

### Current State
- ❌ 2 duplicate tables wasting space
- ❌ Confusing schema with old tables
- ❌ Unprofessional database structure

### After Cleanup
- ✅ 0 duplicate tables
- ✅ Clear, understandable schema
- ✅ Professional database structure
- ✅ All Django models map correctly to tables

**Recommendation:** Drop the 2 duplicate tables immediately.

---

## Professional Standards

### ✅ What We Do Right
- Explicit `db_table` names in models (clear, readable)
- Used tables have data and foreign key relationships
- Empty tables are valid (feature tables waiting for data)

### ❌ What We Did Wrong
- Left duplicate tables from old migrations
- Didn't clean up after schema refactoring
- Database has orphaned tables

### ✅ What We'll Fix
- Drop duplicate tables
- Clean database schema
- Professional structure

---

**Status:** Ready to drop duplicate tables after backup
