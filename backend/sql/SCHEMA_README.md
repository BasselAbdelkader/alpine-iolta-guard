# IOLTA Guard Trust Account System - Database Schema

**File:** `twentysixnovember.sql`  
**Date:** November 26, 2025  
**Version:** Consolidated Schema (Post-Refactor)

## Overview

This SQL file contains the complete database schema for the IOLTA Guard Trust Account System with all field consolidations applied.

## Key Changes from Previous Versions

### 1. **Consolidated Reference Fields**
- **Before:** `check_number` + `reference_number` (two separate fields)
- **After:** `reference_number` only (single field for all transaction references)
- **Impact:** Stores check numbers, wire references, ACH numbers, etc. in one field

### 2. **Consolidated Client Name Fields**
- **Before:** `first_name` + `last_name` (two separate fields)
- **After:** `client_name` (single field)
- **Impact:** Supports business names, individuals, and various name formats

### 3. **New Fields Added**
- `bank_transactions.check_is_printed` - Boolean to track if check has been printed
- `check_sequences` table - Manages sequential check numbering per bank account
- `law_firm` table - Stores law firm configuration and details

## Database Tables (28 Total)

### Core Business Tables
1. **bank_transactions** - Main ledger (withdrawals, deposits, checks, etc.)
   - `reference_number` - Consolidated field for check #, wire ref, etc.
   - `check_is_printed` - Tracks printing status
   
2. **clients** - Client/customer information
   - `client_name` - Single consolidated name field
   
3. **cases** - Legal cases linked to clients
4. **vendors** - Payees and service providers
5. **bank_accounts** - Bank account details
6. **settlements** - 3-way settlement tracking
7. **settlement_distributions** - Settlement payment distributions

### Settings & Configuration
8. **law_firm** - Law firm details (name, address, phone, etc.)
9. **check_sequences** - Check number sequencing per account
10. **settings** - Application settings
11. **vendor_types** - Vendor categorization

### Audit & Import
12. **bank_transaction_audit** - Transaction change history
13. **import_logs** - Data import tracking
14. **import_audit** - Import audit trail
15. **bank_reconciliations** - Monthly reconciliation records
16. **settlement_reconciliations** - Settlement reconciliation tracking

### System Tables
17. **case_number_counter** - Case number sequencing
18. **user_profiles** - Extended user information
19-28. **Django/Auth tables** - Authentication and framework tables

## Important Fields to Note

### bank_transactions Table
```sql
reference_number VARCHAR(100) NOT NULL  -- Consolidated field (was check_number + reference_number)
check_is_printed BOOLEAN NOT NULL        -- NEW: Tracks if check was printed
payee VARCHAR(255) NOT NULL              -- Payee name
status VARCHAR(20) NOT NULL              -- pending/cleared/voided
transaction_type VARCHAR(20) NOT NULL    -- DEPOSIT/WITHDRAWAL
```

### clients Table
```sql
client_name VARCHAR(200) NOT NULL        -- Consolidated field (was first_name + last_name)
client_number VARCHAR(50)                -- Unique client identifier (CLT-2025-001)
trust_account_status VARCHAR(30) NOT NULL -- ACTIVE_WITH_FUNDS, etc.
```

### check_sequences Table
```sql
bank_account_id BIGINT NOT NULL          -- Links to bank_accounts
next_check_number INTEGER NOT NULL       -- Next available check number
last_assigned_number INTEGER             -- Last assigned check number
```

## How to Use This Schema

### Fresh Installation
```bash
# Create database
docker exec iolta_db_alpine createdb -U iolta_user iolta_guard_db

# Load schema
docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db < /app/sql/twentysixnovember.sql

# Run Django migrations to sync
docker exec iolta_backend_alpine python /app/manage.py migrate --fake
```

### Backup Current Database
```bash
docker exec iolta_db_alpine pg_dump -U iolta_user -d iolta_guard_db > backup_$(date +%Y%m%d).sql
```

### Verify Schema
```bash
# Check bank_transactions has reference_number (not check_number)
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\d bank_transactions" | grep reference_number

# Check clients has client_name (not first_name/last_name)
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\d clients" | grep client_name
```

## Schema Statistics
- **Total Tables:** 28
- **Total Lines:** 1,913
- **File Size:** 53KB
- **Database Version:** PostgreSQL 16.9

## Notes
- All tables use `bigint` for primary keys (auto-incrementing)
- Timestamps use `timestamp with time zone`
- Currency fields use `numeric(15,2)` for precision
- No ownership or privileges included (--no-owner --no-privileges)
