# IOLTA Guard - Audit & Compliance Guide

**Document Type:** Compliance Documentation
**Last Updated:** November 13, 2025
**Version:** 1.0
**Target Audience:** Compliance Officers, Auditors, State Bar Regulators, Law Firm Partners

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Regulatory Framework](#regulatory-framework)
3. [System Audit Controls](#system-audit-controls)
4. [Data Integrity & Immutability](#data-integrity--immutability)
5. [Transaction Audit Trail](#transaction-audit-trail)
6. [Compliance Reporting](#compliance-reporting)
7. [Internal Controls](#internal-controls)
8. [Security & Access Controls](#security--access-controls)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [Audit Procedures](#audit-procedures)
11. [Compliance Checklist](#compliance-checklist)

---

## Executive Summary

### Purpose

This document provides comprehensive information about IOLTA Guard's audit controls, compliance features, and regulatory adherence for:
- State bar authorities conducting IOLTA compliance reviews
- External auditors performing financial audits
- Internal compliance officers ensuring regulatory adherence
- Law firm partners responsible for trust account management

### Compliance Overview

IOLTA Guard is designed to meet or exceed requirements for:
- **IOLTA Rules:** State bar regulations for Interest on Lawyers' Trust Accounts
- **ABA Model Rules:** Model Rules of Professional Conduct (Rule 1.15)
- **Financial Auditing:** Generally Accepted Accounting Principles (GAAP)
- **Data Security:** Industry-standard security practices

### Key Compliance Features

✅ **Complete Audit Trail:** Every transaction timestamped and immutable
✅ **No Deletion:** Transactions can be voided but never deleted
✅ **Balance Integrity:** Real-time balance calculation from source transactions
✅ **Client/Case Isolation:** Funds tracked separately by client and matter
✅ **Chronological Ordering:** Transactions displayed in temporal sequence
✅ **Automated Controls:** System prevents negative balances and orphaned transactions
✅ **User Accountability:** All actions tied to authenticated users
✅ **Report Generation:** Comprehensive compliance reports on-demand

---

## Regulatory Framework

### IOLTA (Interest on Lawyers' Trust Accounts) Requirements

**What is IOLTA?**
IOLTA accounts hold client funds in trust, with interest typically directed to state bar foundations for legal aid and access to justice programs.

**Key Regulatory Requirements:**

1. **Separate Accounting:** Each client's funds must be separately accounted for
2. **Detailed Records:** Complete records of deposits, withdrawals, and balances
3. **Immediate Availability:** Funds must be available on demand
4. **No Commingling:** Attorney funds cannot be mixed with client funds
5. **Reconciliation:** Monthly bank reconciliation required
6. **Safekeeping:** Funds held in trust must be protected
7. **Accounting:** Periodic accounting to clients

**IOLTA Guard Compliance:**

| Requirement | How IOLTA Guard Complies |
|-------------|--------------------------|
| Separate Accounting | Each client and case tracked individually with separate balances |
| Detailed Records | Every transaction recorded with date, amount, description, parties |
| Immediate Availability | Real-time balance calculation, instant reporting |
| No Commingling | System enforces client/case assignment for all transactions |
| Reconciliation | Bank reconciliation features with uncleared transaction tracking |
| Safekeeping | Access controls, authentication, audit trails protect data |
| Accounting | Client ledgers, case reports generated on-demand |

### ABA Model Rules of Professional Conduct

**Rule 1.15: Safekeeping Property**

Key provisions:
- Lawyer shall hold property of clients separate from lawyer's own property
- Complete records of client funds shall be kept
- Promptly notify client when funds are received
- Promptly deliver funds when due

**IOLTA Guard Compliance:**

✅ **Separation:** Bank accounts module maintains trust account separation
✅ **Record Keeping:** Comprehensive transaction logging with timestamps
✅ **Notification:** Transaction records support client notification practices
✅ **Prompt Delivery:** Transaction system supports timely fund disbursement
✅ **Accounting:** Client ledger reports provide required accountings

### State-Specific Requirements

**Note:** IOLTA requirements vary by state. Your firm must ensure compliance with your specific jurisdiction's rules. Common variations include:

- **Minimum Balance Thresholds:** Some states require minimum balances
- **Notification Requirements:** Timing of client notification varies
- **Record Retention:** Retention periods range from 5-7 years
- **Reconciliation Frequency:** Monthly reconciliation is standard
- **Audit Requirements:** Some states mandate periodic audits

**IOLTA Guard Design:**
The system is designed to accommodate various state requirements through configurable settings and comprehensive reporting capabilities.

---

## System Audit Controls

### Built-In Audit Features

#### 1. Complete Transaction History

**Feature:** Every financial transaction is permanently recorded.

**Implementation:**
- All transactions stored in `bank_transactions` table
- Fields captured:
  - Transaction ID (unique identifier)
  - Transaction date
  - Transaction type (DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT)
  - Amount
  - Client ID
  - Case ID
  - Bank Account ID
  - Description
  - Payee (for withdrawals)
  - Check number (if applicable)
  - Status (cleared, voided)
  - Void reason (if voided)
  - Created timestamp (when record was created)
  - Updated timestamp (when record was last modified)

**Audit Benefit:** Complete financial history available for review at any time.

#### 2. Immutable Financial Records

**Feature:** Transactions cannot be deleted, only voided.

**Why This Matters:**
- Prevents tampering with financial records
- Maintains complete audit trail
- Voided transactions remain visible with void reason
- Original transaction data preserved

**Implementation:**
- No DELETE operations on `bank_transactions` table
- Void operation sets `status = 'voided'` and adds `void_reason`
- Voided transactions excluded from balance calculations but remain in database
- Void reason required (accountability)

**Database Constraint:**
```sql
-- Application enforces void-only policy
-- Database triggers could be added to prevent DELETE operations
CREATE TRIGGER prevent_transaction_deletion
BEFORE DELETE ON bank_transactions
FOR EACH ROW
EXECUTE FUNCTION raise_exception();
```

**Audit Benefit:** No financial records can be destroyed or hidden.

#### 3. Timestamp Tracking

**Feature:** Creation and modification timestamps on all records.

**Fields:**
- `created_at`: When record was first created (immutable)
- `updated_at`: When record was last modified (auto-updates)

**Implementation:**
```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**Audit Benefit:**
- Establishes timeline of all activities
- Identifies when transactions were entered (vs. transaction date)
- Detects backdating or late entries
- Supports forensic analysis

#### 4. User Attribution

**Feature:** All actions tied to authenticated user.

**Implementation:**
- Session-based authentication required
- User context captured for all transactions
- Authentication log maintained
- Failed login attempts tracked

**Current State:** User ID not explicitly stored in transaction record (future enhancement)

**Recommended Enhancement:**
```python
class BankTransaction(models.Model):
    created_by = models.ForeignKey(User, related_name='transactions_created')
    modified_by = models.ForeignKey(User, related_name='transactions_modified')
```

**Audit Benefit:** Accountability for all financial actions.

#### 5. Balance Calculation Integrity

**Feature:** Balances calculated in real-time from source transactions, never cached.

**Why This Matters:**
- Eliminates risk of balance corruption
- Ensures balance matches transaction history
- Prevents manual balance adjustments
- Always accurate, always auditable

**Implementation:**
```python
def get_current_balance(self):
    """Calculate balance from transactions"""
    deposits = BankTransaction.objects.filter(
        client_id=self.id,
        transaction_type='DEPOSIT'
    ).exclude(status='voided').aggregate(Sum('amount'))['total'] or 0

    withdrawals = BankTransaction.objects.filter(
        client_id=self.id,
        transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT']
    ).exclude(status='voided').aggregate(Sum('amount'))['total'] or 0

    return deposits - withdrawals
```

**Audit Benefit:**
- Balances always match transaction ledger
- No unexplained balance adjustments
- Easy to verify: Sum(deposits) - Sum(withdrawals) = Balance

#### 6. Referential Integrity

**Feature:** All transactions linked to valid client, case, and bank account.

**Database Constraints:**
```sql
-- Foreign key constraints enforce relationships
ALTER TABLE bank_transactions
ADD CONSTRAINT fk_client
FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE PROTECT;

ALTER TABLE bank_transactions
ADD CONSTRAINT fk_case
FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE PROTECT;

ALTER TABLE bank_transactions
ADD CONSTRAINT fk_account
FOREIGN KEY (account_id) REFERENCES bank_accounts(id) ON DELETE PROTECT;
```

**Protection Level:** `ON DELETE PROTECT` prevents deletion of clients/cases with transactions.

**Audit Benefit:**
- No orphaned transactions
- Complete relational integrity
- All transactions traceable to client and matter

---

## Data Integrity & Immutability

### Core Principles

1. **Financial records are immutable:** Once created, transactions cannot be edited or deleted
2. **All changes are additive:** Corrections are new transactions, not edits
3. **Complete history preserved:** Voided transactions remain visible
4. **Temporal integrity:** Timestamps establish sequence of events

### Data Protection Mechanisms

#### 1. Application-Level Controls

**Validation Rules:**
```python
# Client-Case Relationship Validation
if transaction.case.client_id != transaction.client_id:
    raise ValidationError("Case must belong to client")

# Insufficient Funds Prevention
if withdrawal_amount > available_balance:
    raise ValidationError("Insufficient funds")

# Closed Case Protection
if case.status == 'Closed':
    raise ValidationError("Cannot add transactions to closed case")

# Zero Amount Prevention
if amount <= 0:
    raise ValidationError("Amount must be greater than zero")

# Required Fields Enforcement
if not client_id or not case_id:
    raise ValidationError("Client and case required")
```

**Audit Benefit:** System prevents common errors and policy violations.

#### 2. Database-Level Controls

**Constraints:**
```sql
-- Unique client names (prevent duplicates)
ALTER TABLE clients
ADD CONSTRAINT unique_client_name
UNIQUE (first_name, last_name);

-- Unique case numbers
ALTER TABLE cases
ADD CONSTRAINT unique_case_number
UNIQUE (case_number);

-- Positive amounts only
ALTER TABLE bank_transactions
ADD CONSTRAINT positive_amount
CHECK (amount > 0);

-- Required fields
ALTER TABLE bank_transactions
ALTER COLUMN client_id SET NOT NULL,
ALTER COLUMN case_id SET NOT NULL,
ALTER COLUMN account_id SET NOT NULL,
ALTER COLUMN amount SET NOT NULL,
ALTER COLUMN transaction_date SET NOT NULL;
```

**Audit Benefit:** Data integrity enforced at storage layer (defense in depth).

#### 3. Transaction Atomicity

**ACID Properties:**
- **Atomicity:** Complex operations are all-or-nothing
- **Consistency:** Database always in valid state
- **Isolation:** Concurrent operations don't interfere
- **Durability:** Committed data survives failures

**Implementation:**
```python
from django.db import transaction

@transaction.atomic
def transfer_funds(from_case, to_case, amount):
    """Transfer funds between cases atomically"""
    # Both transactions succeed or both fail
    BankTransaction.objects.create(...)  # Withdrawal
    BankTransaction.objects.create(...)  # Deposit
```

**Audit Benefit:** No partial transactions, no inconsistent states.

---

## Transaction Audit Trail

### Transaction Lifecycle

```
1. Transaction Created
   ↓
2. Recorded in database
   ↓
3. Timestamps captured (created_at)
   ↓
4. Balance updated (calculated)
   ↓
5. Transaction appears in ledgers
   ↓
6. [Optional] Transaction voided
   ↓
7. Void reason recorded
   ↓
8. Balance recalculated (excludes voided)
   ↓
9. Voided transaction remains visible
```

### Audit Trail Components

#### 1. Transaction Record

**Essential Data:**
- **Who:** Client, case, payee
- **What:** Transaction type, amount, description
- **When:** Transaction date, created timestamp, updated timestamp
- **Where:** Bank account
- **Why:** Description, memo fields
- **Status:** Cleared, voided
- **Evidence:** Check number, reference numbers

#### 2. Void Trail

**When Transaction is Voided:**
- Original transaction remains in database
- Status changed to 'voided'
- Void reason required and stored
- Updated timestamp recorded
- Voided transaction excluded from balance calculations
- Voided transaction remains in audit reports

**Example:**
```sql
SELECT
    id,
    transaction_date,
    amount,
    description,
    status,
    void_reason,
    created_at,
    updated_at
FROM bank_transactions
WHERE status = 'voided'
ORDER BY updated_at DESC;
```

#### 3. Chronological Ledger

**Transactions Displayed in Temporal Order:**
- Primary sort: `transaction_date` (oldest first)
- Secondary sort: `id` (creation sequence)
- Running balance calculated for each row
- Clear visual audit trail

**Why Oldest-First:**
- Matches accounting conventions
- Shows natural flow of funds
- Easy to trace cause and effect
- Audit-friendly presentation

**Implementation:**
```python
transactions = BankTransaction.objects.filter(
    case_id=case_id
).order_by('transaction_date', 'id')
```

---

## Compliance Reporting

### Standard Reports

#### 1. Client Ledger Report

**Purpose:** Complete transaction history for a client across all cases.

**Contents:**
- Client information
- All cases
- All transactions (chronological)
- Running balances by case
- Total balance

**Use Case:**
- Periodic client accounting
- Response to client requests
- Audit documentation

**Screenshot placeholder:** [URL_HERE - Client Ledger Report]

#### 2. Case Transaction Report

**Purpose:** Transaction history for a specific legal matter.

**Contents:**
- Case information
- All deposits
- All withdrawals
- Running balance
- Current balance

**Use Case:**
- Matter-specific accounting
- Case closing documentation
- Dispute resolution

#### 3. Bank Reconciliation Report

**Purpose:** Match internal records to bank statements.

**Contents:**
- Bank account information
- Cleared transactions
- Uncleared transactions (outstanding checks, deposits in transit)
- Calculated bank balance
- Reconciliation date

**Use Case:**
- Monthly reconciliation
- Audit verification
- Internal controls

#### 4. Negative Balance Report

**Purpose:** Identify any accounts with negative balances (should not exist).

**Contents:**
- Clients with negative balances
- Cases with negative balances
- Amount of overdraft
- Last transaction date

**Use Case:**
- Internal control monitoring
- Error detection
- Compliance verification

**Note:** System should prevent negative balances, so this report should typically be empty.

#### 5. Audit Trail Report

**Purpose:** Complete chronological log of all system activities.

**Contents:**
- All transactions
- Creation timestamps
- User actions
- Status changes
- Void reasons

**Use Case:**
- External audits
- Internal investigations
- Regulatory reviews
- Compliance documentation

#### 6. Unallocated Funds Report

**Purpose:** Identify deposits not yet assigned to specific cases.

**Contents:**
- Deposits without case assignment
- Amount and date
- Days unallocated

**Use Case:**
- Ensure proper fund allocation
- Identify data entry backlog
- Compliance with allocation rules

---

## Internal Controls

### Preventative Controls

**1. Required Client/Case Assignment**
- **Control:** System requires client and case for all transactions
- **Prevents:** Orphaned funds, lost transactions
- **Implementation:** Database NOT NULL constraints + application validation

**2. Insufficient Funds Prevention**
- **Control:** System blocks withdrawals exceeding available balance
- **Prevents:** Negative balances, overdrafts
- **Implementation:** Pre-transaction balance check

**3. Closed Case Protection**
- **Control:** System blocks transactions on closed cases
- **Prevents:** Inadvertent transactions on completed matters
- **Implementation:** Status check before transaction creation

**4. Duplicate Prevention**
- **Control:** Unique constraints on client names, case numbers
- **Prevents:** Duplicate records, data confusion
- **Implementation:** Database unique constraints

**5. Zero Amount Prevention**
- **Control:** Transactions must have amount > 0
- **Prevents:** Meaningless transactions, data clutter
- **Implementation:** Validation rule

### Detective Controls

**1. Balance Reconciliation**
- **Control:** Monthly bank reconciliation required
- **Detects:** Discrepancies, errors, fraud
- **Implementation:** Reconciliation report

**2. Negative Balance Monitoring**
- **Control:** Report identifies negative balances
- **Detects:** System failures, calculation errors
- **Implementation:** Negative balance report

**3. Audit Trail Review**
- **Control:** Complete transaction log available
- **Detects:** Unauthorized activities, patterns
- **Implementation:** Audit trail report

**4. Unallocated Funds Monitoring**
- **Control:** Report shows unassigned deposits
- **Detects:** Data entry delays, errors
- **Implementation:** Unallocated funds report

### Corrective Controls

**1. Transaction Voiding**
- **Control:** Incorrect transactions can be voided with reason
- **Corrects:** Data entry errors
- **Implementation:** Void function with required reason

**2. Status Changes**
- **Control:** Cases can be reopened if necessary
- **Corrects:** Premature case closures
- **Implementation:** Case status modification

---

## Security & Access Controls

### Authentication

**Current Implementation:**
- **Method:** Session-based authentication
- **Session Duration:** 30 minutes idle timeout
- **Session Security:** Secure cookies, HTTPS enforcement (production)
- **Password Policy:** Django defaults (PBKDF2 hashing, 600,000 iterations)

**Audit Considerations:**
- All users must authenticate before access
- Sessions expire automatically
- Login attempts can be logged
- Failed login tracking available

### Authorization

**Current State:** All authenticated users have full access.

**Planned Enhancement:** Role-based access control (RBAC)
- **Firm Administrator:** Full access
- **Attorney:** Full operational access
- **Paralegal:** Limited access (no deletion/voiding)
- **Bookkeeper:** Financial focus
- **Auditor:** Read-only

**Audit Benefit:** Principle of least privilege, action accountability.

### Data Protection

**In Transit:**
- **Development:** HTTP (Docker internal network)
- **Production:** HTTPS/TLS 1.3 mandatory
- **Headers:** Secure headers enforced (HSTS, X-Frame-Options, etc.)

**At Rest:**
- **Database:** PostgreSQL native encryption (optional)
- **Backups:** Encrypted backup storage recommended
- **Passwords:** Hashed with PBKDF2 (never stored in plain text)

**Audit Benefit:** Client data protected from unauthorized access.

---

## Backup & Disaster Recovery

### Backup Strategy

**Database Backups:**
```bash
# Daily automated backups
docker exec iolta_db_alpine pg_dump -U iolta_user iolta_guard_db \
    | gzip > backup_$(date +%Y%m%d).sql.gz

# Retention: 30 daily, 12 monthly, 7 yearly
```

**Application Backups:**
- Docker volumes backed up daily
- Configuration files versioned in Git
- Static files backed up weekly

**Backup Verification:**
- Monthly restore tests
- Backup integrity checks
- Off-site backup storage

### Disaster Recovery

**Recovery Time Objective (RTO):** 4 hours
**Recovery Point Objective (RPO):** 24 hours (last nightly backup)

**Recovery Procedure:**
1. Provision new infrastructure
2. Restore database from latest backup
3. Restore application files
4. Verify data integrity
5. Test system functionality
6. Resume operations

**Audit Benefit:** Financial data protected against loss.

---

## Audit Procedures

### For External Auditors

#### Pre-Audit Checklist

**System Access:**
- [ ] Provide read-only database access
- [ ] Provide system demonstration
- [ ] Export audit trail reports
- [ ] Generate all standard reports

**Documentation Provided:**
- [ ] This Audit & Compliance Guide
- [ ] Software Architecture Overview
- [ ] Database Schema Documentation
- [ ] List of all users and roles
- [ ] Change log (system modifications)

#### Audit Scope

**Areas for Review:**
1. **Transaction Completeness:** All transactions recorded
2. **Balance Accuracy:** Balances match transaction ledgers
3. **Client/Case Accuracy:** Proper fund allocation
4. **Reconciliation:** Bank statements match internal records
5. **Internal Controls:** Preventative controls functioning
6. **Data Integrity:** No unauthorized modifications
7. **Security:** Access controls appropriate
8. **Backup/Recovery:** Disaster recovery capabilities

#### Audit Procedures

**1. Balance Verification**
```sql
-- Verify client balance matches transaction sum
SELECT
    c.id,
    c.first_name || ' ' || c.last_name as client,
    (
        COALESCE(SUM(CASE WHEN bt.transaction_type = 'DEPOSIT' THEN bt.amount ELSE 0 END), 0) -
        COALESCE(SUM(CASE WHEN bt.transaction_type IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN bt.amount ELSE 0 END), 0)
    ) as calculated_balance
FROM clients c
LEFT JOIN bank_transactions bt ON bt.client_id = c.id AND bt.status != 'voided'
GROUP BY c.id, c.first_name, c.last_name;
```

**2. Reconciliation Test**
- Export uncleared transactions report
- Compare to bank statement
- Verify cleared transactions match bank records
- Confirm outstanding items are legitimate

**3. Internal Control Testing**
- **Test 1:** Attempt withdrawal exceeding balance (should fail)
- **Test 2:** Attempt transaction without client (should fail)
- **Test 3:** Attempt transaction on closed case (should fail)
- **Test 4:** Verify voided transactions excluded from balance

**4. Data Integrity Testing**
- Count total transactions in database
- Verify no deleted transactions (all have created_at)
- Check for negative balances (should be none)
- Verify referential integrity (all FKs valid)

**5. Audit Trail Review**
- Export complete transaction log
- Verify all transactions have timestamps
- Check for suspicious patterns (batch entries, off-hours, etc.)
- Review voided transactions and void reasons

#### Sample SQL Queries for Auditors

**Total Trust Balance:**
```sql
SELECT
    SUM(CASE WHEN transaction_type = 'DEPOSIT' THEN amount ELSE 0 END) as total_deposits,
    SUM(CASE WHEN transaction_type IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN amount ELSE 0 END) as total_withdrawals,
    SUM(CASE WHEN transaction_type = 'DEPOSIT' THEN amount ELSE -amount END) as net_balance
FROM bank_transactions
WHERE status != 'voided';
```

**Transactions by Month:**
```sql
SELECT
    DATE_TRUNC('month', transaction_date) as month,
    transaction_type,
    COUNT(*) as count,
    SUM(amount) as total
FROM bank_transactions
WHERE status != 'voided'
GROUP BY month, transaction_type
ORDER BY month, transaction_type;
```

**Voided Transactions:**
```sql
SELECT
    id,
    transaction_date,
    amount,
    transaction_type,
    description,
    void_reason,
    updated_at as voided_date
FROM bank_transactions
WHERE status = 'voided'
ORDER BY updated_at DESC;
```

**Longest Open Cases:**
```sql
SELECT
    case_number,
    case_title,
    opened_date,
    CURRENT_DATE - opened_date as days_open
FROM cases
WHERE status = 'Open'
ORDER BY days_open DESC
LIMIT 20;
```

---

## Compliance Checklist

### Monthly Compliance Tasks

- [ ] Perform bank reconciliation for all trust accounts
- [ ] Review uncleared transactions
- [ ] Review negative balance report (should be empty)
- [ ] Review unallocated funds report
- [ ] Verify all transactions have client/case assignment
- [ ] Generate and file monthly trust account reports
- [ ] Review closed cases for zero balances
- [ ] Backup database

### Quarterly Compliance Tasks

- [ ] Generate client ledgers for active clients
- [ ] Review inactive client list
- [ ] Test disaster recovery procedure
- [ ] Review user access list
- [ ] Update this compliance documentation
- [ ] Internal audit of controls

### Annual Compliance Tasks

- [ ] External audit (if required by state)
- [ ] Review and update security policies
- [ ] Review record retention policies
- [ ] System security assessment
- [ ] Staff training on trust account procedures
- [ ] State bar compliance filing (if required)

### Pre-Audit Preparation

- [ ] Export complete audit trail
- [ ] Generate all standard reports
- [ ] Prepare bank reconciliations (12 months)
- [ ] List all system users
- [ ] Document any system changes
- [ ] Gather bank statements
- [ ] Prepare this compliance guide for auditor

---

## Regulatory Citations

### ABA Model Rules

**Rule 1.15: Safekeeping Property**
- (a) Separate client property from lawyer's property
- (b) Keep records of client property
- (c) Notify client of receipt of property
- (d) Promptly deliver property to client when due

**Source:** American Bar Association Model Rules of Professional Conduct
**Link:** https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_1_15_safekeeping_property/

### State Bar Rules

*Note: Each state has specific IOLTA rules. Consult your state bar association for requirements in your jurisdiction.*

**Examples:**
- California: Business and Professions Code §6211
- New York: 22 NYCRR Part 1300 (IOLA)
- Texas: Texas Rules of Professional Conduct Rule 1.14

### Accounting Standards

**GAAP (Generally Accepted Accounting Principles)**
- ASC 606: Revenue Recognition
- ASC 840: Leases
- ASC 450: Contingencies

**AICPA Guidelines**
- SAS 122: Auditing Standards
- SSAE 18: Attestation Standards

---

## Appendix

### A. Database Schema (Relevant Tables)

**clients**
- id, client_number, first_name, last_name
- email, phone, address, city, state, zip_code
- trust_account_status, is_active
- created_at, updated_at

**cases**
- id, client_id (FK), case_number, case_title
- matter_type, description, opened_date, closed_date
- status (Open/Closed)
- created_at, updated_at

**bank_transactions**
- id, account_id (FK), client_id (FK), case_id (FK)
- transaction_type, amount, transaction_date
- payee, description, check_number
- status (cleared/voided), void_reason
- created_at, updated_at

**bank_accounts**
- id, account_name, account_number, routing_number
- bank_name, account_type
- current_balance (calculated)
- created_at, updated_at

### B. Report Templates

See [COMPLIANCE_REPORTS.md](./COMPLIANCE_REPORTS.md) for sample report formats.

### C. Contact Information

**System Administrator:** [Your Contact]
**Compliance Officer:** [Your Contact]
**IT Support:** [Your Support Contact]
**External Auditor:** [Auditor Contact]

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-13 | Development Team | Initial release |

**Approval:**

- [ ] Compliance Officer
- [ ] Managing Partner
- [ ] IT Director
- [ ] External Auditor (review)

**Next Review Date:** 2026-02-13 (Quarterly)

---

## Certification

This document accurately represents the audit controls and compliance features of IOLTA Guard as of November 13, 2025.

**Prepared By:** Development Team
**Date:** November 13, 2025
**Contact:** [Your Contact Information]

---

*This document is confidential and intended for audit and compliance purposes only.*
*Unauthorized distribution is prohibited.*

---

**END OF AUDIT & COMPLIANCE GUIDE**
