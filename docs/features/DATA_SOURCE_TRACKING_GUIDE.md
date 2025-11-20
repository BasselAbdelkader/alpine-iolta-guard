# Data Source Tracking - Implementation Guide

**Date:** November 10, 2025
**Status:** ✅ **IMPLEMENTED**
**Purpose:** Track how data was inserted (webapp, csv, api) and log all imports

---

## 🎯 Overview

We now track the source of all data entries in the system:
- **`data_source`** field added to: clients, cases, vendors, bank_transactions
- **`import_logs`** table tracks all import operations

---

## 📊 Data Source Field

### Values
- **`webapp`** - Created through web interface (default)
- **`csv`** - Imported from CSV file
- **`api`** - Created via API calls

### Tables Updated
1. **clients** - `data_source` column
2. **cases** - `data_source` column
3. **vendors** - `data_source` column
4. **bank_transactions** - `data_source` column

### Default Behavior
- All existing records: `data_source='webapp'`
- QuickBooks imports: `data_source='csv'`
- Future API integrations: `data_source='api'`

---

## 📋 Import Logs Table

### Purpose
Tracks every import operation with detailed statistics and error logs.

### Schema
```sql
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    import_type VARCHAR(50),        -- 'quickbooks_csv', 'generic_csv', 'api_bulk'
    filename VARCHAR(255),           -- Original filename
    status VARCHAR(20),              -- 'in_progress', 'completed', 'failed', 'partial'

    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Statistics
    total_rows INTEGER,
    clients_created INTEGER,
    clients_existing INTEGER,
    cases_created INTEGER,
    transactions_created INTEGER,
    transactions_skipped INTEGER,

    -- Error tracking
    errors JSONB,                    -- Array of error objects
    summary JSONB,                   -- Additional metadata

    -- Audit
    created_by_id INTEGER,           -- User who performed import
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 🔍 Verification Queries

### Check Data Source Distribution

```sql
-- Summary by table
SELECT
    'clients' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE data_source = 'webapp') as webapp,
    COUNT(*) FILTER (WHERE data_source = 'csv') as csv,
    COUNT(*) FILTER (WHERE data_source = 'api') as api
FROM clients
UNION ALL
SELECT
    'cases',
    COUNT(*),
    COUNT(*) FILTER (WHERE data_source = 'webapp'),
    COUNT(*) FILTER (WHERE data_source = 'csv'),
    COUNT(*) FILTER (WHERE data_source = 'api')
FROM cases
UNION ALL
SELECT
    'vendors',
    COUNT(*),
    COUNT(*) FILTER (WHERE data_source = 'webapp'),
    COUNT(*) FILTER (WHERE data_source = 'csv'),
    COUNT(*) FILTER (WHERE data_source = 'api')
FROM vendors
UNION ALL
SELECT
    'bank_transactions',
    COUNT(*),
    COUNT(*) FILTER (WHERE data_source = 'webapp'),
    COUNT(*) FILTER (WHERE data_source = 'csv'),
    COUNT(*) FILTER (WHERE data_source = 'api')
FROM bank_transactions;
```

**Run in database:**
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    'clients' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE data_source = 'webapp') as webapp,
    COUNT(*) FILTER (WHERE data_source = 'csv') as csv,
    COUNT(*) FILTER (WHERE data_source = 'api') as api
FROM clients
UNION ALL
SELECT 'cases', COUNT(*),
    COUNT(*) FILTER (WHERE data_source = 'webapp'),
    COUNT(*) FILTER (WHERE data_source = 'csv'),
    COUNT(*) FILTER (WHERE data_source = 'api')
FROM cases
UNION ALL
SELECT 'bank_transactions', COUNT(*),
    COUNT(*) FILTER (WHERE data_source = 'webapp'),
    COUNT(*) FILTER (WHERE data_source = 'csv'),
    COUNT(*) FILTER (WHERE data_source = 'api')
FROM bank_transactions;
"
```

### View All Imports

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    id,
    import_type,
    filename,
    status,
    clients_created,
    cases_created,
    transactions_created,
    transactions_skipped,
    started_at,
    completed_at,
    EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds
FROM import_logs
ORDER BY started_at DESC
LIMIT 10;
"
```

### View Latest Import Details

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    *
FROM import_logs
ORDER BY started_at DESC
LIMIT 1;
"
```

### View Import Errors

```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    id,
    import_type,
    filename,
    status,
    started_at,
    errors
FROM import_logs
WHERE jsonb_array_length(errors) > 0
ORDER BY started_at DESC;
"
```

### Find QuickBooks Imported Data

```bash
# Clients from QuickBooks
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    client_number,
    first_name || ' ' || last_name as name,
    data_source,
    created_at
FROM clients
WHERE data_source = 'csv'
ORDER BY created_at DESC
LIMIT 10;
"

# Cases from QuickBooks
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    case_number,
    case_title,
    data_source,
    created_at
FROM cases
WHERE data_source = 'csv'
ORDER BY created_at DESC
LIMIT 10;
"

# Transactions from QuickBooks
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
    transaction_date,
    transaction_type,
    amount,
    payee,
    data_source,
    created_at
FROM bank_transactions
WHERE data_source = 'csv'
ORDER BY created_at DESC
LIMIT 10;
"
```

---

## 📈 Reporting

### Import Success Rate

```sql
SELECT
    status,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM import_logs
GROUP BY status;
```

### Imports by Type

```sql
SELECT
    import_type,
    COUNT(*) as total_imports,
    SUM(clients_created) as total_clients_created,
    SUM(cases_created) as total_cases_created,
    SUM(transactions_created) as total_transactions_created,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds
FROM import_logs
WHERE status IN ('completed', 'partial')
GROUP BY import_type;
```

### Recent Import Activity

```sql
SELECT
    DATE(started_at) as date,
    COUNT(*) as imports,
    SUM(clients_created) as clients,
    SUM(cases_created) as cases,
    SUM(transactions_created) as transactions
FROM import_logs
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY date DESC;
```

---

## 🔧 Usage in Code

### QuickBooks Importer (Already Implemented)

```python
from apps.clients.utils import QuickBooksImporter

# Create importer with filename
importer = QuickBooksImporter(user, filename='quickbooks.csv')

# Import data - automatically creates import_log and sets data_source='csv'
result = importer.import_data(validated_data)

# Result includes import_log_id
print(result['summary']['import_log_id'])
```

### Manual Data Source Setting

For future implementations (e.g., API imports):

```python
# When creating via API
client = Client.objects.create(
    client_number='API-0001',
    first_name='John',
    last_name='Doe',
    data_source='api'  # Set source
)

# When creating via webapp forms (default)
client = Client.objects.create(
    client_number='TEST-0080',
    first_name='Jane',
    last_name='Smith',
    data_source='webapp'  # Or omit - defaults to 'webapp'
)
```

### Querying by Source

```python
# Get all CSV-imported clients
csv_clients = Client.objects.filter(data_source='csv')

# Get all webapp-created transactions
webapp_transactions = BankTransaction.objects.filter(data_source='webapp')

# Count by source
from django.db.models import Count
stats = Client.objects.values('data_source').annotate(count=Count('id'))
```

---

## 🧹 Cleanup

### Remove QuickBooks Imported Data

```sql
-- Delete in correct order (foreign keys)
DELETE FROM bank_transactions WHERE data_source = 'csv';
DELETE FROM cases WHERE data_source = 'csv';
DELETE FROM clients WHERE data_source = 'csv';

-- Delete import logs (optional)
DELETE FROM import_logs WHERE import_type = 'quickbooks_csv';
```

**Or via bash:**
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
DELETE FROM bank_transactions WHERE data_source = 'csv';
DELETE FROM cases WHERE data_source = 'csv';
DELETE FROM clients WHERE data_source = 'csv';
"
```

---

## 📊 Dashboard Queries

### Data Entry Summary

```sql
-- Summary of how all data was entered
SELECT
    'Clients' as entity_type,
    data_source,
    COUNT(*) as count
FROM clients
GROUP BY data_source
UNION ALL
SELECT 'Cases', data_source, COUNT(*)
FROM cases
GROUP BY data_source
UNION ALL
SELECT 'Transactions', data_source, COUNT(*)
FROM bank_transactions
GROUP BY data_source
ORDER BY entity_type, data_source;
```

### Import History

```sql
SELECT
    TO_CHAR(started_at, 'YYYY-MM-DD HH24:MI') as time,
    import_type,
    filename,
    status,
    clients_created || ' clients, ' ||
    cases_created || ' cases, ' ||
    transactions_created || ' transactions' as summary,
    CASE
        WHEN status = 'completed' THEN '✅'
        WHEN status = 'partial' THEN '⚠️'
        WHEN status = 'failed' THEN '❌'
        ELSE '🔄'
    END as icon
FROM import_logs
ORDER BY started_at DESC
LIMIT 20;
```

---

## 🎯 Benefits

### 1. **Data Lineage**
- Know exactly where each record came from
- Trace imports back to original files
- Audit data entry methods

### 2. **Error Tracking**
- Complete history of all import attempts
- Detailed error logs for debugging
- Statistics for success rates

### 3. **Selective Operations**
- Delete only CSV-imported data
- Report on manually-entered vs imported
- Identify data quality issues by source

### 4. **Compliance & Audit**
- Who imported what, when
- Original filenames preserved
- Full audit trail for regulatory requirements

---

## ✅ Status

**Implementation:** ✅ Complete
**Database:** ✅ Updated (all existing records set to 'webapp')
**Importer:** ✅ Updated (sets data_source='csv')
**Import Logs:** ✅ Created and integrated
**Indexes:** ✅ Added for performance

**Ready to Use!** Next QuickBooks import will automatically:
- Set `data_source='csv'` on all created records
- Create import_log entry with full statistics
- Track all errors and successes

---

## 🔮 Future Enhancements

1. **API Integration**
   - Set `data_source='api'` for API-created records
   - Create API import logs

2. **Bulk Edit Source**
   - Admin interface to change data_source if incorrect

3. **Import Dashboard**
   - Web UI to view import_logs table
   - Visual charts of data sources
   - Download error reports

4. **Scheduled Imports**
   - Automated import tracking
   - Email notifications on completion

---

**Implemented by:** Claude Code
**Date:** November 10, 2025
**Status:** 🟢 **PRODUCTION READY**
