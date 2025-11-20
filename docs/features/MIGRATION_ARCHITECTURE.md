# Migration Architecture - SaaS Ready

## Overview

This document describes the final migration architecture for IOLTA Guard, designed for fully automated SaaS provisioning.

**Status:** ✅ PRODUCTION READY

---

## Migration Files

All apps use clean `0001_initial.py` migrations with proper dependency ordering:

```
backend/apps/
├── clients/migrations/
│   └── 0001_initial.py          (No dependencies)
├── vendors/migrations/
│   └── 0001_initial.py          (Depends: clients)
├── bank_accounts/migrations/
│   └── 0001_initial.py          (Depends: clients, vendors)
├── settlements/migrations/
│   └── 0001_initial.py          (Depends: clients, vendors, bank_accounts)
├── settings/migrations/
│   └── 0001_initial.py          (Depends: bank_accounts)
└── reports/migrations/
    └── 0001_initial.py          (No dependencies - views only)
```

---

## Migration Order (Automatic)

Django automatically runs migrations in correct dependency order:

1. **clients** - Creates `clients` and `cases` tables
2. **vendors** - Creates `vendors` and `vendor_types` tables (FK to clients)
3. **bank_accounts** - Creates `bank_accounts`, `bank_transactions`, `bank_reconciliations`, `bank_transaction_audit` (FKs to clients, vendors)
4. **settlements** - Creates `settlements`, `settlement_distributions`, `settlement_reconciliations` (FKs to clients, vendors, bank_accounts)
5. **settings** - Creates `law_firm`, `settings`, `import_audit`, `check_sequences` (FK to bank_accounts)
6. **reports** - Creates database views (no tables)

---

## Key Schema Features

### Clients App
```python
# Table: clients
- client_number (unique, auto-generated)
- first_name, last_name, email, phone
- client_type (individual/business/estate)
- is_active (boolean)
- data_source (webapp/csv_import/api_import)
- import_batch_id (nullable - links to ImportAudit)

# Table: cases
- case_number (unique, auto-generated)
- client_id (FK to clients)
- case_title, case_description, case_amount
- case_status (Open/Pending Settlement/Closed/On Hold)
- opened_date, closed_date
- data_source, import_batch_id
```

### Vendors App
```python
# Table: vendors
- vendor_number (unique, auto-generated)
- vendor_name, contact_person, email, phone
- address, city, state, zip_code
- vendor_type (FK to vendor_types)
- client (FK to clients - nullable, for client-as-vendor)
- data_source, import_batch_id

# Table: vendor_types
- name (Medical Provider, Legal Services, Court/Filing, etc.)
```

### Bank Accounts App
```python
# Table: bank_accounts
- account_number (unique)
- bank_name, bank_address, routing_number
- account_type (Trust Account/Operating Account/Escrow Account)
- opening_balance, next_check_number
- data_source (webapp)

# Table: bank_transactions
- transaction_number (unique, auto-generated)
- bank_account (FK)
- client (FK - nullable), case (FK - nullable), vendor (FK - nullable)
- transaction_date, transaction_type (DEPOSIT/WITHDRAWAL)
- amount, description, check_memo
- reference_number (check number for withdrawals, receipt for deposits)
- item_type (CLIENT_DEPOSIT, VENDOR_PAYMENT, etc.)
- status (pending/cleared/voided/reconciled)
- data_source, import_batch_id

# Table: bank_reconciliations
- bank_account (FK)
- reconciliation_date, statement_balance, book_balance
- is_reconciled, reconciled_by, reconciled_at

# Table: bank_transaction_audit
- transaction (FK)
- action (CREATED/UPDATED/CLEARED/VOIDED/UNVOIDED/DELETED)
- action_date, action_by
- old_values (JSON), new_values (JSON)
- change_reason, ip_address
```

### Settlements App
```python
# Table: settlements
- settlement_number (unique, auto-generated)
- client (FK), case (FK - nullable), bank_account (FK)
- settlement_date, total_amount
- status (PENDING/IN_PROGRESS/COMPLETED/CANCELLED)
- notes, created_by

# Table: settlement_distributions
- settlement (FK)
- distribution_type (VENDOR_PAYMENT, CLIENT_REFUND, ATTORNEY_FEES, etc.)
- amount, description, check_number
- vendor (FK - nullable), client (FK - nullable)
- is_paid, paid_date

# Table: settlement_reconciliations
- settlement (OneToOne FK)
- bank_balance_before, bank_balance_after
- client_balance_before, client_balance_after
- total_distributions
- reconciliation_status (PENDING/BALANCED/UNBALANCED/RESOLVED)
```

### Settings App
```python
# Table: law_firm
- firm_name, doing_business_as
- address_line1, address_line2, city, state, zip_code
- phone, fax, email, website
- principal_attorney, attorney_bar_number, attorney_state
- trust_account_required, iolta_compliant
- trust_account_certification_date
- tax_id, state_registration

# Table: settings
- category, key, value
- display_order, is_active
- Unique together: (category, key)

# Table: import_audit
- import_date, import_type (csv/api)
- file_name, status
- total_records, successful_records, failed_records
- clients_created, cases_created, transactions_created, vendors_created
- clients_skipped, cases_skipped, vendors_skipped
- total_clients_in_csv, total_cases_in_csv, etc.
- preview_data, preview_errors, error_log
- imported_by

# Table: check_sequences
- bank_account (OneToOne FK)
- next_check_number
- last_assigned_number, last_assigned_date
```

---

## Indexes and Performance

### Bank Transactions (Most Queried)
```python
indexes = [
    Index(fields=['bank_account', 'transaction_date']),
    Index(fields=['client_id']),
    Index(fields=['case_id']),
    Index(fields=['vendor_id']),
    Index(fields=['transaction_date', 'transaction_type']),
    Index(fields=['transaction_number']),
    Index(fields=['status', 'transaction_date']),
    Index(fields=['status']),
    Index(fields=['check_number']),
    Index(fields=['reference_number']),
]
```

### Bank Transaction Audit (Compliance)
```python
indexes = [
    Index(fields=['transaction', '-action_date']),
    Index(fields=['action']),
    Index(fields=['action_by']),
    Index(fields=['action_date']),
]
```

---

## Data Source Tracking

All imported entities track their origin:

```python
data_source choices:
- 'webapp' - Created via web interface
- 'csv_import' - Imported from CSV file
- 'api_import' - Imported via API

import_batch_id:
- Links to ImportAudit.id for full audit trail
- Allows batch deletion of imported data
```

---

## Deployment Process

### 1. Build Docker Images
```bash
docker-compose -f docker-compose.alpine.yml build
```

This copies all migration files from `backend/apps/*/migrations/` into the backend container at `/app/apps/*/migrations/`.

### 2. Start Services
```bash
docker-compose -f docker-compose.alpine.yml up -d
```

Starts:
- PostgreSQL 16 Alpine
- Django backend (Alpine)
- Nginx frontend (Alpine)

### 3. Run Migrations
```bash
docker exec iolta_backend_alpine python manage.py migrate
```

Django automatically:
1. Creates `django_migrations` table
2. Runs migrations in dependency order
3. Records each migration in `django_migrations`
4. Creates all tables, indexes, constraints

**Result:** Fully working schema with no data.

### 4. Import Data (Optional)
```bash
cat essential_data_only.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db
```

Imports:
- 79 Clients
- 81 Cases
- 9 Vendors
- 100 Bank Transactions
- 1 Law Firm record
- 1 Bank Account
- All vendor types and settings

---

## SaaS Automation

### For New Law Firm (Clean Slate)
```bash
# Build and start
docker-compose -f docker-compose.alpine.yml build
docker-compose -f docker-compose.alpine.yml up -d

# Wait for healthy
sleep 120

# Migrate
docker exec iolta_backend_alpine python manage.py migrate

# Create admin
docker exec -it iolta_backend_alpine python manage.py createsuperuser

# Done! Clean database ready for customer data
```

### For Demo/Testing (With Sample Data)
```bash
# Same as above, plus:
cat essential_data_only.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db

# Done! Database with realistic sample data
```

---

## Zero Circular Dependencies

Previous issues (FIXED):
- ✅ No self-referencing dependencies
- ✅ No circular dependencies between apps
- ✅ Clean dependency tree: clients → vendors → bank_accounts → settlements → settings

**Verification:**
```bash
docker exec iolta_backend_alpine python manage.py migrate --plan
```

Shows migration order Django will use. Should complete without errors.

---

## Database Table Names

All models explicitly set `db_table` in Meta:

```python
class Client(models.Model):
    class Meta:
        db_table = 'clients'  # Not 'clients_client'

class BankAccount(models.Model):
    class Meta:
        db_table = 'bank_accounts'  # Not 'bank_accounts_bankaccount'
```

This ensures:
- Clean, predictable table names
- No Django auto-generated names
- Easy database debugging
- Matches legacy expectations

---

## Migration History Reset

All apps start at `0001_initial.py`:

**Before (Broken):**
```
clients/
├── 0001_initial.py        (missing fields)
├── 0002_add_fields.py     (conflicts)
├── 0003_sample_data.py    (wrong fields)
```

**After (Clean):**
```
clients/
└── 0001_initial.py        (complete schema)
```

**How We Got Here:**
1. Deleted all old migrations
2. Let Django inspect current models
3. Generated fresh migrations with `makemigrations`
4. Renamed `0002_initial.py` → `0001_initial.py`
5. Removed self-referencing dependencies
6. Tested on fresh database

---

## Essential Data Export

**Includes Only User Tables:**
```bash
pg_dump --data-only --column-inserts \
  --table=clients \
  --table=cases \
  --table=vendors \
  --table=vendor_types \
  --table=bank_accounts \
  --table=bank_transactions \
  --table=law_firm
```

**Excludes System Tables:**
- ❌ django_migrations (auto-created by migrate)
- ❌ django_session (user sessions)
- ❌ django_admin_log (admin actions)
- ❌ auth_user (created by createsuperuser)
- ❌ settlements (customer-specific)
- ❌ import_audit (customer-specific)

---

## File Transfer for Deployment

**Required Files:**
```
/home/amin/Projects/ve_demo/
├── docker-compose.alpine.yml       # Orchestration config
├── Dockerfile.alpine.backend       # Backend image definition
├── Dockerfile.alpine.frontend      # Frontend image definition
├── .env                            # Environment variables
├── account.json                    # Service account (if needed)
├── essential_data_only.sql         # Optional sample data
├── backend/                        # Django code + migrations
│   └── apps/*/migrations/
└── frontend/                       # HTML/JS/CSS
```

**Transfer Command:**
```bash
scp -r backend/ frontend/ database/ docker-compose.alpine.yml \
  Dockerfile.alpine.* .env essential_data_only.sql \
  root@customer-server:/root/iolta/
```

---

## Verification Commands

### Check Migrations Applied
```bash
docker exec iolta_backend_alpine python manage.py showmigrations
```

Should show `[X]` for all migrations.

### Check Table Structure
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\dt"
```

Should show all 20+ tables.

### Check Data Imported
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  (SELECT COUNT(*) FROM clients) as clients,
  (SELECT COUNT(*) FROM cases) as cases,
  (SELECT COUNT(*) FROM vendors) as vendors,
  (SELECT COUNT(*) FROM bank_transactions) as transactions;
"
```

Should show: 79 clients, 81 cases, 9 vendors, 100 transactions.

---

## Rollback Strategy

If deployment fails:

```bash
# Stop containers
docker-compose -f docker-compose.alpine.yml down -v

# Remove images
docker rmi iolta-guard-backend-alpine:latest
docker rmi iolta-guard-frontend-alpine:latest

# Start fresh
docker-compose -f docker-compose.alpine.yml build
docker-compose -f docker-compose.alpine.yml up -d
docker exec iolta_backend_alpine python manage.py migrate
```

---

## Summary

✅ **Migrations:** Clean, dependency-ordered, no conflicts
✅ **Schema:** Complete with all tables, indexes, constraints
✅ **Data Export:** Essential tables only, no system tables
✅ **Automation:** Fully scripted deployment process
✅ **SaaS Ready:** Works for clean slate OR with sample data
✅ **Tested:** Working on localhost, ready for customer deployment

**Next Customer Deployment:** Just run the 7 steps in CUSTOMER_DEPLOYMENT_WITH_DATA.md
