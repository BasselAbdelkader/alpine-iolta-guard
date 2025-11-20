# IOLTA Guard - Database Reset & Test Data Guide

## 🎯 Overview

This script provides comprehensive database reset and test data setup for localhost development and testing.

## ✅ What the Script Does

### 1. **Database Reset**
- ✅ Drops ALL existing data from localhost database
- ✅ Resets primary sequences to start at **1001**
- ✅ Clean slate for testing

### 2. **Bank Account Setup**
- ✅ Creates **ONE** IOLTA-compliant bank account
- ✅ Realistic banking information:
  - Account Number: 1234567890
  - Bank Name: First National Bank
  - Account Type: IOLTA Trust Account
  - Routing Number: 021000021

### 3. **Initial Transaction (Creates Differential)**
- ✅ Creates **ONE** transaction with **NO CLIENT** assigned
- ✅ Amount: **$100.00 deposit**
- ✅ Status: CLEARED
- ✅ This creates the $100 differential between:
  - **Trust Balance** (client balances sum)
  - **Bank Register** (bank account balance)

### 4. **Comprehensive Test Data**

#### Clients
- ✅ **15 clients** with realistic names
- ✅ Complete contact information (email, phone, address)
- ✅ IOLTA-compliant data

#### Cases
- ✅ **20-30 cases** across clients
- ✅ Various case types:
  - Personal Injury
  - Real Estate Transaction
  - Estate Planning
  - Family Law Settlement
  - Business Litigation
  - Employment Dispute
  - Insurance Claim
  - Contract Dispute
  - Probate Matter

#### Vendors
- ✅ **12 vendors/payees** with realistic business names
- ✅ Contact information and addresses

#### Transactions (50-70+ transactions)
- ✅ **DEPOSIT transactions** (30-40):
  - Multiple deposits per case
  - Realistic amounts ($1,000 - $50,000)
  - Various dates over past 6 months

- ✅ **WITHDRAWAL transactions** (20-30):
  - Payments to vendors
  - Realistic amounts
  - Ensures positive balances

- ✅ **VOIDED transactions** (15+):
  - Various void reasons:
    - Duplicate entry
    - Incorrect amount
    - Client request
    - Administrative correction
    - Bank error correction

- ✅ **Transaction States**:
  - **CLEARED**: Majority of transactions
  - **PENDING**: 20-30% of active transactions
  - **VOIDED**: 10-15 transactions

### 5. **Audit Trail**
- ✅ **Complete audit records** for EVERY transaction
- ✅ Tracks ALL changes:
  - Initial creation
  - Status changes (PENDING → CLEARED)
  - Void operations
- ✅ Full history in `auditlog_logentry` table

### 6. **Data Validation**
- ✅ All case balances remain **positive** (no negative balances)
- ✅ All data is IOLTA-compliant
- ✅ Realistic amounts and dates
- ✅ Proper audit trail for compliance

---

## 🚀 Usage

### Quick Run

```bash
# Navigate to project directory
cd /Users/bassel/Documents/current/iolta-guard-production-v2

# Run the script
python3 reset_database_with_test_data.py
```

### What You'll See

```
======================================================================
  IOLTA Guard - Database Reset & Test Data Setup
  Environment: localhost
======================================================================

======================================================================
  Clearing All Existing Data
======================================================================
✓ Cleared audit logs
✓ Cleared transactions
✓ Cleared cases
✓ Cleared clients
✓ Cleared vendors
✓ Cleared bank accounts

======================================================================
  Resetting Database Sequences
======================================================================
✓ Reset clients_client_id_seq to 1001
✓ Reset clients_case_id_seq to 1001
✓ Reset bank_accounts_transaction_id_seq to 1001
... (all sequences reset)

======================================================================
  Creating IOLTA Bank Account
======================================================================
✓ Created bank account: First National Bank
  → Account Number: 1234567890
  → Account Type: IOLTA Trust Account
  → Initial Balance: $0.00

======================================================================
  Creating Clients and Cases
======================================================================
✓ Created client: John Anderson with 2 case(s)
✓ Created client: Sarah Mitchell with 1 case(s)
✓ Created client: Michael Thompson with 3 case(s)
... (15 clients total)

======================================================================
  Creating Vendors
======================================================================
✓ Created vendor: Medical Records Inc.
✓ Created vendor: Court Reporter Services LLC
... (12 vendors total)

======================================================================
  Creating Initial Unassigned Transaction
======================================================================
  → This creates the $100 differential between trust and bank register
✓ Created unassigned transaction: $100.00
  → Transaction ID: 1001
  → Status: CLEARED
  → This creates $100 differential (in bank but not in client trust)

======================================================================
  Creating Comprehensive Transaction Test Data
======================================================================
  → Creating DEPOSITS...
✓ Created 35 deposit transactions
  → Creating WITHDRAWALS...
✓ Created 22 withdrawal transactions
  → Creating VOIDED transactions...
✓ Created 15 voided transactions

======================================================================
  Transaction Summary
======================================================================
  → Total Transactions: 72
  →   - Deposits: 35
  →   - Withdrawals: 22
  →   - Voided: 15
  →   - Cleared: 45
  →   - Pending: 12

======================================================================
  Creating Comprehensive Audit Trails
======================================================================
✓ Created 105 audit log entries
  → All transactions have complete audit trails

======================================================================
  Data Validation
======================================================================
  → Bank Accounts: 1
✓ ✓ Exactly 1 bank account created
  → Clients: 15
✓ ✓ 15 clients created
  → Cases: 28
✓ ✓ 28 cases created
  → Vendors: 12
✓ ✓ 12 vendors created
  → Total Transactions: 73
  →   - VOIDED: 15
  →   - CLEARED: 45
  →   - PENDING: 13
✓ ✓ 73 transactions created with all states
  → Unassigned Transactions: 1
✓ ✓ $100 differential transaction created (unassigned to client)
  → Audit Log Entries: 105
✓ ✓ Complete audit trails created (105 entries)
✓ ✓ All case balances are positive

======================================================================
  ✅ ALL VALIDATIONS PASSED
======================================================================

======================================================================
  🎉 DATABASE RESET COMPLETE!
======================================================================
✓ Database reset successfully with comprehensive test data
✓ Ready for testing with realistic IOLTA-compliant data
```

---

## 📊 Expected Database State

### After Running Script

| Component | Count | Details |
|-----------|-------|---------|
| **Bank Accounts** | 1 | IOLTA Trust Account |
| **Clients** | 15 | With contact info |
| **Cases** | 20-30 | Various types |
| **Vendors** | 12 | Payees for withdrawals |
| **Transactions** | 70+ | Mixed types/states |
| **Audit Entries** | 100+ | Complete history |

### Transaction Breakdown

| Type | Count | Percentage |
|------|-------|------------|
| **Deposits** | 35-40 | ~50% |
| **Withdrawals** | 20-25 | ~30% |
| **Voided** | 15 | ~20% |

### Transaction States

| Status | Count | Percentage |
|--------|-------|------------|
| **CLEARED** | 45-50 | ~65% |
| **PENDING** | 10-15 | ~15% |
| **VOIDED** | 15 | ~20% |

---

## 🔍 Verify the Data

### Check Trust Balance vs Bank Register

```bash
# Login to application
# Navigate to Dashboard

# You should see:
Trust Balance: $XX,XXX.XX (sum of all client balances)
Bank Register: $XX,XXX.XX + $100.00 (includes unassigned $100)

# Difference: $100.00
```

### Check Transaction Types

```sql
-- In database
SELECT
    transaction_type,
    status,
    COUNT(*) as count
FROM bank_accounts_transaction
GROUP BY transaction_type, status
ORDER BY transaction_type, status;
```

Expected output:
```
transaction_type | status  | count
-----------------+---------+-------
DEPOSIT         | CLEARED |   25
DEPOSIT         | PENDING |   10
WITHDRAWAL      | CLEARED |   20
WITHDRAWAL      | PENDING |    5
DEPOSIT         | VOIDED  |    8
WITHDRAWAL      | VOIDED  |    7
```

### Check Unassigned Transaction

```sql
SELECT
    id,
    transaction_date,
    transaction_type,
    amount,
    payee,
    description,
    status
FROM bank_accounts_transaction
WHERE client_id IS NULL AND case_id IS NULL;
```

Expected output:
```
id  | transaction_date | transaction_type | amount  | payee                | status
----+------------------+------------------+---------+----------------------+--------
1001| 2024-XX-XX      | DEPOSIT          | 100.00  | Initial Bank Deposit | CLEARED
```

### Check Audit Trail

```sql
SELECT COUNT(*) FROM auditlog_logentry;
```

Should return: **100+** audit entries

---

## ⚠️ Important Notes

### When to Run This Script

✅ **DO run when:**
- Starting fresh development
- Need clean test data
- Testing new features
- Demonstrating to stakeholders
- QA testing cycles

❌ **DO NOT run when:**
- In production environment
- You have real client data
- During active development with important test data

### Data Characteristics

✅ **All data is:**
- IOLTA-compliant
- Realistic (names, amounts, dates)
- Properly balanced (no negative balances)
- Fully audited (complete history)

✅ **The $100 differential:**
- Represents funds in bank account NOT assigned to any client
- This is realistic for IOLTA accounts (bank fees, interest, etc.)
- Can be tracked and reconciled
- Demonstrates trust vs register difference

---

## 🧪 Testing Scenarios

### Scenario 1: Trust Balance Reconciliation
1. Check Dashboard
2. Verify trust balance
3. Verify bank register balance
4. Confirm $100 differential
5. Find the unassigned transaction

### Scenario 2: Transaction State Changes
1. Find PENDING transactions
2. Mark as CLEARED
3. Verify audit trail updated
4. Check balance recalculation

### Scenario 3: Void Transactions
1. Find CLEARED transaction
2. Void with reason
3. Verify balance adjustment
4. Check audit trail shows void

### Scenario 4: Case Ledgers
1. Select any client
2. View case details
3. Review transaction ledger
4. Verify running balance calculations
5. Check audit trail for each transaction

### Scenario 5: Reports
1. Generate client ledger
2. Generate trust balance report
3. Verify all data appears correctly
4. Export to PDF

---

## 🔧 Customization

### Adjust Transaction Counts

Edit `reset_database_with_test_data.py`:

```python
# Line ~250: Adjust deposits per case
num_deposits = random.randint(2, 4)  # Change to (5, 10) for more

# Line ~320: Adjust withdrawals per case
num_withdrawals = random.randint(1, 3)  # Change to (2, 5) for more

# Line ~380: Adjust voided transactions
for i in range(15):  # Change to range(50) for more voided
```

### Change Initial Differential

```python
# Line ~50
INITIAL_DIFFERENTIAL = Decimal('100.00')  # Change to any amount
```

### Add More Clients

```python
# Line ~60-80: Extend CLIENT_NAMES list
CLIENT_NAMES = [
    # Add more names...
]
```

---

## 📞 Support

### Troubleshooting

**Issue: ModuleNotFoundError**
```bash
# Ensure Django environment is set up
cd trust_account
python3 manage.py shell < ../reset_database_with_test_data.py
```

**Issue: Database connection failed**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check database exists
psql -U bank_user -d bank_account_db -c "SELECT 1"
```

**Issue: Permission denied**
```bash
# Make script executable
chmod +x reset_database_with_test_data.py
```

---

## ✅ Verification Checklist

After running script, verify:

- [ ] Bank account exists with correct details
- [ ] 15 clients created
- [ ] 20+ cases created
- [ ] 12 vendors created
- [ ] 70+ transactions created
- [ ] Transaction states: CLEARED, PENDING, VOIDED all present
- [ ] Unassigned $100 transaction exists
- [ ] Trust balance ≠ Bank register (by $100)
- [ ] All case balances are positive
- [ ] Audit trail complete (100+ entries)
- [ ] Can login and view dashboard
- [ ] Can view client ledgers
- [ ] Can view transaction details
- [ ] Audit trail shows for each transaction

---

*Database Reset Guide*
*Version: 1.0*
*Last Updated: 2025-10-12*
*For: IOLTA Guard Trust Account Management System*
