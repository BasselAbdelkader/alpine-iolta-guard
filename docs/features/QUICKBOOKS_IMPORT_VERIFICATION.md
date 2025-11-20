# QuickBooks Import - Verification Guide

**Date:** November 10, 2025
**Purpose:** How to verify QuickBooks import and understand what data is created

---

## 🔍 What Gets Created During Import

### 1. **Clients** ✅ YES
- **Source:** Account Name column in QuickBooks CSV
- **How:** Name is split into first_name and last_name
- **Logic:**
  - If client exists (matching first+last name) → Use existing
  - If new → Create with client_number format: `QB-0001`, `QB-0002`, etc.

**Example:**
```
QuickBooks: "John Smith"
→ Client: first_name="John", last_name="Smith", client_number="QB-0001"
```

### 2. **Cases** ✅ YES
- **Created:** One case per client
- **Format:** `{Client Name} Case`
- **Case Number:** `QB-{timestamp}-{client_id}`
- **Status:** Open
- **Opened Date:** Date of first transaction for that client

**Example:**
```
Client: "John Smith"
→ Case: case_title="John Smith Case", case_number="QB-20251110134500-123"
```

### 3. **Transactions** ✅ YES
- **Created:** All transactions from CSV
- **Linked to:** Bank Account, Client, Case
- **Fields Populated:**
  - `bank_account` → First bank account in system
  - `client` → Client from Account Name
  - `case` → Case created for this client
  - `transaction_date` → Date from CSV
  - `transaction_type` → "Withdrawal" or "Deposit"
  - `amount` → Payment or Deposit amount
  - `payee` → Payee column
  - `check_number` → Ref No column
  - `description` → Memo column
  - `status` → "Cleared" or "Pending"

### 4. **Vendors** ❌ NO
- **NOT Created:** Payee names are stored as text in transaction.payee field
- **Reason:** Vendors are separate entities with addresses, tax IDs, etc.
- **What Happens:** Payee name is just copied to the transaction record

---

## 📊 How to Verify Import Results

### Quick Check - Database Counts

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  'Before' as period,
  79 as clients,
  81 as cases,
  100 as transactions
UNION ALL
SELECT
  'After' as period,
  (SELECT COUNT(*) FROM clients) as clients,
  (SELECT COUNT(*) FROM cases) as cases,
  (SELECT COUNT(*) FROM bank_transactions) as transactions;
"
```

**Expected Output:**
```
 period | clients | cases | transactions
--------+---------+-------+--------------
 Before |      79 |    81 |          100
 After  |     XXX |   XXX |          XXX  ← Should be higher
```

### Detailed Check - QuickBooks Data

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  (SELECT COUNT(*) FROM clients WHERE client_number LIKE 'QB-%') as qb_clients,
  (SELECT COUNT(*) FROM cases WHERE case_number LIKE 'QB-%') as qb_cases,
  (SELECT COUNT(*) FROM bank_transactions
   WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%')) as qb_transactions;
"
```

**What to Look For:**
- `qb_clients`: Number of NEW clients created (with QB- prefix)
- `qb_cases`: Number of cases created from import
- `qb_transactions`: Number of transactions imported

### Check Sample Clients

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  client_number,
  first_name || ' ' || last_name as full_name,
  created_at::date as created
FROM clients
WHERE client_number LIKE 'QB-%'
ORDER BY created_at DESC
LIMIT 10;
"
```

### Check Sample Cases

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  c.case_number,
  c.case_title,
  cl.first_name || ' ' || cl.last_name as client_name,
  c.opened_date,
  (SELECT COUNT(*) FROM bank_transactions WHERE case_id = c.id) as transaction_count
FROM cases c
JOIN clients cl ON c.client_id = cl.id
WHERE c.case_number LIKE 'QB-%'
ORDER BY c.created_at DESC
LIMIT 10;
"
```

### Check Sample Transactions

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  bt.transaction_date,
  bt.transaction_type,
  bt.amount,
  bt.payee,
  cl.first_name || ' ' || cl.last_name as client_name,
  ca.case_title
FROM bank_transactions bt
JOIN clients cl ON bt.client_id = cl.id
JOIN cases ca ON bt.case_id = ca.id
WHERE ca.case_number LIKE 'QB-%'
ORDER BY bt.created_at DESC
LIMIT 10;
"
```

---

## 🌐 Verify in Web Interface

### 1. Check Clients Page
```
URL: http://localhost/clients
```

**Look for:**
- New clients with numbers like "QB-0001", "QB-0002"
- Names matching your QuickBooks data

### 2. Check Client Detail
```
URL: http://localhost/clients/{id}
```

**Look for:**
- Case with title: "{Client Name} Case"
- Transactions list showing imported transactions
- Correct balances

### 3. Check Case Detail
```
URL: http://localhost/cases/{id}
```

**Look for:**
- Transaction list (should be ordered oldest-first)
- Correct amounts
- Payee names
- Status (Cleared/Pending)

### 4. Check Bank Transactions
```
URL: http://localhost/bank-transactions
```

**Look for:**
- New transactions added today
- Linked to QuickBooks cases

---

## 🧹 Clean Up Partial Import (If Needed)

If the import failed partway and you want to start fresh:

### Option 1: Restore Full Backup
```bash
cd /home/amin/Projects/ve_demo/backups/
./restore_backup.sh
```

### Option 2: Delete Only QuickBooks Data
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
-- Delete in correct order (foreign keys)
DELETE FROM bank_transactions
WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%');

DELETE FROM cases
WHERE case_number LIKE 'QB-%';

DELETE FROM clients
WHERE client_number LIKE 'QB-%';
"
```

**Verify cleanup:**
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  (SELECT COUNT(*) FROM clients WHERE client_number LIKE 'QB-%') as qb_clients,
  (SELECT COUNT(*) FROM cases WHERE case_number LIKE 'QB-%') as qb_cases,
  (SELECT COUNT(*) FROM bank_transactions
   WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%')) as qb_transactions;
"
```

**Expected:** All counts should be 0

---

## 📋 Import Summary Template

After import completes, run this to get a summary:

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
-- QuickBooks Import Summary
SELECT '=== QUICKBOOKS IMPORT SUMMARY ===' as title;

SELECT
  'Clients Created' as metric,
  COUNT(*) as count
FROM clients
WHERE client_number LIKE 'QB-%'
UNION ALL
SELECT
  'Clients Matched (Existing)' as metric,
  COUNT(DISTINCT bt.client_id) -
  (SELECT COUNT(*) FROM clients WHERE client_number LIKE 'QB-%') as count
FROM bank_transactions bt
JOIN cases ca ON bt.case_id = ca.id
WHERE ca.case_number LIKE 'QB-%'
UNION ALL
SELECT
  'Cases Created' as metric,
  COUNT(*) as count
FROM cases
WHERE case_number LIKE 'QB-%'
UNION ALL
SELECT
  'Transactions Imported' as metric,
  COUNT(*) as count
FROM bank_transactions
WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%')
UNION ALL
SELECT
  'Total Deposits' as metric,
  SUM(amount)::integer as count
FROM bank_transactions
WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%')
  AND transaction_type = 'Deposit'
UNION ALL
SELECT
  'Total Withdrawals' as metric,
  SUM(amount)::integer as count
FROM bank_transactions
WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%')
  AND transaction_type = 'Withdrawal';
"
```

---

## ⚠️ Common Issues

### Issue: No New Clients Created
**Reason:** All clients matched existing names
**Check:** Look at `clients_existing` count in import summary

### Issue: Transactions Missing
**Reason:** Validation errors or wrong transaction type mapping
**Check:** Import errors list shows which rows failed

### Issue: Wrong Balances
**Reason:** Transaction type mapping incorrect (Deposit vs Withdrawal)
**Check:** Review transaction types in QuickBooks vs IOLTA Guard

### Issue: Payees Not Showing in Vendors
**Expected Behavior:** Payees are NOT vendors, they're just text in transactions
**Solution:** Manually create vendor records if needed

---

## 🎯 Expected Results for Your CSV

Based on `quickbooks_anonymized.csv`:
- **Total Rows:** 1,263 transactions
- **Unique Clients:** 193
- **Expected:**
  - New Clients: ~193 (or less if names match existing)
  - Cases Created: ~193
  - Transactions: ~1,260 (some may have validation errors)

---

## 🔧 Re-Import After Fix

Since the previous import partially failed, you need to:

1. **Clean up partial data:**
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
DELETE FROM bank_transactions
WHERE case_id IN (SELECT id FROM cases WHERE case_number LIKE 'QB-%');
DELETE FROM cases WHERE case_number LIKE 'QB-%';
DELETE FROM clients WHERE client_number LIKE 'QB-%';
"
```

2. **Verify cleanup:**
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  (SELECT COUNT(*) FROM clients) as clients,
  (SELECT COUNT(*) FROM cases) as cases,
  (SELECT COUNT(*) FROM bank_transactions) as transactions;
"
```

**Should show:** clients=79, cases=81, transactions=100 (back to backup state)

3. **Import again:**
- Go to http://localhost/import-quickbooks
- Upload CSV
- Validate
- Import

---

**Status:** ✅ Fixed - Client number generation now handles string format correctly
**Ready to re-import after cleanup!**
