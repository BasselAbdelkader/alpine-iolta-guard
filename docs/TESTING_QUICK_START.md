# CSV IMPORT TESTING QUICK START

**After merging the import feature, use this guide to test it**

---

## 🧪 6 ESSENTIAL TESTS

### Test 1: Basic Import to Staging (5 min)

**What:** Upload CSV and verify it goes to staging tables

**Steps:**
1. Login as any user
2. Go to Settings → Import CSV Data
3. Upload `test_data.csv`
4. Click "Import"
5. Check status = "Pending Review"

**Verify in database:**
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

# Should have data
SELECT COUNT(*) FROM staging_clients;
SELECT COUNT(*) FROM staging_cases;
SELECT COUNT(*) FROM staging_bank_transactions;

# Should NOT have new production data yet
SELECT COUNT(*) FROM clients WHERE data_source = 'csv_import' ORDER BY created_at DESC LIMIT 5;

\q
```

**Expected:** Staging has data, production does NOT

---

### Test 2: Approve Workflow (5 min)

**What:** Approver reviews and commits staging data to production

**Prerequisites:**
- Grant approval permission:
  ```bash
  docker exec -it iolta_backend_prod python manage.py shell
  ```
  ```python
  from apps.settings.models import UserProfile
  profile = UserProfile.objects.get(user__username='admin')
  profile.can_approve_imports = True
  profile.save()
  exit()
  ```

**Steps:**
1. Logout, login as approver (admin)
2. Go to Approval Dashboard (`/approval-dashboard.html`)
3. See pending import from Test 1
4. Click "View Details"
5. Click "Approve" with notes: "Test approval"

**Verify in database:**
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

# Staging should be empty now
SELECT COUNT(*) FROM staging_clients;  -- Should be 0

# Production should have new data
SELECT client_name, city FROM clients WHERE data_source = 'csv_import' ORDER BY id DESC LIMIT 5;

# Import log should show committed
SELECT approval_status, reviewed_by_id, review_notes FROM import_logs ORDER BY id DESC LIMIT 1;

\q
```

**Expected:** Staging deleted, production has data, status = 'committed'

---

### Test 3: Reject Workflow (5 min)

**What:** Approver rejects import and deletes staging data

**Steps:**
1. Login as regular user
2. Upload another CSV file
3. Verify status = "Pending Review"
4. Logout, login as approver
5. Go to Approval Dashboard
6. Click "Reject" with notes: "Bad data"

**Verify in database:**
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

# Staging should be empty
SELECT COUNT(*) FROM staging_clients;  -- Should be 0

# Import log should show rejected
SELECT approval_status, review_notes FROM import_logs ORDER BY id DESC LIMIT 1;

\q
```

**Expected:** Staging deleted, status = 'rejected', production unchanged

---

### Test 4: Dual Control (3 min)

**What:** User cannot approve own import

**Steps:**
1. Login as user with approval permission (admin)
2. Upload CSV file as THIS USER
3. Try to approve own import

**Expected:** Error message: "You cannot approve your own import (dual control violation)"

**Verify:** Staging data remains, status still 'pending_review'

---

### Test 5: Chronological Order (5 min)

**What:** Transactions processed in date order (oldest first)

**Test CSV:**
Create file with random date order:
```csv
Date,Ref No.,Type,Payee,Account,Memo,Payment,Deposit,Status
2024-01-15,REF003,Deposit,Jane Doe,Client Trust Account,Payment received,,500.00,Cleared
2024-01-10,REF001,Deposit,John Smith,Client Trust Account,Retainer,,1000.00,Cleared
2024-01-20,REF005,Withdrawal,Law Office Supplies,Client Trust Account,Office supplies,50.00,,Cleared
```

**Steps:**
1. Import CSV to staging
2. Approve import
3. Check production transaction order

**Verify in database:**
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

SELECT transaction_date, transaction_type, amount
FROM bank_transactions
WHERE data_source = 'csv_import'
ORDER BY id DESC LIMIT 3;

\q
```

**Expected order (oldest first):**
```
2024-01-10 | DEPOSIT     | 1000.00
2024-01-15 | DEPOSIT     |  500.00
2024-01-20 | WITHDRAWAL  |   50.00
```

---

### Test 6: Permission Check (3 min)

**What:** Users without permission can't approve

**Steps:**
1. Create user without approval permission:
   ```bash
   docker exec -it iolta_backend_prod python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import User
   from apps.settings.models import UserProfile
   user = User.objects.create_user('testuser', password='testpass123')
   profile = UserProfile.objects.create(user=user, can_approve_imports=False)
   exit()
   ```

2. Login as testuser
3. Try to access `/approval-dashboard.html`

**Expected:** Can only see OWN pending imports (not others')

4. Try to approve via API:
   ```bash
   curl -X POST http://localhost/api/v1/imports/approve/1/ \
     -H "Cookie: sessionid=<testuser_session>" \
     -H "Content-Type: application/json"
   ```

**Expected:** 403 Forbidden error

---

## 🎯 QUICK VERIFICATION COMMANDS

### Check if staging tables exist:
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db -c "\dt staging_*"
```

### Check if import_logs has approval fields:
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db -c "\d import_logs"
```

### Check if imports app is registered:
```bash
docker exec -it iolta_backend_prod python manage.py shell -c "from apps.imports.models import StagingClient; print('OK')"
```

### Check if API endpoints exist:
```bash
docker exec -it iolta_backend_prod python manage.py show_urls | grep imports
```

### Check current pending imports:
```bash
curl -X GET http://localhost/api/v1/imports/pending/ \
  -H "Cookie: sessionid=<your_session>" \
  -H "Content-Type: application/json"
```

---

## 📊 TEST DATA SAMPLES

### Sample CSV File (test_data.csv)

```csv
Date,Ref No.,Type,Payee,Account,Memo,Payment,Deposit,Reconciliation Status,Added in Banking,Balance
2024-01-10,REF001,Deposit,John Smith,Client Trust Account,Retainer,,1000.00,Cleared,2024-01-10,1000.00
2024-01-15,REF002,Deposit,Jane Doe,Client Trust Account,Settlement,,500.00,Cleared,2024-01-15,1500.00
2024-01-20,REF003,Withdrawal,Law Office Supplies,Client Trust Account,Office supplies,50.00,,Cleared,2024-01-20,1450.00
```

### Expected Import Results

**Staging Tables (before approval):**
- `staging_clients`: 2 records (John Smith, Jane Doe)
- `staging_cases`: 2 records (auto-created from client names)
- `staging_bank_transactions`: 3 records
- `import_logs`: 1 record (approval_status='pending_review')

**Production Tables (after approval):**
- `clients`: +2 new records
- `cases`: +2 new records
- `bank_transactions`: +3 new records
- `import_logs`: Updated (approval_status='committed')

---

## 🚨 COMMON ISSUES & FIXES

### Issue: "No module named 'apps.imports'"

**Cause:** `imports` app not in INSTALLED_APPS

**Fix:**
```python
# backend/trust_account_project/settings.py
INSTALLED_APPS = [
    # ...
    'apps.imports',  # Add this
]
```
Then restart: `docker restart iolta_backend_prod`

---

### Issue: API returns 404 for /api/v1/imports/pending/

**Cause:** URL routing not configured

**Fix:**
```python
# backend/trust_account_project/urls.py
urlpatterns = [
    # ...
    path('api/v1/imports/', include('apps.imports.api.urls')),  # Add this
]
```
Then restart: `docker restart iolta_backend_prod`

---

### Issue: "Table staging_clients does not exist"

**Cause:** Migrations not run

**Fix:**
```bash
docker exec -it iolta_backend_prod python manage.py migrate imports
docker exec -it iolta_backend_prod python manage.py migrate settings
```

---

### Issue: Transactions in wrong order

**Cause:** Missing `.order_by()` in approval view

**Fix:** Check `apps/imports/api/views.py:130`:
```python
staging_transactions = StagingBankTransaction.objects.filter(
    import_batch_id=import_batch_id
).order_by('transaction_date', 'staging_id')  # Must have this
```

---

## ✅ SUCCESS CHECKLIST

After running all 6 tests, verify:

- [ ] Test 1: CSV imports to staging (not production)
- [ ] Test 2: Approve workflow commits to production
- [ ] Test 3: Reject workflow deletes staging
- [ ] Test 4: Cannot approve own import
- [ ] Test 5: Transactions in chronological order
- [ ] Test 6: Permissions enforced

**If all pass → Feature merge successful! 🎉**

---

## 📈 PERFORMANCE BENCHMARKS

Expected processing times:

| Operation | Records | Time |
|-----------|---------|------|
| Import to staging | 100 | ~2 sec |
| Import to staging | 1000 | ~10 sec |
| Approve to production | 100 | ~5 sec |
| Approve to production | 1000 | ~30 sec |
| Reject staging | Any | ~1 sec |

If slower, check:
- Database indexes on staging tables
- Transaction atomic blocks
- Network latency

---

## 🔄 CLEANUP AFTER TESTING

After testing, you may want to:

```bash
# Clear all test data from staging
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

DELETE FROM staging_bank_transactions;
DELETE FROM staging_cases;
DELETE FROM staging_clients;

# Delete test imports from import_logs
DELETE FROM import_logs WHERE filename LIKE '%test%';

# Delete test users
DELETE FROM user_profiles WHERE user_id IN (
  SELECT id FROM auth_user WHERE username = 'testuser'
);
DELETE FROM auth_user WHERE username = 'testuser';

\q
```

---

**Happy Testing! 🧪**
