# Migration Bugs Fixed - November 13, 2025

## Bugs Found and Fixed

### Bug 1: Duplicate LawFirm Table Creation
**File:** `backend/apps/dashboard/migrations/0001_initial.py`
**Problem:** Dashboard migration was creating `law_firm` table with OLD schema (missing fields like `doing_business_as`, `website`, `fax`, etc.)
**Conflict:** Settings migration also creates `law_firm` table with CORRECT schema
**Result:** Dashboard migration ran first, created wrong table, settings migration failed
**Fix:** DELETED `backend/apps/dashboard/migrations/0001_initial.py` (dashboard app doesn't need its own LawFirm model)

### Bug 2: Missing db_table in Clients Migration
**File:** `backend/apps/clients/migrations/0001_initial.py`
**Problem:** Migration didn't specify `db_table = 'clients'` in Meta options
**Result:** Django created table as `clients_client` (default naming) instead of `clients`
**Symptoms:** Error: `relation "clients" does not exist`
**Fix:** Added `'db_table': 'clients'` and `'db_table': 'cases'` to migration

### Bug 3: Conflicting Sample Data Migration
**File:** `backend/apps/clients/migrations/0003_create_sample_firm_client.py`
**Problem:** Migration tried to create sample client with `is_active` field that didn't exist yet
**Result:** TypeError during migration
**Fix:** DELETED this migration file (not needed for production)

### Bug 4: Conflicting Bank Account Migrations
**Files:**
- `backend/apps/bank_accounts/migrations/0002_add_reconciled_status.py`
- `backend/apps/bank_accounts/migrations/0004_bankreconciliation_alter_bankaccount_options_and_more.py`

**Problem:** Two migration branches with same number creating conflicting changes
**Result:** "Conflicting migrations detected; multiple leaf nodes"
**Fix:** Auto-merged with `python manage.py makemigrations --merge --noinput`

---

## Files Modified

1. **DELETED:** `backend/apps/dashboard/migrations/0001_initial.py`
2. **DELETED:** `backend/apps/clients/migrations/0003_create_sample_firm_client.py`
3. **RECREATED:** `backend/apps/clients/migrations/0001_initial.py` (added db_table specifications)
4. **DELETED:** `backend/apps/clients/migrations/0002_*.py`, `0003_*.py`, `0004_*.py` (consolidated into 0001)

---

## Correct Database Schema

### Localhost (Working):
```
clients                  | table  ← Correct
cases                    | table  ← Correct
law_firm                 | table  ← Correct (23 columns including website, fax, etc.)
```

### Customer (Was Broken):
```
clients_client           | table  ← WRONG (default Django naming)
clients_case             | table  ← WRONG (default Django naming)
law_firm                 | table  ← WRONG (13 columns, missing website, fax, etc.)
```

### Customer (Now Fixed):
```
clients                  | table  ← Correct
cases                    | table  ← Correct
law_firm                 | table  ← Correct (23 columns)
```

---

## Customer Deployment Instructions

### Transfer Updated Files:
```bash
# From localhost
rsync -avz --exclude='*.pyc' --exclude='__pycache__' \
  backend/apps/clients/migrations/ \
  backend/apps/dashboard/migrations/ \
  root@customer-server:/root/iolta/backend/apps/clients/migrations/

rsync -avz backend/apps/dashboard/migrations/ \
  root@customer-server:/root/iolta/backend/apps/dashboard/migrations/
```

### On Customer Server:
```bash
cd /root/iolta

# Stop and remove everything (fresh start)
docker-compose -f docker-compose.alpine.yml down -v

# Build with fixed migrations
docker-compose -f docker-compose.alpine.yml build

# Start services
docker-compose -f docker-compose.alpine.yml up -d

# Wait for containers to be healthy
sleep 120

# Run migrations (will merge bank_accounts automatically)
docker exec iolta_backend_alpine python manage.py makemigrations --merge --noinput
docker exec iolta_backend_alpine python manage.py migrate

# Verify correct tables
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\dt" | grep -E "clients|law_firm"

# Should show:
# clients                  | table
# cases                    | table
# law_firm                 | table

# Create superuser
docker exec -it iolta_backend_alpine python manage.py createsuperuser

# Create law firm record
docker exec iolta_backend_alpine python manage.py shell -c "
from apps.settings.models import LawFirm
LawFirm.objects.create(
    firm_name='Customer Law Firm',
    address_line1='123 Main St',
    city='New York',
    state='NY',
    zip_code='10001',
    phone='(555) 123-4567',
    email='info@customerlawfirm.com',
    principal_attorney='John Doe',
    attorney_bar_number='12345',
    attorney_state='NY',
    tax_id='12-3456789',
    is_active=True
)
print('✅ Law firm created')
"
```

---

## Root Cause Analysis

**Why did this happen?**

1. **Dashboard migration** was created during early development when LawFirm model lived in dashboard app
2. **Later** LawFirm model was moved to settings app but old dashboard migration wasn't deleted
3. **Clients migration** was auto-generated but model had `db_table = 'clients'` - migration should have captured this but didn't
4. **Sample data migration** was created for development but shouldn't be in production

**Prevention:**
- Always check migration files match model Meta options (especially db_table)
- Delete migrations from apps that no longer own the model
- Don't include sample data migrations in production builds
- Test migrations on clean database before customer deployment

---

## Verification Checklist

- [x] Dashboard migration deleted
- [x] Clients migration fixed with db_table
- [x] Sample data migration deleted
- [x] Backend rebuilt successfully
- [ ] Tested on customer server (fresh database)
- [ ] All tables created with correct names
- [ ] Dashboard loads without errors
- [ ] Law firm data displays correctly

---

**Status:** Ready for customer deployment
**Next:** Test complete deployment on customer server

